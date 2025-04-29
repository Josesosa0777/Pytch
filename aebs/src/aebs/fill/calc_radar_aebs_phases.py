# -*- dataeval: init -*-
import interface
import numpy
from primitives.aebs import AebsPhases

init_params = {
    'flr25': dict(
        sgn_group=[  # AEBS
            {
                "AEBSState": ("CAN_MFC_Public_AEBS1_2A", "AEBS1_AEBSState_2A"),
                "CollisionWarningLevel": ("CAN_MFC_Public_AEBS1_2A", "AEBS1_CollisionWarningLevel_2A"),
                "PAEBS_state_check": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                      "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_system_state"),

            },  # MF4
            {
                "AEBSState": ("CAN_MFC_Public_AEBS1_2A", "AEBS1_AEBSState_2A"),
                "CollisionWarningLevel": ("CAN_MFC_Public_AEBS1_2A", "AEBS1_CollisionWarningLevel_2A"),
                "PAEBS_state_check": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                      "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_PaebsOutput.hmi.paebs_system_state"),
            },
            {
                "AEBSState": ("MFC5xx_Device.KB.MTSI_stKBFreeze_020ms_t",
                              "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_EbOutput_hmi_output_aebs_system_state"),
                "CollisionWarningLevel": ("MFC5xx_Device.KB.MTSI_stKBFreeze_020ms_t",
                                          "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_EbOutput_hmi_output_aebs_warning_level"),
                "PAEBS_state_check": ("MFC5xx_Device.KB.MTSI_stKBFreeze_020ms_t",
                                      "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_system_state"),
            },
            {
                "AEBSState": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                              "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_EbOutput_hmi_output_aebs_system_state"),
                "CollisionWarningLevel": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                          "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_EbOutput_hmi_output_aebs_warning_level"),
                "PAEBS_state_check": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                      "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_system_state"),

            },
            {
                "AEBSState": ("MTSI_stKBFreeze_020ms_t",
                              "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_EbOutput_hmi_output_aebs_system_state"),
                "CollisionWarningLevel": ("MTSI_stKBFreeze_020ms_t",
                                          "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_EbOutput_hmi_output_aebs_warning_level"),
                "PAEBS_state_check": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                      "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_system_state"),
            },
            {
                'AEBSState': ("AEBS1_2A_s2A", "AEBS1_AEBSState_2A"),
                'CollisionWarningLevel': ("AEBS1_2A_s2A", "AEBS1_CollisionWarningLevel_2A"),
                "PAEBS_state_check": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                      "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_system_state"),
            },
            {
                "AEBSState": ("AEBS1_2A_s2A", "AEBS1_AdvncdEmrgencyBrakingSyste"),
                "CollisionWarningLevel": ("AEBS1_2A_s2A", "AEBS1_CollisionWarningLevel_2A"),
                "PAEBS_state_check": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                      "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_system_state"),
            },
            {
                "AEBSState": ("AEBS1_A0_sA0", "AEBS1_AEBSState_A0"),
                "CollisionWarningLevel": ("AEBS1_A0_sA0", "AEBS1_CollisionWarningLevel_A0"),
                "PAEBS_state_check": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                      "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_system_state"),
            },
            {
                "AEBSState": ("AEBS1_s2A", "AEBSState"),
                "CollisionWarningLevel": ("AEBS1_s2A", "CollisionWarningLevel"),
                "PAEBS_state_check": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                      "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_system_state"),
            },
            {
                'AEBSState': ('AEBS1_2A', 'AEBS1_AEBSState_2A'),
                'CollisionWarningLevel': ('AEBS1_2A', 'AEBS1_CollisionWarningLevel_2A'),
                "PAEBS_state_check": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                      "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_system_state"),
            },
            {  # FCW
                "AEBSState": ("AEBS1_2A_s2A", "AEBS1_AEBSState_2A_s2A"),
                "CollisionWarningLevel": ("AEBS1_2A_s2A", "AEBS1_CollisionWarningLevel_2A_s2A"),
                "PAEBS_state_check": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                      "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_system_state"),
            },
            {
                "AEBSState": ("AEBS1_A0_sA0", "AEBS1_AEBSState_A0_sA0"),
                "CollisionWarningLevel": ("AEBS1_A0_sA0", "AEBS1_CollisionWarningLevel_A0_sA0"),
                "PAEBS_state_check": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                      "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_system_state"),
            },
            # KBCN
            {
                "AEBSState": ("Rte_SWCNorm_RPort_norm_om_AEBS1_DEP_om_norm_AEBS1_Buf",
                              "ARS4xx_Device_SW_Every10ms_Rte_SWCNorm_RPort_norm_om_AEBS1_DEP_om_norm_AEBS1_Buf_forward_collision_aebs_state"),
                "CollisionWarningLevel": ("Rte_SWCNorm_RPort_norm_om_AEBS1_DEP_om_norm_AEBS1_Buf",
                                          "ARS4xx_Device_SW_Every10ms_Rte_SWCNorm_RPort_norm_om_AEBS1_DEP_om_norm_AEBS1_Buf_collision_warning_level"),
                "PAEBS_state_check": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                      "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_system_state"),
            },
            {
                "AEBSState": ("CAN_Vehicle_AEBS1_2A", "AEBS1_AEBSState_2A"),
                "CollisionWarningLevel": ("CAN_Vehicle_AEBS1_2A", "AEBS1_CollisionWarningLevel_2A"),
                "PAEBS_state_check": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                      "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_system_state"),
            },
            {
                "AEBSState": ("AEBS1_2A", "AEBS1_AEBSState_2A_s2A"),
                "CollisionWarningLevel": ("AEBS1_2A", "AEBS1_CollisionWarningLevel_2A_s2A"),
                "PAEBS_state_check": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                      "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_system_state"),
            },
            {
                "AEBSState": ("AEBS1_A1", "AEBS1_AEBSState_A1_sA1"),
                "CollisionWarningLevel": ("AEBS1_A1", "AEBS1_CollisionWarningLevel_A1_sA1"),
                "PAEBS_state_check": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                      "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_system_state"),
            },
            {"AEBSState": ("CAN_VEHICLE_AEBS1_2A", "AEBS1_AEBSState_2A"),
             "CollisionWarningLevel": ("CAN_VEHICLE_AEBS1_2A", "AEBS1_CollisionWarningLevel_2A"),
             "PAEBS_state_check": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                   "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_system_state"),
             },
            {
                "AEBSState": ("CAN_MFC_Public_AEBS1_2A", "AEBS1_AEBSState_2A"),
                "CollisionWarningLevel": ("CAN_MFC_Public_AEBS1_2A", "AEBS1_CollisionWarningLevel_2A"),
                "PAEBS_state_check": (
                "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_PaebsOutput.hmi.paebs_system_state"),
            }
        ]),
}


