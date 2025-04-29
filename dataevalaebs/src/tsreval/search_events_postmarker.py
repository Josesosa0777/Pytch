# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList
from measproc.report2 import Report
import numpy as np
from decimal import *


class Search(iSearch):
    dep = (
        "calc_postmarker_json_data",
        "calc_common_time-tsrresim",
    )

    def fill(self):
        self.module_all = self.get_modules()
        reports = []
        meta_info_reports, traffic_sign_report, weather_conditions_percentage = self.module_all.fill(self.dep[0])
        self.time = self.module_all.fill(self.dep[1])
        # self.time = self.modules.fill(self.dep[0])
        # report_list = self.modules.fill(self.dep[1])
        # if report_list == 0:
        #     print("No labels to add")
        #     return None

        for item in traffic_sign_report:
            votes = self.batch.get_labelgroups(item["Name"])
            report = Report(cIntervalList(self.time), item["Name"], votes=votes)
            interval = self.get_index((long(item["Start"]), long(item["End"]),))
            idx = report.addInterval(interval)
            report.vote(idx, item["Name"], item["Value"])
            reports.append(report)

        return reports

    def get_index(self, interval):
        st_time, ed_time = interval
        # format = "%" + ".%df"%len(str(self.time[0]))
        # getcontext().prec = 6
        # Conversion microsec_to_sec
        st_time = st_time / 1000000.0
        ed_time = ed_time / 1000000.0
        # st_index = (np.abs(self.time - st_time)).argmin()
        # ed_index = (np.abs(self.time - ed_time)).argmin()
        st_index = max(self.time.searchsorted(st_time, side='right') - 1, 0)
        ed_index = max(self.time.searchsorted(ed_time, side='right') - 1, 0)

        if st_index == ed_index:
            ed_index += 1
        return (st_index, ed_index)

    def search(self, reports):
        for report in reports:
            self.batch.add_entry(report)
        return
