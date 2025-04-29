# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
    dep = {
        'distance_accuracy': "calc_flc25_distance_to_lane_accuracy@aebs.fill"
    }

    def fill(self):
        time, valid_interval = self.modules.fill(self.dep['distance_accuracy'])

        event_votes = 'FLC25 events'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'FLC25 events', votes=votes)

        jumps = [[start] for start, end in valid_interval]
        for jump, interval in zip(jumps, valid_interval):
            idx = report.addInterval(interval)
            report.vote(idx, event_votes, "strong distance change")

        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
