# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
  dep = {
    'camera_status': "calc_flc25_camera_reset_events@aebs.fill"
  }

  def fill(self):
    time, reset_counter_mask, reset_reason_data, reset_counter = self.modules.fill(self.dep['camera_status'])

    event_votes = 'FLC25 events'
    votes = self.batch.get_labelgroups(event_votes)
    report = Report(cIntervalList(time), 'FLC25 events', votes=votes)
    # Add quantity
    batch = self.get_batch()

    qua_group = 'FLC25 camera check'
    quas = batch.get_quanamegroup(qua_group)
    report.setNames(qua_group, quas)

    intervals = maskToIntervals(reset_counter_mask)
    jumps = [[start] for start, end in intervals]

    for jump, interval in zip(jumps, intervals):
      idx = report.addInterval(interval)
      report.vote(idx, event_votes, "Camera Reset")
      report.set(idx, qua_group, 'ResetReason', reset_reason_data[jump])
      report.set(idx, qua_group, 'ResetCounter', reset_counter[jump])

    return report

  def search(self, report):
    self.batch.add_entry(report)
    return


