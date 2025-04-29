# -*- dataeval: init -*-
from collections import namedtuple

from interface.Interfaces import iCalc

class Calc(iCalc):
  dep = namedtuple('Dep', ['egomotion'])('calc_flr20_egomotion@aebs.fill')

  def __call__(self, report):
    batch = self.get_batch()
    qua_group = 'ego vehicle'
    quas = batch.get_quanamegroup(qua_group)
    report.setNames(qua_group, quas)

    egomotion = self.get_modules().fill(self.dep.egomotion)
    egomotion = egomotion.rescale(report.intervallist.Time)

    for idx, (start, end) in report.iterIntervalsWithId():
      report.set(idx, qua_group, 'speed', egomotion.vx[start])
    return

