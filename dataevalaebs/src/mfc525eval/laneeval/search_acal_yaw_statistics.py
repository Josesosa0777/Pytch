# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

#Actl script
from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
    dep = {
        'yaw_statistics': "calc_flc25_acal_yaw_statistics@aebs.fill"
    }

    def fill(self):
        time,value, count, mean, std, min, max , sum,violation= self.modules.fill(self.dep['yaw_statistics'])

        event_votes = 'FLC25 events'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'FLC25 events', votes=votes)

        # Add quantity
        batch = self.get_batch()

        qua_group = 'FLC25 ACAL YAW Statistics'
        quas = batch.get_quanamegroup(qua_group)
        report.setNames(qua_group, quas)

        # intervals = maskToIntervals(value)
        idx=report.addInterval((0,10))

        report.vote(idx, event_votes, 'YAW Statistics')
        report.set(idx, qua_group, 'Count', count)
        report.set(idx, qua_group, 'Mean', mean)
        report.set(idx, qua_group, 'Min', min)
        report.set(idx, qua_group, 'Max', max)
        report.set(idx, qua_group, 'Std', std)
        report.set(idx, qua_group, 'Sum', sum)
        report.set(idx, qua_group, 'Violation', violation)

        return report

    def search(self, report):
        self.batch.add_entry(report)
        return