# -*- dataeval: init -*-
import numpy as np
from interface import iCalc


class Calc(iCalc):

		def check(self):
				sgn_group = [
						{
								"iNumOfUsedObjects": ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas","MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_HeaderObjList_iNumOfUsedObjects"),
						},
						{
								"iNumOfUsedObjects": ("CEM_FDP_KB_M_p_TpfOutputIfMeas","MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_HeaderObjList_iNumOfUsedObjects"),
						},
				]
				source = self.get_source()
				group = source.selectSignalGroup(sgn_group)
				return group


		def fill(self, group):
				time, numOfUsedObjects = group.get_signal("iNumOfUsedObjects")
				mask = numOfUsedObjects > 40
				if not np.any(mask):
					max_indice = np.where(numOfUsedObjects == max(numOfUsedObjects))[0][0]
					mask[max_indice] = True
				return time, mask, numOfUsedObjects


if __name__ == "__main__":
		from config.Config import init_dataeval

		meas_path = r"\\corp.knorr-bremse.com\str\measure\DAS\ConvertedMeas_Xcellis\FER\ACC_AEBS\F30\B365_5288\FC213410_FU213230\2021-12-15\mi5id5288__2021-12-15_05-50-59.h5"
		config, manager, manager_modules = init_dataeval(["-m", meas_path])
		tracks = manager_modules.calc("calc_flc25_num_of_detected_objects@aebs.fill", manager)
		print(tracks)

