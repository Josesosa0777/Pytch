# -*- dataeval: init -*-

from interface import iCalc
from measproc.IntervalList import cIntervalList, maskToIntervals

sgs = [
    {
        "StateId": (
        "MFC5xx Device.ACTL.EcuOmc_FreezeData", "MFC5xx_Device_ACTL_EcuOmc_FreezeData_Status_CurrentState_u_StateId"),
    },
    {
        "StateId": (
        "MFC5xx_Device.ACTL.EcuOmc_FreezeData", "MFC5xx_Device_ACTL_EcuOmc_FreezeData_Status_CurrentState_u_StateId"),
    },
    {
        "StateId": (
        "MFC5xx Device.ACTL.EcuOmc_FreezeData", "MFC5xx Device.ACTL.EcuOmc_FreezeData.Status.CurrentState.u_StateId"),
    },
]


class cFill(iCalc):
    dep = ('calc_common_time-flr25')

    def check(self):
        source = self.get_source()
        group = source.selectSignalGroup(sgs)
        return group

    def fill(self, group):
        time = self.modules.fill('calc_common_time-flr25')

        time_ACTL, value_ACTL = group.get_signal('StateId', ScaleTime=time)

        ACTL_masked_values = (value_ACTL != 7)

        return time, ACTL_masked_values


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\evaluation\pytch2_eval\rrec2mf4\mf4_eval\2025-02-18\mi5id5649__2025-02-18_13-15-53.mf4"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flr25_egomotion = manager_modules.calc('calc_actl_eval@aebs.fill', manager)
    # print flr25_egomotion.vx
