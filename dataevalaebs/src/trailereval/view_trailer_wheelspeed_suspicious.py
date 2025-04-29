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
                "ABS_Active": ("PGN65315_Tx", "ABS_Active"),
                "RSP_Active": ("PGN65315_Tx", "RSP_Active"),
                "VDC_Active": ("PGN65315_Tx", "VDC_Active"),
                "EMR_Active": ("PGN65315_Tx", "EMR_Active"),
                "vVeh": ("PGN65313_Tx", "vVeh"),
                "vWhl0": ("PGN65313_Tx", "vWhl0"),
                "vWhl1": ("PGN65313_Tx", "vWhl1"),
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
        pn = datavis.cPlotNavigator(title="Wheelspeed Suspicious")

        ax = pn.addAxis(ylabel="")

        # Subplot 1
        if 'RedWLReq_PGN65315_Tx' in group:
            time00, value00, unit00 = group.get_signal_with_unit("RedWLReq_PGN65315_Tx")
            pn.addSignal2Axis(ax, "RedWLReq_PGN65315_Tx.", time00, value00, unit=unit00)

        if 'AmbWLReq_PGN65315_Tx' in group:
            time00, value00, unit00 = group.get_signal_with_unit("AmbWLReq_PGN65315_Tx")
            pn.addSignal2Axis(ax, "AmbWLReq_PGN65315_Tx.", time00, value00, unit=unit00)

        if 'AmbInfReq' in group:
            time00, value00, unit00 = group.get_signal_with_unit("AmbInfReq")
            pn.addSignal2Axis(ax, "AmbInfReq.", time00, value00, unit=unit00)

        # Subplot 2
        ax = pn.addAxis(ylabel="")
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

        # Subplot 3
        ax = pn.addAxis(ylabel="")
        if 'vVeh' in group:
            time04, value04, unit04 = group.get_signal_with_unit("vVeh")
            pn.addSignal2Axis(ax, "vVeh", time04, value04, unit=unit04)

        if 'vWhl0' in group:
            time04, value04, unit04 = group.get_signal_with_unit("vWhl0")
            pn.addSignal2Axis(ax, "vWhl0", time04, value04, unit=unit04)

        if 'vWhl1' in group:
            time04, value04, unit04 = group.get_signal_with_unit("vWhl1")
            pn.addSignal2Axis(ax, "vWhl1", time04, value04, unit=unit04)

        self.sync.addClient(pn)
        return