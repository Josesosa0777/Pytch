# -*- dataeval: init -*-
import numpy as np
from interface import iCalc

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
    {
        "left_lane_marking_c0": ("MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                                 "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_LkInput_sensor_input_left_lane_line_c0"),
        "right_lane_marking_c0": ("MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                                  "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_LkInput_sensor_input_right_lane_line_c0"),
        "FrontAxleSpeed": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                           "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_EBC2_EBC2_MeanSpdFA"),
        "steering_wheel_angle": ("MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                                 "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_LkInput_driver_input_steering_whl_angle"),
    }
]


class cFill(iCalc):
    dep = ('calc_common_time-flc25',)

    def check(self):
        source = self.get_source()
        group = source.selectSignalGroup(sgs)
        return group

    def fill(self, group):
        time = self.modules.fill('calc_common_time-flc25')
        rescale_kwargs = {'ScaleTime': time}
        _, left_lane_marking_c0, unit = group.get_signal_with_unit('left_lane_marking_c0', **rescale_kwargs)
        _, right_lane_marking_c0, unit = group.get_signal_with_unit('right_lane_marking_c0', **rescale_kwargs)
        _, ego_speed, unit = group.get_signal_with_unit('FrontAxleSpeed', **rescale_kwargs)
        _, steering_wheel_angle, unit = group.get_signal_with_unit('steering_wheel_angle', **rescale_kwargs)

        left_c0_diff = np.append(np.diff(left_lane_marking_c0), 0)
        right_c0_diff = np.append(np.diff(right_lane_marking_c0), 0)

        left_plane_c0 = (0.2 < left_c0_diff) & (left_c0_diff < 0.8) & (ego_speed > 50) & (steering_wheel_angle < 0.2)
        left_nlane_c0 = (left_c0_diff < -0.2) & (left_c0_diff > -0.8) & (ego_speed > 50) & (steering_wheel_angle > -0.2)
        right_plane_c0 = (0.2 < right_c0_diff) & (right_c0_diff < 0.8) & (ego_speed > 50) & (steering_wheel_angle < 0.2)
        right_nlane_c0 = (right_c0_diff < -0.2) & (right_c0_diff > -0.8) & (ego_speed > 50) & (
                    steering_wheel_angle > -0.2)
        return time, left_nlane_c0, left_plane_c0, right_nlane_c0, right_plane_c0


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\Measurement\Lane_evaluation\ldws_state\test\2022-04-12\mi5id786__2022-04-12_14-31-02.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    data = manager_modules.calc('calc_flc25_lane_c0_jump@aebs.fill', manager)
    print data
