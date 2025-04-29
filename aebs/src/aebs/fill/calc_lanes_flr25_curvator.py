# -*- dataeval: init -*-

import numpy as np

import interface
from aebs.fill.calc_lanes import create_line
from primitives.lane import LaneData, PolyClothoid
from aebs.fill import calc_radar_egomotion


class Calc(interface.iCalc):
		dep = ('calc_common_time-flr25',)

		def check(self):
				sgs = [
						{

								"C2"   : ("VehDyn", "ARS4xx_Device_AlgoVehCycle_VehDyn_Lateral_Curve_Curve"),
								"C1"   : ("VehDyn","ARS4xx_Device_AlgoVehCycle_VehDyn_Lateral_Curve_C1"),


						},
						{

								"C2": ("ARS4xx Device.AlgoVehCycle.VehDyn", "ARS4xx_Device_AlgoVehCycle_VehDyn_Lateral_Curve_Curve"),
								"C1": ("ARS4xx Device.AlgoVehCycle.VehDyn", "ARS4xx_Device_AlgoVehCycle_VehDyn_Lateral_Curve_C1"),

						},
				]
				group = self.get_source().selectSignalGroup(sgs)
				return group

		def fill(self, group):
				time = self.get_modules().fill('calc_common_time-flr25')
				rescale_kwargs = {'ScaleTime': time, 'Order': 'valid'}
				# line
				C0 = np.zeros_like(time)
				C1 = group.get_value('C1', **rescale_kwargs)
				C2 = group.get_value('C2', **rescale_kwargs)
				C3 = np.zeros_like(time)
				line = PolyClothoid.from_physical_coeffs(time,C0,C1,C2,C3)
				return line




if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"\\pu2w6168\shared-drive\measurements\flr25\2020-05-13\FCW__2020-05-13_05-39-39.mat"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		flr25_curvator_lanes = manager_modules.calc('calc_lanes_flr25_curvator@aebs.fill', manager)
		print flr25_curvator_lanes
