# -*- dataeval: init -*-

import numpy as np

import datavis
from interface import iView


class View(iView):
    def check(self):
        sgs = [
            {
                "right_lane_marking_c0": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                          "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_c0"),
                "left_lane_marking_c0": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_c0"),
                "C0_Left_A": ("Video_Lane_Left_A", "C0_Left_A"),
                "C0_Right_A": ("Video_Lane_Right_A", "C0_Right_A"),
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
        pn = datavis.cPlotNavigator(title="Compare C0 FLC25vsMFC525")

        ax = pn.addAxis(ylabel="Compare left C0")
        if 'left_lane_marking_c0' in group:
            time00, value00, unit00 = group.get_signal_with_unit("left_lane_marking_c0")
            pn.addSignal2Axis(ax, "left lane marking c0", time00, value00, unit=unit00)

        if 'C0_Left_A' in group:
            time00, value00, unit00 = group.get_signal_with_unit("C0_Left_A")
            pn.addSignal2Axis(ax, "C0_Left_A", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="Compare right C0")
        if 'right_lane_marking_c0' in group:
            time00, value00, unit00 = group.get_signal_with_unit("right_lane_marking_c0")
            pn.addSignal2Axis(ax, "right lane marking c0", time00, value00, unit=unit00)

        if 'C0_Right_A' in group:
            time00, value00, unit00 = group.get_signal_with_unit("C0_Right_A")
            pn.addSignal2Axis(ax, "C0_Right_A", time00, value00, unit=unit00)

        self.sync.addClient(pn)
        return

