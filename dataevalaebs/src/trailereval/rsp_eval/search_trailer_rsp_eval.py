# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
    dep = {
        'calc_trailer_rsp_eval_events': "calc_trailer_rsp_eval@aebs.fill"
    }

    def fill(self):
        time, RSPTestActive_masked_array, RSPStep1Active_masked_array, RSPStep2Active_masked_array, \
        RSPTestedLifted_masked_array, RSPVDCActive_masked_array = self.modules.fill(self.dep['calc_trailer_rsp_eval_events'])

        event_votes = 'Trailer'
        votes = self.batch.get_labelgroups(event_votes)

        report = Report(cIntervalList(time), 'Trailer', votes=votes)

        RSPTestActive_event_intervals = maskToIntervals(RSPTestActive_masked_array)
        jumps = [[start] for start, end in RSPTestActive_event_intervals]
        for jump, RSPTestActive_event_interval in zip(jumps, RSPTestActive_event_intervals):
            idx = report.addInterval(RSPTestActive_event_interval)
            report.vote(idx, event_votes, 'Rsptestactive=1')

        RSPStep1Active_event_intervals = maskToIntervals(RSPStep1Active_masked_array)
        jumps = [[start] for start, end in RSPStep1Active_event_intervals]
        for jump, RSPStep1Active_event_interval in zip(jumps, RSPStep1Active_event_intervals):
            idx = report.addInterval(RSPStep1Active_event_interval)
            report.vote(idx, event_votes, 'RspStep1Active=1')

        RSPStep2Active_event_intervals = maskToIntervals(RSPStep2Active_masked_array)
        jumps = [[start] for start, end in RSPStep2Active_event_intervals]
        for jump, RSPStep2Active_event_interval in zip(jumps, RSPStep2Active_event_intervals):
            idx = report.addInterval(RSPStep2Active_event_interval)
            report.vote(idx, event_votes, 'RspStep2Active=1')

        RSPTestedLifted_intervals = maskToIntervals(RSPTestedLifted_masked_array)
        jumps = [[start] for start, end in RSPTestedLifted_intervals]
        for jump, RSPTestedLifted_interval in zip(jumps, RSPTestedLifted_intervals):
            idx = report.addInterval(RSPTestedLifted_interval)
            report.vote(idx, event_votes, 'RSPTestedLifted=1')

        RSPVDCActive_intervals = maskToIntervals(RSPVDCActive_masked_array)
        jumps = [[start] for start, end in RSPVDCActive_intervals]
        for jump, RSPVDCActive_interval in zip(jumps, RSPVDCActive_intervals):
            idx = report.addInterval(RSPVDCActive_interval)
            report.vote(idx, event_votes, 'RSPVDCActive=1')

        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
