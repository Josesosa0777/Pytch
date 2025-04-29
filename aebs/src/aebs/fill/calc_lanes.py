# -*- dataeval: init -*-

import copy

import interface
from primitives.lane import LaneData, PolyClothoid, VideoLineProp

init_params = {
		'flc25': dict(
						common_time = "calc_common_time-flc25",
						sgs = [{
								"RefPoint_X"                 : (" Video_Lane_Left_A", "C0_Left_A"),  # TODO
								"RefPoint_Y"                 : (" Video_Lane_Right_A", "C0_Right_A"),  # TODO

								"Position_Left"              : (" Video_Lane_Left_A", "C0_Left_A"),
								"Position_Right"             : (" Video_Lane_Right_A", "C0_Right_A"),
								"Position_Left2"             : (" Video_Lane_Next_Left_A", "C0_Next_Left_A"),
								"Position_Right2"            : (" Video_Lane_Next_Right_A", "C0_Next_Right_A"),
								"Heading_Angle_Left"         : (" Video_Lane_Left_A", "C1_Left_A"),
								"Heading_Angle_Right"        : (" Video_Lane_Right_A", "C1_Right_A"),
								"Heading_Angle_Left2"        : (" Video_Lane_Next_Left_A", "C1_Next_Left_A"),
								"Heading_Angle_Right2"       : (" Video_Lane_Next_Right_A", "C1_Next_Right_A"),
								"Curvature_Left"             : (" Video_Lane_Left_A", "C2_Left_A"),
								"Curvature_Right"            : (" Video_Lane_Right_A", "C2_Right_A"),
								"Curvature_Left2"            : (" Video_Lane_Next_Left_A", "C2_Next_Left_A"),
								"Curvature_Right2"           : (" Video_Lane_Next_Right_A", "C2_Next_Right_A"),
								"Curvature_Derivative_Right2": (" Video_Lane_Next_Right_A", "C3_Next_Right_A"),
								"Curvature_Derivative_Left2" : (" Video_Lane_Next_Left_A", "C3_Next_Left_A"),
								"Curvature_Derivative_Right" : (" Video_Lane_Right_A", "C3_Right_A"),
								"Curvature_Derivative_Left"  : (" Video_Lane_Left_A", "C3_Left_A"),
								"View_Range_Left"            : (" Video_Lane_Left_B", "View_Range_Left_B"),
								"View_Range_Right"           : (" Video_Lane_Right_B", "View_Range_Right_B"),
								"View_Range_Left2"           : (" Video_Lane_Next_Left_B", "View_Range_Next_Left_B"),
								"View_Range_Right2"          : (" Video_Lane_Next_Right_B", "View_Range_Next_Right_B"),
						},
						{
								"RefPoint_X"                 : ("LaneInfo_LH_A", "C0"),  # TODO
								"RefPoint_Y"                 : ("LaneInfo_RH_A", "C0"),  # TODO
								
								"Position_Left"              : ("LaneInfo_LH_A", "C0"),
								"Position_Right"             : ("LaneInfo_RH_A", "C0"),
								"Position_Left2"             : ("LaneInfo_nextLH_A", "C0"),
								"Position_Right2"            : ("LaneInfo_nextRH_A", "C0"),
								"Heading_Angle_Left"         : ("LaneInfo_LH_A", "C1"),
								"Heading_Angle_Right"        : ("LaneInfo_RH_A", "C1"),
								"Heading_Angle_Left2"        : ("LaneInfo_nextLH_A", "C1"),
								"Heading_Angle_Right2"       : ("LaneInfo_nextRH_A", "C1"),
								"Curvature_Left"             : ("LaneInfo_LH_A", "C2"),
								"Curvature_Right"            : ("LaneInfo_RH_A", "C2"),
								"Curvature_Left2"            : ("LaneInfo_nextLH_A", "C2"),
								"Curvature_Right2"           : ("LaneInfo_nextRH_A", "C2"),
								"Curvature_Derivative_Right2": ("LaneInfo_nextRH_A", "C3"),
								"Curvature_Derivative_Left2" : ("LaneInfo_nextLH_A", "C3"),
								"Curvature_Derivative_Right" : ("LaneInfo_RH_A", "C3"),
								"Curvature_Derivative_Left"  : ("LaneInfo_LH_A", "C3"),
								"View_Range_Left"            : ("LaneInfo_LH_B", "Lane_View_Range"),
								"View_Range_Right"           : ("LaneInfo_RH_B", "Lane_View_Range"),
								"View_Range_Left2"           : ("LaneInfo_nextLH_B", "Lane_View_Range"),
								"View_Range_Right2"          : ("LaneInfo_nextRH_B", "Lane_View_Range"),
						}]
		),
}


