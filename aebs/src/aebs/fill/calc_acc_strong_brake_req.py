# -*- dataeval: init -*-

from interface import iCalc

sgs = [
    {
        "strong_brake_request": ("XBR_2A", "XBR_ExtAccelDem_2A"),
    },
    {
        "strong_brake_request": ("XBR_0B_2A_d0B_s2A", "XBR_ExtAccelDem_2A"),
    },
    {
        "strong_brake_request": ("XBR_0B_2A_d0B_s2A_XBR_0B_2A_CAN21", "XBR_ExtAccelDem_2A"),
    },
    {
        "strong_brake_request": ("XBR_0B_2A_d0B_s2A_XBR_0B_2A_CAN21","XBR_ExtAccelDem_0B_2A"),
    }
]


class cFill(iCalc):
    dep = ('calc_common_time-flr25',)

    def check(self):
        source = self.get_source()
        group = source.selectSignalGroup(sgs)
        return group

    def fill(self, group):
        time = self.modules.fill('calc_common_time-flr25')
        # rescale_kwargs = {'ScaleTime': time, 'Order': 'valid'}
        # vx
        _, brake_data, unit_vx = group.get_signal_with_unit('strong_brake_request', ScaleTime=time)

        valid_strong_brake_mask = (brake_data < -2.5)  # Good Target Selection

        return time, valid_strong_brake_mask, brake_data


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\report\ACC_evaluation\test5\2020-08-25\UFO__2020-08-25_12-53-02.mat"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flr25_egomotion = manager_modules.calc('calc_acc_strong_brake_req@aebs.fill', manager)
    # print flr25_egomotion.vx
