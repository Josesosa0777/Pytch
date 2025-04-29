# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
    dep = {
        'compare_c0': "calc_flc25_compare_c0@aebs.fill"
    }

    def fill(self):
        time, left_lane_pdiff, left_lane_ndiff, right_lane_pdiff, right_lane_ndiff = self.modules.fill(self.dep['compare_c0'])

        event_votes = 'FLC25 events'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'FLC25 events', votes=votes)

        left_lane_pdiff_intervals = maskToIntervals(left_lane_pdiff)
        jumps = [[start] for start, end in left_lane_pdiff_intervals]
        for jump, left_lane_pdiff_interval in zip(jumps, left_lane_pdiff_intervals):
            idx = report.addInterval(left_lane_pdiff_interval)
            report.vote(idx, event_votes, 'Left_lane_C0 Above Threshold')

        left_lane_ndiff_intervals = maskToIntervals(left_lane_ndiff)
        jumps = [[start] for start, end in left_lane_ndiff_intervals]
        for jump, left_lane_ndiff_interval in zip(jumps, left_lane_ndiff_intervals):
            idx = report.addInterval(left_lane_ndiff_interval)
            report.vote(idx, event_votes, "Left_lane_C0 Above Threshold")

        right_lane_pdiff_intervals = maskToIntervals(right_lane_pdiff)
        jumps = [[start] for start, end in right_lane_pdiff_intervals]
        for jump, right_lane_pdiff_interval in zip(jumps, right_lane_pdiff_intervals):
            idx = report.addInterval(right_lane_pdiff_interval)
            report.vote(idx, event_votes, "Right_lane_C0 Above Threshold")

        right_lane_ndiff_intervals = maskToIntervals(right_lane_ndiff)
        jumps = [[start] for start, end in right_lane_ndiff_intervals]
        for jump, right_lane_ndiff_interval in zip(jumps, right_lane_ndiff_intervals):
            idx = report.addInterval(right_lane_ndiff_interval)
            report.vote(idx, event_votes, "Right_lane_C0 Above Threshold")

        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
