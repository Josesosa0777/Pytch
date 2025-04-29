# -*- dataeval: init -*-

from collections import namedtuple

from interface.Interfaces import iCalc
from aebs.labeling.track import labelMovState, labelAssoState

class Calc(iCalc):
  dep = namedtuple('Dep', ['radar_status'])('fill_flr25_radar_status@aebs.fill')

  def __call__(self, report):
    batch = self.get_batch()

    qua_group = 'FLR25 radar check'
    quas = batch.get_quanamegroup(qua_group)
    report.setNames(qua_group, quas)

    t = report.intervallist.Time
    radar_status = self.get_modules().fill(self.dep.radar_status)

    for idx, (start, end) in report.iterIntervalsWithId():

      report.set(idx, qua_group, 'Cat2LastResetReason', radar_status)
    return
