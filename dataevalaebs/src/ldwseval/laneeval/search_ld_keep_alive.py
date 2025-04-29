# -*- dataeval: init -*-

"""
Search for events of engine running / not running
"""
# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
  dep = {
    'keep_alive': "calc_flc25_keep_alive@aebs.fill"
  }

  def fill(self):
    time, KeepAlive_left,KeepAlive_right = self.modules.fill(self.dep['keep_alive'])

    event_votes = 'FLC25 keep alive'
    votes = self.batch.get_labelgroups(event_votes)
    report = Report(cIntervalList(time), 'FLC25 keep alive', votes=votes)

    KeepAlive_left_status_intervals = maskToIntervals(KeepAlive_left)
    jumps = [[start] for start, end in KeepAlive_left_status_intervals]
    for jump, KeepAlive_left_status_interval in zip(jumps, KeepAlive_left_status_intervals):
      idx = report.addInterval(KeepAlive_left_status_interval)
      report.vote(idx, event_votes, "KeepAlive_Left")

    KeepAlive_right_status_intervals = maskToIntervals(KeepAlive_right)
    jumps = [[start] for start, end in KeepAlive_right_status_intervals]
    for jump, KeepAlive_right_status_interval in zip(jumps, KeepAlive_right_status_intervals):
      idx = report.addInterval(KeepAlive_right_status_interval)
      report.vote(idx, event_votes, "KeepAlive_Right")

    return report

  def search(self, report):
    self.batch.add_entry(report)
    return


