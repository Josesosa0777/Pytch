# -*- dataeval: init -*-

from interface import iCalc
import numpy as np
from matplotlib import pyplot as plt
from dmw import SignalFilters

sgs = [
    {
        "ACC1_ACCMode": ("CAN_MFC_Public_ACC1_2A","ACC1_ACCMode_2A"),
        "VehDynSync_Longitudinal_Accel": ("MFC5xx Device.VDY.VehDyn","MFC5xx Device.VDY.VehDyn.Longitudinal.Accel"),
        "XBR_ExtAccelDem": ("CAN_MFC_Public_XBR_0B_2A","XBR_ExtAccelDem_0B_2A"),
        "AEBS_signal": ("CAN_MFC_Public_EBC1_0B","EBC1_ABSActive_0B"),
        "Gear_shift_signal": ("CAN_MFC_Public_ETC1_03","ETC1_TransShiftInProcess_03"),
    },
    #{
        #"ACC1_ACCMode": ("CAN_VEHICLE_ACC1_2A","ACC1_ACCMode_2A"),
        #"VehDynSync_Longitudinal_Accel": ("MFC5xx Device.VDY.VehDyn","MFC5xx Device.VDY.VehDyn.Longitudinal.Accel"),
        #"XBR_ExtAccelDem": ("CAN_VEHICLE_XBR_0B_2A","XBR_ExtAccelDem_0B_2A"),
    #},
    #{
        #"ACC1_ACCMode": ("CAN_MFC_Public_ACC1_2A","ACC1_ACCMode_2A"),
        #"VehDynSync_Longitudinal_Accel": ("MFC5xx Device.FCU.VehDynSync", "MFC5xx_Device_FCU_VehDynSync_Longitudinal_Accel"),
        #"XBR_ExtAccelDem": ("CAN_MFC_Public_XBR_0B_2A","XBR_ExtAccelDem_0B_2A"),
    #}
]

class cFill(iCalc):
    dep = ('calc_common_time-flr25')

    def check(self):
        source = self.get_source()
        group = source.selectSignalGroup(sgs)
        return group

    def fill(self, group):
        time = self.modules.fill('calc_common_time-flr25')

        _, acc_mode, unit_vy = group.get_signal_with_unit('ACC1_ACCMode', ScaleTime=time)
        _, VehDyn, unit_vy = group.get_signal_with_unit('VehDynSync_Longitudinal_Accel', ScaleTime=time)
        _, xbr, unit_vy = group.get_signal_with_unit('XBR_ExtAccelDem', ScaleTime=time)
        _, aebs_events, unit_vy = group.get_signal_with_unit('AEBS_signal', ScaleTime=time)
        _, gear_shift, unit_vy = group.get_signal_with_unit('Gear_shift_signal', ScaleTime=time)

        filtered_VehDyn = SignalFilters.savgol_filter(VehDyn,window_length=53,polyorder=9)

        delay = 3  # for 180msec
        Vehdyn_diff = np.append(filtered_VehDyn, filtered_VehDyn[-3:])
        Vehdyn_diff = Vehdyn_diff[delay:] - Vehdyn_diff[:-delay]
        time_diff = np.append(time, time[-3:])
        time_diff = time_diff[delay:] - time_diff[:-delay]

        VehJerk = np.divide(Vehdyn_diff, time_diff)

        valid_VehDyn_data = np.zeros_like(VehJerk, dtype=bool)
        valid_VehDyn_data = np.where((VehJerk < -5), True, valid_VehDyn_data)

        valid_acc_data = (acc_mode == 2)
        valid_xbr_data = (xbr<0)
        no_aebs_events = (aebs_events == 0)
        no_gear_shift = (gear_shift == 0)
        valid_jerk_mask = (valid_acc_data & valid_VehDyn_data & valid_xbr_data & no_gear_shift & no_aebs_events)

        return time, valid_jerk_mask, VehDyn

if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\acc-test\2024-01-09\mi5id5506__2024-01-09_10-02-03.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flr25_egomotion = manager_modules.calc('calc_acc_jerk@aebs.fill', manager)