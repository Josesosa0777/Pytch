# -*- dataeval: init -*-

import numpy as np

import interface
from aebs.fill.calc_lanes import create_line
from primitives.lane import LaneData, PolyClothoid
from aebs.fill import calc_radar_egomotion


class Calc(interface.iCalc):
		dep = ('calc_common_time-flc25',)

		def check(self):
				sgs = [
						{

								"C1": ("MTSI_stKBFreeze_020ms_t",
											"MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsInput_vehicle_input_ego_lat_pred_ego_curvature_angle"),
								"C2": ("MTSI_stKBFreeze_020ms_t",
											"MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsInput_vehicle_input_ego_lat_pred_ego_curvature"),
								"C3": ("MTSI_stKBFreeze_020ms_t",
											 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsInput_vehicle_input_ego_lat_pred_ego_curvature_change"),

						},
						{

								"C1": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
											 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsInput_vehicle_input_ego_lat_pred_ego_curvature_angle"),
								"C2": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
											 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsInput_vehicle_input_ego_lat_pred_ego_curvature"),
								"C3": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
											 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsInput_vehicle_input_ego_lat_pred_ego_curvature_change"),

						},
						{

								"C3": ("MTSI_stKBFreeze_040ms_t",
											 "MFC5xx_Device_KB_MTSI_stKBFreeze_040ms_t_sFlc25_PaebsInput_vehicle_input_ego_lat_pred_ego_curvature_change"),
								"C1": ("MTSI_stKBFreeze_040ms_t",
											 "MFC5xx_Device_KB_MTSI_stKBFreeze_040ms_t_sFlc25_PaebsInput_vehicle_input_ego_lat_pred_ego_curvature_angle"),
								"C2": ("MTSI_stKBFreeze_040ms_t",
											 "MFC5xx_Device_KB_MTSI_stKBFreeze_040ms_t_sFlc25_PaebsInput_vehicle_input_ego_lat_pred_ego_curvature"),

						},
						{

								"C3": ("MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t",
											 "MFC5xx_Device_KB_MTSI_stKBFreeze_040ms_t_sFlc25_PaebsInput_vehicle_input_ego_lat_pred_ego_curvature_change"),
								"C1": ("MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t",
											 "MFC5xx_Device_KB_MTSI_stKBFreeze_040ms_t_sFlc25_PaebsInput_vehicle_input_ego_lat_pred_ego_curvature_angle"),
								"C2": ("MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t",
											 "MFC5xx_Device_KB_MTSI_stKBFreeze_040ms_t_sFlc25_PaebsInput_vehicle_input_ego_lat_pred_ego_curvature"),

						},

				]
				group = self.get_source().selectSignalGroup(sgs)
				return group

		def fill(self, group):
				time = self.get_modules().fill('calc_common_time-flc25')
				rescale_kwargs = {'ScaleTime': time, 'Order': 'valid'}
				# line
				C0 = np.zeros_like(time)
				C1 = group.get_value('C1', **rescale_kwargs)
				C2 = group.get_value('C2', **rescale_kwargs)
				C3 = group.get_value('C3', **rescale_kwargs)
				line = PolyClothoid.from_physical_coeffs(time, C0, C1, C2, C3)
				return line



if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"\\pu2w6168\shared-drive\measurements\pAEBS\new_requirment\AOA\HMC-QZ-STR__2021-02-16_09-40-07.mat"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		flr25_curvator_lanes = manager_modules.calc('calc_lanes_flc25_paebs_ego_path_prediction@aebs.fill', manager)
		print flr25_curvator_lanes
