# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
    dep = {
        'high_speed_cut_in': "calc_high_speed_cut_in@aebs.fill"
    }

    def fill(self):
        common_time, high_speed_cut_in_objects = self.modules.fill(self.dep['high_speed_cut_in'])
        event_votes = 'ACC event'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(common_time), 'ACC event', votes = votes)
        batch = self.get_batch()

        qua_group = 'ACC check'
        quas = batch.get_quanamegroup(qua_group)
        report.setNames(qua_group, quas)

        for obj in high_speed_cut_in_objects:
            intervals = maskToIntervals(obj['event_mask'])
            jumps = [[start] for start, end in intervals]

            for jump, interval in zip(jumps, intervals):
                idx = report.addInterval(interval)
                report.vote(idx, event_votes, "High Speed Cut-In")
                report.set(idx, qua_group, 'acc target present(dx)', obj['dx'][jump])
                report.set(idx, qua_group, 'brake request', obj['acc_xbr'][jump])
        return report

    def search(self, report):
        self.batch.add_entry(report)
        return