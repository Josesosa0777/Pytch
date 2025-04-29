# -*- dataeval: init -*-

import numpy as np

import datavis
from interface import iView


class View(iView):
    def check(self):
        sgs = [
            {
                "left_lane_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                      "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_quality"),
                "right_lane_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                       "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_quality"),
                "FrontAxleSpeed": ("EBC2", "FrontAxleSpeed_s0B"),
                "steering_wheel_angle": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_steering_wheel_angle"),
            },
            {
                "left_lane_quality": ("MTSI_stKBFreeze_020ms_t",
                                      "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_quality"),
                "right_lane_quality": ("MTSI_stKBFreeze_020ms_t",
                                       "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_quality"),
                "FrontAxleSpeed": ("EBC2_s0B", "FrontAxleSpeed"),
                "steering_wheel_angle": ( "MTSI_stKBFreeze_020ms_t",
                "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_steering_wheel_angle"),
            },
            {
                "left_lane_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                      "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_quality"),
                "right_lane_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                       "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_quality"),
                "FrontAxleSpeed": ("EBC2_0B", "EBC2_FrontAxleSpeed_0B_s0B"),
                "steering_wheel_angle": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_steering_wheel_angle"),
            },
            {
                "left_lane_quality": ("MTSI_stKBFreeze_020ms_t",
                                      "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_quality"),
                "right_lane_quality": ("MTSI_stKBFreeze_020ms_t",
                                       "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_quality"),
                "FrontAxleSpeed": ("EBC2_0B", "EBC2_FrontAxleSpeed_0B_s0B"),
                "steering_wheel_angle": ("MTSI_stKBFreeze_020ms_t",
                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_steering_wheel_angle"),
            },
            {
                "ego_left_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_quality"),
                "ego_right_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                      "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_quality"),
                "FrontAxleSpeed": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                   "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_EBC2_EBC2_MeanSpdFA"),
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
        pn = datavis.cPlotNavigator(title="Lane Quality Check")

        ax = pn.addAxis(ylabel="Left_lane_quality_check")
        if 'left_lane_quality' in group:
            time00, value00, unit00 = group.get_signal_with_unit("left_lane_quality")
            pn.addSignal2Axis(ax, "left_lane_quality", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="Right_lane_quality_check")
        if 'right_lane_quality' in group:
            time00, value00, unit00 = group.get_signal_with_unit("right_lane_quality")
            pn.addSignal2Axis(ax, "right_lane_quality", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="Ego Speed")
        if 'FrontAxleSpeed' in group:
            time00, value00, unit00 = group.get_signal_with_unit("FrontAxleSpeed")
            pn.addSignal2Axis(ax, "Ego Speed", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="Steering Wheel Angle")
        if 'steering_wheel_angle' in group:
            time00, value00, unit00 = group.get_signal_with_unit("steering_wheel_angle")
            pn.addSignal2Axis(ax, "Steering Wheel Angle", time00, value00, unit=unit00)

        self.sync.addClient(pn)
        return

