# -*- dataeval: init -*-

import numpy as np

import interface
from measproc import cIntervalList
from measproc.report2 import Report
from primitives.bases import PrimitiveCollection

class Search(interface.iSearch):
  dep = 'fill_flr20_raw_tracks@aebs.fill',
  quantity_setters = (
    'set_egospeed-start@egoeval',
    'set_drivendistance@egoeval',
  )
  
  optdep = quantity_setters
  
  def _create_report(self, intervals):
    votes = self.batch.get_labelgroups()
    names = self.batch.get_quanamegroups()
    title = "In-lane objects"
    return Report(intervals, title, votes=votes, names=names)
  
  def fill(self):
    # load fills
    objects = self.modules.fill(self.dep[0])
    if not isinstance(objects, PrimitiveCollection):
      objects = PrimitiveCollection(objects.time, {0: objects})  # for iteration
    time_scale = objects.time
    
    # create report
    report = self._create_report(cIntervalList(time_scale))
    
    # add intervals
    candidates_mask = np.zeros_like(time_scale, dtype=np.bool)
    for obj in objects.itervalues():
      # filter...
      candidates_mask |= obj.lane.same
    candidates_intvals = cIntervalList.fromMask(time_scale, candidates_mask)
    for st, end in candidates_intvals:
      index = report.addInterval([st, end])
    
    # set general quantities
    for qua in self.quantity_setters:
      if qua in self.passed_optdep:
        set_qua_for_report = self.modules.get_module(qua)
        set_qua_for_report(report)
      else:
        self.logger.warning("Inactive quantity setter: %s" % qua)
    return report
  
  def search(self, report):
    tags = ()
    result = self.FAILED if report.isEmpty() else self.PASSED
    self.batch.add_entry(report, result=result, tags=tags)
    return
