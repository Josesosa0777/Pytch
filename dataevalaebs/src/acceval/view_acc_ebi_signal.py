# -*- dataeval: init -*-

import numpy as np

import datavis
from interface import iView


class View(iView):
    def check(self):
        sgs = [
            {
                "XBR_Urgency": ("XBR_0B_2A", "XBR_Urgency_0B_2A_d0B_s2A"),
                "XBR_EBIMode": ("XBR_0B_2A", "XBR_EBIMode_0B_2A_d0B_s2A"),
                "XBR_ExtAccelDem": ("XBR_0B_2A", "XBR_ExtAccelDem_0B_2A_d0B_s2A"),
            },
            {
                "XBR_Urgency": ("XBR_0B_2A_d0B_s2A", "XBR_Urgency_0B_2A"),
                "XBR_EBIMode": ("XBR_0B_2A_d0B_s2A", "XBR_EBIMode_0B_2A"),
                "XBR_ExtAccelDem": ("XBR_0B_2A_d0B_s2A", "XBR_ExtAccelDem_0B_2A"),
            },
            {
                "XBR_Urgency": ("XBR", "XBRUrgency_d0B_s2A"),
                "XBR_EBIMode": ("XBR", "XBREBIMode_d0B_s2A"),
                "XBR_ExtAccelDem": ("XBR", "ExtlAccelerationDemand_d0B_s2A"),
            },
            {
                "XBR_Urgency": ("XBR_A0_d0B_sA0", "XBRUrgency"),
                "XBR_EBIMode": ("XBR_A0_d0B_sA0", "XBREBIMode"),
                "XBR_ExtAccelDem": ("XBR_A0_d0B_sA0", "ExternalAccelDemand"),
            },
            {
                "XBR_Urgency": ("XBR_0B_2A","XBR_Urgency_0B_2A_d0B_s2A"),
                "XBR_EBIMode": ("XBR_0B_2A", "XBR_EBIMode_0B_2A_d0B_s2A"),
                "XBR_ExtAccelDem": ("XBR_0B_2A","XBR_ExtAccelDem_0B_2A_d0B_s2A"),
            },
            {
                "XBR_Urgency": ("XBR_2A", "XBR_Urgency_2A"),
                "XBR_EBIMode": ("XBR_2A", "XBR_EBIMode_2A"),
                "XBR_ExtAccelDem": ("XBR_2A", "XBR_ExtAccelDem_2A"),
            },
            {
                "XBR_Urgency": ("XBR_A0_0B", "XBR_Urgency_A0_0B"),
                "XBR_EBIMode": ("XBR_A0_0B", "XBR_EBIMode_A0_0B"),
                "XBR_ExtAccelDem": ("XBR_A0_0B", "XBR_ExtAccelDem_A0_0B"),
            },
            {
                "XBR_Urgency": ("XBR_0B_2A", "XBR_Urgency_0B_2A"),
                "XBR_EBIMode": ("XBR_0B_2A", "XBR_EBIMode_0B_2A"),
                "XBR_ExtAccelDem": ("XBR_0B_2A", "XBR_ExtAccelDem_0B_2A"),
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
        pn = datavis.cPlotNavigator(title="XBR Signal Analysis")

        ax = pn.addAxis(ylabel="External ACC Demand in XBR")
        if 'XBR_ExtAccelDem' in group:
            time00, value00, unit00 = group.get_signal_with_unit("XBR_ExtAccelDem")
            pn.addSignal2Axis(ax, "XBR_ExtAccelDem", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="EBI in XBR")
        if 'XBR_EBIMode' in group:
            time00, value00, unit00 = group.get_signal_with_unit("XBR_EBIMode")
            pn.addSignal2Axis(ax, "XBR_EBIMode", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="Urgency in XBR")
        if 'XBR_Urgency' in group:
            time00, value00, unit00 = group.get_signal_with_unit("XBR_Urgency")
            pn.addSignal2Axis(ax, "XBR_Urgency", time00, value00, unit=unit00)

        self.sync.addClient(pn)
        return

