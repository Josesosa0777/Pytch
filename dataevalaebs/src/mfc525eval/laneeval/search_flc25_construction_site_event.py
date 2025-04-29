# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
    dep = {
        'construction_site_event': "calc_flc25_construction_site_event@aebs.fill"
    }

    def fill(self):
        time, construction_site_masked_array, frontAxleSpeed_value = self.modules.fill(self.dep['construction_site_event'])

        event_votes = 'FLC25 LDWS'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'FLC25 LDWS', votes=votes)

        batch = self.get_batch()
        qua_group = 'FLC25 LDWS'
        quas = batch.get_quanamegroup(qua_group)
        report.setNames(qua_group, quas)

        construction_site_intervals = maskToIntervals(construction_site_masked_array)
        jumps = [[start] for start, end in construction_site_intervals]
        for jump, construction_site_interval in zip(jumps, construction_site_intervals):
            idx = report.addInterval(construction_site_interval)
            report.vote(idx, event_votes, 'ConstructionSiteAvailable')
            report.set(idx, qua_group, 'FrontAxleSpeed', frontAxleSpeed_value[jump[0]])

        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
