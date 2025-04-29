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
            # paebs plot
            {
                "accped_pos": ("EEC2_00_s00", "EEC2_AccPedalPos1_00"),
                "brkped_pos": ("EBC1_0B_s0B", "EBC1_BrkPedPos_0B"),
                "brake_switch": ("EBC1_0B_s0B", "EBC1_EBSBrakeSwitch_0B"),
                "steer_angle": ("VDC2_0B_s0B", "VDC2_SteerWhlAngle_0B"),
                "dir_ind": ("Rte_SWC_Preprocessor_RPort_prep_norm_OEL_DEP_norm_prep_postp_OEL_Buf",
                            "ARS4xx_Device_SW_Every10ms_Rte_SWC_Preprocessor_RPort_prep_norm_OEL_DEP_norm_prep_postp_OEL_Buf_OEL_TurnSigSw"),

                "xbr_demand": ("XBR_0B_2A_d0B_s2A", "XBR_CtrlMode_0B_2A"),
                "xbr_ctrl_mode": ("XBR_0B_2A_d0B_s2A", "XBR_ExtAccelDem_0B_2A"),
            },
            
            ]
        # select signals
        group = self.source.selectLazySignalGroup(sgs)
        # give warning for not available signals
        for alias in sgs[0]:
            if alias not in group:
                self.logger.warning("Signal for '%s' not available" % alias)
        return group

    def view(self, group):
        pn = datavis.cPlotNavigator(title="Driver activities and AEBS outputs")

        ax = pn.addAxis(ylabel="pos.", ylim=(-5.0, 105.0))
        # accel. pedal
        if 'accped_pos' in group:
            time00, value00, unit00 = group.get_signal_with_unit("accped_pos")
            pn.addSignal2Axis(ax, "accel. p. pos.", time00, value00, unit=unit00)
        # brake pedal
        if 'brkped_pos' in group:
            time02, value02, unit02 = group.get_signal_with_unit("brkped_pos")
            pn.addSignal2Axis(ax, "brake p. pos.", time02, value02, unit=unit02)
        # brake switch
        if 'brake_switch' in group:
            time02, value02, unit02 = group.get_signal_with_unit("brake_switch")
            ax = pn.addTwinAxis(ax, ylabel = 'brake switch', color = 'g')
            pn.addSignal2Axis(ax, "brake switch", time02, value02, unit=unit02)
        

        # steering wheel
        ax = pn.addAxis(ylabel="angle", ylim=(-100.0, 100.0))
        if 'steer_angle' in group:
            time04, value04, unit04 = group.get_signal_with_unit("steer_angle")
            if unit04 == "rad" or not unit04:  # assuming rad if unit is empty
                value04 = np.rad2deg(value04)
                unit04 = "deg"
            pn.addSignal2Axis(ax, "steering wheel angle", time04, value04, unit=unit04)
        # direction indicator
        yticks = {0: "none", 1: "left", 2: "right", 3: "n/a"}
        yticks = dict((k, "%d (%s)" % (k, v)) for k, v in yticks.iteritems())
        ax = pn.addTwinAxis(ax, ylabel="state", ylim=(-1.0, 4.0), yticks=yticks, color='g')
        if 'dir_ind' in group:
            time05, value05, unit05 = group.get_signal_with_unit("dir_ind")
            pn.addSignal2Axis(ax, "dir. indicator", time05, value05, unit=unit05)

        # XBR demand
        ax = pn.addAxis(ylabel="decel.", ylim=(-11.0, 11.0))
        if 'xbr_demand' in group:
            time04, value04, unit04 = group.get_signal_with_unit("xbr_demand")
            pn.addSignal2Axis(ax, "XBR_ExtAccelDem", time04, value04, unit=unit04)
        # XBR control mode
        yticks = {0: "off", 1: "add", 2: "max", 3: "n/a"}
        yticks = dict((k, "%d (%s)" % (k, v)) for k, v in yticks.iteritems())
        ax = pn.addTwinAxis(ax, ylabel="mode", ylim=(-1.0, 4.0), yticks=yticks, color='g')
        if 'xbr_ctrl_mode' in group:
            time05, value05, unit05 = group.get_signal_with_unit("xbr_ctrl_mode")
            pn.addSignal2Axis(ax, "XBR_CtrlMode", time05, value05, unit=unit05)

        self.sync.addClient(pn)
        return

    def extend_aebs_state_axis(self, pn, ax):
        return
