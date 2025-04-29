# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
    dep = {
        'dtc_events': "calc_flr25_dm1_dtc_events@aebs.fill"
    }

    def fill(self):
        time, dtc_data = self.modules.fill(self.dep['dtc_events'])

        event_votes = 'DM1 event'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'DM1 event', votes=votes)
        batch = self.get_batch()

        # Save dtc active intervals in database, based on amberwarning lamp activity
        qua_group = 'DTC event check'
        quas = batch.get_quanamegroup(qua_group)
        report.setNames(qua_group, quas)

        intervals = maskToIntervals(dtc_data['valid_warning_mask'])
        jumps = [[start] for start, end in intervals]

        for jump, interval in zip(jumps, intervals):
            idx = report.addInterval(interval)
            report.vote(idx, event_votes, "DM1 AmberWarningLamp")
            report.set(idx, qua_group, 'AmberWarningLamp', dtc_data['AmberWarningLamp'][jump])
        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
