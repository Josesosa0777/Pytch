# -*- dataeval: init -*-

"""
Search for events of engine running / not running
"""

import interface
import numpy as np
from measproc import cIntervalList
from measproc.report2 import Report

class Search(interface.iSearch):

    def check(self):
        sgs = [
            {
                "n_engine": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                             "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_EEC1_EEC1_EngSpd"),
            },
            {
                "n_engine": ("MFC5xx_Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFdf_CanInput_EEC1_EEC1_EngSpd"),
            },
            {
                "n_engine": ("EEC1_00_s00", "EEC1_EngSpd_00"),
            },
            {
                "n_engine": ("EEC1_00", "EEC1_EngSpd_00_s00"),
            },
            {
                "n_engine": ("EEC1", "EngSpeed_s00"),

            },
            {
                "n_engine": ("EEC1_00_s00", "EEC1_EngSpeed_00"),
            },
            {
                "n_engine": ("EEC1_00", "EEC1_EngSpd_00"),
            },
            {
                "n_engine": ("EEC1_00_s00", "EngineSpeed"),
            },
            {  # FLR20, ARS430 combined endurance run
                "n_engine": ("EEC1_00", "EEC1_EngSpd_00_C2"),
            },
            {  # FLR25 #TODO need to change and get CAN signal
                "n_engine": ("Rte_SWC_AEBS_RPort_aebs_im_general_DEP_im_aebs_general_Buf",
                             "ARS4xx_Device_SW_Every10ms_Rte_SWC_AEBS_RPort_aebs_im_general_DEP_im_aebs_general_Buf_EngineSpeed"),
            },
            {  # FCW #TODO need to change and get CAN signal
                "n_engine": ("EEC1_s00", "EEC1_EngSpd_s00"),
            },
            {
                "n_engine": ("EEC1_00_s00_EEC1_00_CAN21", "EEC1_EngSpd_00"),
            },
            {
                "n_engine": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                             "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_EEC1_EEC1_EngSpd"),
            },
            {
                "n_engine": ("Rte_SWC_Preprocessor_RPort_prep_norm_EEC1_DEP_norm_prep_postp_EEC1_Buf",
                             "ARS4xx_Device_SW_Every10ms_Rte_SWC_Preprocessor_RPort_prep_norm_EEC1_DEP_norm_prep_postp_EEC1_Buf_EEC1_EngSpd"),
            },
            {
                "n_engine": ("CAN_Vehicle_EEC1_00", "EEC1_EngSpd_00"),
            },
            {
                "n_engine": ("CAN_MFC_Public_EEC1_00","EEC1_EngSpd_00"),

            },
        ]
        group = self.source.selectSignalGroup(sgs)
        return group

    def fill(self, group):
        time, n_engine = group.get_signal('n_engine')

        votes = self.batch.get_labelgroups("is_file_corrupt")
        report = Report(cIntervalList(time), "is_file_corrupt", votes=votes)

        if np.any(np.diff(time) > 100):
            # add intervals
            intervals = {
                'yes': (n_engine >= 1.0) & (n_engine < 8128.0),
                'no': n_engine < 1.0,
            }
            for vote, mask in intervals.iteritems():
                intvals = cIntervalList.fromMask(time, mask)
                for st, end in intvals:
                    index = report.addInterval([st, end])
                    report.vote(index, 'is_file_corrupt', vote)
                    break
                break

        return report

    def search(self, report):
        self.batch.add_entry(report, result=self.PASSED)
        return
