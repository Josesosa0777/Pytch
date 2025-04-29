# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
    dep = {
        'Lane_c0_jump': "calc_flc25_lane_c0_jump@aebs.fill"
    }

    def fill(self):
        time, left_nlane_c0, left_plane_c0, right_nlane_c0, right_plane_c0 = self.modules.fill(self.dep['Lane_c0_jump'])

        event_votes = 'FLC25 events'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'FLC25 events', votes=votes)

        left_lane_c0_intervals = maskToIntervals(left_nlane_c0)
        jumps = [[start] for start, end in left_lane_c0_intervals]
        for jump, left_lane_c0_interval in zip(jumps, left_lane_c0_intervals):
            idx = report.addInterval(left_lane_c0_interval)
            report.vote(idx, event_votes, 'Left Lane C0 Jump')

        right_lane_c0_intervals = maskToIntervals(right_nlane_c0)
        jumps = [[start] for start, end in right_lane_c0_intervals]
        for jump, right_lane_c0_interval in zip(jumps, right_lane_c0_intervals):
            idx = report.addInterval(right_lane_c0_interval)
            report.vote(idx, event_votes, "Right Lane C0 Jump")

        left_plane_c0_intervals = maskToIntervals(left_plane_c0)
        jumps = [[start] for start, end in left_plane_c0_intervals]
        for jump, left_plane_c0_interval in zip(jumps, left_plane_c0_intervals):
            idx = report.addInterval(left_plane_c0_interval)
            report.vote(idx, event_votes, 'Left Lane C0 Jump')

        right_plane_c0_intervals = maskToIntervals(right_plane_c0)
        jumps = [[start] for start, end in right_plane_c0_intervals]
        for jump, right_plane_c0_interval in zip(jumps, right_plane_c0_intervals):
            idx = report.addInterval(right_plane_c0_interval)
            report.vote(idx, event_votes, "Right Lane C0 Jump")

        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
