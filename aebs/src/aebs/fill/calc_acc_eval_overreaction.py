# -*- dataeval: init -*-

from interface import iCalc
import numpy as np

sgs = [
    {
        "TSC1_ReqTorqueLimit_2A": ("TSC1_2A_00", "TSC1_ReqTorqueLimit_2A_00"),
        "XBR_ExtAccelDem_2A": ("XBR_2A", "XBR_ExtAccelDem_2A"),
    },
    {
        "TSC1_ReqTorqueLimit_2A": ("TSC1_00_2A_d00_s2A", "TSC1_ReqTorqueLimit_2A_00"),
        "XBR_ExtAccelDem_2A": ("XBR_0B_2A_d0B_s2A", "XBR_ExtAccelDem_2A"),
    },
    {
        "TSC1_ReqTorqueLimit_2A": ("TSC1_00_2A_d00_s2A_TSC1_00_2A_CAN21", "TSC1_ReqTorqueLimit_2A_00"),
        "XBR_ExtAccelDem_2A": ("XBR_0B_2A_d0B_s2A_XBR_0B_2A_CAN21", "XBR_ExtAccelDem_2A"),
    },
    {
        "TSC1_ReqTorqueLimit_2A": ("TSC1_00_2A_d00_s2A", "TSC1_ReqTorqueLimit_2A_00"),
        "XBR_ExtAccelDem_2A": ("XBR_0B_2A_d0B_s2A_XBR_0B_2A_CAN21", "XBR_ExtAccelDem_2A"),
    },
    {
        "TSC1_ReqTorqueLimit_2A": ("TSC1_00_2A_d00_s2A_TSC1_00_2A_CAN21","TSC1_EngReqTorqueLimit_00_2A"),
        "XBR_ExtAccelDem_2A": ("XBR_0B_2A_d0B_s2A_XBR_0B_2A_CAN21","XBR_ExtAccelDem_0B_2A"),
    },
    {
        "TSC1_ReqTorqueLimit_2A": ("TSC1_00_2A_d00_s2A","TSC1_EngReqTorqueLimit_00_2A"),
        "XBR_ExtAccelDem_2A": ("XBR_0B_2A_d0B_s2A_XBR_0B_2A_CAN21","XBR_ExtAccelDem_0B_2A"),
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
        torque_time, torque_limit_data, unit_vx = group.get_signal_with_unit('TSC1_ReqTorqueLimit_2A', ScaleTime=time)
        _, signal_data, unit_vx = group.get_signal_with_unit('XBR_ExtAccelDem_2A', ScaleTime=time)

        index = np.argmax(signal_data < 0)
        timestamp = time[index] - 1
        valid_data = np.where((torque_time > timestamp) & (torque_time < time[index]))
        valid_data_mask = (torque_limit_data[valid_data] > 0)

        return time, valid_data_mask, valid_data, torque_limit_data


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\report\ACC_evaluation\test5\2020-08-25\UFO__2020-08-25_12-53-02.mat"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flr25_egomotion = manager_modules.calc('calc_acc_eval_overreaction@aebs.fill', manager)
    # print flr25_egomotion.vx
