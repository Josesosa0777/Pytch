# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

#Actl script
from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
    dep = {
        'actl_values': "calc_actl_eval@aebs.fill"
    }

    def fill(self):
        time, ACTL_values= self.modules.fill(
            self.dep['actl_values'])

        event_votes = 'ACTL event'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'ACTL event', votes=votes)

        intervals = maskToIntervals(ACTL_values)
        jumps = [[start] for start, end in intervals]

        for jump, interval in zip(jumps, intervals):
            idx = report.addInterval(interval)
            report.vote(idx, event_votes, "Not_Equal_To_Normal")

        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
