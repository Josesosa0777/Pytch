# -*- dataeval: init -*-

"""
Plot basic driver activities and FCW outputs

FCW-relevant driver activities (pedal activation, steering etc.) and
FCW outputs (in AEBS1 messages) are shown.
"""

import numpy as np
from numpy import rad2deg
import datavis
from interface import iView
from measparser.signalproc import rescale
from measproc.IntervalList import maskToIntervals


mps2kph = lambda v: v*3.6
DETAIL_LEVEL = 1
class View(iView):
		dep = ('calc_radar_egomotion-flr25@aebs.fill',)
		def check(self):
				sgs = [
						{
								# driver
								"accped_pos": ("EEC2_00", "EEC2_APPos1_00"),
								"brkped_pos": ("EBC1_0B", "EBC1_BrkPedPos_0B"),
								"steer_angle": ("VDC2_0B", "VDC2_SteerWhlAngle_0B"),
								"dir_ind": ("OEL_21", "OEL_TurnSigSw_21"),
						}, {
								# driver
								"accped_pos": ("EEC2_00", "EEC2_APPos1_00"),
								"brkped_pos": ("EBC1_0B", "EBC1_BrkPedPos_0B"),
								"steer_angle": ("VDC2_0B", "VDC2_SteerWhlAngle_0B"),
								"dir_ind": ("OEL_21", "OEL_TurnSigSw_21"),
						},
						{  # AEBS Resim
								"accped_pos": ("EEC2_00_s00", "EEC2_APPos1_00"),
								"brkped_pos": ("EBC1_0B_s0B", "EBC1_BrkPedPos_0B"),
								"steer_angle": ("VDC2_0B_s0B", "VDC2_SteerWhlAngle_0B"),
								"turn_signal_right": ("Rte_SWC_AEBS_RPort_im_eb_driver_DEP_im_eb_driver_Buf",
								"ARS4xx_Device_SW_Every10ms_Rte_SWC_AEBS_RPort_im_eb_driver_DEP_im_eb_driver_Buf_turn_signal_right"),
								"turn_signal_left": ("Rte_SWC_AEBS_RPort_im_eb_driver_DEP_im_eb_driver_Buf",
								"ARS4xx_Device_SW_Every10ms_Rte_SWC_AEBS_RPort_im_eb_driver_DEP_im_eb_driver_Buf_turn_signal_left"),

						},
						{
								# driver
								"accped_pos": ("EEC2_00", "EEC2_APPos1_00"),
								"brkped_pos": ("EBC1_0B", "EBC1_BrkPedPos_0B"),
								"steer_angle": ("VDC2_0B", "VDC2_SteerWhlAngle_0B"),
								"dir_ind": ("OEL_E6", "OEL_TurnSigSw_E6"),  # SA 0xE6
						}, {
								# driver
								"accped_pos": ("EEC2_00", "EEC2_APPos1_00"),
								"brkped_pos": ("EBC1_0B", "EBC1_BrkPedPos_0B"),
								"steer_angle": ("VDC2_0B", "VDC2_SteerWhlAngle_0B"),
								"dir_ind": ("OEL_27", "OEL_TurnSigSw_27"),  # SA 0x27
						},
						{
								"accped_pos": ("EEC2_00", "EEC2_APPos1_00"),
								"brkped_pos": ("EBC1_0B", "EBC1_BrkPedPos_0B"),
								"steer_angle": ("VDC2_0B", "VDC2_SteerWhlAngle_0B"),
								"dir_ind": ("OEL_32", "OEL_TurnSigSw_32"),

						},
						# FCW
						{
								"accped_pos": ("EEC2_00_s00", "EEC2_APPos1_00_s00"),
								"brkped_pos": ("EBC1_0B_s0B", "EBC1_BrkPedPos_0B_s0B"),
								"brake_switch": ("EBC1_0B_s0B", "EBC1_EBSBrakeSwitch_0B"),
								"steer_angle": ("VDC2_0B_s0B", "VDC2_SteerWhlAngle_0B_s0B"),
								"dir_ind": ("OEL_32_s32", "OEL_TurnSigSw_32_s32"),

						},
						{
								"accped_pos": ("EEC2_00_s00", "EEC2_AccPedalPos1_00"),
								"brkped_pos": ("EBC1_0B_s0B", "EBC1_BrkPedPos_0B"),
								"brake_switch": ("EBC1_0B_s0B", "EBC1_EBSBrakeSwitch_0B"),
								"steer_angle": ("VDC2_0B_s0B", "VDC2_SteerWhlAngle_0B"),
								"dir_ind": ("Rte_SWC_Preprocessor_RPort_prep_norm_OEL_DEP_norm_prep_postp_OEL_Buf",
														"ARS4xx_Device_SW_Every10ms_Rte_SWC_Preprocessor_RPort_prep_norm_OEL_DEP_norm_prep_postp_OEL_Buf_OEL_TurnSigSw"),

						},
						{
								"accped_pos": ("EEC2_00_s00", "EEC2_AccPedalPos1_00"),
								"brkped_pos": ("EBC1_0B_s0B", "EBC1_BrkPedPos_0B"),
								"brake_switch": ("EBC1_0B_s0B", "EBC1_EBSBrakeSwitch_0B"),
								"steer_angle": ("VDC2_0B_s0B", "VDC2_SteerWhlAngle_0B"),
								"dir_ind": ("Rte_SWC_Preprocessor_RPort_prep_norm_OEL_DEP_norm_prep_postp_OEL_Buf",
														"ARS4xx_Device_SW_Every10ms_Rte_SWC_Preprocessor_RPort_prep_norm_OEL_DEP_norm_prep_postp_OEL_Buf_OEL_TurnSigSw"),
						},
						{
							"accped_pos": ("EEC2_00_s00_EEC2_00", "EEC2_AccPedalPos1_00"),
							"brkped_pos": ("EBC1_0B_s0B_EBC1_0B", "EBC1_BrkPedPos_0B"),
							"brake_switch": ("EBC1_0B_s0B_EBC1_0B", "EBC1_EBSBrakeSwitch_0B"),
							"steer_angle": ("VDC2_0B_s0B_VDC2_0B", "VDC2_SteerWhlAngle_0B"),
							"dir_ind": ("Rte_SWC_Preprocessor_RPort_prep_norm_OEL_DEP_norm_prep_postp_OEL_Buf",
										"ARS4xx_Device_SW_Every10ms_Rte_SWC_Preprocessor_RPort_prep_norm_OEL_DEP_norm_prep_postp_OEL_Buf_OEL_TurnSigSw"),
						},
						{
								"accped_pos": ("EEC2_s00", "AccelPedalPos1"),
								"brkped_pos": ("EBC1_0B_s0B", "BrakePedalPosition"),
								"brake_switch": ("EBC1_0B_s0B", "EBC1_EBSBrakeSwitch_0B"),
								"steer_angle": ("VDC2_0B_s0B", "SteeringWheelAngle"),
								"dir_ind": ("OEL_s32", "TurnSignalSwitch"),
						},
						{
								"accped_pos"  : ("EEC2_00","EEC2_APPos1_00"),
								"brkped_pos"  : ("EBC1_0B","EBC1_BrkPedPos_0B"),
								"brake_switch": ("EBC1_0B","EBC1_EBSBrkSw_0B"),
								"steer_angle" : ("VDC2_0B","VDC2_SteerWhlAngle_0B_s0B"),
								"dir_ind"     : ("OEL_32","OEL_TurnSigSw_32_s32"),

						},
					{
						"accped_pos": ("CAN_Vehicle_EEC2_00", "EEC2_AccPedalPos1_00"),
						"brkped_pos": ("CAN_Vehicle_EBC1_0B", "EBC1_BrkPedPos_0B"),
						"brake_switch": ("CAN_Vehicle_EBC1_0B", "EBC1_EBSBrakeSwitch_0B"),
						"steer_angle": ("CAN_Vehicle_VDC2", "SteerWheelAngle"),
						"dir_ind": ("CAN_MFC_Public_OEL_32", "OEL_TurnSignalSwitch_32"),
					}
				]
				# select signals
				group = self.source.selectLazySignalGroup(sgs)
				# give warning for not available signals
				for alias in sgs[0]:
						if alias not in group:
								self.logger.warning("Signal for '%s' not available" % alias)
				# process signals
				ego = self.modules.fill(self.dep[0])

				return group, ego

		def view(self, group, ego):
				"""

				:param commonTime:
				:param signals: Rescaled signals
								"acc_pedal_pos"
								"vehicle_speed"
								"obj_speed"
								"ego_long_state"
								"aps_system_state"
								"acc_active"
								"aps_object_id"
								"eba_quality"
								"ped_confidence"
				:return:
				"""
				t = ego.time
				pn = datavis.cPlotNavigator(title="Ego vehicle and Driver activities")
				########################################## Ego vehicle ###################################################
				# speed
				ax = pn.addAxis(ylabel='speed', ylim=(-5.0, 100.0))
				pn.addSignal2Axis(ax, 'ego speed', t, mps2kph(ego.vx), unit='km/h')
				self.extend_speed_axis(pn, ax)

				# acceleration
				ax = pn.addAxis(ylabel='accel.conti', ylim=(-10.0, 10.0))
				pn.addSignal2Axis(ax, 'ego acceleration', t, ego.ax, unit='m/s^2')
				self.extend_accel_axis(pn, ax)

				# yaw rate
				if DETAIL_LEVEL > 0:
						ax = pn.addAxis(ylabel="yaw rate", ylim=(-12.0, 12.0))
						pn.addSignal2Axis(ax, "yaw rate", t, rad2deg(ego.yaw_rate), unit="deg/s")
				########################################## Driver Activities ###################################################

				ax = pn.addAxis(ylabel="pos.", ylim=(-5.0, 105.0))
				# accel. pedal
				if 'accped_pos' in group:
						time00, value00, unit00 = group.get_signal_with_unit("accped_pos")
						pn.addSignal2Axis(ax, "accel. p. pos.", time00, value00, unit=unit00)
				# brake pedal
				if 'brkped_pos' in group:
						time02, value02, unit02 = group.get_signal_with_unit("brkped_pos")
						pn.addSignal2Axis(ax, "brake p. pos.", time02, value02, unit=unit02)
				# brake switch
				if 'brake_switch' in group:
						time02, value02, unit02 = group.get_signal_with_unit("brake_switch")
						ax = pn.addTwinAxis(ax, ylabel='brake switch', color='g')
						pn.addSignal2Axis(ax, "brake switch", time02, value02, unit=unit02)

				# steering wheel
				ax = pn.addAxis(ylabel="angle", ylim=(-100.0, 100.0))
				if 'steer_angle' in group:
						time04, value04, unit04 = group.get_signal_with_unit("steer_angle")
						if unit04 == "rad" or not unit04:  # assuming rad if unit is empty
								value04 = np.rad2deg(value04)
								unit04 = "deg"
						pn.addSignal2Axis(ax, "steering wheel angle", time04, value04, unit=unit04)
				# direction indicator
				yticks = {0: "none", 1: "left", 2: "right", 3: "n/a"}
				yticks = dict((k, "%d (%s)" % (k, v)) for k, v in yticks.iteritems())
				ax = pn.addTwinAxis(ax, ylabel="state", ylim=(-1.0, 4.0), yticks=yticks, color='g')
				if 'turn_signal_right' and 'turn_signal_left' in group:
						time05, value05, unit05 = group.get_signal_with_unit("turn_signal_right")
						time06, value06, unit06 = group.get_signal_with_unit("turn_signal_left")
						dir_ind = np.zeros(time05.shape, dtype=float)
						right_turn_interval_list = maskToIntervals(value05==1)
						for interval in right_turn_interval_list:
								dir_ind[interval[0]:interval[1]] = 2
						left_turn_interval_list = maskToIntervals(value06==1)
						for interval in left_turn_interval_list:
								dir_ind[interval[0]:interval[1]] = 1
						pn.addSignal2Axis(ax, "dir. indicator", time05, dir_ind, unit=unit05)
				if 'dir_ind' in group:
						time07, value07, unit07 = group.get_signal_with_unit("dir_ind")
						pn.addSignal2Axis(ax, "dir. indicator", time07, value07, unit=unit07)

				self.sync.addClient(pn)
				return


		def extend_speed_axis(self, pn, ax):
				return

		def extend_accel_axis(self, pn, ax):
				return

