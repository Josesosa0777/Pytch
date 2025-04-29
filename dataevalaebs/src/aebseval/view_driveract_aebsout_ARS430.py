# -*- dataeval: init -*-

"""
Plot basic driver activities and AEBS outputs

AEBS-relevant driver activities (pedal activation, steering etc.) and
AEBS outputs (in AEBS1 and XBR messages) are shown.
"""

import numpy as np

import datavis
from interface import iView
from measparser.signalproc import rescale


class View(iView):
    def check(self):
        sgs = [{
            # driver
            "accped_pos"    : ("EEC2_00", "EEC2_APPos1_00_C2"),
            "brkped_pos"    : ("EBC1_0B", "EBC1_BrkPedPos_0B_C2"),
            "steer_angle"   : ("VDC2_0B", "VDC2_SteerWhlAngle_0B_C2"),
            "dir_ind"       : ("OEL_32", "OEL_TurnSigSw_32_C2"),
            # AC100 aebs
            "flr20_aebs_state"    : ("AEBS1_2A", "AEBS1_AEBSState_2A_C1"),
            "flr20_xbr_demand"    : ("XBR_2A", "XBR_ExtAccelDem_2A_C1"),
            "flr20_xbr_ctrl_mode" : ("XBR_2A", "XBR_CtrlMode_2A_C1"),
            # ARS430 aebs
            "ars430_aebs_state"   : ("AEBS1_2A", "AEBS1_AEBSState_2A_C3"),
            "ars430_xbr_demand"   : ("XBR_2A", "XBR_ExtAccelDem_2A_C3"),
            "ars430_xbr_ctrl_mode": ("XBR_2A", "XBR_CtrlMode_2A_C3"),
        }]
        # select signals
        group = self.source.selectLazySignalGroup(sgs)
        # give warning for not available signals
        for alias in sgs[0]:
            if alias not in group:
                self.logger.warning("Signal for '%s' not available" % alias)
        return group

    def view(self, group):
        pn = datavis.cPlotNavigator(title="Driver activities and AEBS outputs")

        # pedal positions---------------------------------------------------------------------
        ax = pn.addAxis(ylabel="pos.", ylim=(-5.0, 105.0))
        # accel. pedal
        if 'accped_pos' in group:
            time00, value00, unit00 = group.get_signal_with_unit("accped_pos")
            pn.addSignal2Axis(ax, "accel. p. pos.", time00, value00, unit=unit00)
        # brake pedal
        if 'brkped_pos' in group:
            time02, value02, unit02 = group.get_signal_with_unit("brkped_pos")
            pn.addSignal2Axis(ax, "brake p. pos.", time02, value02, unit=unit02)

        # steering wheel----------------------------------------------------------------------
        ax = pn.addAxis(ylabel="angle", ylim=(-100.0, 100.0))
        if 'steer_angle' in group:
            time04, value04, unit04 = group.get_signal_with_unit("steer_angle")
            if unit04 == "rad" or not unit04:  # assuming rad if unit is empty
                value04 = np.rad2deg(value04)
                unit04 = "deg"
            pn.addSignal2Axis(ax, "steering wheel angle", time04, value04, unit=unit04)

        # direction indicator-----------------------------------------------------------------
        yticks = {0: "none", 1: "left", 2: "right", 3: "n/a"}
        yticks = dict((k, "%d (%s)" % (k, v)) for k, v in yticks.iteritems())
        ax = pn.addTwinAxis(ax, ylabel="state", ylim=(-1.0, 4.0), yticks=yticks, color='g')
        if 'dir_ind' in group:
            time05, value05, unit05 = group.get_signal_with_unit("dir_ind")
            pn.addSignal2Axis(ax, "dir. indicator", time05, value05, unit=unit05)

        # AEBS state--------------------------------------------------------------------------
        yticks = {0: "not ready", 1: "temp. n/a", 2: "deact.", 3: "ready",
                  4: "override", 5: "warning", 6: "part. brk.", 7: "emer. brk.",
                  14: "error", 15: "n/a"}
        yticks = dict((k, "(%s) %d" % (v, k)) for k, v in yticks.iteritems())
        ax = pn.addAxis(ylabel="AEBS state", yticks=yticks)
        ax.set_ylim((-0.5, 7.5))
        ftime = None
        if 'flr20_aebs_state' in group:
            ftime, fvalue = group.get_signal("flr20_aebs_state")
            pn.addSignal2Axis(ax, "AC100", ftime, fvalue)
        if 'ars430_aebs_state' in group:
            atime, avalue = group.get_signal("ars430_aebs_state")
            avalue = rescale(atime, avalue, ftime)[1]
            pn.addSignal2Axis(ax, "ARS430", ftime, avalue)


        # XBR demand--------------------------------------------------------------------------
        ax = pn.addAxis(ylabel="decel.", ylim=(-11.0, 11.0))
        ftime = None
        if 'flr20_xbr_demand' in group:
            ftime, fvalue = group.get_signal("flr20_xbr_demand")
            pn.addSignal2Axis(ax, "AC100 XBR_ExtAccelDem", ftime, fvalue)
        if 'ars430_xbr_demand' in group:
            atime, avalue = group.get_signal("ars430_xbr_demand", ScaleTime=ftime)
            #avalue = rescale(atime, avalue, ftime)[1]
            pn.addSignal2Axis(ax, "ARS430 XBR_ExtAccelDem", ftime, avalue, color='k')

        # XBR control mode--------------------------------------------------------------------
        yticks = {0: "off", 1: "add", 2: "max", 3: "n/a"}
        yticks = dict((k, "%d (%s)" % (k, v)) for k, v in yticks.iteritems())
        ax = pn.addTwinAxis(ax, ylabel="XBR_CtrlMode", ylim=(-1.0, 4.0), yticks=yticks, color='g')
        ftime = None
        if 'flr20_xbr_ctrl_mode' in group:
            ftime, fvalue = group.get_signal("flr20_xbr_ctrl_mode")
            pn.addSignal2Axis(ax, "AC100", ftime, fvalue, color='g')
        if 'ars430_xbr_ctrl_mode' in group:
            atime, avalue = group.get_signal("ars430_xbr_ctrl_mode")
            avalue = rescale(atime, avalue, ftime)[1]
            pn.addSignal2Axis(ax, "ARS430", ftime, avalue)

        self.sync.addClient(pn)
        return
