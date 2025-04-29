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
                "AdaptiveCruiseCtrlMode": ("ACC1_2A", "AdaptiveCruiseCtrlMode"),
                "AdaptiveCruiseCtrlSetSpeed": ("ACC1_2A", "AdaptiveCruiseCtrlSetSpeed"),
                "DistanceToForwardVehicle": ("ACC1_2A", "DistanceToForwardVehicle"),
                "SpeedOfForwardVehicle": ("ACC1_2A", "SpeedOfForwardVehicle"),
                "ACCDistanceAlertSignal": ("ACC1_2A", "ACCDistanceAlertSignal"),
                "AdptiveCruiseCtrlSetDistanceMode": ("ACC1_2A", "AdptiveCruiseCtrlSetDistanceMode"),
                "ACCSystemShutoffWarning": ("ACC1_2A", "ACCSystemShutoffWarning"),
                "ActualRetarderPercentTorque": ("ERC1", "ActualRetarderPercentTorque"),
                "RetarderTorqueMode": ("ERC1", "RetarderTorqueMode"),
                "CruiseCtrlAccelerateSwitch": ("CCVS1_27", "CruiseCtrlAccelerateSwitch"),
                "CruiseCtrlEnableSwitch": ("CCVS1_27", "CruiseCtrlEnableSwitch"),
                "CruiseCtrlPauseSwitch": ("CCVS1_27", "CruiseCtrlPauseSwitch"),
                "CruiseCtrlResumeSwitch": ("CCVS1_27", "CruiseCtrlResumeSwitch"),
                "CruiseCtrlSetSwitch": ("CCVS1_27", "CruiseCtrlSetSwitch"),
                "BrakeSwitch": ("CCVS1_27", "BrakeSwitch"),
            },
            {
                "AdaptiveCruiseCtrlMode": ("ACC1_2A", "ACC1_Mode_2A"),
                "AdaptiveCruiseCtrlSetSpeed": ("ACC1_2A", "ACC1_SetSpeed_2A"),
                "DistanceToForwardVehicle": ("ACC1_2A", "ACC1_DistanceOfForwardVehicle_2A"),
                "SpeedOfForwardVehicle": ("ACC1_2A", "ACC1_SpeedOfForwardVehicle_2A"),
                "ACCDistanceAlertSignal": ("ACC1_2A", "ACC1_DistanceAlert_2A"),
                "AdptiveCruiseCtrlSetDistanceMode": ("ACC1_2A", "ACC1_DistanceMode_2A"),
                "ACCSystemShutoffWarning": ("ACC1_2A", "ACC1_SystemShutoffWarning_2A"),
                "ActualRetarderPercentTorque": ("ERC1_10", "ERC1_ActRetPercTrq_10"),
                "RetarderTorqueMode": ("ERC1_10", "ERC1_RetTrqMode_10"),
                "CruiseCtrlAccelerateSwitch": ("CCVS1_27", "CCVS_CCAccelSwitch_27"),
                "CruiseCtrlEnableSwitch": (
                    "ort_prep_norm_CCVS1_DEP_norm_prep_postp_CCVS1_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_Preprocessor_RPort_prep_norm_CCVS1_DEP_norm_prep_postp_CCVS1_Buf_CruiseCtrlEnableSwitch"),
                "CruiseCtrlPauseSwitch": ("CCVS1_27", "CCVS_CCPauseSwitch_27"),
                "CruiseCtrlResumeSwitch": ("CCVS1_27", "CCVS_CCResumeSwitch_27"),
                "CruiseCtrlSetSwitch": ("CCVS1_27", "CCVS_CCSetSwitch_27"),
                "BrakeSwitch": ("CCVS1_27", "CCVS_BrakeSwitch_27"),
            },
            {
                "AdaptiveCruiseCtrlMode": ("ACC1_2A_s2A", "AdaptiveCruiseCtrlMode"),
                "AdaptiveCruiseCtrlSetSpeed": ("ACC1_2A_s2A", "AdaptiveCruiseCtrlSetSpeed"),
                "DistanceToForwardVehicle": ("ACC1_2A_s2A", "DistanceToForwardVehicle"),
                "SpeedOfForwardVehicle": ("ACC1_2A_s2A", "SpeedOfForwardVehicle"),
                "ACCDistanceAlertSignal": ("ACC1_2A_s2A", "ACCDistanceAlertSignal"),
                "AdptiveCruiseCtrlSetDistanceMode": ("ACC1_2A_s2A", "AdptiveCruiseCtrlSetDistanceMode"),
                "ACCSystemShutoffWarning": ("ACC1_2A_s2A", "ACCSystemShutoffWarning"),
                "ActualRetarderPercentTorque": ("ERC1_0F_s0F", "ActualRetarderPercentTorque"),
                "RetarderTorqueMode": ("ERC1_0F_s0F", "RetarderTorqueMode"),
                "CruiseCtrlAccelerateSwitch": ("CCVS1_27_s27", "CruiseCtrlAccelerateSwitch"),
                "CruiseCtrlEnableSwitch": ("CCVS1_27_s27", "CruiseCtrlEnableSwitch"),
                "CruiseCtrlPauseSwitch": ("CCVS1_27_s27", "CruiseCtrlPauseSwitch"),
                "CruiseCtrlResumeSwitch": ("CCVS1_27_s27", "CruiseCtrlResumeSwitch"),
                "CruiseCtrlSetSwitch": ("CCVS1_27_s27", "CruiseCtrlSetSwitch"),
                "BrakeSwitch": ("CCVS1_27_s27", "BrakeSwitch"),
            },
            {
                "AdaptiveCruiseCtrlMode"                    : ("ACC1_2A", "ACC1_Mode_2A"),
                "AdaptiveCruiseCtrlSetSpeed"                : ("ACC1_2A", "ACC1_SetSpeed_2A"),
                "DistanceToForwardVehicle": ("ACC1_2A", "ACC1_DistanceOfForwardVehicle_2A"),
                "SpeedOfForwardVehicle"   : ("ACC1_2A", "ACC1_SpeedOfForwardVehicle_2A"),
                "ACCDistanceAlertSignal"           : ("ACC1_2A", "ACC1_DistanceAlert_2A"),
                "ACCSystemShutoffWarning"    : ("ACC1_2A", "ACC1_SystemShutoffWarning_2A"),
                "AdptiveCruiseCtrlSetDistanceMode"            : ("ACC1_2A", "ACC1_DistanceMode_2A"),
                "ActualRetarderPercentTorque"     :  ("ERC1_10","ERC1_ActRetPercTrq_10"),
                "RetarderTorqueMode"              : ("ERC1_10","ERC1_RetTrqMode_10"),
                "CruiseCtrlAccelerateSwitch": ("CCVS1_27", "CruiseCtrlAccelerateSwitch_s27"),
                "CruiseCtrlEnableSwitch"    : ("CCVS1_27", "CruiseCtrlEnableSwitch_s27"),
                "CruiseCtrlPauseSwitch"     : ("CCVS1_27", "CruiseCtrlPauseSwitch_s27"),
                "CruiseCtrlResumeSwitch"    : ("CCVS1_27", "CruiseCtrlResumeSwitch_s27"),
                "CruiseCtrlSetSwitch"       : ("CCVS1_27", "CruiseCtrlSetSwitch_s27"),
                "BrakeSwitch"               : ("CCVS1_27", "BrakeSwitch_s27"),

            },
        ] #_IDX8877
        # select signals
        group = self.source.selectLazySignalGroup(sgs)
        # give warning for not available signals
        for alias in sgs[0]:
            if alias not in group:
                self.logger.warning("Signal for '%s' not available" % alias)
        return group

    def view(self, group):
        pn = datavis.cPlotNavigator(title="ACC Evaluation")

        ax = pn.addAxis(ylabel="")

        # ACC_mode_2A
        if 'AdaptiveCruiseCtrlMode' in group:
            time00, value00, unit00 = group.get_signal_with_unit("AdaptiveCruiseCtrlMode")
            pn.addSignal2Axis(ax, "AdaptiveCruiseCtrlMode.", time00, value00, unit=unit00)

        if 'AdaptiveCruiseCtrlSetSpeed' in group:
            time04, value04, unit04 = group.get_signal_with_unit("AdaptiveCruiseCtrlSetSpeed")
            pn.addSignal2Axis(ax, "AdaptiveCruiseCtrlSetSpeed", time04, value04, unit=unit04)

        # DistanceToForwardVehicle
        ax = pn.addAxis(ylabel="")
        if 'DistanceToForwardVehicle' in group:
            time00, value00, unit00 = group.get_signal_with_unit("DistanceToForwardVehicle")
            pn.addSignal2Axis(ax, "DistanceToForwardVehicle.", time00, value00, unit=unit00)

        # SpeedOfForwardVehicle
        ax = pn.addAxis(ylabel="")
        if 'SpeedOfForwardVehicle' in group:
            time00, value00, unit00 = group.get_signal_with_unit("SpeedOfForwardVehicle")
            pn.addSignal2Axis(ax, "SpeedOfForwardVehicle.", time00, value00, unit=unit00)
        if 'ACCDistanceAlertSignal' in group:
            time04, value04, unit04 = group.get_signal_with_unit("ACCDistanceAlertSignal")
            pn.addSignal2Axis(ax, "ACCDistanceAlertSignal", time04, value04, unit=unit04)

        # ACC_SetSpeed
        ax = pn.addAxis(ylabel="")

        if 'AdptiveCruiseCtrlSetDistanceMode' in group:
            time04, value04, unit04 = group.get_signal_with_unit("AdptiveCruiseCtrlSetDistanceMode")
            pn.addSignal2Axis(ax, "AdptiveCruiseCtrlSetDistanceMode", time04, value04, unit=unit04)
        if 'ACCSystemShutoffWarning' in group:
            time04, value04, unit04 = group.get_signal_with_unit("ACCSystemShutoffWarning")
            pn.addSignal2Axis(ax, "ACCSystemShutoffWarning", time04, value04, unit=unit04)

        ax = pn.addAxis(ylabel="")
        if 'ActualRetarderPercentTorque' in group:
            time04, value04, unit04 = group.get_signal_with_unit("ActualRetarderPercentTorque")
            pn.addSignal2Axis(ax, "ActualRetarderPercentTorque", time04, value04, unit=unit04)
        if 'RetarderTorqueMode' in group:
            time04, value04, unit04 = group.get_signal_with_unit("RetarderTorqueMode")
            pn.addSignal2Axis(ax, "RetarderTorqueMode", time04, value04, unit=unit04)

        ax = pn.addAxis(ylabel="")
        if 'CruiseCtrlAccelerateSwitch' in group:
            time04, value04, unit04 = group.get_signal_with_unit("CruiseCtrlAccelerateSwitch")
            pn.addSignal2Axis(ax, "CruiseCtrlAccelerateSwitch", time04, value04, unit=unit04)
        if 'CruiseCtrlEnableSwitch' in group:
            time04, value04, unit04 = group.get_signal_with_unit("CruiseCtrlEnableSwitch")
            pn.addSignal2Axis(ax, "CruiseCtrlEnableSwitch", time04, value04, unit=unit04)

        ax = pn.addAxis(ylabel="")
        if 'CruiseCtrlPauseSwitch' in group:
            time04, value04, unit04 = group.get_signal_with_unit("CruiseCtrlPauseSwitch")
            pn.addSignal2Axis(ax, "CruiseCtrlPauseSwitch", time04, value04, unit=unit04)
        if 'CruiseCtrlResumeSwitch' in group:
            time04, value04, unit04 = group.get_signal_with_unit("CruiseCtrlResumeSwitch")
            pn.addSignal2Axis(ax, "CruiseCtrlResumeSwitch", time04, value04, unit=unit04)

        ax = pn.addAxis(ylabel="")
        if 'CruiseCtrlSetSwitch' in group:
            time04, value04, unit04 = group.get_signal_with_unit("CruiseCtrlSetSwitch")
            pn.addSignal2Axis(ax, "CruiseCtrlSetSwitch", time04, value04, unit=unit04)
        if 'BrakeSwitch' in group:
            time04, value04, unit04 = group.get_signal_with_unit("BrakeSwitch")
            pn.addSignal2Axis(ax, "BrakeSwitch", time04, value04, unit=unit04)

        self.sync.addClient(pn)
        return

    def extend_aebs_state_axis(self, pn, ax):
        return
