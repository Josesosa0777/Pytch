# -*- dataeval: init -*-

from interface import iCalc

sgs = [
    {
        "ego_left_quality": ("LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_quality"),
        "ego_right_quality": ("LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_quality"),
    },
    {
        "ego_left_quality" : ("MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_quality"),
        "ego_right_quality": ("MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_quality"),
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
        _, ego_left_quality_index, unit = group.get_signal_with_unit('ego_left_quality', **rescale_kwargs)
        _, ego_right_quality_index, unit = group.get_signal_with_unit('ego_right_quality', **rescale_kwargs)
        left_lane_quality = (ego_left_quality_index > 45) & (ego_left_quality_index < 55)
        right_lane_quality = (ego_right_quality_index > 45) & (ego_right_quality_index < 55)
        return time, left_lane_quality, right_lane_quality


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\Measurement\PAEBS\AOA\2021-02-16\HMC-QZ-STR__2021-02-16_09-40-07.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    data = manager_modules.calc('calc_flc25_lane_quality@aebs.fill', manager)
    print data
