# -*- dataeval: init -*-

from interface import iCalc
import numpy as np

sgs = [
    {
        "reset_reason": ("FS_SafeSection_Mirror", "MFC5xx_Device_ST_FS_SafeSection_Mirror_FsData_u_ResetReason"),
        "reset_counter": ("FS_SafeSection_Mirror", "MFC5xx_Device_ST_FS_SafeSection_Mirror_FsData_u_ResetCounter"),
    },
    {
        "reset_reason": (
        "MFC5xx Device.ST.FS_SafeSection_Mirror", "MFC5xx_Device_ST_FS_SafeSection_Mirror_FsData_u_ResetReason"),
        "reset_counter": (
        "MFC5xx Device.ST.FS_SafeSection_Mirror", "MFC5xx_Device_ST_FS_SafeSection_Mirror_FsData_u_ResetCounter"),
    },
    {
        "reset_reason": (
        "MFC5xx_Device.ST.FS_SafeSection_Mirror", "MFC5xx_Device_ST_FS_SafeSection_Mirror_FsData_u_ResetReason"),
        "reset_counter": (
        "MFC5xx_Device.ST.FS_SafeSection_Mirror", "MFC5xx_Device_ST_FS_SafeSection_Mirror_FsData_u_ResetCounter"),
    },
    {
        "reset_reason": (
        "MFC5xx Device.ST.FS_SafeSection_Mirror", "MFC5xx Device.ST.FS_SafeSection_Mirror.FsData.u_ResetReason"),
        "reset_counter": (
        "MFC5xx Device.ST.FS_SafeSection_Mirror", "MFC5xx Device.ST.FS_SafeSection_Mirror.FsData.u_ResetCounter"),
    }
]


class cFill(iCalc):
    dep = ('calc_common_time-flc25',)

    def check(self):
        source = self.get_source()
        group = source.selectSignalGroup(sgs)
        return group

    def fill(self, group):
        time = self.modules.fill('calc_common_time-flc25')
        rescale_kwargs = {'ScaleTime': time, 'Order': 'valid'}
        # vx
        _, reset_reason, unit_vx = group.get_signal_with_unit('reset_reason', **rescale_kwargs)
        counter_time, reset_counter, unit_vx = group.get_signal_with_unit('reset_counter', **rescale_kwargs)

        valid_reset_reason_data = reset_reason[~reset_reason.mask].data
        valid_reset_counter = reset_counter[~reset_counter.mask].data
        valid_reset_counter_mask = (valid_reset_counter[1:] > valid_reset_counter[:-1])
        valid_reset_counter_mask = np.insert(valid_reset_counter_mask, 0, False)

        return time, valid_reset_counter_mask, valid_reset_reason_data, valid_reset_counter
