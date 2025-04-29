# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
    dep = {
        'wheelspeed_suspicious_events': "calc_trailer_wheelspeed_suspicious@aebs.fill"
    }

    def fill(self):
        time, wheelspeed_suspicious_events = self.modules.fill(self.dep['wheelspeed_suspicious_events'])

        event_votes = 'Trailer'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'Trailer', votes=votes)

        wheelspeed_suspicious_intervals = maskToIntervals(wheelspeed_suspicious_events)
        jumps = [[start] for start, end in wheelspeed_suspicious_intervals]
        for jump, wheelspeed_suspicious_interval in zip(jumps, wheelspeed_suspicious_intervals):
            idx = report.addInterval(wheelspeed_suspicious_interval)
            report.vote(idx, event_votes, 'wheelspeed suspicious')

        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
