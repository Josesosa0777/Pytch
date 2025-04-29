# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
    dep = {
        'cem_status': "calc_flc25_cem_states_detection@aebs.fill"
    }

    def fill(self):
        time, cem_status= self.modules.fill(self.dep['cem_status'])

        event_votes = 'FLC25 CEM state'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'FLC25 CEM state', votes=votes)

        cem_failed_status_intervals = maskToIntervals(cem_status)
        jumps = [[start] for start, end in cem_failed_status_intervals]
        for jump, cem_failed_status_interval in zip(jumps, cem_failed_status_intervals):
            idx = report.addInterval(cem_failed_status_interval)
            report.vote(idx, event_votes, "CEMState_FAILURE")

        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
