# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
    dep = {
        'wl_active': "calc_trailer_wl_active@aebs.fill"
    }

    def fill(self):
        time, wl_active_events = self.modules.fill(self.dep['wl_active'])

        event_votes = 'Trailer'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'Trailer', votes=votes)

        wl_active_intervals = maskToIntervals(wl_active_events)
        jumps = [[start] for start, end in wl_active_intervals]
        for jump, wl_active_interval in zip(jumps, wl_active_intervals):
            idx = report.addInterval(wl_active_interval)
            report.vote(idx, event_votes, "WL active")

        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
