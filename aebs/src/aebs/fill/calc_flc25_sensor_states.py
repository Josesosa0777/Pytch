# -*- dataeval: init -*-
import numpy as np
from measproc.IntervalList import cIntervalList, maskToIntervals
from interface import iCalc

sgs = [
    {
        "sensorRadar_state": ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas",
                              "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorRadar_state"),
        "sensorCamera_state": ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas",
                               "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorCamera_state"),
    },
    {
        "sensorRadar_state": ("MFC5xx_Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas",
                              "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorRadar_state"),
        "sensorCamera_state": ("MFC5xx_Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas",
                               "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorCamera_state"),
    },
    {
        "sensorRadar_state": ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas",
                              "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas.sensorRadar.state"),
        "sensorCamera_state": ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas",
                               "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas.sensorCamera.state"),
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
        _, sensorRadar_state, sensorRadar_state_unit = group.get_signal_with_unit('sensorRadar_state', **rescale_kwargs)
        _, sensorCamera_state, sensorCamera_state_unit = group.get_signal_with_unit('sensorCamera_state',
                                                                                    **rescale_kwargs)

        # mapping = {0: 'FAILED', 1: 'DEGRADED',2: 'AVAILABLE'}
        cam_state = (sensorCamera_state == 1)
        radar_state = (sensorRadar_state == 1)

        cam_intervals = maskToIntervals(cam_state)
        for start, end in cam_intervals:
            # If Signal starts from DEGRADED state
            if start == 0:
                cam_state[start:end] = False
            # sensorRadar_state not going from AVAILABLE to DEGREDATION state
            elif sensorCamera_state[start - 1] != 2:
                cam_state[start:end] = False

        radar_intervals = maskToIntervals(radar_state)
        for start, end in radar_intervals:
            # If Signal starts from DEGRADED state
            if start == 0:
                radar_state[start:end] = False

            # sensorRadar_state not going from AVAILABLE to DEGREDATION state
            elif sensorRadar_state[start - 1] != 2:
                radar_state[start:end] = False

            if (time[end - 1] - time[start]) < 0.60:
                radar_state[start:end] = False

        return time, cam_state, radar_state


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\evaluation\pytch2_eval\rrec2mf4\mf4_eval\2025-02-18\mi5id5649__2025-02-18_13-15-53.mf4"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    data = manager_modules.calc('calc_flc25_sensor_states@aebs.fill', manager)
    print(data)
