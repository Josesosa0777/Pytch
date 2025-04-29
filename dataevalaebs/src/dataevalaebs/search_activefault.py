# -*- dataeval: init -*-

import numpy

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList
from measproc.report2 import Report
from measparser.signalgroup import SignalGroupList
from measparser.signalproc import selectTimeScale
from aebs.labeling.system_status import ActiveFault
from measparser.signalgroup import SignalGroupError

ENABLE_HACK_FOR_GROSSE_VEHNE = True  # Redmine #2263

class Search(iSearch):
  def check(self):
    smess_groups = []
    smess_groups.extend([{'fault': ('ACC_S02', 'ActiveFault%02d' % i)}
                         for i in xrange(1, 9)])
    smess_groups = self.source.filterSignalGroups(smess_groups)
    smess_groups = SignalGroupList.from_arbitrary(smess_groups, self.source)
    a087_groups = []
    for i in xrange(1, 4):
      a087_groups.extend([{'fault': ('General_radar_status', 'fault_%01d_ID_bit8' % i)},
                          {'fault': ('General_radar_status', 'fault_%01d_ID' % i)}])
    a087_groups = self.source.filterSignalGroups(a087_groups)
    a087_groups = SignalGroupList.from_arbitrary(a087_groups, self.source)
    if not (sum([len(grp) for grp in smess_groups])
            and sum([len(grp) for grp in a087_groups])):
      raise SignalGroupError
    groups = {'smess_fault': smess_groups, 'a087_fault': a087_groups}

    times = []
    strict_grow = True
    for fault_type in groups.iterkeys():
      if sum([len(grp) for grp in groups[fault_type]]):
        try:
          fault_time = groups[fault_type].select_time_scale(strictly_growing_check=strict_grow)
        except IndexError:
          continue
        else:
          times.append(fault_time)
    try:
      time = selectTimeScale(times, StrictlyGrowingCheck=strict_grow)
    except IndexError, e:
      raise AssertionError(e.message)

    return groups, time

  def fill(self, groups, time):
    active_fault = ActiveFault()
    labels = self.batch.get_labelgroups(active_fault.LABEL_GROUP)
    
    reports = [Report(cIntervalList(time), 'trw-active-faults', votes=labels),
               Report(cIntervalList(time), 'a087-active-faults', votes=labels)]

    for fault_type, report in zip(groups.iterkeys(), reports):
      is_dtc_id = fault_type != 'a087_fault'
      if sum([len(grp) for grp in groups[fault_type]]):
        iter_faults = iter(groups[fault_type].get_value('fault', ScaleTime=time))
        for fault in iter_faults:
          if ENABLE_HACK_FOR_GROSSE_VEHNE:
            if (("MAN_GV" in self.source.FileName or
                 "GV_TGX" in self.source.FileName) and
                fault_type == 'smess_fault' and 127 in fault):
              fault = fault.astype(numpy.uint16)
              fault[fault == 127] = active_fault.FREE  # ignore FAULT_SIGNAL_ERROR_EBC5_XBR_STATE (0x7F)
          if fault_type == 'a087_fault' and fault.dtype.str == '|u1':
            msb = fault.astype(numpy.uint16)
            lsb = iter_faults.next().astype(numpy.uint16)
            fault = (msb << 8) + lsb
          active_fault(report, fault, is_dtc_id=is_dtc_id)
    return reports

  def search(self, reports):
    for report in reports:
      self.batch.add_entry(report)
    return
