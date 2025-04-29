# -*- dataeval: init -*-

import numpy as np

import datavis
from interface import iView


class View(iView):
    def check(self):
        sgs = [
            {
                "left_lane_marking_c0": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_c0"),
                "right_lane_marking_c0": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                          "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_c0"),
                "FrontAxleSpeed": ("EBC2", "FrontAxleSpeed_s0B"),
                "steering_wheel_angle": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_steering_wheel_angle"),
            },
            {
                "left_lane_marking_c0": ("MTSI_stKBFreeze_020ms_t",
                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_c0"),
                "right_lane_marking_c0": ("MTSI_stKBFreeze_020ms_t",
                                          "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_c0"),
                "FrontAxleSpeed": ("EBC2_s0B", "FrontAxleSpeed"),
                "steering_wheel_angle": ("MTSI_stKBFreeze_020ms_t",
                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_steering_wheel_angle"),
            },
            {
                "left_lane_marking_c0": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_c0"),
                "right_lane_marking_c0": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                          "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_c0"),
                "FrontAxleSpeed": ("EBC2_0B", "EBC2_FrontAxleSpeed_0B_s0B"),
                "steering_wheel_angle": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_steering_wheel_angle"),
            },
            {
                "left_lane_marking_c0": ("MTSI_stKBFreeze_020ms_t",
                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_c0"),
                "right_lane_marking_c0": ("MTSI_stKBFreeze_020ms_t",
                                          "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_c0"),
                "FrontAxleSpeed": ("EBC2_0B", "EBC2_FrontAxleSpeed_0B_s0B"),
                "steering_wheel_angle": ("MTSI_stKBFreeze_020ms_t",
                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_steering_wheel_angle"),
            },
            {
                "left_lane_marking_c0": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_c0"),
                "right_lane_marking_c0": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                          "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_c0"),
                "FrontAxleSpeed": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                   "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_EBC2_EBC2_MeanSpdFA"),
                "steering_wheel_angle": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_steering_wheel_angle"),
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
        pn = datavis.cPlotNavigator(title="Lane C0 Jump (Tare Stripe)")

        ax = pn.addAxis(ylabel="Left_lane_c0_jump")
        if 'left_lane_marking_c0' in group:
            time00, value00, unit00 = group.get_signal_with_unit("left_lane_marking_c0")
            pn.addSignal2Axis(ax, "left_lane_marking_c0", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="Right_lane_c0_jump")
        if 'right_lane_marking_c0' in group:
            time00, value00, unit00 = group.get_signal_with_unit("right_lane_marking_c0")
            pn.addSignal2Axis(ax, "right_lane_marking_c0", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="Ego Speed")
        if 'FrontAxleSpeed' in group:
            time00, value00, unit00 = group.get_signal_with_unit("FrontAxleSpeed")
            pn.addSignal2Axis(ax, "ego speed", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="Steering Wheel Angle")
        if 'steering_wheel_angle' in group:
            time00, value00, unit00 = group.get_signal_with_unit("steering_wheel_angle")
            pn.addSignal2Axis(ax, "steering_wheel_angle", time00, value00, unit=unit00)

        self.sync.addClient(pn)
        return

