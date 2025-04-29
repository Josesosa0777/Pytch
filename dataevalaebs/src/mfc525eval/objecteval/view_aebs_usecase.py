# -*- dataeval: init -*-

import numpy as np

import datavis
from interface import iView


class View(iView):
		def check(self):
				sgs  = [
						{
						# relevant AEBS object
						"AEBS_ttc": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t", "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_EbOutput_hmi_output_aebs_ttc"),
						"AEBS_obj_Dist_X": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t", "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_aebs_object_dx"),
						"AEBS_obj_Dist_Y": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t", "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_aebs_object_dy"),
						"AEBS_obj_ID": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t", "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_aebs_object_id"),
						"AEBS_vrel_y": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t", "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_aebs_object_vy_rel"),
						# AEBS-Function
						"AEBS_State": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t", "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_EbOutput_hmi_output_aebs_system_state"),
						"CollWarnLvl": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t", "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_EbOutput_hmi_output_aebs_warning_level"),
						"Ego_vel": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t", "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_vehicle_brake_system_front_axle_speed"),
						},
					]
				# select signals
				group = self.source.selectLazySignalGroup(sgs)
				# give warning for not available signals
				for alias in sgs[0]:
						if alias not in group:
								self.logger.warning("Signal for '%s' not available" % alias)
				return group

		def view(self, group):
				pn = datavis.cPlotNavigator(title="AEBS_usecase_eval")

				ax = pn.addAxis(ylabel="ID", ylim=(0, 110.0))
				if 'AEBS_obj_ID' in group:
						time_AEBS_obj_ID, value_AEBS_obj_ID, unit_AEBS_obj_ID = group.get_signal_with_unit("AEBS_obj_ID") #could add multiplic here
						pn.addSignal2Axis(ax, "AEBS_obj_ID", time_AEBS_obj_ID, value_AEBS_obj_ID, unit=unit_AEBS_obj_ID)

				ax = pn.addAxis(ylabel="State")
				if 'AEBS_State' in group:
						time00, value00, unit00 = group.get_signal_with_unit("AEBS_State")
						pn.addSignal2Axis(ax, "AEBS_State", time00, value00, unit=unit00)

				ax = pn.addAxis(ylabel="Level")
				if 'CollWarnLvl' in group:
						time00, value00, unit00 = group.get_signal_with_unit("CollWarnLvl")
						pn.addSignal2Axis(ax, "CollWarnLvl", time00, value00, unit=unit00)
				
				ax = pn.addAxis(ylabel="Vel")
				if 'Ego_vel' in group:
						time00, value00, unit00 = group.get_signal_with_unit("Ego_vel")
						pn.addSignal2Axis(ax, "Ego_vel", time00, value00, unit=unit00)

				ax = pn.addAxis(ylabel="Dist", ylim=(0, 120))
				if 'AEBS_obj_Dist_X' in group:
						time00, value00, unit00 = group.get_signal_with_unit("AEBS_obj_Dist_X")
						pn.addSignal2Axis(ax, "AEBS_obj_Dist_X", time00, value00, unit=unit00)		

				ax = pn.addAxis(ylabel="Pos",ylim=(-3, 3))
				if 'AEBS_vrel_y' in group and "AEBS_obj_Dist_Y" in group and "AEBS_ttc" in group:
						time_AEBS_vrel_y, value_AEBS_vrel_y, unit_AEBS_vrel_y = group.get_signal_with_unit("AEBS_vrel_y")
						rescale_kwargs = {'ScaleTime': time_AEBS_vrel_y}
						time_AEBS_ttc, value_AEBS_ttc, unit_AEBS_ttc = group.get_signal_with_unit("AEBS_ttc", **rescale_kwargs)
						time_AEBS_obj_Dist_Y, value_AEBS_obj_Dist_Y, unit_AEBS_obj_Dist_Y = group.get_signal_with_unit("AEBS_obj_Dist_Y", **rescale_kwargs)
						value_est_lat_pos = value_AEBS_obj_Dist_Y + value_AEBS_vrel_y* value_AEBS_ttc
						pn.addSignal2Axis(ax, "AEBS_EST_LAT_POS_AT_CRASHPOINT", time_AEBS_vrel_y, value_est_lat_pos, unit=unit_AEBS_obj_Dist_Y)		
						value_est_lat_pos_max = 1.5
						value_est_lat_pos_min = -1.5
						ax.fill_between(time_AEBS_obj_Dist_Y, value_est_lat_pos_max, value_est_lat_pos_min, color="green", alpha="0.3")    

				self.sync.addClient(pn)
				return

		#def extend_aebs_state_axis(self, pn, ax):
		#		return
