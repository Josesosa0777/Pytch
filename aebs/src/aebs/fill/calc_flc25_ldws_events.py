# -*- dataeval: init -*-
import numpy as np
from interface import iCalc
from primitives.ldws import LdwsStatus

sgs = [
    {
        "ldw_enabled": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                        "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_ldw_enabled"),
        "lane_departure_imminent_left": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_LkOutput_hmi_output_lane_departure_imminent_left"),
        "lane_departure_imminent_right": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                          "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_LkOutput_hmi_output_lane_departure_imminent_right"),
        "lane_departure_system_status": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_LkOutput_hmi_output_lane_departure_system_status"),
    },
    {
        "ldw_enabled": ("MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                        "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_LkInput_status_input_ldw_enabled_status"),
        "lane_departure_imminent_left": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_LkOutput_hmi_output_lane_departure_imminent_left"),
        "lane_departure_imminent_right": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                          "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_LkOutput_hmi_output_lane_departure_imminent_right"),
        "lane_departure_system_status": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_LkOutput_hmi_output_lane_departure_system_status"),
    }
]


class cFill(iCalc):
    DEACTIVATED_BY_DRIVER = 2
    READY = 3
    WARNING = 5
    dep = ('calc_common_time-flc25',)

    def check(self):
        source = self.get_source()
        group = source.selectSignalGroup(sgs)
        return group

    def fill(self, group):
        time = self.modules.fill('calc_common_time-flc25')
        rescale_kwargs = {'ScaleTime': time}
        _, ldw_enabled, unit = group.get_signal_with_unit('ldw_enabled', **rescale_kwargs)
        _, lane_departure_imminent_left, unit = group.get_signal_with_unit('lane_departure_imminent_left',
                                                                           **rescale_kwargs)
        _, lane_departure_imminent_right, unit = group.get_signal_with_unit('lane_departure_imminent_right',
                                                                            **rescale_kwargs)
        _, lane_departure_system_status, unit = group.get_signal_with_unit('lane_departure_system_status',
                                                                           **rescale_kwargs)

        deactivated_by_driver = lane_departure_system_status == self.DEACTIVATED_BY_DRIVER
        ready = lane_departure_system_status == self.READY
        warning = lane_departure_system_status == self.WARNING

        if np.all(ldw_enabled == 1):
            imminent_left = (lane_departure_imminent_left == 1)
            imminent_right = (lane_departure_imminent_right == 1)
            system_status = LdwsStatus(time, warning, ready, deactivated_by_driver)

        return time, imminent_left, imminent_right, system_status


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\Measurement\Lane_evaluation\ldws_state\2022-04-12\mi5id786__2022-04-12_14-20-59.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    data = manager_modules.calc('calc_flc25_ldws_events@aebs.fill', manager)
    print data
