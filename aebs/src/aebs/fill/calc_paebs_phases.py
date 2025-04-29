# -*- dataeval: init -*-
import interface
import numpy
from primitives.aebs import AebsPhases

init_params = {
    'flc25': dict(
        # add signals for paebs events
        sgn_group=[  # PAEBS
            {
                "PAEBSState": ("AEBS1_A1_sA1", "AEBS1_AEBSState_A1"),
                "CollisionWarningLevel": ("AEBS1_A1_sA1", "AEBS1_CollisionWarningLevel_A1"),
            },
            {
                "PAEBSState": ("AEBS1_A1", "AEBS1_AEBSState_A1_sA1"),
                "CollisionWarningLevel": ("AEBS1_A1", "AEBS1_CollisionWarningLevel_A1_sA1"),
            },
            {
                "PAEBSState": ("MTSI_stKBFreeze_020ms_t",
                               "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_OmLonControlMessages_AEBS1_Paebs_forward_collision_aebs_state"),
                "CollisionWarningLevel": ("MTSI_stKBFreeze_020ms_t",
                                          "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_OmLonControlMessages_AEBS1_Paebs_collision_warning_level"),
            },
            {
                "PAEBSState": ("MTSI_stKBFreeze_020ms_t",
                               "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_system_state"),
                "CollisionWarningLevel": ("MTSI_stKBFreeze_020ms_t",
                                          "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_warning_level"),
            },
            {
                "PAEBSState": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                               "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_system_state"),
                "CollisionWarningLevel": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                          "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_warning_level"),
            },
            {
                "PAEBSState": ("AEBS1_2A", "AEBS1_AEBSState_2A"),
                "CollisionWarningLevel": ("AEBS1_2A", "AEBS1_CollisionWarningLevel_2A"),
            },
            {
                "PAEBSState": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                               "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_PaebsOutput.hmi.paebs_system_state"),
                "CollisionWarningLevel": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                          "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_PaebsOutput.hmi.paebs_warning_level"),
            },
        ]),

    'paebs': dict(
        # add signals for paebs events
        sgn_group=[  # PAEBS
            {
                "PAEBSState": ("AEBS1_A1_sA1", "AEBS1_AEBSState_A1"),
                "CollisionWarningLevel": ("AEBS1_A1_sA1", "AEBS1_CollisionWarningLevel_A1"),
            },
            {
                "PAEBSState": ("CAN_MFC_Public_AEBS1_2A", "AEBS1_AEBSState_2A"),
                "CollisionWarningLevel": ("CAN_MFC_Public_AEBS1_2A", "AEBS1_CollisionWarningLevel_2A"),
            },
            {
                "PAEBSState": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                               "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_PaebsOutput.hmi.paebs_system_state"),
                "CollisionWarningLevel": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                          "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_PaebsOutput.hmi.paebs_warning_level"),
            },
            {
                "PAEBSState": ("MFC5xx_Device.KB.MTSI_stKBFreeze_020ms_t",
                               "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_system_state"),
                "CollisionWarningLevel": ("MFC5xx_Device.KB.MTSI_stKBFreeze_020ms_t",
                                          "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_warning_level"),
            },
            {
                "PAEBSState": ("AEBS1_A1", "AEBS1_AEBSState_A1_sA1"),
                "CollisionWarningLevel": ("AEBS1_A1", "AEBS1_CollisionWarningLevel_A1_sA1"),
            },
            {
                "PAEBSState": ("MTSI_stKBFreeze_020ms_t",
                               "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_OmLonControlMessages_AEBS1_Paebs_forward_collision_aebs_state"),
                "CollisionWarningLevel": ("MTSI_stKBFreeze_020ms_t",
                                          "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_OmLonControlMessages_AEBS1_Paebs_collision_warning_level"),
            },
            {
                "CollisionWarningLevel": ("MTSI_stKBFreeze_040ms_t",
                                          "MFC5xx_Device_KB_MTSI_stKBFreeze_040ms_t_sFlc25_EbOutput_hmi_output_aebs_warning_level"),
                "PAEBSState": ("MTSI_stKBFreeze_040ms_t",
                               "MFC5xx_Device_KB_MTSI_stKBFreeze_040ms_t_sFlc25_EbOutput_hmi_output_aebs_system_state"),
            },
            {
                "PAEBSState": ("MTSI_stKBFreeze_020ms_t",
                               "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_system_state"),
                "CollisionWarningLevel": ("MTSI_stKBFreeze_020ms_t",
                                          "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_warning_level"),
            },
            {
                "PAEBSState": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                               "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_system_state"),
                "CollisionWarningLevel": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                          "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_warning_level"),
            },
            {
                "PAEBSState": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                               "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_PaebsOutput.hmi.paebs_system_state"),
                "CollisionWarningLevel": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                          "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_PaebsOutput.hmi.paebs_warning_level"),
            },
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
        time, status = group.get_signal('PAEBSState')
        level = group.get_value('CollisionWarningLevel', ScaleTime=time)
        return time, status, level

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
    data = manager_modules.calc('calc_paebs_phases-flc25@aebs.fill', manager)
    print(data)
