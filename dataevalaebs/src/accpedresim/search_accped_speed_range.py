# -*- dataeval: init -*-
import numpy as np
from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
    dep = {
        'vehicle_in_accped_speed_range': "calc_vehicle_in_accped_speed_range@aebs.fill"
    }

    def fill(self):
        time, percentage_speed_range = self.modules.fill(self.dep['vehicle_in_accped_speed_range'])

        report = Report(cIntervalList(time), 'FLR25 ACC PED STOP')
        batch = self.get_batch()

        qua_group = 'ACC PED STOP'
        quas = batch.get_quanamegroup(qua_group)
        report.setNames(qua_group, quas)

        idx = report.addInterval((0, len(time)-1))
        report.set(idx, qua_group, 'vehicle_in_accped_speed_range', percentage_speed_range)
        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
