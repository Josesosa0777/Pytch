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

								"C0"      : ("FCUArsRoad", "MFC5xx_Device_FCU_FCUArsRoad_roadEstimation_fC0"),
								"C1"      : ("FCUArsRoad", "MFC5xx_Device_FCU_FCUArsRoad_roadEstimation_fC1"),
								"C2"      : ("FCUArsRoad", "MFC5xx_Device_FCU_FCUArsRoad_roadEstimation_fYawAngle"),


						},
						{

								"C0": ("MFC5xx Device.FCU.FCUArsRoad", "MFC5xx_Device_FCU_FCUArsRoad_roadEstimation_fC0"),
								"C1": ("MFC5xx Device.FCU.FCUArsRoad", "MFC5xx_Device_FCU_FCUArsRoad_roadEstimation_fC1"),
								"C2": ("MFC5xx Device.FCU.FCUArsRoad", "MFC5xx_Device_FCU_FCUArsRoad_roadEstimation_fYawAngle"),

						},
				]
				group = self.get_source().selectSignalGroup(sgs)
				return group

		def fill(self, group):
				time = self.get_modules().fill('calc_common_time-flr25')
				rescale_kwargs = {'ScaleTime': time, 'Order': 'valid'}
				# line
				C0 = group.get_value('C0', **rescale_kwargs)
				C1 = group.get_value('C1', **rescale_kwargs)
				C2 = group.get_value('C2', **rescale_kwargs)
				C3 = np.zeros_like(time)
				line = PolyClothoid.from_physical_coeffs(time, C0,C1,C2,C3)
				return line


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"\\pu2w6168\shared-drive\measurements\cmp_trw_tpf\HMC-QZ-STR__2020-11-19_14-16-50.mat"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		flr25_curvator_lanes = manager_modules.calc('calc_lanes_flr25_roadestimation@aebs.fill', manager)
		print flr25_curvator_lanes
