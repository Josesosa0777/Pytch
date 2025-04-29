# -*- dataeval: init -*-

import numpy as np

import datavis
from interface import iView


class View(iView):
    def check(self):
        sgs = [
            {
                "BSD2_WarningLevel_Front_D0": ("CAN_MFC_Public_BSD2_D0", "BSD2_WarningLevel_Front_D0"),
                "BSD2_WarningLevel_Right_D0": ("CAN_MFC_Public_BSD2_D0", "BSD2_WarningLevel_Right_D0"),

                "BSD4_LatDispMIORightSide_D0": ("CAN_MFC_Public_BSD4_D0", "BSD4_LatDispMIORightSide_D0"),
                "BSD4_LonDispMIORightSide_D0": ("CAN_MFC_Public_BSD4_D0", "BSD4_LonDispMIORightSide_D0"),

                "BSD5_LatDispMIOFront_D0": ("CAN_MFC_Public_BSD5_D0", "BSD5_LatDispMIOFront_D0"),
                "BSD5_LonDispMIOFront_D0": ("CAN_MFC_Public_BSD5_D0", "BSD5_LonDispMIOFront_D0"),

                "EBC2_FrontAxleSpeed": ("CAN_MFC_ARS_EBC2_0B", "EBC2_FrontAxleSpeed_0B"),

                "EBC1_EBSBrakeSwitch": ("CAN_MFC_ARS_EBC1_0B", "EBC1_EBSBrakeSwitch_0B"),
                "OEL_TurnSignalSwitch": ("CAN_MFC_Public_OEL_32", "OEL_TurnSignalSwitch_32"),

                "VDC2_SteerWhlAngle": ("CAN_MFC_Public_VDC2_0B", "VDC2_SteerWhlAngle_0B"),

            },
            {
                "BSD2_WarningLevel_Front_D0": ("CAN_MFC_Public_BSD2_D0", "BSD2_WarningLevel_Front_D0"),
                "BSD2_WarningLevel_Right_D0": ("CAN_MFC_Public_BSD2_D0", "BSD2_WarningLevel_Right_D0"),

                "BSD4_LatDispMIORightSide_D0": ("CAN_MFC_Public_BSD4_D0", "BSD4_LatDispMIORightSide_D0"),
                "BSD4_LonDispMIORightSide_D0": ("CAN_MFC_Public_BSD4_D0", "BSD4_LonDispMIORightSide_D0"),

                "BSD5_LatDispMIOFront_D0": ("CAN_MFC_Public_BSD5_D0", "BSD5_LatDispMIOFront_D0"),
                "BSD5_LonDispMIOFront_D0": ("CAN_MFC_Public_BSD5_D0", "BSD5_LonDispMIOFront_D0"),

                "EBC2_FrontAxleSpeed": ("CAN_MFC_Public_EBC2_0B","EBC2_FrontAxleSpeed_0B"),

                "EBC1_EBSBrakeSwitch": ("CAN_MFC_Public_EBC1_0B","EBC1_EBSBrakeSwitch_0B"),
                "OEL_TurnSignalSwitch": ("CAN_MFC_Public_OEL_32", "OEL_TurnSignalSwitch_32"),

                "VDC2_SteerWhlAngle": ("CAN_MFC_Public_VDC2_0B", "VDC2_SteerWhlAngle_0B"),

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
        pn = datavis.cPlotNavigator(title="BSIS/MOIS Plot", fontSize='large')

        ax = pn.addAxis(ylabel="")
        if 'BSD2_WarningLevel_Front_D0' in group:
            time00, value00, unit00 = group.get_signal_with_unit("BSD2_WarningLevel_Front_D0")
            pn.addSignal2Axis(ax, "BSD2_WarningLevel_Front", time00, value00, unit=unit00, linewidth=2)

        ax = pn.addAxis(ylabel="")
        if 'BSD2_WarningLevel_Right_D0' in group:
            time00, value00, unit00 = group.get_signal_with_unit("BSD2_WarningLevel_Right_D0")
            pn.addSignal2Axis(ax, "BSD2_WarningLevel_Right", time00, value00, unit=unit00, linewidth=2)

        ax = pn.addAxis(ylabel="")
        if 'BSD4_LatDispMIORightSide_D0' in group:
            time00, value00, unit00 = group.get_signal_with_unit("BSD4_LatDispMIORightSide_D0")
            pn.addSignal2Axis(ax, "BSD4_LatDispMIORightSide", time00, value00, unit=unit00, linewidth=2,color='g')

        ax = pn.addAxis(ylabel="")
        if 'BSD4_LonDispMIORightSide_D0' in group:
            time00, value00, unit00 = group.get_signal_with_unit("BSD4_LonDispMIORightSide_D0")
            pn.addSignal2Axis(ax, "BSD4_LonDispMIORightSide", time00, value00, unit=unit00, linewidth=2,color='g')

        ax = pn.addAxis(ylabel="")
        if 'BSD5_LatDispMIOFront_D0' in group:
            time00, value00, unit00 = group.get_signal_with_unit("BSD5_LatDispMIOFront_D0")
            pn.addSignal2Axis(ax, "BSD5_LatDispMIOFront", time00, value00, unit=unit00, linewidth=2,color='r')

        ax = pn.addAxis(ylabel="")
        if 'BSD5_LonDispMIOFront_D0' in group:
            time00, value00, unit00 = group.get_signal_with_unit("BSD5_LonDispMIOFront_D0")
            pn.addSignal2Axis(ax, "BSD5_LonDispMIOFront", time00, value00, unit=unit00, linewidth=2,color='r')

        # Subplot 2
        ax = pn.addAxis(ylabel="")
        if 'EBC2_FrontAxleSpeed' in group:
            time00, value00, unit00 = group.get_signal_with_unit("EBC2_FrontAxleSpeed")
            pn.addSignal2Axis(ax, "EBC2_FrontAxleSpeed", time00, value00, unit=unit00, linewidth=2,color='darkviolet')

        ax = pn.addAxis(ylabel="")
        if 'OEL_TurnSignalSwitch' in group:
            time00, value00, unit00 = group.get_signal_with_unit("OEL_TurnSignalSwitch")
            pn.addSignal2Axis(ax, "OEL_TurnSignalSwitch", time00, value00, unit=unit00, linewidth=2,color='magenta')

        ax = pn.addAxis(ylabel="")
        if 'EBC1_EBSBrakeSwitch' in group:
            time04, value04, unit04 = group.get_signal_with_unit("EBC1_EBSBrakeSwitch")
            pn.addSignal2Axis(ax, "EBC1_EBSBrakeSwitch", time04, value04, unit=unit04, linewidth=2,color='dodgerblue')

        ax = pn.addAxis(ylabel="")
        if 'VDC2_SteerWhlAngle' in group:
            time04, value04, unit04 = group.get_signal_with_unit("VDC2_SteerWhlAngle")
            pn.addSignal2Axis(ax, "VDC2_SteerWhlAngle", time04, value04, unit=unit04, linewidth=2,color='orange')

        self.sync.addClient(pn)
        return
