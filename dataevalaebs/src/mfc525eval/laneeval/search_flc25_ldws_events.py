# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
    dep = {
        'ldws_events': "calc_flc25_ldws_events@aebs.fill"
    }

    def fill(self):
        time, imminent_left, imminent_right, system_status = self.modules.fill(self.dep['ldws_events'])

        event_votes = 'FLC25 events'
        ldws_status = 'LDWS system status'
        votes = self.batch.get_labelgroups(event_votes, ldws_status)
        report = Report(cIntervalList(time), 'FLC25 events', votes=votes)
        exclusive, ldws_system_status = votes[ldws_status]

        # levels = 5
        # id = 0
        # jumps, warnings = system_status.merge_phases(levels)
        # for jump, interval in zip(jumps, warnings):
        #     idx = report.addInterval(interval)
        #     report.vote(id, ldws_status, ldws_system_status[len(jump) - 1])

        imminent_left_intervals = maskToIntervals(imminent_left)
        jumps = [[start] for start, end in imminent_left_intervals]
        for jump, imminent_left_interval in zip(jumps, imminent_left_intervals):
            idx = report.addInterval(imminent_left_interval)
            report.vote(idx, event_votes, "imminent_left_0->1")

        imminent_right_intervals = maskToIntervals(imminent_right)
        jumps = [[start] for start, end in imminent_right_intervals]
        for jump, imminent_right_interval in zip(jumps, imminent_right_intervals):
            idx = report.addInterval(imminent_right_interval)
            report.vote(idx, event_votes, "imminent_right_0->1")

        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
