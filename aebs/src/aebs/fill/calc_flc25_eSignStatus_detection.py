# -*- dataeval: init -*-

from interface import iCalc
import numpy as np
from measproc.IntervalList import cIntervalList, maskToIntervals

sgs = [
    {
        "LD_sSigHeader_eSigStatus": ("MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_sigHeader_eSigStatus"),
        "TPF_sSigHeader_eSigStatus": ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
                                      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_sSigHeader_eSigStatus"),
    },
    {
        "LD_sSigHeader_eSigStatus": ("MFC5xx_Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_sigHeader_eSigStatus"),
        "TPF_sSigHeader_eSigStatus": ("MFC5xx_Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
                                      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_sSigHeader_eSigStatus"),
    },
    {
        "LD_sSigHeader_eSigStatus": ("MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.sigHeader.eSigStatus"),
        "TPF_sSigHeader_eSigStatus": ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
                                      "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.sSigHeader.eSigStatus"),
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
        _, LD_sSigHeader_values, LD_sSigHeader_unit = group.get_signal_with_unit('LD_sSigHeader_eSigStatus',
                                                                                 **rescale_kwargs)
        _, TPF_sSigHeader_values, TPF_sSigHeader_unit = group.get_signal_with_unit('TPF_sSigHeader_eSigStatus',
                                                                                   **rescale_kwargs)

        # mapping_eSig = {0: 'AL_SIG_STATE_INIT', 1: 'AL_SIG_STATE_OK', 2: 'AL_SIG_STATE_INVALID'}
        LD_eSignStatus = (LD_sSigHeader_values != 1)
        TPF_eSignStatus = (TPF_sSigHeader_values != 1)

        return time, LD_eSignStatus, TPF_eSignStatus, TPF_sSigHeader_values, LD_sSigHeader_values


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\evaluation\pytch2_eval\rrec2mf4\mf4_eval\2025-02-18\mi5id5649__2025-02-18_13-15-53.mf4"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    data = manager_modules.calc('calc_flc25_eSignStatus_detection@aebs.fill', manager)
    print(data)
