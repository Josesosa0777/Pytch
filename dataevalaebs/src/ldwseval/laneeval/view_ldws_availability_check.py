# -*- dataeval: init -*-

import numpy as np

import datavis
from interface import iView
from pyutils.enum import enum


LDWSState = enum(
    NOT_READY=0,
    TEMP_NOT_AVAILABLE=1,
    DEACTIVATED=2,
    READY_NO_WARNING_ACTIVE=3,
    SUPPRESSED_WARNING=4,
	LANE_DEPARTURE_WARNING = 5,
	ERROR = 14,
	NOT_AVAILABLE = 15
)

def as_yticks(myenum):
    return {v: '%s(%d)' % (k, v) for k, v in myenum._asdict().iteritems()}

class View(iView):
		def check(self):
				sgs = [
							{
								"ldws_state": ("FLI2_E8", "FLI2_LDWSState_E8_sE8"),
								"front_axle_speed": ("EBC2_0B", "EBC2_FrontAxleSpeed_0B_s0B"),
								"Left_lane_quality": ("FLI3_E8", "FLI3_LaneMarkQualityLeft_E8_sE8"),
								"Right_lane_quality": ("FLI3_E8", "FLI3_LaneMarkQualityRight_E8_sE8"),
								"left_lane_marking_id": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
										"MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_id"),
								"right_lane_marking_id": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
										  "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_id"),

								"nxt_left_lane_marking_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_next_left_lane_marking_quality"),
								"nxt_right_lane_marking_quality": (	"MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",	"MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_next_right_lane_marking_quality"),

								"nxt_left_lane_marking_id": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_next_left_lane_marking_id"),
								"nxt_right_lane_marking_id": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_next_right_lane_marking_id"),

							},
					{
						"ldws_state": ("FLI2_E8", "FLI2_LDWSState_E8_sE8"),
						"front_axle_speed": ("EBC2_0B", "EBC2_FrontAxleSpeed_0B_s0B"),
						"Left_lane_quality":("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
											 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_OmLatControlMessages_FLI3_lane_mark_quality_on_the_left_side"),
						"Right_lane_quality":("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
											  "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_OmLatControlMessages_FLI3_lane_mark_quality_on_the_right_side"),
						"left_lane_marking_id": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
												 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_id"),
						"right_lane_marking_id": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
												  "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_id"),

						"nxt_left_lane_marking_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
														  "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_next_left_lane_marking_quality"),
						"nxt_right_lane_marking_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
														   "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_next_right_lane_marking_quality"),

						"nxt_left_lane_marking_id": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
													 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_next_left_lane_marking_id"),
						"nxt_right_lane_marking_id": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
													  "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_next_right_lane_marking_id"),

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
				pn = datavis.cPlotNavigator(title="LDWS Availability Check")

				ax = pn.addAxis(ylabel="LDWS State", ylim=(0.0, 10.0), yticks=as_yticks(LDWSState))
				# EBC2 speed
				if 'ldws_state' in group:
						time00, value00, unit00 = group.get_signal_with_unit("ldws_state")
						pn.addSignal2Axis(ax, "ldws_state", time00, value00, unit=unit00)

				ax = pn.addAxis(ylabel="Front Axle Speed", ylim=(-5.0, 105.0))

				if 'front_axle_speed' in group:
						time00, value00, unit00 = group.get_signal_with_unit("front_axle_speed")
						pn.addSignal2Axis(ax, "front_axle_speed", time00, value00, unit=unit00)

				ax = pn.addAxis(ylabel="Lane Quality", ylim=(-1.0, 4.0))
				if 'Left_lane_quality' in group:
						time00, value00, unit00 = group.get_signal_with_unit("Left_lane_quality")
						pn.addSignal2Axis(ax, "LaneMarkQualityLeft", time00, value00, unit=unit00)

				if 'Right_lane_quality' in group:
						time00, value00, unit00 = group.get_signal_with_unit("Right_lane_quality")
						pn.addSignal2Axis(ax, "LaneMarkQualityRight", time00, value00, unit=unit00)

				if 'nxt_left_lane_marking_quality' in group:
						time00, value00, unit00 = group.get_signal_with_unit("nxt_left_lane_marking_quality")
						pn.addSignal2Axis(ax, "NxtLaneMarkQualityLeft", time00, value00, unit=unit00)

				if 'nxt_right_lane_marking_quality' in group:
						time00, value00, unit00 = group.get_signal_with_unit("nxt_right_lane_marking_quality")
						pn.addSignal2Axis(ax, "NxtLaneMarkQualityRight", time00, value00, unit=unit00)


				ax = pn.addAxis(ylabel="Left Lane Marking ID")
				if 'left_lane_marking_id' in group:
					time00, value00, unit00 = group.get_signal_with_unit("left_lane_marking_id")
					pn.addSignal2Axis(ax, "LeftLaneMarkingID", time00, value00, unit=unit00)

				if 'nxt_left_lane_marking_id' in group:
					time00, value00, unit00 = group.get_signal_with_unit("nxt_left_lane_marking_id")
					pn.addSignal2Axis(ax, "Nxt_left_lane_marking_id", time00, value00, unit=unit00)

				ax = pn.addAxis(ylabel="Right Lane Marking ID")
				if 'right_lane_marking_id' in group:
					time00, value00, unit00 = group.get_signal_with_unit("right_lane_marking_id")
					pn.addSignal2Axis(ax, "RightLaneMarkingID", time00, value00, unit=unit00)

				if 'nxt_right_lane_marking_id' in group:
					time00, value00, unit00 = group.get_signal_with_unit("nxt_right_lane_marking_id")
					pn.addSignal2Axis(ax, "Nxt_right_lane_marking_id", time00, value00, unit=unit00)
				
				self.sync.addClient(pn)
				return

		def extend_aebs_state_axis(self, pn, ax):
				return
