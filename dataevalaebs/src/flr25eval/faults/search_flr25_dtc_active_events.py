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
        #  calc_flr25_dm1_dtc_events calc_flr25_dtc_events
        event_votes = 'DTC event'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'DTC event', votes=votes)
        batch = self.get_batch()

        # Save DTC IDs and their counter values for each measurement
        qua_group = 'DTC event check'
        quas = batch.get_quanamegroup(qua_group)
        report.setNames(qua_group, quas)

        for dtc in dtc_data['dtc_history']:
            idx = report.addInterval((int(dtc[3]), int(dtc[3]) + 1))
            report.vote(idx, event_votes, "FLR25 DTC active")
            report.set(idx, qua_group, 'DTC in DEC', dtc[0])
            dtc_in_hex = hex(int(dtc[0]))
            if len(dtc_in_hex) < 8:
                dtc_in_hex = (dtc_in_hex).replace('x', 'x0')
            report.set(idx, qua_group, 'DTC in HEX', dtc_in_hex)
            report.set(idx, qua_group, 'DTC counter', dtc[1])
            report.set(idx, qua_group, 'DTC timestamp', dtc[2])
            # report.set(idx, qua_group, 'DEM event ids', dtc[4])
        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
