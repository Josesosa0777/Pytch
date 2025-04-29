# -*- dataeval: init -*-

import numpy as np

import datavis
from interface import iView


class View(iView):
    def check(self):
        sgs = [
            {
                "vVeh": ("PGN65313_Tx", "vVeh"),
                "RideHeiLevel": ("RGE21_Tx_TICAN", "RideHeiLevel"),
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
        pn = datavis.cPlotNavigator(title="iLvl out of driving level")

        ax = pn.addAxis(ylabel="")

        # Subplot 1
        if 'vVeh' in group:
            time00, value00, unit00 = group.get_signal_with_unit("vVeh")
            pn.addSignal2Axis(ax, "vVeh.", time00, value00, unit=unit00)

        # Subplot 2
        ax = pn.addAxis(ylabel="")
        if 'RideHeiLevel' in group:
            time00, value00, unit00 = group.get_signal_with_unit("RideHeiLevel")
            pn.addSignal2Axis(ax, "RideHeiLevel.", time00, value00, unit=unit00)

        self.sync.addClient(pn)
        return