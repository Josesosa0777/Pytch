# -*- dataeval: init -*-

import numpy as np

import datavis
from interface import iView


class View(iView):
    def check(self):
        sgs = [
            {
                "ABS_Active": ("PGN65315_Tx", "ABS_Active"),
                "RSP_Active": ("PGN65315_Tx", "RSP_Active"),
                "VDC_Active": ("PGN65315_Tx", "VDC_Active"),
                "EMR_Active": ("PGN65315_Tx", "EMR_Active"),
                "RSP_TestPulse": ("PGN65314_Tx", "RSP_TestPulse"),
                "RSP_Step_1": ("PGN65314_Tx", "RSP_Step_1"),
                "RSP_Step_2": ("PGN65314_Tx", "RSP_Step_2"),
                "RSP_Step_3": ("PGN65314_Tx", "RSP_Step_3"),
                "ABSAct": ("PGN65316_Tx", "ABSAct"),
                "RSPAct": ("PGN65316_Tx", "RSPAct"),
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
        pn = datavis.cPlotNavigator(title="ABS & RSP Flag Active")

        ax = pn.addAxis(ylabel="")

        # Subplot 1
        if 'ABS_Active' in group:
            time00, value00, unit00 = group.get_signal_with_unit("ABS_Active")
            pn.addSignal2Axis(ax, "ABS_Active.", time00, value00, unit=unit00)

        if 'RSP_Active' in group:
            time00, value00, unit00 = group.get_signal_with_unit("RSP_Active")
            pn.addSignal2Axis(ax, "RSP_Active.", time00, value00, unit=unit00)

        if 'VDC_Active' in group:
            time00, value00, unit00 = group.get_signal_with_unit("VDC_Active")
            pn.addSignal2Axis(ax, "VDC_Active.", time00, value00, unit=unit00)

        if 'EMR_Active' in group:
            time00, value00, unit00 = group.get_signal_with_unit("EMR_Active")
            pn.addSignal2Axis(ax, "EMR_Active.", time00, value00, unit=unit00)

        # Subplot 2
        ax = pn.addAxis(ylabel="")
        if 'RSP_TestPulse' in group:
            time00, value00, unit00 = group.get_signal_with_unit("RSP_TestPulse")
            pn.addSignal2Axis(ax, "RSP_TestPulse.", time00, value00, unit=unit00)

        if 'RSP_Step_1' in group:
            time00, value00, unit00 = group.get_signal_with_unit("RSP_Step_1")
            pn.addSignal2Axis(ax, "RSP_Step_1.", time00, value00, unit=unit00)

        if 'RSP_Step_2' in group:
            time00, value00, unit00 = group.get_signal_with_unit("RSP_Step_2")
            pn.addSignal2Axis(ax, "RSP_Step_2.", time00, value00, unit=unit00)

        if 'RSP_Step_3' in group:
            time00, value00, unit00 = group.get_signal_with_unit("RSP_Step_3")
            pn.addSignal2Axis(ax, "RSP_Step_3.", time00, value00, unit=unit00)

        # Subplot 3
        ax = pn.addAxis(ylabel="")
        if 'ABSAct' in group:
            time04, value04, unit04 = group.get_signal_with_unit("ABSAct")
            pn.addSignal2Axis(ax, "ABSAct", time04, value04, unit=unit04)

        if 'RSPAct' in group:
            time04, value04, unit04 = group.get_signal_with_unit("RSPAct")
            pn.addSignal2Axis(ax, "RSPAct", time04, value04, unit=unit04)

        self.sync.addClient(pn)
        return