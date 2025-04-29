# -*- dataeval: init -*-

from interface import iCalc

sgs = [
    {
        "AdaptiveCruiseCtrlMode": ("ACC1_2A", "ACC1_Mode_2A"),
        "EBC1_EBSBrkSw_0B": ("EBC1_0B", "EBC1_EBSBrkSw_0B"),
    },
    {
        "AdaptiveCruiseCtrlMode": ("ACC1_2A_s2A", "AdaptiveCruiseCtrlMode"),
        "EBC1_EBSBrkSw_0B": ("EBC1_0B_s0B", "EBC1_EBSBrkSw_0B"),
    },
    {
        "AdaptiveCruiseCtrlMode": ("ACC1_2A_s2A_ACC1_2A_CAN21", "AdaptiveCruiseCtrlMode"),
        "EBC1_EBSBrkSw_0B": ("EBC1_0B_s0B_EBC1_0B_CAN21", "EBC1_EBSBrkSw_0B"),
    },
    {
        "AdaptiveCruiseCtrlMode": ("ACC1_2A_s2A_ACC1_2A_CAN21","ACC1_ACCMode_2A"),
        "EBC1_EBSBrkSw_0B": ("EBC1_0B_s0B_EBC1_0B_CAN21","EBC1_EBSBrakeSwitch_0B"),
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
        _, signal_data, unit_vx = group.get_signal_with_unit('EBC1_EBSBrkSw_0B', ScaleTime=time)
        _, cruise_data, unit_vx = group.get_signal_with_unit('AdaptiveCruiseCtrlMode', ScaleTime=time)

        valid_data = (signal_data == 1)

        return time, valid_data, cruise_data

if __name__ == '__main__':

    from config.Config import init_dataeval

    meas_path = r"C:\KBData\report\ACC_evaluation\test5\2020-08-25\UFO__2020-08-25_12-53-02.mat"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flr25_egomotion = manager_modules.calc('calc_acc_brakepedal_override@aebs.fill', manager)
    # print flr25_egomotion.vx
