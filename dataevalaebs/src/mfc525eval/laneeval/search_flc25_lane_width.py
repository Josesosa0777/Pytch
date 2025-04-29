# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
    dep = {
        'Lane_width': "calc_flc25_lane_width@aebs.fill"
    }

    def fill(self):
        time, lane_width_check = self.modules.fill(self.dep['Lane_width'])

        event_votes = 'FLC25 events'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'FLC25 events', votes=votes)

        intervals = maskToIntervals(lane_width_check)
        jumps = [[start] for start, end in intervals]
        for jump, interval in zip(jumps, intervals):
            idx = report.addInterval(interval)
            report.vote(idx, event_votes, "Not realistic lane width")

        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
