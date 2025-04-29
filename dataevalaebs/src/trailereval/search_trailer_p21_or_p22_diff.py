# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
    dep = {
        'p21_or_p22_diff_events': "calc_trailer_p21_p22_diff@aebs.fill"
    }

    def fill(self):
        time, p21_or_p22_diff_events = self.modules.fill(self.dep['p21_or_p22_diff_events'])

        event_votes = 'Trailer'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'Trailer', votes=votes)

        p21_or_p22_diff_intervals = maskToIntervals(p21_or_p22_diff_events)
        jumps = [[start] for start, end in p21_or_p22_diff_intervals]
        for jump, p21_or_p22_diff_interval in zip(jumps, p21_or_p22_diff_intervals):
            idx = report.addInterval(p21_or_p22_diff_interval)
            report.vote(idx, event_votes, 'p21_or_p22_diff.')

        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
