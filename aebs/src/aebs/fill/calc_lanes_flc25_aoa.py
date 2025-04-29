# -*- dataeval: init -*-

import copy
import logging

import interface
from primitives.lane import LaneData, PolyClothoid, VideoLineProp
from pyutils.cache_manager import get_modules_cache, store_modules_cache

logger = logging.getLogger('calc_lanes_flc25_aoa')
signal_group = [
		{
				"ego_centerline_view_range"         : ("MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_ego_centerline_view_range"),
				"ego_centerline_c0"                 : ("MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_ego_centerline_c0"),
				"ego_centerline_c1"                 : ("MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_ego_centerline_c1"),
				"ego_centerline_c2"                 : ("MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_ego_centerline_c2"),
				"ego_centerline_c3"                 : ("MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_ego_centerline_c3"),

				"left_centerline_view_range"        : ("MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_centerline_view_range"),
				"left_centerline_c0"                : ("MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_centerline_c0"),
				"left_centerline_c1"                : ("MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_centerline_c1"),
				"left_centerline_c2"                : ("MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_centerline_c2"),
				"left_centerline_c3"                : ("MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_centerline_c3"),

				"right_centerline_view_range"       : ("MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_centerline_view_range"),
				"right_centerline_c0"               : ("MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_centerline_c0"),
				"right_centerline_c1"               : ("MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_centerline_c1"),
				"right_centerline_c2"               : ("MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_centerline_c2"),
				"right_centerline_c3"               : ("MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_centerline_c3"),

				"left_lane_marking_view_range"      : ("MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_view_range"),
				"left_lane_marking_c0"              : ("MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_c0"),
				"left_lane_marking_c1"              : ("MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_c1"),
				"left_lane_marking_c3"              : ("MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_c3"),
				"left_lane_marking_c2"              : ("MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_c2"),

				"right_lane_marking_view_range"     : ("MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_view_range"),
				"right_lane_marking_c0"             : ("MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_c0"),
				"right_lane_marking_c1"             : ("MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_c1"),
				"right_lane_marking_c2"             : ("MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_c2"),
				"right_lane_marking_c3"             : ("MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_c3"),

				"next_left_lane_marking_view_range" : ("MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_next_left_lane_marking_view_range"),
				"next_left_lane_marking_c0"         : ("MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_next_left_lane_marking_c0"),
				"next_left_lane_marking_c1"         : ("MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_next_left_lane_marking_c1"),
				"next_left_lane_marking_c2"         : ("MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_next_left_lane_marking_c2"),
				"next_left_lane_marking_c3"         : ("MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_next_left_lane_marking_c3"),

				"next_right_lane_marking_view_range": ("MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_next_right_lane_marking_view_range"),
				"next_right_lane_marking_c0"        : ("MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_next_right_lane_marking_c0"),
				"next_right_lane_marking_c1"        : ("MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_next_right_lane_marking_c1"),
				"next_right_lane_marking_c2"        : ("MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_next_right_lane_marking_c2"),
				"next_right_lane_marking_c3"        : ("MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_next_right_lane_marking_c3"),

		},
		{
				"ego_centerline_view_range"         : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_ego_centerline_view_range"),
				"ego_centerline_c0"                 : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_ego_centerline_c0"),
				"ego_centerline_c1"                 : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_ego_centerline_c1"),
				"ego_centerline_c2"                 : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_ego_centerline_c2"),
				"ego_centerline_c3"                 : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_ego_centerline_c3"),

				"left_centerline_view_range"        : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_centerline_view_range"),
				"left_centerline_c0"                : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_centerline_c0"),
				"left_centerline_c1"                : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_centerline_c1"),
				"left_centerline_c2"                : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_centerline_c2"),
				"left_centerline_c3"                : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_centerline_c3"),

				"right_centerline_view_range"       : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_centerline_view_range"),
				"right_centerline_c0"               : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_centerline_c0"),
				"right_centerline_c1"               : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_centerline_c1"),
				"right_centerline_c2"               : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_centerline_c2"),
				"right_centerline_c3"               : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_centerline_c3"),

				"left_lane_marking_view_range"      : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_view_range"),
				"left_lane_marking_c0"              : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_c0"),
				"left_lane_marking_c1"              : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_c1"),
				"left_lane_marking_c3"              : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_c3"),
				"left_lane_marking_c2"              : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_c2"),

				"right_lane_marking_view_range"     : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_view_range"),
				"right_lane_marking_c0"             : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_c0"),
				"right_lane_marking_c1"             : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_c1"),
				"right_lane_marking_c2"             : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_c2"),
				"right_lane_marking_c3"             : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_c3"),

				"next_left_lane_marking_view_range" : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_next_left_lane_marking_view_range"),
				"next_left_lane_marking_c0"         : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_next_left_lane_marking_c0"),
				"next_left_lane_marking_c1"         : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_next_left_lane_marking_c1"),
				"next_left_lane_marking_c2"         : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_next_left_lane_marking_c2"),
				"next_left_lane_marking_c3"         : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_next_left_lane_marking_c3"),

				"next_right_lane_marking_view_range": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_next_right_lane_marking_view_range"),
				"next_right_lane_marking_c0"        : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_next_right_lane_marking_c0"),
				"next_right_lane_marking_c1"        : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_next_right_lane_marking_c1"),
				"next_right_lane_marking_c2"        : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_next_right_lane_marking_c2"),
				"next_right_lane_marking_c3"        : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
																							 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_next_right_lane_marking_c3"),

		}
]


