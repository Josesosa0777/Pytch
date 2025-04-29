# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
    dep = {
        'Lane_quality_drop': "calc_flc25_lane_quality_drop@aebs.fill"
    }

    def fill(self):
        time, left_lane_quality_drop, right_lane_quality_drop = self.modules.fill(self.dep['Lane_quality_drop'])

        event_votes = 'FLC25 events'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'FLC25 events', votes=votes)

        left_lane_intervals = maskToIntervals(left_lane_quality_drop)
        jumps = [[start] for start, end in left_lane_intervals if end - start > 1]
        for jump, left_lane_interval in zip(jumps, left_lane_intervals):
            idx = report.addInterval(left_lane_interval)
            report.vote(idx, event_votes, "Left Lane Quality drop")
            
        right_lane_intervals = maskToIntervals(right_lane_quality_drop)
        jumps = [[start] for start, end in right_lane_intervals if time[end] - time[start] > 1]
        for jump, right_lane_interval in zip(jumps, right_lane_intervals):
            idx = report.addInterval(right_lane_interval)
            report.vote(idx, event_votes, "Right Lane Quality drop")

        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
