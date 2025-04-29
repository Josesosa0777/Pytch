# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
    dep = {
        'lane_quality_drop': "calc_flc25_lane_drop_worst_case@aebs.fill"
    }

    def fill(self):
        time, worst_case_events = self.modules.fill(self.dep['lane_quality_drop'])

        event_votes = 'FLC25 events'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'FLC25 events', votes=votes)

        worst_case_events_intervals = maskToIntervals(worst_case_events)
        jumps = [[start] for start, end in worst_case_events_intervals]
        for jump, worst_case_events_interval in zip(jumps, worst_case_events_intervals):
            idx = report.addInterval(worst_case_events_interval)
            report.vote(idx, event_votes, "worst lane drop")

        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
