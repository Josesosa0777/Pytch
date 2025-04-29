# -*- dataeval: init -*-

from interface import iCalc

sgs = [
    {
        "ego_left_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                             "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_quality"),
        "ego_right_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                              "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_quality"),
        "FrontAxleSpeed": ("EBC2", "FrontAxleSpeed_s0B"),
    },
    {
        "ego_left_quality": ("MTSI_stKBFreeze_020ms_t",
                             "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_quality"),
        "ego_right_quality": ("MTSI_stKBFreeze_020ms_t",
                              "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_quality"),
        "FrontAxleSpeed": ("EBC2_s0B", "FrontAxleSpeed"),
    },
    {
        "ego_left_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                             "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_quality"),
        "ego_right_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                              "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_quality"),
        "FrontAxleSpeed": ("EBC2_0B", "EBC2_FrontAxleSpeed_0B_s0B"),
    },
    {
        "ego_left_quality": ("MTSI_stKBFreeze_020ms_t",
                             "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_quality"),
        "ego_right_quality": ("MTSI_stKBFreeze_020ms_t",
                              "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_quality"),
        "FrontAxleSpeed": ("EBC2_0B", "EBC2_FrontAxleSpeed_0B_s0B"),
    },
    {
        "ego_left_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                             "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_quality"),
        "ego_right_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                              "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_quality"),
        "FrontAxleSpeed": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                           "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_EBC2_EBC2_MeanSpdFA"),
    },
    {
        "ego_left_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                             "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_LkInput_sensor_input_left_lane_line_quality"),
        "ego_right_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                              "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_LkInput_sensor_input_right_lane_line_quality"),
        "FrontAxleSpeed": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                           "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_EBC2_EBC2_MeanSpdFA"),
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
        _, ego_left_quality, unit = group.get_signal_with_unit('ego_left_quality', **rescale_kwargs)
        _, ego_right_quality, unit = group.get_signal_with_unit('ego_right_quality', **rescale_kwargs)
        _, ego_speed, unit = group.get_signal_with_unit('FrontAxleSpeed', **rescale_kwargs)
        worst_case = (ego_speed >=30) & ((ego_left_quality==0)|(ego_left_quality==1)) & ((ego_right_quality==0)|(ego_right_quality==1))
        return time, worst_case


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\Measurement\Lane_evaluation\ldws_state\2022-04-12\mi5id786__2022-04-12_14-20-59.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    data = manager_modules.calc('calc_flc25_lane_drop_worst_case@aebs.fill', manager)
    print data
