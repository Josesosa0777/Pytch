# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
  dep = {
    'radar_status': "calc_flr25_crash_events@aebs.fill"
  }
  # optdep = {
  #   'error_code': 'set_radar_status@trackeval',
  # }

  def fill(self):
    time, reset_reason_mask, reset_reason_data, address_data = self.modules.fill(self.dep['radar_status'])

    event_votes = 'FLR25 events'
    votes = self.batch.get_labelgroups(event_votes)
    report = Report(cIntervalList(time), 'FLR25 events', votes=votes)
    # Add quantity
    batch = self.get_batch()

    qua_group = 'FLR25 radar check'
    quas = batch.get_quanamegroup(qua_group)
    report.setNames(qua_group, quas)

    intervals = maskToIntervals(reset_reason_mask)
    jumps = [[start] for start, end in intervals]

    for jump, interval in zip(jumps, intervals):
      idx = report.addInterval(interval)
      report.vote(idx, event_votes, "Radar Reset")
      report.set(idx, qua_group, 'Cat2LastResetReason', reset_reason_data[jump])
      report.set(idx, qua_group, 'Address', address_data[jump])

    # set_radar_status_for_report = self.modules.get_module(self.optdep["error_code"])
    # set_radar_status_for_report(report)
    return report

  def search(self, report):
    self.batch.add_entry(report)
    return


