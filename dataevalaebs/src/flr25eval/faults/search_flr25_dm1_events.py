# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
  dep = {
    'dm1_signal_status': "calc_flr25_dm1_events@aebs.fill"
  }

  def fill(self):
    time, amber_warning_mask, failure_mode_id_mask, amber_warning_data, failure_mode_id_data = self.modules.fill(self.dep['dm1_signal_status'])

    event_votes = 'DM1 event'
    votes = self.batch.get_labelgroups(event_votes)
    report = Report(cIntervalList(time), 'DM1 event', votes=votes)
    # Add quantity
    batch = self.get_batch()

    qua_group = 'DM1 signals check'
    quas = batch.get_quanamegroup(qua_group)
    report.setNames(qua_group, quas)

    intervals = maskToIntervals(amber_warning_mask)
    jumps = [[start] for start, end in intervals]

    for jump, interval in zip(jumps, intervals):
      idx = report.addInterval(interval)
      report.vote(idx, event_votes, "DM1 AmberWarningLamp")
      report.set(idx, qua_group, 'AmberWarningLamp', amber_warning_data[jump])
      
    intervals = maskToIntervals(failure_mode_id_mask)
    jumps = [[start] for start, end in intervals]

    for jump, interval in zip(jumps, intervals):
      idx = report.addInterval(interval)
      report.vote(idx, event_votes, "DM1 FailureModeIdentifier")
      report.set(idx, qua_group, 'FailureModeIdentifier', failure_mode_id_data[jump])

    return report

  def search(self, report):
    self.batch.add_entry(report)
    return


