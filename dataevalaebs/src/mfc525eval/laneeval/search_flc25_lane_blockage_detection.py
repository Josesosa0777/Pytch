# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
    dep = {
        'blockage_status': "calc_flc25_lane_blockage_detection@aebs.fill"
    }

    def fill(self):
        time, cb_unknown_status, cb_no_blockage, cb_condensation, cb_top_part_blockage,\
        cb_bottom_part_blockage, cb_blockage, cb_left_part_blockage, cb_right_part_blockage = self.modules.fill(self.dep['blockage_status'])

        event_votes = 'FLC25 Blockage state'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'FLC25 Blockage state', votes=votes)

        """cb_unknown_status_intervals = maskToIntervals(cb_unknown_status)
        jumps = [[start] for start, end in cb_unknown_status_intervals]
        for jump, cb_unknown_status_interval in zip(jumps, cb_unknown_status_intervals):
            idx = report.addInterval(cb_unknown_status_interval)
            report.vote(idx, event_votes, "CB_UNKNOWN_STATUS")"""

        cb_no_blockage_intervals = maskToIntervals(cb_no_blockage)
        jumps = [[start] for start, end in cb_no_blockage_intervals]
        for jump, cb_no_blockage_interval in zip(jumps, cb_no_blockage_intervals):
            interval_list = list(cb_no_blockage_interval)
            interval_list[0] = interval_list[0]+2
            interval_list = tuple(interval_list)
            if interval_list[0] >= interval_list[1]:
                idx = report.addInterval(cb_no_blockage_interval)
            else:
                idx = report.addInterval(interval_list)
            report.vote(idx, event_votes, "CB_NO_BLOCKAGE")

        # cb_condensation_intervals = maskToIntervals(cb_condensation)
        # jumps = [[start] for start, end in cb_condensation_intervals]
        # for jump, cb_condensation_interval in zip(jumps, cb_condensation_intervals):
        #     idx = report.addInterval(cb_condensation_interval)
        #     report.vote(idx, event_votes, "CB_CONDENSATION")

        cb_top_part_blockage_intervals = maskToIntervals(cb_top_part_blockage)
        jumps = [[start] for start, end in cb_top_part_blockage_intervals]
        for jump, cb_top_part_blockage_interval in zip(jumps, cb_top_part_blockage_intervals):
            idx = report.addInterval(cb_top_part_blockage_interval)
            report.vote(idx, event_votes, "CB_TOP_PART_BLOCKAGE")

        cb_bottom_part_blockage_intervals = maskToIntervals(cb_bottom_part_blockage)
        jumps = [[start] for start, end in cb_bottom_part_blockage_intervals]
        for jump, cb_bottom_part_blockage_interval in zip(jumps, cb_bottom_part_blockage_intervals):
            idx = report.addInterval(cb_bottom_part_blockage_interval)
            report.vote(idx, event_votes, "CB_BOTTOM_PART_BLOCKAGE")

        cb_blockage_intervals = maskToIntervals(cb_blockage)
        jumps = [[start] for start, end in cb_blockage_intervals]
        for jump, cb_blockage_interval in zip(jumps, cb_blockage_intervals):
            idx = report.addInterval(cb_blockage_interval)
            report.vote(idx, event_votes, "CB_BLOCKAGE")

        cb_left_part_blockage_intervals = maskToIntervals(cb_left_part_blockage)
        jumps = [[start] for start, end in cb_left_part_blockage_intervals]
        for jump, cb_left_part_blockage_interval in zip(jumps, cb_left_part_blockage_intervals):
            idx = report.addInterval(cb_left_part_blockage_interval)
            report.vote(idx, event_votes, "CB_LEFT_PART_BLOCKAGE")

        cb_right_part_blockage_intervals = maskToIntervals(cb_right_part_blockage)
        jumps = [[start] for start, end in cb_right_part_blockage_intervals]
        for jump, cb_right_part_blockage_interval in zip(jumps, cb_right_part_blockage_intervals):
            idx = report.addInterval(cb_right_part_blockage_interval)
            report.vote(idx, event_votes, "CB_RIGHT_PART_BLOCKAGE")

        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
