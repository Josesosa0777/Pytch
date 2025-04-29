# -*- dataeval: init -*-
import numpy as np

from interface import iCalc

sgs = [
    {
        "dirk_red_button_counter": ("CAN_VEHICLE_DIRK_2A","DIRK_CntRedButton_2A"),
        "dirk_green_button_counter": ("CAN_VEHICLE_DIRK_2A","DIRK_CntGreenButton_2A"),
    },
    {
        "dirk_red_button_counter": ("CAN_MFC_Public_DIRK_2A","DIRK_CntRedButton_2A"),
        "dirk_green_button_counter": ("CAN_MFC_Public_DIRK_2A","DIRK_CntGreenButton_2A"),
    }
]

class cFill(iCalc):
    dep = ('calc_common_time-flr25')

    def check(self):
        source = self.get_source()
        group = source.selectSignalGroup(sgs)
        return group

    def fill(self, group):
        time = self.modules.fill('calc_common_time-flr25')
        # rescale_kwargs = {'ScaleTime': time, 'Order': 'valid'}
        # vx
        _, dirk_red_data, unit_vx = group.get_signal_with_unit('dirk_red_button_counter', ScaleTime=time)
        _, dirk_green_data, unit_vx = group.get_signal_with_unit('dirk_green_button_counter', ScaleTime=time)

        dirk_red_diff = np.insert(np.diff(dirk_red_data),0,0)
        valid_dirk_red_mask = (dirk_red_diff == 1)  # Wrong target selection

        dirk_green_diff = np.insert(np.diff(dirk_green_data),0,0)
        valid_dirk_green_mask = (dirk_green_diff == 1)  # Good Target Selection

        return time, valid_dirk_red_mask, valid_dirk_green_mask, dirk_red_data, dirk_green_data

if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\test-acc-brake\dirk-events\Sample_report_for1meas\2023-11-08\mi5id5506__2023-11-08_12-42-30.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flr25_egomotion = manager_modules.calc('calc_acc_eval_dirk@aebs.fill', manager)
    # print flr25_egomotion.vx
