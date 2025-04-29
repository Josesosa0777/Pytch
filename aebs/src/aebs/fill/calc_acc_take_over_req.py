# -*- dataeval: init -*-

from interface import iCalc

sgs = [
    {
        "take_over_request": ("ACC1_2A", "ACC1_DistanceAlert_2A"),
    },
    {
        "take_over_request": ("ACC1_2A_s2A", "ACCDistanceAlertSignal"),
    },
    {
        "take_over_request": ("ACC1_2A_s2A_ACC1_2A_CAN21", "ACCDistanceAlertSignal"),
    },
    {
        "take_over_request": ("ACC1_2A_s2A_ACC1_2A_CAN21","ACC1_ACCDistanceAlertSignal_2A"),

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
        _, take_over_data, unit_vx = group.get_signal_with_unit('take_over_request', ScaleTime=time)

        valid_take_over_mask = (take_over_data != 0)  # Good Target Selection

        return time, valid_take_over_mask, take_over_data


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\report\ACC_evaluation\FR201550_B_2_0_2020-06-10_09-36-55.MF4"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flr25_egomotion = manager_modules.calc('calc_acc_take_over_req@aebs.fill', manager)
    # print flr25_egomotion.vx
