# -*- dataeval: init -*-

from interface import iCalc
import numpy as np
from measproc.IntervalList import cIntervalList, maskToIntervals

sgs = [
    {
        "ACC1_ACCSystemShutoffWarning_2A_s2A": ("ACC1_2A_CAN22","ACC1_ACCSystemShutoffWarning_2A_s2A"),
    },
    {
        "ACC1_ACCSystemShutoffWarning_2A_s2A": ("ACC1_2A_CAN24","ACC1_ACCSystemShutoffWarning_2A_s2A"),
    },
    {
        "ACC1_ACCSystemShutoffWarning_2A_s2A": ("CAN_MFC_Public_ACC1_2A","ACC1_ACCSystemShutoffWarning_2A"),
    },
    {
        "ACC1_ACCSystemShutoffWarning_2A_s2A": ("CAN_VEHICLE_ACC1_2A","ACC1_ACCSystemShutoffWarning_2A"),
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

        _, acc_shutdown, unit_vy = group.get_signal_with_unit('ACC1_ACCSystemShutoffWarning_2A_s2A', ScaleTime=time)

        acc_shutdown_mask = (acc_shutdown == 1)

        return time, acc_shutdown_mask, acc_shutdown

if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\test-acc-brake\shutdown\2023-10-19\mi5id5386__2023-10-19_16-30-52.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flr25_egomotion = manager_modules.calc('calc_acc_shutdown@aebs.fill', manager)