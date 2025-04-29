# -*- dataeval: init -*-
from collections import OrderedDict

import interface
from measproc.IntervalList import cIntervalList
from measproc.report2 import Report
from kbtools_user.DataAC100 import cDataAC100
from kbtools_user.SimKBAEBS import cSimKBAEBS

class Search(interface.iSearch):
  dep = 'calc_aebs_wrapper@silkbaebs',
  def check(self):
    t, simout = self.get_modules().fill(self.dep[0])
    return t, simout

  def fill(self, t, simout):
    masks = OrderedDict([
      ('warning', simout['acoacoi_SetRequest'] == 1.0),
      ('partial_brake', simout['acopebp_SetRequest'] == 1.0),
      ('emergency_brake', simout['acopebe_SetRequest'] == 1.0),
    ])
    return t, masks

  def search(self, t, masks):
    batch = self.get_batch()
    for title, mask in masks.iteritems():
      intervals = cIntervalList.fromMask(t, mask)
      report = Report(intervals, title)
      batch.add_entry(report)
    return

