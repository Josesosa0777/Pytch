# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
    dep = {
        'abs_and_rsp_active_events': "calc_trailer_abs_and_rsp_active@aebs.fill"
    }

    def fill(self):
        time, abs_and_rsp_active_events = self.modules.fill(self.dep['abs_and_rsp_active_events'])

        event_votes = 'Trailer'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'Trailer', votes=votes)

        abs_and_rsp_active_intervals = maskToIntervals(abs_and_rsp_active_events)
        jumps = [[start] for start, end in abs_and_rsp_active_intervals]
        for jump, abs_and_rsp_active_interval in zip(jumps, abs_and_rsp_active_intervals):
            idx = report.addInterval(abs_and_rsp_active_interval)
            report.vote(idx, event_votes, 'ABS_and_RSP active')

        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
