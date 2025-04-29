# -*- dataeval: init -*-

from interface import iCalc
import numpy as np
from measproc.IntervalList import cIntervalList, maskToIntervals

sgs = [
    {
        "CemState": ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas",
                     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_CemState"),
        "SigHeader_eSigStatus": ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas",
                                 "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sSigHeader_eSigStatus"),
    },
    {
        "CemState": ("MFC5xx_Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas",
                     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_CemState"),
        "SigHeader_eSigStatus": ("MFC5xx_Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas",
                                 "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sSigHeader_eSigStatus"),
    },
    {
        "CemState": ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas",
                     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas.CemState"),
        "SigHeader_eSigStatus": ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas",
                                 "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas.sSigHeader.eSigStatus"),
    },
]


class cFill(iCalc):
    dep = ('calc_common_time-flc25',)

    def check(self):
        source = self.get_source()
        group = source.selectSignalGroup(sgs)
        return group

    def fill(self, group):
        time = self.modules.fill('calc_common_time-flc25')
        rescale_kwargs = {'ScaleTime': time}
        _, cemState_values, cemState_unit = group.get_signal_with_unit('CemState', **rescale_kwargs)
        _, eSigStatus_values, eSigStatus_unit = group.get_signal_with_unit('SigHeader_eSigStatus', **rescale_kwargs)

        # mapping_cem = {0: 'OFF', 1: 'INIT', 2: 'NORMAL', 3: 'FAILURE'}
        # mapping_eSig = {0: 'AL_SIG_STATE_INIT', 1: 'AL_SIG_STATE_OK', 2: 'AL_SIG_STATE_INVALID'}
        cemState = cemState_values != 2
        eSigStatus = eSigStatus_values != 1

        cem_intervals = maskToIntervals(cemState)
        for start, end in cem_intervals:
            # If Signal starts from DEGRADED state
            if start == 0:
                cemState[start:end] = False
            # sensorRadar_state not going from NORMAL to FAILURE state
            elif cemState_values[start - 1] != 2:
                cemState[start:end] = False

        eSigStatus_intervals = maskToIntervals(eSigStatus)
        for start, end in eSigStatus_intervals:
            # If Signal starts from DEGRADED state
            if start == 0:
                eSigStatus[start:end] = False
            # sensorRadar_state not going from AL_SIG_STATE_OK to AL_SIG_STATE_INVALID state
            elif eSigStatus_values[start - 1] != 1:
                eSigStatus[start:end] = False

        cem_status = cemState | eSigStatus

        return time, cem_status


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\evaluation\pytch2_eval\rrec2mf4\mf4_eval\2025-02-18\mi5id5649__2025-02-18_13-15-53.mf4"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    data = manager_modules.calc('calc_flc25_cem_states_detection@aebs.fill', manager)
    print(data)
