# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
    dep = {
        'no_braking_events': "calc_trailer_no_braking@aebs.fill"
    }

    def fill(self):
        time, no_braking_events = self.modules.fill(self.dep['no_braking_events'])

        event_votes = 'Trailer'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'Trailer', votes=votes)

        no_braking_intervals = maskToIntervals(no_braking_events)
        jumps = [[start] for start, end in no_braking_intervals]
        for jump, no_braking_interval in zip(jumps, no_braking_intervals):
            idx = report.addInterval(no_braking_interval)
            report.vote(idx, event_votes, 'no braking event')

        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
