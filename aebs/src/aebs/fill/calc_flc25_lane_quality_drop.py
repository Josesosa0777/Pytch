# -*- dataeval: init -*-

from interface import iCalc
import numpy as np

MIN_EGO_SPEED = 70
FCT_QUALITY_LIMIT = 50
STEERING_WHL_ANGLE_GRADIENT_LIMIT = 0

sgs = [
    {
        "ego_left_quality": ("LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_quality"),
        "ego_right_quality": ("LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_quality"),
        "FrontAxleSpeed": ("EBC2_s0B","FrontAxleSpeed"),
        #"steering_wheel_angle_gradient": ("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsInput_driver_input_steering_wheel_angle_gradient"),
    },
    {
        "ego_left_quality": ("LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_quality"),
        "ego_right_quality": ("LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_quality"),
        "FrontAxleSpeed": ("EBC2_s0B","Front_axle_speed"),
        #"steering_wheel_angle_gradient": ("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsInput_driver_input_steering_wheel_angle_gradient"),
    },
    {
        "ego_left_quality": ("MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_quality"),
        "ego_right_quality": ("MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_quality"),
        "FrontAxleSpeed": ("EBC2","FrontAxleSpeed_s0B"),
        #"steering_wheel_angle_gradient": ("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsInput_driver_input_steering_wheel_angle_gradient"),
    },
    {
        "ego_left_quality": ("MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_quality"),
        "ego_right_quality": ("MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_quality"),
        "FrontAxleSpeed": ("EBC2_0B","EBC2_FrontAxleSpeed_0B_s0B"),
        #"steering_wheel_angle_gradient": ("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsInput_driver_input_steering_wheel_angle_gradient"),
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
        _, left_quality, unit = group.get_signal_with_unit('ego_left_quality', **rescale_kwargs)
        _, right_quality, unit = group.get_signal_with_unit('ego_right_quality', **rescale_kwargs)
        _, ego_speed, unit = group.get_signal_with_unit('FrontAxleSpeed', **rescale_kwargs)
        #_, steering_data, unit = group.get_signal_with_unit('FrontAxleSpeed', **rescale_kwargs)

        left_quality_mask = (0 <= left_quality) & (left_quality < FCT_QUALITY_LIMIT)
        right_quality_mask = (0 <= right_quality) & (right_quality < FCT_QUALITY_LIMIT)
        speed_mask = ego_speed > MIN_EGO_SPEED
        #steering_mask = steering_data < STEERING_WHL_ANGLE_GRADIENT_LIMIT
        left_quality_drop = left_quality_mask & speed_mask # & steering_mask
        right_quality_drop = right_quality_mask & speed_mask # & steering_mask

        
        return time, left_quality_drop, right_quality_drop

