# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
    dep = {
        'lane_change_status': "calc_flc25_lane_cutting_analysis@aebs.fill"
    }

    def fill(self):
        time, left_departure_warning, right_departure_warning = self.modules.fill(self.dep['lane_change_status'])

        event_votes = 'FLC25 LDWS'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'FLC25 LDWS', votes=votes)

        left_lane_warning_intervals = maskToIntervals(left_departure_warning)
        jumps = [[start] for start, end in left_lane_warning_intervals]
        for jump, left_lane_warning_interval in zip(jumps, left_lane_warning_intervals):
            idx = report.addInterval(left_lane_warning_interval)
            report.vote(idx, event_votes, 'LeftLaneDepartureWarning')

        right_lane_warning_intervals = maskToIntervals(right_departure_warning)
        jumps = [[start] for start, end in right_lane_warning_intervals]
        for jump, right_lane_warning_interval in zip(jumps, right_lane_warning_intervals):
            idx = report.addInterval(right_lane_warning_interval)
            report.vote(idx, event_votes, 'RightLaneDepartureWarning')

        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
