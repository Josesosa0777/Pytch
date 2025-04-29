# -*- dataeval: init -*-

import numpy as np

from interface import iSearch
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList, maskToIntervals
from aebs.par.aebs_state import aebs_state_dict
from aebs.par.paebs_state import paebs_state_dict


class Search(iSearch):
    optdep = {
        'egospeedstart': 'set_egospeed-start@egoeval',
        'egospeedmin': 'set_egospeed-min@egoeval',
        'drivdist': 'set_drivendistance@egoeval',
    }

    sgs = [
        {"PAEBSState": ("CAN_MFC_Public_AEBS1_2A", "AEBS1_AEBSState_2A"), },
        {"PAEBSState": ("CAN_VEHICLE_AEBS1_2A", "AEBS1_AEBSState_2A")},
        {"PAEBSState": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                        "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_system_state")},
        {"PAEBSState": ("MTSI_stKBFreeze_020ms_t",
                        "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_system_state")},
        {"PAEBSState": ("AEBS1_A1_sA1", "AEBS1_AEBSState_A1")},
        {"PAEBSState": ("AEBS1_A0_sA0", "FwdCollisionAEBSSysState")},
        {"PAEBSState": ("AEBS1_A0_sA0", "AEBS1_AEBSState_2A")},
        {"PAEBSState": ("AEBS1_2A", "AEBS1_AEBSState_2A")},
        {"PAEBSState": ("AEBS1_A0_sA0", "AEBS1_AEBSState_A0_sA0")},
        {"PAEBSState": ("AEBS1", "AEBS_St")},
        {"PAEBSState": ("AEBS1_2A", "AEBS1_AEBSState_2A_C1")},
        {"PAEBSState": ("AEBS1_A0", "AEBS1_AEBSState_A0")},
    ]

    def check(self):
        group = self.source.selectSignalGroup(self.sgs)
        return group

    def fill(self, group):
        # get signals
        time, status = group.get_signal("PAEBSState")
        # init report
        title = "PAEBS state"
        votes = self.batch.get_labelgroups('PAEBS state')
        report = Report(cIntervalList(time), title, votes=votes)

        if not np.any(np.diff(time) > 100):
            # find intervals
            uniques = np.unique(status)
            for value in uniques:
                mask = status == value
                label = paebs_state_dict[value]
                for st, end in maskToIntervals(mask):
                    index = report.addInterval((st, end))
                    report.vote(index, 'PAEBS state', label)
            report.sort()
            # set general quantities
            for qua in 'drivdist', 'egospeedmin', 'egospeedstart':
                if self.optdep[qua] in self.passed_optdep:
                    set_qua_for_report = self.modules.get_module(self.optdep[qua])
                    set_qua_for_report(report)
                else:
                    self.logger.warning("Inactive module: %s" % self.optdep[qua])
        else:
            self.logger.error("Skip measurement due to high difference in time array")
        return report

    def search(self, report):
        self.batch.add_entry(report, result=self.PASSED)
        return
