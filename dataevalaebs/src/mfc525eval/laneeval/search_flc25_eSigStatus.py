# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
    dep = {
        'eSignStatus': "calc_flc25_eSignStatus_detection@aebs.fill"
    }

    def fill(self):
        time,  LD_eSignStatus,TPF_eSignStatus,TPF_sSigHeader_values, LD_sSigHeader_values= self.modules.fill(self.dep['eSignStatus'])

        event_votes = 'FLC25 eSign Status'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'FLC25 eSign Status', votes=votes)

        LD_eSignStatus_intervals = maskToIntervals(LD_eSignStatus)
        jumps = [[start] for start, end in LD_eSignStatus_intervals]
        for jump, LD_eSignStatus_interval in zip(jumps, LD_eSignStatus_intervals):
            idx = report.addInterval(LD_eSignStatus_interval)
            if LD_sSigHeader_values[jump]==0:
                report.vote(idx, event_votes, "LD AL_SIG_STATE_INIT")
            else:
                report.vote(idx, event_votes, "LD AL_SIG_STATE_INVALID")

        TPF_eSignStatus_intervals = maskToIntervals(TPF_eSignStatus)
        jumps = [[start] for start, end in TPF_eSignStatus_intervals]
        for jump, TPF_eSignStatus_interval in zip(jumps, TPF_eSignStatus_intervals):
            idx = report.addInterval(TPF_eSignStatus_interval)
            if TPF_sSigHeader_values[jump] == 0:
                report.vote(idx, event_votes, "TPF AL_SIG_STATE_INIT")
            else:
                report.vote(idx, event_votes, "TPF AL_SIG_STATE_INVALID")
        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
