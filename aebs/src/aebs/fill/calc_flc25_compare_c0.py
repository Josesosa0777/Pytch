# -*- dataeval: init -*-
import numpy as np
from interface import iCalc
from primitives.ldws import LdwsStatus

sgs = [
    {
        "right_lane_marking_c0": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                  "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_c0"),
        "left_lane_marking_c0": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_c0"),
        "C0_Left_A": ("Video_Lane_Left_A", "C0_Left_A"),
        "C0_Right_A": ("Video_Lane_Right_A", "C0_Right_A"),
        "FrontAxleSpeed": ("EBC2_0B", "EBC2_FrontAxleSpeed_0B_s0B"),
        "left_lane_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                              "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_quality"),
        "right_lane_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                               "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_quality"),
        "LaneInfo_LH_B_Quality_A0_sA0": ("LaneInfo_LH_B_A0", "LaneInfo_LH_B_Quality_A0_sA0"),
        "LaneInfo_RH_B_Quality_A0_sA0": ("LaneInfo_RH_B_A0", "LaneInfo_RH_B_Quality_A0_sA0"),

    },
    {
        "right_lane_marking_c0": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                  "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_c0"),
        "left_lane_marking_c0": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_c0"),
        "C0_Left_A": ("Video_Lane_Left_A", "C0_Left_A"),
        "C0_Right_A": ("Video_Lane_Right_A", "C0_Right_A"),
        "FrontAxleSpeed": ("EBC2", "FrontAxleSpeed_s0B"),
        "left_lane_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                              "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_quality"),
        "right_lane_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                               "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_quality"),
        "LaneInfo_LH_B_Quality_A0_sA0": ("LaneInfo_LH_B_A0", "LaneInfo_LH_B_Quality_A0_sA0"),
        "LaneInfo_RH_B_Quality_A0_sA0": ("LaneInfo_RH_B_A0", "LaneInfo_RH_B_Quality_A0_sA0"),

    },
    {
        "right_lane_marking_c0": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                  "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_c0"),
        "left_lane_marking_c0": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_c0"),
        "C0_Left_A": ("Video_Lane_Left_A", "C0_Left_A"),
        "C0_Right_A": ("Video_Lane_Right_A", "C0_Right_A"),
        "FrontAxleSpeed": ("EBC2_s0B", "FrontAxleSpeed"),
        "left_lane_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                              "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_quality"),
        "right_lane_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                               "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_quality"),
        "LaneInfo_LH_B_Quality_A0_sA0": ("LaneInfo_LH_B_A0", "LaneInfo_LH_B_Quality_A0_sA0"),
        "LaneInfo_RH_B_Quality_A0_sA0": ("LaneInfo_RH_B_A0", "LaneInfo_RH_B_Quality_A0_sA0"),

    },
    {
        "right_lane_marking_c0": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                  "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_c0"),
        "left_lane_marking_c0": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_c0"),
        "C0_Left_A": ("Video_Lane_Left_A", "C0_Left_A"),
        "C0_Right_A": ("Video_Lane_Right_A", "C0_Right_A"),
        "FrontAxleSpeed": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                           "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_EBC2_EBC2_MeanSpdFA"),
        "left_lane_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                              "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_quality"),
        "right_lane_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                               "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_quality"),
        "LaneInfo_LH_B_Quality_A0_sA0": ("LaneInfo_LH_B_A0", "LaneInfo_LH_B_Quality_A0_sA0"),
        "LaneInfo_RH_B_Quality_A0_sA0": ("LaneInfo_RH_B_A0", "LaneInfo_RH_B_Quality_A0_sA0"),
    },
    {
        "right_lane_marking_c0": ("MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                                  "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_LkInput_sensor_input_right_lane_line_c0"),
        "left_lane_marking_c0": ("MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                                 "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_LkInput_sensor_input_left_lane_line_c0"),
        "left_lane_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                              "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_LkInput_sensor_input_left_lane_line_quality"),
        "right_lane_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                               "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_LkInput_sensor_input_right_lane_line_quality"),
        "C0_Left_A": ("Video_Lane_Left_A", "C0_Left_A"),
        "C0_Right_A": ("Video_Lane_Right_A", "C0_Right_A"),
        "FrontAxleSpeed": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                           "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_EBC2_EBC2_MeanSpdFA"),
        "left_lane_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                              "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_quality"),
        "right_lane_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                               "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_quality"),
        "LaneInfo_LH_B_Quality_A0_sA0": ("LaneInfo_LH_B_A0", "LaneInfo_LH_B_Quality_A0_sA0"),
        "LaneInfo_RH_B_Quality_A0_sA0": ("LaneInfo_RH_B_A0", "LaneInfo_RH_B_Quality_A0_sA0"),

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
        _, C0_Left_A, unit = group.get_signal_with_unit('C0_Left_A', **rescale_kwargs)
        _, right_lane_marking_c0, unit = group.get_signal_with_unit('right_lane_marking_c0', **rescale_kwargs)
        _, C0_Right_A, unit = group.get_signal_with_unit('C0_Right_A', **rescale_kwargs)
        _, ego_speed, unit = group.get_signal_with_unit('FrontAxleSpeed', **rescale_kwargs)
        _, left_lane_quality, unit = group.get_signal_with_unit('left_lane_quality', **rescale_kwargs)
        _, right_lane_quality, unit = group.get_signal_with_unit('right_lane_quality', **rescale_kwargs)
        _, laneInfo_LH, unit = group.get_signal_with_unit('LaneInfo_LH_B_Quality_A0_sA0', **rescale_kwargs)
        _, laneInfo_RH, unit = group.get_signal_with_unit('LaneInfo_RH_B_Quality_A0_sA0', **rescale_kwargs)

        left_diff = C0_Left_A + left_lane_marking_c0
        right_diff = C0_Right_A + right_lane_marking_c0

        left_lane_pdiff = (left_diff > 0.2) & (ego_speed >= 50) & (left_lane_quality > 1) & (laneInfo_LH > 50)
        left_lane_ndiff = (left_diff < -0.2) & (ego_speed >= 50) & (left_lane_quality > 1) & (laneInfo_LH > 50)
        right_lane_pdiff = (right_diff > 0.2) & (ego_speed >= 50) & (right_lane_quality > 1) & (laneInfo_RH > 50)
        right_lane_ndiff = (right_diff < -0.2) & (ego_speed >= 50) & (right_lane_quality > 1) & (laneInfo_RH > 50)

        return time, left_lane_pdiff, left_lane_ndiff, right_lane_pdiff, right_lane_ndiff


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\Measurement\Lane_evaluation\ldws_state\test\2022-04-12\mi5id786__2022-04-12_14-31-02.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    data = manager_modules.calc('calc_flc25_compare_c0@aebs.fill', manager)
    print data
