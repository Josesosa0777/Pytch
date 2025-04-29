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
                "PPneuDem": ("PGN65312_Tx", "PPneuDem"),
                "PPneuCh0": ("PGN65312_Tx", "PPneuCh0"),
                "PPneuCh1": ("PGN65312_Tx", "PPneuCh1"),
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
        pn = datavis.cPlotNavigator(title="No Braking")

        ax = pn.addAxis(ylabel="")

        if 'ABS_Active' in group:
            time00, value00, unit00 = group.get_signal_with_unit("ABS_Active")
            pn.addSignal2Axis(ax, "ABS_Active.", time00, value00, unit=unit00)

        if 'RSP_Active' in group:
            time00, value00, unit00 = group.get_signal_with_unit("RSP_Active")
            pn.addSignal2Axis(ax, "RSP_Active.", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="")
        if 'VDC_Active' in group:
            time00, value00, unit00 = group.get_signal_with_unit("VDC_Active")
            pn.addSignal2Axis(ax, "VDC_Active.", time00, value00, unit=unit00)

        if 'EMR_Active' in group:
            time00, value00, unit00 = group.get_signal_with_unit("EMR_Active")
            pn.addSignal2Axis(ax, "EMR_Active.", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="")
        if 'PPneuDem' in group:
            time00, value00, unit00 = group.get_signal_with_unit("PPneuDem")
            pn.addSignal2Axis(ax, "PPneuDem.", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="")
        if 'PPneuCh0' in group:
            time00, value00, unit00 = group.get_signal_with_unit("PPneuCh0")
            pn.addSignal2Axis(ax, "PPneuCh0.", time00, value00, unit=unit00)

        if 'PPneuCh1' in group:
            time00, value00, unit00 = group.get_signal_with_unit("PPneuCh1")
            pn.addSignal2Axis(ax, "PPneuCh1.", time00, value00, unit=unit00)

        self.sync.addClient(pn)
        return