class Flc25CanLine(PolyClothoid, VideoLineProp):
		def __init__(self, time, c0, c1, c2, c3, view_range):
				PolyClothoid.__init__(self, time, c0, c1, c2, c3)
				VideoLineProp.__init__(self, time, view_range, None, None)
				return

		@staticmethod
		def a0_to_c0(a0):
				return a0

		@staticmethod
		def a1_to_c1(a1):
				return a1

		@staticmethod
		def a2_to_c2(a2):
				return a2

		@staticmethod
		def a3_to_c3(a3):
				return a3

		@staticmethod
		def c0_to_a0(c0):
				return c0

		@staticmethod
		def c1_to_a1(c1):
				return c1

		@staticmethod
		def c2_to_a2(c2):
				return c2

		@staticmethod
		def c3_to_a3(c3):
				return c3

		def translate(self, dx, dy):
				newobj = copy.copy(self)
				newobj = PolyClothoid.translate(newobj, dx, dy)
				newobj = VideoLineProp.translate(newobj, dx, dy)
				return newobj


class Calc(interface.iCalc):
		dep = {
				'common_time': None
		}

		def init(self, sgs, common_time):
				self.sgs = sgs
				self.dep["common_time"] = common_time
				return

		def check(self):
				group = self.source.selectSignalGroup(self.sgs)
				return group

		def fill(self, group):
				time = self.get_modules().fill(self.dep["common_time"])
				rescale_kwargs = {'ScaleTime': time}
				# camera offset
				# dx0_raw = group.get_value('RefPoint_X', **rescale_kwargs)s
				import numpy as np
				dx0_raw = np.zeros(time.size)
				dy0_raw = np.zeros(time.size)
				# dx0_raw = group.get_value('RefPoint_X', **rescale_kwargs)
				# dy0_raw = group.get_value('RefPoint_Y', **rescale_kwargs)
				dx0, dy0 = convert_sensor_offset(dx0_raw, dy0_raw)
				# left line
				c0_raw = group.get_value('Position_Left', **rescale_kwargs)
				c1_raw = group.get_value('Heading_Angle_Left', **rescale_kwargs)
				c2_raw = group.get_value('Curvature_Left', **rescale_kwargs)
				c3_raw = group.get_value('Curvature_Derivative_Left', **rescale_kwargs)
				vr_raw = group.get_value('View_Range_Left', **rescale_kwargs)
				left_line = create_line(
								time, c0_raw, c1_raw, c2_raw, c3_raw, vr_raw, dx0, dy0, group.winner)
				# right line
				c0_raw = group.get_value('Position_Right', **rescale_kwargs)
				c1_raw = group.get_value('Heading_Angle_Right', **rescale_kwargs)
				c2_raw = group.get_value('Curvature_Right', **rescale_kwargs)
				c3_raw = group.get_value('Curvature_Derivative_Right', **rescale_kwargs)
				vr_raw = group.get_value('View_Range_Right', **rescale_kwargs)
				right_line = create_line(
								time, c0_raw, c1_raw, c2_raw, c3_raw, vr_raw, dx0, dy0, group.winner)
				# left left line
				c0_raw = group.get_value('Position_Left2', **rescale_kwargs)
				c1_raw = group.get_value('Heading_Angle_Left2', **rescale_kwargs)
				c2_raw = group.get_value('Curvature_Left2', **rescale_kwargs)
				c3_raw = group.get_value('Curvature_Derivative_Left2', **rescale_kwargs)
				vr_raw = group.get_value('View_Range_Left2', **rescale_kwargs)
				left_left_line = create_line(
								time, c0_raw, c1_raw, c2_raw, c3_raw, vr_raw, dx0, dy0, group.winner)
				# right right line
				c0_raw = group.get_value('Position_Right2', **rescale_kwargs)
				c1_raw = group.get_value('Heading_Angle_Right2', **rescale_kwargs)
				c2_raw = group.get_value('Curvature_Right2', **rescale_kwargs)
				c3_raw = group.get_value('Curvature_Derivative_Right2', **rescale_kwargs)
				vr_raw = group.get_value('View_Range_Right2', **rescale_kwargs)
				right_right_line = create_line(
								time, c0_raw, c1_raw, c2_raw, c3_raw, vr_raw, dx0, dy0, group.winner)
				# return value
				lines = LaneData(left_line, right_line, left_left_line, right_right_line)
				return lines


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
		line = Flc25CanLine.from_physical_coeffs(time, c0, c1, c2, c3, view_range)
		return line


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"C:\KBData\Data\Development\PythonToolchainSupport\ContiMeasurementsSuport\mfc525_interface\measurements\newmfc\NY00__2020-08-20_13-42-05.mat"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		flr25_egomotion = manager_modules.calc('calc_lanes-flc25@aebs.fill', manager)
		print flr25_egomotion
