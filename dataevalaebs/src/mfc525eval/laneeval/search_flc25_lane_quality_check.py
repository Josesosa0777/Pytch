# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
    dep = {
        'Lane_quality': "calc_flc25_lane_quality_check@aebs.fill"
    }

    def fill(self):
        time, left_lane_quality, right_lane_quality = self.modules.fill(self.dep['Lane_quality'])

        event_votes = 'FLC25 events'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'FLC25 events', votes=votes)

        left_lane_quality_intervals = maskToIntervals(left_lane_quality)
        jumps = [[start] for start, end in left_lane_quality_intervals]
        for jump, left_lane_quality_interval in zip(jumps, left_lane_quality_intervals):
            idx = report.addInterval(left_lane_quality_interval)
            report.vote(idx, event_votes, "Worst Left Lane Detection")

        right_lane_quality_intervals = maskToIntervals(right_lane_quality)
        jumps = [[start] for start, end in right_lane_quality_intervals]
        for jump, right_lane_quality_interval in zip(jumps, right_lane_quality_intervals):
            idx = report.addInterval(right_lane_quality_interval)
            report.vote(idx, event_votes, "Worst Right Lane Detection")

        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
