# -*- dataeval: init -*-

from interface import iCalc
import numpy as np

sgs = [
    {
        "ego_left_clothoidNear_offset": ("LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidNear_offset"),
        "ego_right_clothoidNear_offset": ("LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_clothoidNear_offset"),
        "EBC2_MeanSpdFA_0B": ("EBC2_0B", "EBC2_MeanSpdFA_0B"),
    },
    {
        "ego_left_clothoidNear_offset" : ("MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidNear_offset"),
        "ego_right_clothoidNear_offset": ("MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_clothoidNear_offset"),
        "EBC2_MeanSpdFA_0B"            : ("EBC2","FrontAxleSpeed_s0B"),


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
        _, ego_left_clothoidNear_offset, unit = group.get_signal_with_unit('ego_left_clothoidNear_offset',
                                                                           **rescale_kwargs)
        _, ego_right_clothoidNear_offset, unit = group.get_signal_with_unit('ego_right_clothoidNear_offset',
                                                                            **rescale_kwargs)
        _, ebc2_mean_spead, unit = group.get_signal_with_unit('EBC2_MeanSpdFA_0B',
                                                                            **rescale_kwargs)
        lane_width = np.absolute(ego_left_clothoidNear_offset) + np.absolute(ego_right_clothoidNear_offset)
        lane_width_check = lane_width_check = ((((lane_width < 2) | (lane_width > 5)) & ((ego_left_clothoidNear_offset != 0) & (ego_right_clothoidNear_offset != 0))) & (ebc2_mean_spead > 10))
        return time, lane_width_check


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\Measurement\PAEBS\AOA\2021-02-16\HMC-QZ-STR__2021-02-16_09-40-07.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    data = manager_modules.calc('calc_flc25_lane_width@aebs.fill', manager)
    print data