def convert_sensor_offset(refpoint_x, refpoint_y):
		dx0 = -refpoint_x
		dy0 = refpoint_y
		return dx0, dy0


def convert_coeffs(offset, heading, curvature, curvature_rate):
		c0 = -offset
		c1 = -heading
		c2 = -curvature
		c3 = -curvature_rate
		return c0, c1, c2, c3


def convert_view_range(view_range):
		return view_range


def create_line(time, c0, c1, c2, c3, view_range, dx0, dy0, winner):
		view_range = convert_view_range(view_range)
		line = Flc25AoaLine.from_physical_coeffs(time, c0, c1, c2, c3, view_range)
		return line


class Flc25AoaLine(PolyClothoid, VideoLineProp):
		def __init__(self, time, c0, c1, c2, c3, view_range):
				PolyClothoid.__init__(self, time, c0, c1, c2, c3)
				VideoLineProp.__init__(self, time, view_range, None, None)
				return

		def translate(self, dx, dy):
				newobj = copy.copy(self)
				newobj = PolyClothoid.translate(newobj, dx, dy)
				newobj = VideoLineProp.translate(newobj, dx, dy)
				return newobj


class Calc(interface.iCalc):
		dep = ('calc_common_time-flc25')

		def check(self):
				source = self.get_source()
				group = source.selectSignalGroup(signal_group)
				return group

		def fill(self, group):
				import time
				start = time.time()

				common_time = self.get_modules().fill('calc_common_time-flc25')

				# polynominal

				import numpy as np
				dx0_raw = np.zeros(common_time.size)
				dy0_raw = np.zeros(common_time.size)
				# dx0_raw = group.get_value('RefPoint_X', ScaleTime = common_time)
				# dy0_raw = group.get_value('RefPoint_Y', ScaleTime = common_time)
				dx0, dy0 = convert_sensor_offset(dx0_raw, dy0_raw)
				# ego centerline
				c0_raw = group.get_value('ego_centerline_c0', ScaleTime = common_time)
				c1_raw = group.get_value('ego_centerline_c1', ScaleTime = common_time)
				c2_raw = group.get_value('ego_centerline_c2', ScaleTime = common_time)
				c3_raw = group.get_value('ego_centerline_c3', ScaleTime = common_time)
				vr_raw = group.get_value('ego_centerline_view_range', ScaleTime = common_time)
				ego_centerline = create_line(
								common_time, c0_raw, c1_raw, c2_raw, c3_raw, vr_raw, dx0, dy0, group.winner)
				# left centerline
				c0_raw = group.get_value('left_centerline_c0', ScaleTime = common_time)
				c1_raw = group.get_value('left_centerline_c1', ScaleTime = common_time)
				c2_raw = group.get_value('left_centerline_c2', ScaleTime = common_time)
				c3_raw = group.get_value('left_centerline_c3', ScaleTime = common_time)
				vr_raw = group.get_value('left_centerline_view_range', ScaleTime = common_time)
				left_centerline = create_line(
								common_time, c0_raw, c1_raw, c2_raw, c3_raw, vr_raw, dx0, dy0, group.winner)
				# right centerlline
				c0_raw = group.get_value('right_centerline_c0', ScaleTime = common_time)
				c1_raw = group.get_value('right_centerline_c1', ScaleTime = common_time)
				c2_raw = group.get_value('right_centerline_c2', ScaleTime = common_time)
				c3_raw = group.get_value('right_centerline_c3', ScaleTime = common_time)
				vr_raw = group.get_value('right_centerline_view_range', ScaleTime = common_time)
				right_centerlline = create_line(
								common_time, c0_raw, c1_raw, c2_raw, c3_raw, vr_raw, dx0, dy0, group.winner)

				# left lanemarking
				c0_raw = group.get_value('left_lane_marking_c0', ScaleTime = common_time)
				c1_raw = group.get_value('left_lane_marking_c1', ScaleTime = common_time)
				c2_raw = group.get_value('left_lane_marking_c2', ScaleTime = common_time)
				c3_raw = group.get_value('left_lane_marking_c3', ScaleTime = common_time)
				vr_raw = group.get_value('left_lane_marking_view_range', ScaleTime = common_time)
				left_lanemarking = create_line(
								common_time, c0_raw, c1_raw, c2_raw, c3_raw, vr_raw, dx0, dy0, group.winner)

				# right lanemarking
				c0_raw = group.get_value('right_lane_marking_c0', ScaleTime = common_time)
				c1_raw = group.get_value('right_lane_marking_c1', ScaleTime = common_time)
				c2_raw = group.get_value('right_lane_marking_c2', ScaleTime = common_time)
				c3_raw = group.get_value('right_lane_marking_c3', ScaleTime = common_time)
				vr_raw = group.get_value('right_lane_marking_view_range', ScaleTime = common_time)
				right_lanemarking = create_line(
								common_time, c0_raw, c1_raw, c2_raw, c3_raw, vr_raw, dx0, dy0, group.winner)

				# next left lanemarking
				c0_raw = group.get_value('next_left_lane_marking_c0', ScaleTime = common_time)
				c1_raw = group.get_value('next_left_lane_marking_c1', ScaleTime = common_time)
				c2_raw = group.get_value('next_left_lane_marking_c2', ScaleTime = common_time)
				c3_raw = group.get_value('next_left_lane_marking_c3', ScaleTime = common_time)
				vr_raw = group.get_value('next_left_lane_marking_view_range', ScaleTime = common_time)
				next_left_lanemarking = create_line(
								common_time, c0_raw, c1_raw, c2_raw, c3_raw, vr_raw, dx0, dy0, group.winner)

				# next right lanemarking
				c0_raw = group.get_value('next_right_lane_marking_c0', ScaleTime = common_time)
				c1_raw = group.get_value('next_right_lane_marking_c1', ScaleTime = common_time)
				c2_raw = group.get_value('next_right_lane_marking_c2', ScaleTime = common_time)
				c3_raw = group.get_value('next_right_lane_marking_c3', ScaleTime = common_time)
				vr_raw = group.get_value('next_right_lane_marking_view_range', ScaleTime = common_time)
				next_right_lanemarking = create_line(
								common_time, c0_raw, c1_raw, c2_raw, c3_raw, vr_raw, dx0, dy0, group.winner)

				# return value
				# lines = LaneData(left_lanemarking, right_lanemarking,next_left_lanemarking,next_right_lanemarking)
				lines=[]
				lines.append(ego_centerline)
				lines.append(left_centerline)
				lines.append(right_centerlline)
				lines.append(left_lanemarking)
				lines.append(right_lanemarking)
				lines.append(next_left_lanemarking)
				lines.append(next_right_lanemarking)

				done = time.time()
				elapsed = done - start
				logger.info("AOA Lanes loaded in " + str(elapsed))
				return lines , common_time


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"\\pu2w6168\shared-drive\measurements\pAEBS\new_requirment\AOA\HMC-QZ-STR__2021-02-16_09-40-07.mat"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		flc25_lanes ,time= manager_modules.calc('calc_lanes_flc25_aoa@aebs.fill', manager)
		print flc25_lanes
