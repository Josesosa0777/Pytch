# -*- dataeval: init -*-

import numpy as np

import datavis
from interface import iView


class View(iView):
    def check(self):
        sgs = [
            {
                "ldw_enabled": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_ldw_enabled"),
                "lane_departure_imminent_left": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                                 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_LkOutput_hmi_output_lane_departure_imminent_left"),
                "lane_departure_imminent_right": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                                  "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_LkOutput_hmi_output_lane_departure_imminent_right"),
                "lane_departure_system_status": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                                 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_LkOutput_hmi_output_lane_departure_system_status"),
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
        pn = datavis.cPlotNavigator(title="LDWS events")

        ax = pn.addAxis(ylabel="LDWS enabled")
        if 'ldw_enabled' in group:
            time00, value00, unit00 = group.get_signal_with_unit("ldw_enabled")
            pn.addSignal2Axis(ax, "LDWS enabled", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="imminent_left_departure")
        if 'lane_departure_imminent_left' in group:
            time00, value00, unit00 = group.get_signal_with_unit("lane_departure_imminent_left")
            pn.addSignal2Axis(ax, "LDWS imminent left", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="imminent_right_departure")
        if 'lane_departure_imminent_right' in group:
            time00, value00, unit00 = group.get_signal_with_unit("lane_departure_imminent_right")
            pn.addSignal2Axis(ax, "LDWS imminent right", time00, value00, unit=unit00)

        if 'lane_departure_system_status' in group:
            mapping = {2: 'deactivated_by_driver', 3: 'ready', 5: 'warning'}
            ax = pn.addAxis(ylabel="System status", yticks=mapping, ylim=(min(mapping) - 0.5, max(mapping) + 0.5))
            time00, value00, unit00 = group.get_signal_with_unit("lane_departure_system_status")
            pn.addSignal2Axis(ax, "LDWS system status", time00, value00, unit=unit00)

        self.sync.addClient(pn)
        return

