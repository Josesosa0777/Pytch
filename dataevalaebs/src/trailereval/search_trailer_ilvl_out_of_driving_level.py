# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
    dep = {
        'ilvl_out_of_driving_level_event': "calc_trailer_ilvl_out_of_driving_level@aebs.fill"
    }

    def fill(self):
        time, ilvl_out_of_driving_level_event = self.modules.fill(self.dep['ilvl_out_of_driving_level_event'])

        event_votes = 'Trailer'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'Trailer', votes=votes)

        ilvl_out_of_driving_level_intervals = maskToIntervals(ilvl_out_of_driving_level_event)
        jumps = [[start] for start, end in ilvl_out_of_driving_level_intervals]
        for jump, ilvl_out_of_driving_level_interval in zip(jumps, ilvl_out_of_driving_level_intervals):
            idx = report.addInterval(ilvl_out_of_driving_level_interval)
            report.vote(idx, event_votes, 'ilvl_out_of_driving_level')

        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
