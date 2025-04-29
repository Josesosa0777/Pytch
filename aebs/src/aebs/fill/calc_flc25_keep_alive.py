# -*- dataeval: init -*-
import numpy as np
from interface import iCalc
from primitives.ldws import LdwsStatus

sgs = [
    {
        "right_lane_marking_type": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                    "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_type"),
        "left_lane_marking_type": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                   "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_type"),
        "road_ego_left_quality": ("MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_quality"),
        "road_ego_right_quality": ("MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_quality"),

    },
    {
        "right_lane_marking_type": ("MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_LkInput_sensor_input_right_lane_line_type"),
        "left_lane_marking_type": ("MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                                   "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_LkInput_sensor_input_left_lane_line_type"),
        "road_ego_left_quality": ("MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_quality"),
        "road_ego_right_quality": ("MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_quality"),
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
        _, left_lane_marking_type, left_marking_type_unit = group.get_signal_with_unit('left_lane_marking_type',
                                                                                       **rescale_kwargs)
        _, road_ego_left_quality, left_quality_unit = group.get_signal_with_unit('road_ego_left_quality',
                                                                                 **rescale_kwargs)

        _, right_lane_marking_type, right_marking_type_unit = group.get_signal_with_unit('right_lane_marking_type',
                                                                                         **rescale_kwargs)
        _, road_ego_right_quality, right_quality_unit = group.get_signal_with_unit('road_ego_right_quality',
                                                                                   **rescale_kwargs)

        masked_left_lane_marking = (left_lane_marking_type == 0)
        masked_ego_left_quality = (road_ego_left_quality < 25)
        KeepAlive_left = masked_left_lane_marking & masked_ego_left_quality

        masked_right_lane_marking = (right_lane_marking_type == 0)
        masked_ego_right_quality = (road_ego_right_quality < 25)

        KeepAlive_right = masked_right_lane_marking & masked_ego_right_quality

        return time, KeepAlive_left, KeepAlive_right


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\Measurement\Lane_evaluation\ldws_state\2022-04-12\mi5id786__2022-04-12_14-20-59.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    data = manager_modules.calc('calc_flc25_keep_alive@aebs.fill', manager)
    print data
