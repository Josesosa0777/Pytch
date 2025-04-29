# -*- dataeval: init -*-
import numpy
from interface import iCalc


class Calc(iCalc):

		def check(self):
				sgn_group = [
						{
								"VersionNumber": ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t","MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_uiVersionNumber")
						},
						{
								"VersionNumber": ("FCUArs430FusionObjectList_t","MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_uiVersionNumber"),

						},
				]
				source = self.get_source()
				group = source.selectSignalGroup(sgn_group)
				return group


		def fill(self, group):
				time00, fusionProtocol = group.get_signal("VersionNumber")
				return fusionProtocol


if __name__ == "__main__":
		from config.Config import init_dataeval

		meas_path = r"\\corp.knorr-bremse.com\str\measure\DAS\ConvertedMeas_Xcellis\FER\ACC_F30\FC212993_FU212450\2021-10-26\mi5id787__2021-10-26_15-54-10.h5"
		config, manager, manager_modules = init_dataeval(["-m", meas_path])
		tracks = manager_modules.calc("calc_flc25_fusion_protocol@aebs.fill", manager)
		print(tracks)

