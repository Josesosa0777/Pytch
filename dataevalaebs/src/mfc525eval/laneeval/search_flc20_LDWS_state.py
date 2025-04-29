# -*- dataeval: init -*-

import numpy as np

from interface import iSearch
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList, maskToIntervals
from aebs.par.lane_quality_state import lane_quality_dict

class Search(iSearch):
    sgs = [
        {
            "StateOfLDWS": ("FLI2_E8_sE8_FLI2_E8_CAN26", "FLI2_LDWSState_E8"),
        },
        {
            "StateOfLDWS": ("FLI2_E8", "FLI2_LDWSState_E8"),

        },
        {
            "StateOfLDWS": ("FLI2_E8_CAN26", "FLI2_StateOfLDWS"),
        },
        {
            "StateOfLDWS": ("FLI2_E8_sE8_FLI2_E8_CAN26", "FLI2_LDWSState_E8"),
        },
        {
            "StateOfLDWS": ("FLI2_E8", "FLI2_LDWSState_E8_sE8"),
        },
        {
            "StateOfLDWS": ("CAN_MFC_Public_FLI2_E8", "FLI2_LDWSState_E8"),
        },
        {
            "StateOfLDWS": ("CAN_VEHICLE_FLI2_E8", "FLI2_LDWSState_E8"),
        },
        {
            "StateOfLDWS": (
                "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_OmLatControlMessages_FLI2_lane_departure_warning_system_state"),

        },
        {
            "StateOfLDWS": ("CAN_SRR_Private_FLI2_E8", "FLI2_LDWSState_E8"),

        },
        {
            "StateOfLDWS": (
                "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_OmLatControlMessages.FLI2.lane_departure_warning_system_state"),
        },
    ]

    def check(self):
        group = self.source.selectSignalGroup(self.sgs)
        return group

    def fill(self, group):
        # get signals
        t, LDWS_state = group.get_signal("StateOfLDWS")

        # init report
        title = "FLC20 LDWS state"
        votes = self.batch.get_labelgroups(title)
        report = Report(cIntervalList(t), title, votes=votes)

        # find intervals
        LDWS_not_ready = (LDWS_state == 0)
        LDWS_not_avail = (LDWS_state == 1)
        LDWS_deact_drv = (LDWS_state == 2)
        LDWS_ready = (LDWS_state == 3)
        LDWS_driver_ovrd = (LDWS_state == 4)
        LDWS_warning = (LDWS_state == 5)
        LDWS_error = (LDWS_state > 5)

        for st, end in maskToIntervals(LDWS_not_ready):
            index = report.addInterval((st, end))
            report.vote(index, title, 'not ready')

        for st, end in maskToIntervals(LDWS_not_avail):
            index = report.addInterval((st, end))
            report.vote(index, title, 'temp. not avail')

        for st, end in maskToIntervals(LDWS_deact_drv):
            index = report.addInterval((st, end))
            report.vote(index, title, 'deact. by driver')

        for st, end in maskToIntervals(LDWS_ready):
            index = report.addInterval((st, end))
            report.vote(index, title, 'ready')

        for st, end in maskToIntervals(LDWS_driver_ovrd):
            index = report.addInterval((st, end))
            report.vote(index, title, 'driver override')

        for st, end in maskToIntervals(LDWS_warning):
            index = report.addInterval((st, end))
            report.vote(index, title, 'warning')

        for st, end in maskToIntervals(LDWS_error):
            index = report.addInterval((st, end))
            report.vote(index, title, 'error')

        report.sort()
        return report

    def search(self, report):
        self.batch.add_entry(report, result=self.PASSED)
        return
