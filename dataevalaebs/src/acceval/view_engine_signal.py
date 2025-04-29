# -*- dataeval: init -*-

"""
Plot basic driver activities and AEBS outputs

AEBS-relevant driver activities (pedal activation, steering etc.) and
AEBS outputs (in AEBS1 and XBR messages) are shown.
"""

import numpy as np

import datavis
from interface import iView


class View(iView):
    def check(self):
        sgs = [
            {
                "EBC2_MeanSpdFA_0B": ("EBC2_0B", "EBC2_MeanSpdFA_0B"),
                "TSC1_EngineReqTorqueHR_2A": ("TSC1_00_2A", "TSC1_EngineReqTorqueHR_2A"),
                "TSC1_OverrideControlMode_2A_00": ("TSC1_00_2A", "TSC1_OverrideControlMode_2A_00"),
                "TSC1_ReqTorqueLimit_2A_00": ("TSC1_00_2A", "TSC1_ReqTorqueLimit_2A_00"),
                "XBR_CtrlMode_2A": ("XBR_0B_2A", "XBR_CtrlMode_2A"),
                "XBR_ExtAccelDem_2A": ("XBR_0B_2A", "XBR_ExtAccelDem_2A"),

                "EBC1_EBSBrkSw_0B": ("EBC1_0B", "EBC1_EBSBrkSw_0B"),
                "EBC5_FoundationBrakeUse_0B": ("EBC5_0B", "EBC5_FoundationBrakeUse_0B"),
                "EEC2_APPos1_00": ("EEC2_00", "EEC2_APPos1_00"),
                "EBC1_BrkPedPos_0B": ("EBC1_0B", "EBC1_BrkPedPos_0B"),
                "ETC2_CurrentGear_03": ("ETC2_03", "ETC2_CurrentGear_03"),
                "ETC2_SelectGear_03": ("ETC2_03", "ETC2_SelectGear_03"),
            },
            {
                "EBC2_MeanSpdFA_0B": ("EBC2_0B", "EBC2_MeanSpdFA_0B"),
                "TSC1_EngineReqTorqueHR_2A": ("TSC1_2A_00", "TSC1_EngineReqTorqueHR_2A"),
                "TSC1_OverrideControlMode_2A_00": ("TSC1_2A_00", "TSC1_OverrideControlMode_2A_00"),
                "TSC1_ReqTorqueLimit_2A_00": ("TSC1_2A_00", "TSC1_ReqTorqueLimit_2A_00"),
                "XBR_CtrlMode_2A": ("XBR_2A", "XBR_CtrlMode_2A"),
                "XBR_ExtAccelDem_2A": ("XBR_2A", "XBR_ExtAccelDem_2A"),

                "EBC1_EBSBrkSw_0B": ("EBC1_0B", "EBC1_EBSBrkSw_0B"),
                "EBC5_FoundationBrakeUse_0B": ("EBC5_0B", "EBC5_FoundationBrakeUse_0B"),
                "EEC2_APPos1_00": ("EEC2_00", "EEC2_APPos1_00"),
                "EBC1_BrkPedPos_0B": ("EBC1_0B", "EBC1_BrkPedPos_0B"),
                "ETC2_CurrentGear_03": ("ETC2_03", "ETC2_CurrentGear_03"),
                "ETC2_SelectGear_03": ("ETC2_03", "ETC2_SelectGear_03"),
            },
            {
                "EBC2_MeanSpdFA_0B": ("EBC2_0B_s0B", "EBC2_MeanSpdFA_0B"),
                "TSC1_EngineReqTorqueHR_2A": ("TSC1_00_2A_d00_s2A", "TSC1_EngineReqTorqueHR_2A"),
                "TSC1_OverrideControlMode_2A_00": ("TSC1_00_2A_d00_s2A", "TSC1_OverrideControlMode_2A_00"),
                "TSC1_ReqTorqueLimit_2A_00": ("TSC1_00_2A_d00_s2A", "TSC1_ReqTorqueLimit_2A_00"),
                "XBR_CtrlMode_2A": ("XBR_0B_2A_d0B_s2A", "XBR_CtrlMode_2A"),
                "XBR_ExtAccelDem_2A": ("XBR_0B_2A_d0B_s2A", "XBR_ExtAccelDem_2A"),

                "EBC1_EBSBrkSw_0B": ("EBC1_0B_s0B", "EBC1_EBSBrkSw_0B"),
                "EBC5_FoundationBrakeUse_0B": ("EBC5_0B_s0B", "EBC5_FoundationBrakeUse_0B"),
                "EEC2_APPos1_00": ("EEC2_00_s00", "EEC2_APPos1_00"),
                "EBC1_BrkPedPos_0B": ("EBC1_0B_s0B", "EBC1_BrkPedPos_0B"),
                "ETC2_CurrentGear_03": ("ETC2_03_s03", "ETC2_CurrentGear_03"),
                "ETC2_SelectGear_03": ("ETC2_03_s03", "ETC2_SelectGear_03"),
            }
        ]
        # select signals
        group = self.source.selectLazySignalGroup(sgs)
        # give warning for not available signals
        for alias in sgs[0]:
            if alias not in group:
                self.logger.warning("Signal for '%s' not available" % alias)
        return group

    def view(self, group):
        pn = datavis.cPlotNavigator(title="Engine Evaluation")


        # ACC_SetSpeed
        ax = pn.addAxis(ylabel="")
        if 'EBC2_MeanSpdFA_0B' in group:
            time04, value04, unit04 = group.get_signal_with_unit("EBC2_MeanSpdFA_0B")
            pn.addSignal2Axis(ax, "EBC2_MeanSpdFA_0B", time04, value04, unit=unit04)
        if 'TSC1_EngineReqTorqueHR_2A' in group:
            time04, value04, unit04 = group.get_signal_with_unit("TSC1_EngineReqTorqueHR_2A")
            pn.addSignal2Axis(ax, "TSC1_EngineReqTorqueHR_2A", time04, value04, unit=unit04)

        ax = pn.addAxis(ylabel="")

        if 'TSC1_OverrideControlMode_2A_00' in group:
            time04, value04, unit04 = group.get_signal_with_unit("TSC1_OverrideControlMode_2A_00")
            pn.addSignal2Axis(ax, "TSC1_OverrideControlMode_2A_00", time04, value04, unit=unit04)
        if 'TSC1_ReqTorqueLimit_2A_00' in group:
            time04, value04, unit04 = group.get_signal_with_unit("TSC1_ReqTorqueLimit_2A_00")
            pn.addSignal2Axis(ax, "TSC1_ReqTorqueLimit_2A_00", time04, value04, unit=unit04)

        ax = pn.addAxis(ylabel="")
        if 'XBR_CtrlMode_2A' in group:
            time04, value04, unit04 = group.get_signal_with_unit("XBR_CtrlMode_2A")
            pn.addSignal2Axis(ax, "XBR_CtrlMode_2A", time04, value04, unit=unit04)
        if 'XBR_ExtAccelDem_2A' in group:
            time04, value04, unit04 = group.get_signal_with_unit("XBR_ExtAccelDem_2A")
            pn.addSignal2Axis(ax, "XBR_ExtAccelDem_2A", time04, value04, unit=unit04)

        ax = pn.addAxis(ylabel="")
        if 'EBC1_EBSBrkSw_0B' in group:
            time04, value04, unit04 = group.get_signal_with_unit("EBC1_EBSBrkSw_0B")
            pn.addSignal2Axis(ax, "EBC1_EBSBrkSw_0B", time04, value04, unit=unit04)
        if 'EBC5_FoundationBrakeUse_0B' in group:
            time04, value04, unit04 = group.get_signal_with_unit("EBC5_FoundationBrakeUse_0B")
            pn.addSignal2Axis(ax, "EBC5_FoundationBrakeUse_0B", time04, value04, unit=unit04)

        ax = pn.addAxis(ylabel="")
        if 'EEC2_APPos1_00' in group:
            time04, value04, unit04 = group.get_signal_with_unit("EEC2_APPos1_00")
            pn.addSignal2Axis(ax, "EEC2_APPos1_00", time04, value04, unit=unit04)
        if 'EBC1_BrkPedPos_0B' in group:
            time04, value04, unit04 = group.get_signal_with_unit("EBC1_BrkPedPos_0B")
            pn.addSignal2Axis(ax, "EBC1_BrkPedPos_0B", time04, value04, unit=unit04)

        ax = pn.addAxis()
        if 'ETC2_CurrentGear_03' in group:
            time04, value04, unit04 = group.get_signal_with_unit("ETC2_CurrentGear_03")
            pn.addSignal2Axis(ax, "ETC2_CurrentGear_03", time04, value04, unit=unit04)
        if 'ETC2_SelectGear_03' in group:
            time04, value04, unit04 = group.get_signal_with_unit("ETC2_SelectGear_03")
            pn.addSignal2Axis(ax, "ETC2_SelectGear_03", time04, value04, unit=unit04)

        self.sync.addClient(pn)
        return

    def extend_aebs_state_axis(self, pn, ax):
        return
