# -*- dataeval: init -*-
import numpy
from interface import iCalc


class Calc(iCalc):

		def check(self):
				sgn_group = [{
						"SensorStatus": ("Video_Data_General_B", "SensorStatus"),
				}]
				source = self.get_source()
				group = source.selectSignalGroup(sgn_group)
				return group


		def fill(self, group):
				t, status = group.get_signal("SensorStatus")
				return status


if __name__ == "__main__":
		from config.Config import init_dataeval

		meas_path = r"\\pu2w6474\shared-drive\measurements\TSR_evaluation\HMC-QZ-STR__2021-01-25_13-16-05.h5"
		config, manager, manager_modules = init_dataeval(["-m", meas_path])
		tracks = manager_modules.calc("calc_flc25_sensor_status@aebs.fill", manager)
		print(tracks)

