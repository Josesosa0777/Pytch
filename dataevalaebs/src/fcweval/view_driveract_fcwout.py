# -*- dataeval: init -*-

"""
Plot basic driver activities and FCW outputs

FCW-relevant driver activities (pedal activation, steering etc.) and
FCW outputs (in AEBS1 messages) are shown.
"""

import numpy as np

import datavis
from interface import iView


class View(iView):
    def check(self):
        sgs = [
            {
                "accped_pos": ("EEC2_00_s00", "EEC2_APPos1_00_s00"),
                "brkped_pos": ("EBC1_0B_s0B", "EBC1_BrkPedPos_0B_s0B"),
                "steer_angle": ("VDC2_0B_s0B", "VDC2_SteerWhlAngle_0B_s0B"),
                "dir_ind": ("OEL_32_s32", "OEL_TurnSigSw_32_s32"),

                "aebs_state": ("AEBS1_A0_sA0", "AEBS1_AEBSState_A0_sA0"),
                "coll_warn_level": ("AEBS1_A0_sA0", "AEBS1_CollisionWarningLevel_A0_sA0"),
            },
            {
                "accped_pos": ("EEC2_00_s00", "EEC2_APPos1_00"),
                "brkped_pos": ("EBC1_0B_s0B", "EBC1_BrkPedPos_0B"),
                "steer_angle": ("VDC2_0B_s0B", "VDC2_SteerWhlAngle_0B"),
                "dir_ind": ("OEL_32_s32", "OEL_TurnSigSw_32"),

                "aebs_state": ("AEBS1_A0_sA0", "AEBS1_AEBSState_A0"),
                "coll_warn_level": ("AEBS1_A0_sA0", "AEBS1_CollisionWarningLevel_A0"),
            },
            {
                "accped_pos": ("CAN_Vehicle_EEC2_00", "EEC2_AccPedalPos1_00"),
                "brkped_pos": ("CAN_Vehicle_EBC1_0B", "EBC1_BrkPedPos_0B"),
                "steer_angle": ("CAN_Vehicle_VDC2", "SteerWheelAngle"),
                "dir_ind": ("CAN_MFC_Public_OEL_32", "OEL_TurnSignalSwitch_32"),

                "aebs_state": ("CAN_Vehicle_AEBS1_2A", "AEBS1_AEBSState_2A"),
                "coll_warn_level": ("CAN_Vehicle_AEBS1_2A", "AEBS1_CollisionWarningLevel_2A"),
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

        # AEBS state
        yticks = {0: "not ready", 1: "temp. n/a", 2: "deact.", 3: "ready",
                  4: "override", 5: "warning", 6: "part. brk.", 7: "emer. brk.",
                  14: "error", 15: "n/a"}
        yticks = dict((k, "(%s) %d" % (v, k)) for k, v in yticks.iteritems())
        ax = pn.addAxis(ylabel="state", yticks=yticks)
        ax.set_ylim((-1.0, 8.0))
        if 'aebs_state' in group:
            time00, value00, unit00 = group.get_signal_with_unit("aebs_state")
            pn.addSignal2Axis(ax, "AEBSState", time00, value00, unit=unit00)
        # extend axis e.g. with simulated signal(s)
        self.extend_aebs_state_axis(pn, ax)
        # coll. warn. level
        ax = pn.addTwinAxis(ax, ylabel="level", ylim=(-1.0, 8.0), color='g')
        ax.set_yticks(xrange(8))
        if 'coll_warn_level' in group:
            time01, value01, unit01 = group.get_signal_with_unit("coll_warn_level")
            pn.addSignal2Axis(ax, "CollisionWarningLevel", time01, value01, unit=unit01)

        self.sync.addClient(pn)
        return

    def extend_aebs_state_axis(self, pn, ax):
        return
