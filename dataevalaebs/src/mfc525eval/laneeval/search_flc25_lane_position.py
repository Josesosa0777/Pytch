# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
    dep = {
        'lane_line_position': "calc_flc25_lane_position@aebs.fill"
    }

    def fill(self):
        time, left_adjacent_lane_position, right_adjacent_lane_position = self.modules.fill(self.dep['lane_line_position'])

        event_votes = 'FLC25 events'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'FLC25 events', votes=votes)

        left_lane_intervals = maskToIntervals(left_adjacent_lane_position)
        jumps = [[start] for start, end in left_lane_intervals]
        for jump, left_lane_interval in zip(jumps, left_lane_intervals):
            idx = report.addInterval(left_lane_interval)
            report.vote(idx, event_votes, 'left lane is not within range')

        right_lane_intervals = maskToIntervals(right_adjacent_lane_position)
        jumps = [[start] for start, end in right_lane_intervals]
        for jump, right_lane_interval in zip(jumps, right_lane_intervals):
            idx = report.addInterval(right_lane_interval)
            report.vote(idx, event_votes, 'right lane is not within range')

        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
