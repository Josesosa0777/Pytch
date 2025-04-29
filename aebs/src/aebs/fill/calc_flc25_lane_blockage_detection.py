# -*- dataeval: init -*-

from interface import iCalc

sgs = [
    {
        "ui8_BlockageStatus": ("MFC5xx Device.CB.pCbRteOut", "MFC5xx_Device_CB_pCbRteOut_ui8_BlockageStatus"),
    },
    {
        "ui8_BlockageStatus": ("MFC5xx_Device.CB.pCbRteOut", "MFC5xx_Device_CB_pCbRteOut_ui8_BlockageStatus"),
    },
    {
        "ui8_BlockageStatus": ("MFC5xx Device.CB.pCbRteOut", "MFC5xx Device.CB.pCbRteOut.ui8_BlockageStatus"),
    },
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
        _, blockage_status, unit = group.get_signal_with_unit('ui8_BlockageStatus', **rescale_kwargs)
        cb_unknown_status = (blockage_status == 0)
        cb_no_blockage = (blockage_status == 1)
        cb_condensation = (blockage_status == 3)
        cb_top_part_blockage = (blockage_status == 4)
        cb_bottom_part_blockage = (blockage_status == 5)
        cb_blockage = (blockage_status == 6)
        cb_left_part_blockage = (blockage_status == 7)
        cb_right_part_blockage = (blockage_status == 8)
        return time, cb_unknown_status, cb_no_blockage, cb_condensation, cb_top_part_blockage, \
            cb_bottom_part_blockage, cb_blockage, cb_left_part_blockage, cb_right_part_blockage


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\evaluation\pytch2_eval\rrec2mf4\mf4_eval\2025-02-18\mi5id5649__2025-02-18_13-15-53.mf4"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    data = manager_modules.calc('calc_flc25_lane_blockage_detection@aebs.fill', manager)
    print(data)
