# -*- dataeval: init -*-

import numpy as np

import datavis
from interface import iView


class View(iView):
    def check(self):
        sgs = [
            {
                "RedWLReq_PGN65315_Tx": ("PGN65315_Tx", "RedWLReq_PGN65315_Tx"),
                "AmbWLReq_PGN65315_Tx": ("PGN65315_Tx", "AmbWLReq_PGN65315_Tx"),
                "AmbInfReq": ("PGN65315_Tx", "AmbInfReq"),
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
        pn = datavis.cPlotNavigator(title="WL Active")

        ax = pn.addAxis(ylabel="")

        # Subplot 1
        if 'RedWLReq_PGN65315_Tx' in group:
            time00, value00, unit00 = group.get_signal_with_unit("RedWLReq_PGN65315_Tx")
            pn.addSignal2Axis(ax, "RedWLReq_PGN65315_Tx.", time00, value00, unit=unit00)

        # Subplot 2
        ax = pn.addAxis(ylabel="")
        if 'AmbWLReq_PGN65315_Tx' in group:
            time00, value00, unit00 = group.get_signal_with_unit("AmbWLReq_PGN65315_Tx")
            pn.addSignal2Axis(ax, "AmbWLReq_PGN65315_Tx.", time00, value00, unit=unit00)

        # Subplot 3
        ax = pn.addAxis(ylabel="")
        if 'AmbInfReq' in group:
            time04, value04, unit04 = group.get_signal_with_unit("AmbInfReq")
            pn.addSignal2Axis(ax, "AmbInfReq", time04, value04, unit=unit04)

        self.sync.addClient(pn)
        return