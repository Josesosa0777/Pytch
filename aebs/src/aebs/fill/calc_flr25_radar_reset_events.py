# -*- dataeval: init -*-

from interface import iCalc
import numpy as np

sgs = [
    {
        "cat2_last_reset_reason": ("FS_SafeSection_Mirror",
                                   "ARS4xx_Device_SW_Every10ms_FS_SafeSection_Mirror_FsData_u_Cat2LastResetReason"),
        "address": ("FS_SafeSection_Mirror",
                    "ARS4xx_Device_SW_Every10ms_FS_SafeSection_Mirror_FsData_Exception_Mcu_u_Address"),
        "cat2_reset_counter": ("FS_SafeSection_Mirror",
                               "ARS4xx_Device_SW_Every10ms_FS_SafeSection_Mirror_FsData_u_Cat2ResetCounter"),
        "ReturnAddr": ("FS_SafeSection_Mirror",
                       "ARS4xx_Device_SW_Every10ms_FS_SafeSection_Mirror_FsData_Exception_Mcu_a_ReturnAddr"),
    },
    {
        "cat2_last_reset_reason": ("ARS4xx Device.SW_Every10ms.FS_SafeSection_Mirror",
                                   "ARS4xx_Device_SW_Every10ms_FS_SafeSection_Mirror_FsData_u_Cat2LastResetReason"),
        "address": ("ARS4xx Device.SW_Every10ms.FS_SafeSection_Mirror",
                    "ARS4xx_Device_SW_Every10ms_FS_SafeSection_Mirror_FsData_Exception_Mcu_u_Address"),
        "cat2_reset_counter": ("ARS4xx Device.SW_Every10ms.FS_SafeSection_Mirror",
                               "ARS4xx_Device_SW_Every10ms_FS_SafeSection_Mirror_FsData_u_Cat2ResetCounter"),
        "ReturnAddr": ("ARS4xx Device.SW_Every10ms.FS_SafeSection_Mirror",
                       "ARS4xx_Device_SW_Every10ms_FS_SafeSection_Mirror_FsData_Exception_Mcu_a_ReturnAddr"),
    },
    # MF4
    {
        "cat2_last_reset_reason": ("ARS4xx_Device.SW_Every10ms.FS_SafeSection_Mirror",
                                   "ARS4xx_Device_SW_Every10ms_FS_SafeSection_Mirror_FsData_u_Cat2LastResetReason"),
        "address": ("ARS4xx_Device.SW_Every10ms.FS_SafeSection_Mirror",
                    "ARS4xx_Device_SW_Every10ms_FS_SafeSection_Mirror_FsData_Exception_Mcu_u_Address"),
        "cat2_reset_counter": ("ARS4xx_Device.SW_Every10ms.FS_SafeSection_Mirror",
                               "ARS4xx_Device_SW_Every10ms_FS_SafeSection_Mirror_FsData_u_Cat2ResetCounter"),
        "ReturnAddr": ("ARS4xx_Device.SW_Every10ms.FS_SafeSection_Mirror",
                       "ARS4xx_Device_SW_Every10ms_FS_SafeSection_Mirror_FsData_Exception_Mcu_a_ReturnAddr"),
    },
    {
        "cat2_last_reset_reason": ("ARS4xx Device.SW_Every10ms.FS_SafeSection_Mirror",
                                   "ARS4xx Device.SW_Every10ms.FS_SafeSection_Mirror.FsData.u_Cat2LastResetReason"),
        "address": ("ARS4xx Device.SW_Every10ms.FS_SafeSection_Mirror",
                    "ARS4xx Device.SW_Every10ms.FS_SafeSection_Mirror.FsData.Exception.Mcu.u_Address"),
        "cat2_reset_counter": ("ARS4xx Device.SW_Every10ms.FS_SafeSection_Mirror",
                               "ARS4xx Device.SW_Every10ms.FS_SafeSection_Mirror.FsData.u_Cat2ResetCounter"),
        "ReturnAddr": ("ARS4xx Device.SW_Every10ms.FS_SafeSection_Mirror",
                       "ARS4xx Device.SW_Every10ms.FS_SafeSection_Mirror.FsData.Exception.Mcu.a_ReturnAddr"),
    },
]


class cFill(iCalc):
    dep = ('calc_common_time-flr25',)

    def check(self):
        source = self.get_source()
        group = source.selectSignalGroup(sgs)
        return group

    def fill(self, group):
        time = self.modules.fill('calc_common_time-flr25')
        rescale_kwargs = {'ScaleTime': time, 'Order': 'valid'}
        # vx
        _, cat2_last_reset_reason, unit_vx = group.get_signal_with_unit('cat2_last_reset_reason', **rescale_kwargs)
        _, address, unit_vx = group.get_signal_with_unit('address', **rescale_kwargs)
        counter_time, cat2_reset_counter, unit_vx = group.get_signal_with_unit('cat2_reset_counter', **rescale_kwargs)
        _, rtrn_addr, _ = group.get_signal_with_unit('ReturnAddr', **rescale_kwargs)

        valid_reset_reason_data = cat2_last_reset_reason[~cat2_last_reset_reason.mask].data
        valid_address_data = address[~address.mask].data
        valid_reset_counter = cat2_reset_counter[~cat2_reset_counter.mask].data
        valid_reset_counter_mask = (valid_reset_counter[1:] > valid_reset_counter[:-1])
        valid_reset_counter_mask = np.insert(valid_reset_counter_mask, 0, False)

        return time, valid_reset_counter_mask, valid_reset_reason_data, valid_address_data, valid_reset_counter, rtrn_addr


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\evaluation\pytch2_eval\rrec2mf4\mf4_eval\2025-02-18\mi5id5649__2025-02-18_13-15-53.mf4"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flr25_egomotion = manager_modules.calc('calc_flr25_radar_reset_events@aebs.fill', manager)
    print(flr25_egomotion)
