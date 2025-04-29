# -*- dataeval: init -*-

from interface import iCalc
import numpy as np

sgs = [
    {
        "fYaw": (
        "MFC5xx Device.ACAL.pNvmAcalWrite", "MFC5xx_Device_ACAL_pNvmAcalWrite_nvmOnline_sPoseCalibration_fYaw"),
    },
    {
        "fYaw": (
        "MFC5xx Device.ACAL.pNvmAcalWrite", "MFC5xx Device.ACAL.pNvmAcalWrite.nvmOnline.sPoseCalibration.fYaw"),
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
        rescale_kwargs = {'ScaleTime': time, 'Order': 'valid'}

        fYaw_time, fYaw_val = group.get_signal('fYaw')

        # Statistics calculation
        count = len(fYaw_val)
        mean = np.mean(fYaw_val)
        sum = np.sum(fYaw_val)
        std = np.std(fYaw_val)
        min = np.min(fYaw_val)
        max = np.max(fYaw_val)
        val=(abs(mean - fYaw_val) * 57.3248) > 0.5
        violation = len((np.where(val==True)[0]))

        return time, fYaw_val, count, mean, std, min, max, sum, violation
