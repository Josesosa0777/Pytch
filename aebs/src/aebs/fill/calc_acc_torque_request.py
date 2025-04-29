# -*- dataeval: init -*-

from interface import iCalc
import numpy as np

sgs = [
    {
        "AdaptiveCruiseCtrlMode": ("ACC1_2A", "ACC1_Mode_2A"),
        "TSC1_ReqTorqueLimit_2A": ("TSC1_2A_00", "TSC1_ReqTorqueLimit_2A_00"),
        "XBR_ExtAccelDem_2A": ("XBR_2A", "XBR_ExtAccelDem_2A"),
    },
    {
        "AdaptiveCruiseCtrlMode": ("ACC1_2A_s2A", "AdaptiveCruiseCtrlMode"),
        "TSC1_ReqTorqueLimit_2A": ("Rte_SWCNorm_RPort_norm_om_TSC1_DEP_om_norm_TSC1_Buf", "ARS4xx_Device_SW_Every10ms_Rte_SWCNorm_RPort_norm_om_TSC1_DEP_om_norm_TSC1_Buf_engine_requested_torque_torque_limit"),
        "XBR_ExtAccelDem_2A": ("XBR_0B_2A_d0B_s2A", "XBR_ExtAccelDem_2A"),
    },
    {
        "AdaptiveCruiseCtrlMode": ("ACC1_2A_s2A_ACC1_2A_CAN21", "AdaptiveCruiseCtrlMode"),
        "TSC1_ReqTorqueLimit_2A": ("TSC1_00_2A_d00_s2A_TSC1_00_2A_CAN21", "TSC1_ReqTorqueLimit_2A_00"),
        "XBR_ExtAccelDem_2A": ("XBR_0B_2A_d0B_s2A_XBR_0B_2A_CAN21", "XBR_ExtAccelDem_2A"),
    },
    {
        "AdaptiveCruiseCtrlMode": ("ACC1_2A_s2A_ACC1_2A_CAN21", "AdaptiveCruiseCtrlMode"),
        "TSC1_ReqTorqueLimit_2A": ("TSC1_00_2A_d00_s2A", "TSC1_ReqTorqueLimit_2A_00"),
        "XBR_ExtAccelDem_2A": ("XBR_0B_2A_d0B_s2A_XBR_0B_2A_CAN21", "XBR_ExtAccelDem_2A"),
    },
    {
        "AdaptiveCruiseCtrlMode": ("ACC1_2A_s2A_ACC1_2A_CAN21","ACC1_ACCMode_2A"),
        "TSC1_ReqTorqueLimit_2A": ("TSC1_00_2A_d00_s2A_TSC1_00_2A_CAN21","TSC1_EngReqTorqueLimit_00_2A"),
        "XBR_ExtAccelDem_2A": ("XBR_0B_2A_d0B_s2A_XBR_0B_2A_CAN21","XBR_ExtAccelDem_0B_2A"),
    },
    {
        "AdaptiveCruiseCtrlMode":  ("ACC1_2A","ACC1_Mode_2A"),
        "TSC1_ReqTorqueLimit_2A":  ("TSC1_00_2A","TSC1_ReqTorqueLimit_2A_00_d00_s2A"),
        "XBR_ExtAccelDem_2A": ("XBR_0B_2A","XBR_ExtAccelDem_2A_d0B_s2A"),

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
        _, torque_limit_data, unit_vx = group.get_signal_with_unit('TSC1_ReqTorqueLimit_2A', ScaleTime=time)
        _, signal_data, unit_vx = group.get_signal_with_unit('XBR_ExtAccelDem_2A', ScaleTime=time)
        _, acc_mode, unit_vx = group.get_signal_with_unit('AdaptiveCruiseCtrlMode', ScaleTime=time)

        pedal_override_inactive = [0,6,7]
        acc_mode_mask = np.in1d(acc_mode, pedal_override_inactive)
        valid_data_mask = (signal_data < 0) & acc_mode_mask

        return time, valid_data_mask, signal_data, torque_limit_data


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"\\pu2w6474\shared-drive\measurements\new_meas_09_11_21\ARS4xx\mi5id787__2020-12-11_16-14-17.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flr25_egomotion = manager_modules.calc('calc_acc_torque_request@aebs.fill', manager)
    print flr25_egomotion
