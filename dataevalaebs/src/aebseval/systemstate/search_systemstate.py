# -*- dataeval: init -*-

import numpy as np

from interface import iSearch
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList, maskToIntervals
from aebs.par.aebs_state import aebs_state_dict


class Search(iSearch):
    optdep = {
        'egospeedstart': 'set_egospeed-start@egoeval',
        'egospeedmin': 'set_egospeed-min@egoeval',
        'drivdist': 'set_drivendistance@egoeval',
    }

    sgs = [
        {"AEBSState": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                       "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_EbOutput_hmi_output_aebs_system_state")},
        {"AEBSState": ("MTSI_stKBFreeze_020ms_t",
                       "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_EbOutput_hmi_output_aebs_system_state")},
        {"AEBSState": ("MFC5xx_Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_EbOutput_hmi_output_aebs_system_state")},
        {"AEBSState": ("AEBS1_A0_sA0", "FwdCollisionAEBSSysState")},
        {"AEBSState": ("AEBS1_A0_sA0", "AEBS1_AEBSState_2A")},
        {"AEBSState": ("AEBS1_2A", "AEBS1_AEBSState_2A")},
        {"AEBSState": ("AEBS1_A0_sA0", "AEBS1_AEBSState_A0_sA0")},
        {"AEBSState": ("AEBS1", "AEBS_St")},
        {"AEBSState": ("AEBS1_2A", "AEBS1_AEBSState_2A_C1")},
        {"AEBSState": ("AEBS1_A0", "AEBS1_AEBSState_A0")},
        {"AEBSState": ("AEBS1_2A_s2A", "AEBS1_AEBSState_2A")},
        {"AEBSState": ("AEBS1_A0", "AEBS1_AEBSState_A0_sA0")},
        {"AEBSState": ("Rte_SWCNorm_RPort_norm_om_AEBS1_DEP_om_norm_AEBS1_Buf",
                       "ARS4xx_Device_SW_Every10ms_Rte_SWCNorm_RPort_norm_om_AEBS1_DEP_om_norm_AEBS1_Buf_forward_collision_aebs_state")},
        {"AEBSState": ("CAN_Vehicle_AEBS1_2A", "AEBS1_AEBSState_2A")},
        {"AEBSState": ("AEBS1_2A", "AEBS1_AEBSState_2A_s2A")},
        {"AEBSState": ("AEBS1_A1", "AEBS1_AEBSState_A1_sA1")},
        {"AEBSState": ("CAN_VEHICLE_AEBS1_2A","AEBS1_AEBSState_2A")},
        {"AEBSState": ("CAN_MFC_Public_AEBS1_2A","AEBS1_AEBSState_2A")},
    ]

    def check(self):
        group = self.source.selectSignalGroup(self.sgs)
        return group

    def fill(self, group):
        # get signals
        time, status = group.get_signal("AEBSState")

        title = "AEBS state"
        votes = self.batch.get_labelgroups('AEBS state')
        report = Report(cIntervalList(time), title, votes=votes)

        if not np.any(np.diff(time) > 100):
            if status.size != time.size:
                # time = time.resize((n_engine.size))
                time.resize((status.size), refcheck=False)
            # init report
            # find intervals
            uniques = np.unique(status)
            for value in uniques:
                mask = status == value
                if value > 15 or value < 0:
                    value = 15
                    label = aebs_state_dict[value]
                else:
                    label = aebs_state_dict[value]
                for st, end in maskToIntervals(mask):
                    index = report.addInterval((st, end))
                    report.vote(index, 'AEBS state', label)
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