class Calc(interface.iCalc):
    WARNING = 5
    PARTIAL = 6
    EMERGENCY = 7
    IN_CRASH = 6

    def init(self, sgn_group):
        self.sgn_group = sgn_group
        self.group = None  # used by user scripts
        return

    def check(self):
        self.group = self.source.selectLazySignalGroup(self.sgn_group).items()
        group = self.source.selectSignalGroup(self.sgn_group)
        time, status = group.get_signal('AEBSState')
        level = group.get_value('CollisionWarningLevel', ScaleTime=time)
        PAEBS_check_value = group.get_value('PAEBS_state_check', ScaleTime=time)
        status_copy = status.copy()
        for idx, realwarn in enumerate(status):
            if (realwarn == 5 and PAEBS_check_value[idx] >= 5 and PAEBS_check_value[idx] <= 7):
                status_copy[idx] = 3
        return time, status_copy, level

    def fill(self, time, status, level):
        in_crash_level = level == self.IN_CRASH
        warning = status == self.WARNING

        partial = status == self.PARTIAL
        emergency = status == self.EMERGENCY
        emergency[in_crash_level] = False
        in_crash = (status == self.EMERGENCY) & in_crash_level

        acoustical = numpy.zeros_like(warning)
        optical = numpy.zeros_like(warning)

        phases = AebsPhases(
            time,
            warning, partial, emergency, in_crash,
            acoustical, optical
        )
        return phases


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\evaluation\pytch2_eval\rrec2mf4\mf4_eval\2025-02-18\mi5id5649__2025-02-18_13-15-53.mf4"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    tracks = manager_modules.calc('calc_radar_aebs_phases-flr25@aebs.fill', manager)
    print(tracks)
