# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
    dep = {
        'bsis_evaluation': "calc_bsis_evaluation@aebs.fill",
        'operational_hours': "calc_slr_operational_hours@aebs.fill"
    }

    def fill(self):
        time, warning_level_front_value, warning_level_right_value, MOIS_warning_from_front, BSIS_warning_from_right, \
            LatDispMIORightSide_value, LonDispMIORightSide_value, LatDispMIOFront_value, LonDispMIOFront_value, LCDA_warning_from_right = self.modules.fill(
            self.dep['bsis_evaluation'])

        BSIS, MOIS, VDP, LCDA, FNA = self.modules.fill(self.dep['operational_hours'])

        event_votes = 'BSIS Event'
        quantity_name = 'BSIS Event'
        SRR_warning_right_intervals = []
        votes = self.batch.get_labelgroups(event_votes)
        names = self.batch.get_quanamegroups(quantity_name)
        report = Report(cIntervalList(time), 'BSIS Event', votes=votes, names=names)

        right_warning_intervals = maskToIntervals(BSIS_warning_from_right)
        # Check if any front warning present or not
        for intervals in right_warning_intervals:
            if max(warning_level_right_value[intervals[0]:intervals[1]]) > 1:
                level = max(warning_level_right_value[intervals[0]:intervals[1]])
                SRR_warning_right_intervals.append(maskToIntervals((warning_level_right_value == level))[0])
            else:
                SRR_warning_right_intervals.append(intervals)

        SRR_warning_right_jumps = [[start] for start, end in SRR_warning_right_intervals]

        for jump, interval in zip(SRR_warning_right_jumps, SRR_warning_right_intervals):
            idx = report.addInterval(interval)
            if warning_level_right_value[jump[0]] == 1:
                report.vote(idx, event_votes, 'Information Warning')
            elif warning_level_right_value[jump[0]] == 3:
                report.vote(idx, event_votes, 'VDP Warning')
            elif warning_level_right_value[jump[0]] == 5:
                report.vote(idx, event_votes, 'Collision Warning')
            elif warning_level_right_value[jump[0]] == 14:
                report.vote(idx, event_votes, 'NA Status')
            elif warning_level_right_value[jump[0]] == 15:
                report.vote(idx, event_votes, 'Error State')

            report.set(idx, quantity_name, 'LonDispMIORightSide', LonDispMIORightSide_value[jump][0])
            report.set(idx, quantity_name, 'LatDispMIORightSide', LatDispMIORightSide_value[jump][0])

            report.set(idx, quantity_name, 'BSIS', BSIS)
            report.set(idx, quantity_name, 'MOIS', MOIS)
            report.set(idx, quantity_name, 'VDP', VDP)
            report.set(idx, quantity_name, 'LCDA', LCDA)
            report.set(idx, quantity_name, 'FNA', FNA)

        lcda_warning_intervals = maskToIntervals(LCDA_warning_from_right)

        lcda_warning_right_jumps = [[start] for start, end in lcda_warning_intervals]

        for jump, interval in zip(lcda_warning_right_jumps, lcda_warning_intervals):
            idx = report.addInterval(interval)
            if warning_level_right_value[jump[0]] == 1:
                report.vote(idx, event_votes, 'LCDA Information Warning')
            # elif warning_level_right_value[jump[0]] == 3:
            #     report.vote(idx, event_votes, 'LCDA VDP Warning')
            elif warning_level_right_value[jump[0]] == 5:
                report.vote(idx, event_votes, 'LCDA Collision Warning')
            elif warning_level_right_value[jump[0]] == 14:
                report.vote(idx, event_votes, 'LCDA NA Status')
            elif warning_level_right_value[jump[0]] == 15:
                report.vote(idx, event_votes, 'LCDA Error State')

            report.set(idx, quantity_name, 'LonDispMIORightSide', LonDispMIORightSide_value[jump][0])
            report.set(idx, quantity_name, 'LatDispMIORightSide', LatDispMIORightSide_value[jump][0])

            report.set(idx, quantity_name, 'BSIS', BSIS)
            report.set(idx, quantity_name, 'MOIS', MOIS)
            report.set(idx, quantity_name, 'VDP', VDP)
            report.set(idx, quantity_name, 'LCDA', LCDA)
            report.set(idx, quantity_name, 'FNA', FNA)

        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
