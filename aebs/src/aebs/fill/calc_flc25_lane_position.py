# -*- dataeval: init -*-

from interface import iCalc

sgs = [
    {
        "left_ego_line": ("LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidNear_offset"),
        "right_ego_line": ("LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_clothoidNear_offset"),
        "left_adjacent_line": ("LdOutput", "MFC5xx_Device_LD_LdOutput_road_leftI0I_left_clothoidNear_offset"),
        "right_adjacent_line": ("LdOutput", "MFC5xx_Device_LD_LdOutput_road_rightI0I_right_clothoidNear_offset"),
    },
    {
        "left_ego_line": ("MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidNear_offset"),
        "right_ego_line": ("MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_clothoidNear_offset"),
        "left_adjacent_line": ("MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_left0_left_clothoidNear_offset"),
        "right_adjacent_line": ("MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_right0_right_clothoidNear_offset"),
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
        _, left_ego_line_index, unit = group.get_signal_with_unit('left_ego_line', **rescale_kwargs)
        _, right_ego_line_index, unit = group.get_signal_with_unit('right_ego_line', **rescale_kwargs)
        _, left_adjacent_line_index, unit = group.get_signal_with_unit('left_adjacent_line', **rescale_kwargs)
        _, right_adjacent_line_index, unit = group.get_signal_with_unit('right_adjacent_line', **rescale_kwargs)

        # Detect wrong position for left_adjacent_lane
        left_adjacent_lane_position = (((left_adjacent_line_index < (left_ego_line_index + 2.0)) | (left_adjacent_line_index > (left_ego_line_index + 5.0))) & (left_adjacent_line_index != 0) & (left_ego_line_index != 0))

        # Detect wrong position for right_adjacent_lane
        right_adjacent_lane_position = (((right_adjacent_line_index > (right_ego_line_index - 2.0)) | (right_adjacent_line_index < (right_ego_line_index - 5.0))) & (right_adjacent_line_index != 0) & (right_ego_line_index != 0))

        return time, left_adjacent_lane_position, right_adjacent_lane_position


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\Measurement\PAEBS\AOA\2021-02-16\HMC-QZ-STR__2021-02-16_09-40-07.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    data = manager_modules.calc('calc_flc25_lane_line_position@aebs.fill', manager)
    print data
