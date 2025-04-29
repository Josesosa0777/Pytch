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
                "AEBS1_AEBSState_2A_s2A": ("AEBS1_2A", "AEBS1_AEBSState_2A_s2A"),

                "FLI2_LDWSState_E8_sE8": ("FLI2_E8", "FLI2_LDWSState_E8_sE8"),
                "DM1_DTC1_E8_sE8": ("DM1_E8", "DM1_DTC1_E8_sE8"),
                "DM1_DTC2_E8_sE8": ("DM1_E8", "DM1_DTC2_E8_sE8"),
                "DM1_DTC3_E8_sE8": ("DM1_E8", "DM1_DTC3_E8_sE8"),
                "DM1_DTC4_E8_sE8": ("DM1_E8", "DM1_DTC4_E8_sE8"),
                "DM1_DTC5_E8_sE8": ("DM1_E8", "DM1_DTC5_E8_sE8"),

                "FLI2_FwdLaneImagerStatus_E8_sE8": ("FLI2_E8", "FLI2_FwdLaneImagerStatus_E8_sE8"),

                "DM1_DTC1_A0_sA0": ("DM1_A0", "DM1_DTC1_A0_sA0"),
                "DM1_DTC2_A0_sA0": ("DM1_A0", "DM1_DTC2_A0_sA0"),
                "DM1_DTC3_A0_sA0": ("DM1_A0", "DM1_DTC3_A0_sA0"),
                "DM1_DTC4_A0_sA0": ("DM1_A0", "DM1_DTC4_A0_sA0"),
                "DM1_DTC5_A0_sA0": ("DM1_A0", "DM1_DTC5_A0_sA0"),
            },
            {
                "AEBS1_AEBSState_2A_s2A": ("CAN_MFC_Public_AEBS1_2A", "AEBS1_AEBSState_2A"),

                "FLI2_LDWSState_E8_sE8": ("CAN_MFC_Public_FLI2_E8", "FLI2_LDWSState_E8"),

                "DM1_DTC1_E8_sE8": ("CAN_MFC_Public_DM1_0B", "DM1_DTC1_0B"),
                "DM1_DTC2_E8_sE8": ("CAN_MFC_Public_DM1_0B", "DM1_DTC2_0B"),
                "DM1_DTC3_E8_sE8": ("CAN_MFC_Public_DM1_0B", "DM1_DTC3_0B"),
                "DM1_DTC4_E8_sE8": ("CAN_MFC_Public_DM1_0B", "DM1_DTC4_0B"),
                "DM1_DTC5_E8_sE8": ("CAN_MFC_Public_DM1_0B", "DM1_DTC5_0B"),

                "FLI2_FwdLaneImagerStatus_E8_sE8": ("CAN_MFC_Public_FLI2_E8", "FLI2_FwdLaneImagerStatus_E8"),

                "DM1_DTC1_A0_sA0": ("CAN_MFC_Public_DM1_2A", "DM1_DTC1_2A"),
                "DM1_DTC2_A0_sA0": ("CAN_MFC_Public_DM1_2A", "DM1_DTC2_2A"),
                "DM1_DTC3_A0_sA0": ("CAN_MFC_Public_DM1_2A", "DM1_DTC3_2A"),
                "DM1_DTC4_A0_sA0": ("CAN_MFC_Public_DM1_2A", "DM1_DTC4_2A"),
                "DM1_DTC5_A0_sA0": ("CAN_MFC_Public_DM1_2A", "DM1_DTC5_2A"),

            },
            {
                "AEBS1_AEBSState_2A_s2A": ("CAN_MFC_Public_AEBS1_2A", "AEBS1_AEBSState_2A"),

                "FLI2_LDWSState_E8_sE8": ("CAN_MFC_Public_FLI2_E8", "FLI2_LDWSState_E8"),

                "DM1_DTC1_E8_sE8": ("idx102", "DM1_DTC1_0B"),
                "DM1_DTC2_E8_sE8": ("idx102", "DM1_DTC2_0B"),
                "DM1_DTC3_E8_sE8": ("idx102", "DM1_DTC3_0B"),
                "DM1_DTC4_E8_sE8": ("idx102", "DM1_DTC4_0B"),
                "DM1_DTC5_E8_sE8": ("idx102", "DM1_DTC5_0B"),

                "FLI2_FwdLaneImagerStatus_E8_sE8": ("CAN_MFC_Public_FLI2_E8", "FLI2_FwdLaneImagerStatus_E8"),

                "DM1_DTC1_A0_sA0": ("CAN_MFC_Public_DM1_2A", "DM1_DTC1_2A"),
                "DM1_DTC2_A0_sA0": ("CAN_MFC_Public_DM1_2A", "DM1_DTC2_2A"),
                "DM1_DTC3_A0_sA0": ("CAN_MFC_Public_DM1_2A", "DM1_DTC3_2A"),
                "DM1_DTC4_A0_sA0": ("CAN_MFC_Public_DM1_2A", "DM1_DTC4_2A"),
                "DM1_DTC5_A0_sA0": ("CAN_MFC_Public_DM1_2A", "DM1_DTC5_2A"),
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
        pn = datavis.cPlotNavigator(title="Sys Bitfield event")

        ax = pn.addAxis(ylabel="")

        # Subplot 1
        if 'AEBS1_AEBSState_2A_s2A' in group:
            time00, value00, unit00 = group.get_signal_with_unit("AEBS1_AEBSState_2A_s2A")
            value_2 = (value00 == 14).astype(int)
            pn.addSignal2Axis(ax, "AEBS1_AEBSState_2A_s2A.", time00, value_2, unit=unit00)

        if 'FLI2_LDWSState_E8_sE8' in group:
            time00, value00, unit00 = group.get_signal_with_unit("FLI2_LDWSState_E8_sE8")
            value_2 = (value00 == 14).astype(int)
            pn.addSignal2Axis(ax, "FLI2_LDWSState_E8_sE8.", time00, value_2, unit=unit00)

        if 'DM1_DTC1_E8_sE8' in group:
            time00, value00, unit00 = group.get_signal_with_unit("DM1_DTC1_E8_sE8")
            value_2 = (value00 !=0).astype(int)
            pn.addSignal2Axis(ax, "DM1_DTC1_E8_sE8.", time00, value_2, unit=unit00)

        if 'DM1_DTC2_E8_sE8' in group:
            time00, value00, unit00 = group.get_signal_with_unit("DM1_DTC2_E8_sE8")
            value_2 = (value00 !=0).astype(int)
            pn.addSignal2Axis(ax, "DM1_DTC2_E8_sE8.", time00, value_2, unit=unit00)

        if 'DM1_DTC3_E8_sE8' in group:
            time00, value00, unit00 = group.get_signal_with_unit("DM1_DTC3_E8_sE8")
            value_2 = (value00 !=0).astype(int)
            pn.addSignal2Axis(ax, "DM1_DTC3_E8_sE8.", time00, value_2, unit=unit00)

        if 'DM1_DTC4_E8_sE8' in group:
            time00, value00, unit00 = group.get_signal_with_unit("DM1_DTC4_E8_sE8")
            value_2 = (value00 != 0).astype(int)
            pn.addSignal2Axis(ax, "DM1_DTC4_E8_sE8.", time00, value_2, unit=unit00)

        if 'DM1_DTC5_E8_sE8' in group:
            time00, value00, unit00 = group.get_signal_with_unit("DM1_DTC5_E8_sE8")
            value_2 = (value00 != 0).astype(int)
            pn.addSignal2Axis(ax, "DM1_DTC5_E8_sE8.", time00, value_2, unit=unit00)

        if 'FLI2_FwdLaneImagerStatus_E8_sE8' in group:
            time00, value00, unit00 = group.get_signal_with_unit("FLI2_FwdLaneImagerStatus_E8_sE8")
            value_2 = (value00 > 1).astype(int)
            pn.addSignal2Axis(ax, "FLI2_FwdLaneImagerStatus_E8_sE8.", time00, value_2, unit=unit00)

        if 'DM1_DTC1_A0_sA0' in group:
            time00, value00, unit00 = group.get_signal_with_unit("DM1_DTC1_A0_sA0")
            value_2 = (value00 != 0).astype(int)
            pn.addSignal2Axis(ax, "DM1_DTC1_A0_sA0.", time00, value_2, unit=unit00)

        if 'DM1_DTC2_A0_sA0' in group:
            time00, value00, unit00 = group.get_signal_with_unit("DM1_DTC2_A0_sA0")
            value_2 = (value00 != 0).astype(int)
            pn.addSignal2Axis(ax, "DM1_DTC2_A0_sA0.", time00, value_2, unit=unit00)

        if 'DM1_DTC3_A0_sA0' in group:
            time00, value00, unit00 = group.get_signal_with_unit("DM1_DTC3_A0_sA0")
            value_2 = (value00 != 0).astype(int)
            pn.addSignal2Axis(ax, "DM1_DTC3_A0_sA0.", time00, value_2, unit=unit00)

        if 'DM1_DTC4_A0_sA0' in group:
            time00, value00, unit00 = group.get_signal_with_unit("DM1_DTC4_A0_sA0")
            value_2 = (value00 != 0).astype(int)
            pn.addSignal2Axis(ax, "DM1_DTC4_A0_sA0.", time00, value_2, unit=unit00)

        if 'DM1_DTC5_A0_sA0' in group:
            time00, value00, unit00 = group.get_signal_with_unit("DM1_DTC5_A0_sA0")
            value_2 = (value00 != 0).astype(int)
            pn.addSignal2Axis(ax, "DM1_DTC5_A0_sA0.", time00, value_2, unit=unit00)

        self.sync.addClient(pn)
        return

    def extend_aebs_state_axis(self, pn, ax):
        return
