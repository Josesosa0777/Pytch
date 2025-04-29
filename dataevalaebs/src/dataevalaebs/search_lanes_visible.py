# -*- dataeval: init -*-

import interface
from measproc import cIntervalList
from measproc.report2 import Report

VIEWRANGE_MIN = 30.0

class Search(interface.iSearch):
  dep = ('calc_flc20_lanes@aebs.fill',)

  def _create_report(self, intervals):
    batch = self.get_batch()
    votes = None
    names = batch.get_quanamegroups('lane')
    title = "Lane detection availability"
    return Report(intervals, title, votes=votes, names=names)

  def fill(self):
    # load fills
    modules = self.get_modules()
    lanes = modules.fill(self.dep[0])
    time_scale = lanes.time

    # create intervals
    avail = (lanes.left_line.view_range > VIEWRANGE_MIN) | \
            (lanes.right_line.view_range > VIEWRANGE_MIN)
    intvals = cIntervalList.fromMask(time_scale, avail)
    intvals = intvals.merge(0.5).drop(0.1)  # smooth

    report = self._create_report(intvals)
    # add labels/quantities
    for i, (st, end) in enumerate(intvals):
      report.set(i, 'lane', 'left line view range avg',
        lanes.left_line.view_range[st:end].mean())
      report.set(i, 'lane', 'right line view range avg',
        lanes.right_line.view_range[st:end].mean())
    return report

  def search(self, report):
    tags = ()  # TODO: add sensor
    result = self.FAILED if report.isEmpty() else self.PASSED
    batch = self.get_batch()
    batch.add_entry(report, result=result, tags=tags)
    return
