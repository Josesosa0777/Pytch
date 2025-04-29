# -*- dataeval: init -*-

import numpy as np

from interface import iSearch
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList, maskToIntervals
from aebs.par.camera_sensor_status import flc20_sensor_status_dict

class Search(iSearch):
  optdep = {
    'egospeedstart': 'set_egospeed-start@egoeval', 
    'egospeedmin': 'set_egospeed-min@egoeval', 
    'egospeedmax': 'set_egospeed-max@egoeval', 
    'drivdist': 'set_drivendistance@egoeval',
  }

  sgs = [{
    "SensorStatus": ("Video_Data_General_B", "SensorStatus"),
  }]
  optsgs = [{
    "Frame_ID"    : ("Video_Data_General_B", "Frame_ID"),
  }]

  def check(self):
    group = self.source.selectSignalGroup(self.sgs)
    optgroup = self.source.selectLazySignalGroup(self.optsgs)
    return group, optgroup

  def fill(self, group, optgroup):
    # get signals
    t,status = group.get_signal("SensorStatus")
    if "Frame_ID" in optgroup:
      frames = optgroup.get_value("Frame_ID", ScaleTime=t)
    else:
      self.logger.warning("Signal not available: FLC20 Frame_ID")
      frames = None
    # init report
    title = "FLC20 sensor status"
    votes = self.batch.get_labelgroups('camera status')
    names = self.batch.get_quanamegroups('mobileye')
    report = Report(cIntervalList(t), title, votes=votes, names=names)
    # find intervals
    uniques = np.unique(status)
    for value in uniques:
      mask = status == value
      label = flc20_sensor_status_dict[value]
      for st,end in maskToIntervals(mask):
        index = report.addInterval( (st,end) )
        report.vote(index, 'camera status', label)
        if frames is not None:
          report.set( index, 'mobileye', 'frame start', frames[st] )
          report.set( index, 'mobileye', 'frame end',   frames[end-1] )
    report.sort()
    # set general quantities
    for qua in self.optdep:
      if self.optdep[qua] in self.passed_optdep:
        set_qua_for_report = self.modules.get_module(self.optdep[qua])
        set_qua_for_report(report)
      else:
        self.logger.warning("Inactive module: %s" % self.optdep[qua])
    return report

  def search(self, report):
    self.batch.add_entry(report, result=self.PASSED)
    return
