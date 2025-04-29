# -*- dataeval: init -*-

import copy
import logging
import interface
import numpy as np
from primitives.lane import LaneData, PolyClothoid, VideoLineProp
from pyutils.cache_manager import get_modules_cache, store_modules_cache

logger = logging.getLogger('calc_lanes_flc25_abd')
signal_group = [
		{
				"aiLaneBoundariesLeft" : ("ABDLaneData", "MFC5xx_Device_LD_ABDLaneData_sLaneInformation_aiLaneBoundariesLeft"),
				"aiLaneBoundariesRight": ("ABDLaneData",
																	"MFC5xx_Device_LD_ABDLaneData_sLaneInformation_aiLaneBoundariesRight"),
		},
		{
				"aiLaneBoundariesLeft" : (
				"MFC5xx Device.LD.ABDLaneData", "MFC5xx_Device_LD_ABDLaneData_sLaneInformation_aiLaneBoundariesLeft"),
				"aiLaneBoundariesRight": ("MFC5xx Device.LD.ABDLaneData",
																	"MFC5xx_Device_LD_ABDLaneData_sLaneInformation_aiLaneBoundariesRight"),
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
		line = Flc25AbdLine.from_physical_coeffs(time, c0, c1, c2, c3, view_range)
		return line


class Flc25AbdLine(PolyClothoid, VideoLineProp):
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
		dep = ('calc_common_time-flc25', 'fill_lanes_flc25_abd')

		def check(self):
				source = self.get_source()
				group = source.selectSignalGroup(signal_group)
				return group

		def fill(self, group):
				import time
				start = time.time()
				cached_data = get_modules_cache(self.source, "calc_lanes_flc25_abd@aebs.fill")
				if cached_data is None:
						common_time = self.get_modules().fill('calc_common_time-flc25')
						asLaneBoundaryObjects = self.get_modules().fill('fill_lanes_flc25_abd')
						rescale_kwargs = {'ScaleTime': common_time}

						aiLaneBoundariesLeft_0 = np.full(len(common_time),
																						 group.get_value('aiLaneBoundariesLeft', ScaleTime = common_time)[0][0],
																						 dtype = 'uint8')
						aiLaneBoundariesLeft_1 = np.full(len(common_time),
																						 group.get_value('aiLaneBoundariesLeft', ScaleTime = common_time)[0][1],
																						 dtype = 'uint8')
						aiLaneBoundariesLeft_2 = np.full(len(common_time),
																						 group.get_value('aiLaneBoundariesLeft', ScaleTime = common_time)[0][2],
																						 dtype = 'uint8')

						aiLaneBoundariesRight_0 = np.full(len(common_time),
																							group.get_value('aiLaneBoundariesRight', ScaleTime = common_time)[0][0],
																							dtype = 'uint8')
						aiLaneBoundariesRight_1 = np.full(len(common_time),
																							group.get_value('aiLaneBoundariesRight', ScaleTime = common_time)[0][1],
																							dtype = 'uint8')
						aiLaneBoundariesRight_2 = np.full(len(common_time),
																							group.get_value('aiLaneBoundariesRight', ScaleTime = common_time)[0][2],
																							dtype = 'uint8')
						lanes = {}

						lanes['left_lane'] = {}
						lanes['left_lane']['0'] = {}
						lanes['left_lane']['2'] = {}
						lanes['left_lane']['6'] = {}

						lanes['right_lane'] = {}
						lanes['right_lane']['1'] = {}
						lanes['right_lane']['3'] = {}
						lanes['right_lane']['7'] = {}

						# Left Lane
						lanes['left_lane']['0']['Parameters_fDistanceMeter'] = np.zeros(common_time.size)
						lanes['left_lane']['0']['Parameters_fYawAngleRad'] = np.zeros(common_time.size)
						lanes['left_lane']['0']['ClothoidNear_fCurvature'] = np.zeros(common_time.size)
						lanes['left_lane']['0']['ClothoidNear_fCurvatureRate'] = np.zeros(common_time.size)
						lanes['left_lane']['0']['ClothoidNear_fValidLengthMeter'] = np.zeros(common_time.size)
						lanes['left_lane']['0']['ClothoidFar_fCurvature'] = np.zeros(common_time.size)
						lanes['left_lane']['0']['ClothoidFar_fCurvatureRate'] = np.zeros(common_time.size)
						lanes['left_lane']['0']['ClothoidFar_fValidLengthMeter'] = np.zeros(common_time.size)
						lanes['left_lane']['0']['ClothoidVertical_fCurvature'] = np.zeros(common_time.size)
						lanes['left_lane']['0']['ClothoidVertical_fCurvatureRate'] = np.zeros(common_time.size)
						lanes['left_lane']['0']['ClothoidVertical_fValidLengthMeter'] = np.zeros(common_time.size)
						lanes['left_lane']['0']['Status_bAvailable'] = np.zeros(common_time.size)

						lanes['left_lane']['2']['Parameters_fDistanceMeter'] = np.zeros(common_time.size)
						lanes['left_lane']['2']['Parameters_fYawAngleRad'] = np.zeros(common_time.size)
						lanes['left_lane']['2']['ClothoidNear_fCurvature'] = np.zeros(common_time.size)
						lanes['left_lane']['2']['ClothoidNear_fCurvatureRate'] = np.zeros(common_time.size)
						lanes['left_lane']['2']['ClothoidNear_fValidLengthMeter'] = np.zeros(common_time.size)
						lanes['left_lane']['2']['ClothoidFar_fCurvature'] = np.zeros(common_time.size)
						lanes['left_lane']['2']['ClothoidFar_fCurvatureRate'] = np.zeros(common_time.size)
						lanes['left_lane']['2']['ClothoidFar_fValidLengthMeter'] = np.zeros(common_time.size)
						lanes['left_lane']['2']['ClothoidVertical_fCurvature'] = np.zeros(common_time.size)
						lanes['left_lane']['2']['ClothoidVertical_fCurvatureRate'] = np.zeros(common_time.size)
						lanes['left_lane']['2']['ClothoidVertical_fValidLengthMeter'] = np.zeros(common_time.size)
						lanes['left_lane']['2']['Status_bAvailable'] = np.zeros(common_time.size)

						lanes['left_lane']['6']['Parameters_fDistanceMeter'] = np.zeros(common_time.size)
						lanes['left_lane']['6']['Parameters_fYawAngleRad'] = np.zeros(common_time.size)
						lanes['left_lane']['6']['ClothoidNear_fCurvature'] = np.zeros(common_time.size)
						lanes['left_lane']['6']['ClothoidNear_fCurvatureRate'] = np.zeros(common_time.size)
						lanes['left_lane']['6']['ClothoidNear_fValidLengthMeter'] = np.zeros(common_time.size)
						lanes['left_lane']['6']['ClothoidFar_fCurvature'] = np.zeros(common_time.size)
						lanes['left_lane']['6']['ClothoidFar_fCurvatureRate'] = np.zeros(common_time.size)
						lanes['left_lane']['6']['ClothoidFar_fValidLengthMeter'] = np.zeros(common_time.size)
						lanes['left_lane']['6']['ClothoidVertical_fCurvature'] = np.zeros(common_time.size)
						lanes['left_lane']['6']['ClothoidVertical_fCurvatureRate'] = np.zeros(common_time.size)
						lanes['left_lane']['6']['ClothoidVertical_fValidLengthMeter'] = np.zeros(common_time.size)
						lanes['left_lane']['6']['Status_bAvailable'] = np.zeros(common_time.size)

						# Right lane
						lanes['right_lane']['1']['Parameters_fDistanceMeter'] = np.zeros(common_time.size)
						lanes['right_lane']['1']['Parameters_fYawAngleRad'] = np.zeros(common_time.size)
						lanes['right_lane']['1']['ClothoidNear_fCurvature'] = np.zeros(common_time.size)
						lanes['right_lane']['1']['ClothoidNear_fCurvatureRate'] = np.zeros(common_time.size)
						lanes['right_lane']['1']['ClothoidNear_fValidLengthMeter'] = np.zeros(common_time.size)
						lanes['right_lane']['1']['ClothoidFar_fCurvature'] = np.zeros(common_time.size)
						lanes['right_lane']['1']['ClothoidFar_fCurvatureRate'] = np.zeros(common_time.size)
						lanes['right_lane']['1']['ClothoidFar_fValidLengthMeter'] = np.zeros(common_time.size)
						lanes['right_lane']['1']['ClothoidVertical_fCurvature'] = np.zeros(common_time.size)
						lanes['right_lane']['1']['ClothoidVertical_fCurvatureRate'] = np.zeros(common_time.size)
						lanes['right_lane']['1']['ClothoidVertical_fValidLengthMeter'] = np.zeros(common_time.size)
						lanes['right_lane']['1']['Status_bAvailable'] = np.zeros(common_time.size)

						lanes['right_lane']['3']['Parameters_fDistanceMeter'] = np.zeros(common_time.size)
						lanes['right_lane']['3']['Parameters_fYawAngleRad'] = np.zeros(common_time.size)
						lanes['right_lane']['3']['ClothoidNear_fCurvature'] = np.zeros(common_time.size)
						lanes['right_lane']['3']['ClothoidNear_fCurvatureRate'] = np.zeros(common_time.size)
						lanes['right_lane']['3']['ClothoidNear_fValidLengthMeter'] = np.zeros(common_time.size)
						lanes['right_lane']['3']['ClothoidFar_fCurvature'] = np.zeros(common_time.size)
						lanes['right_lane']['3']['ClothoidFar_fCurvatureRate'] = np.zeros(common_time.size)
						lanes['right_lane']['3']['ClothoidFar_fValidLengthMeter'] = np.zeros(common_time.size)
						lanes['right_lane']['3']['ClothoidVertical_fCurvature'] = np.zeros(common_time.size)
						lanes['right_lane']['3']['ClothoidVertical_fCurvatureRate'] = np.zeros(common_time.size)
						lanes['right_lane']['3']['ClothoidVertical_fValidLengthMeter'] = np.zeros(common_time.size)
						lanes['right_lane']['3']['Status_bAvailable'] = np.zeros(common_time.size)

						lanes['right_lane']['7']['Parameters_fDistanceMeter'] = np.zeros(common_time.size)
						lanes['right_lane']['7']['Parameters_fYawAngleRad'] = np.zeros(common_time.size)
						lanes['right_lane']['7']['ClothoidNear_fCurvature'] = np.zeros(common_time.size)
						lanes['right_lane']['7']['ClothoidNear_fCurvatureRate'] = np.zeros(common_time.size)
						lanes['right_lane']['7']['ClothoidNear_fValidLengthMeter'] = np.zeros(common_time.size)
						lanes['right_lane']['7']['ClothoidFar_fCurvature'] = np.zeros(common_time.size)
						lanes['right_lane']['7']['ClothoidFar_fCurvatureRate'] = np.zeros(common_time.size)
						lanes['right_lane']['7']['ClothoidFar_fValidLengthMeter'] = np.zeros(common_time.size)
						lanes['right_lane']['7']['ClothoidVertical_fCurvature'] = np.zeros(common_time.size)
						lanes['right_lane']['7']['ClothoidVertical_fCurvatureRate'] = np.zeros(common_time.size)
						lanes['right_lane']['7']['ClothoidVertical_fValidLengthMeter'] = np.zeros(common_time.size)
						lanes['right_lane']['7']['Status_bAvailable'] = np.zeros(common_time.size)

						# for for left 0,2,6 right 1,3,7
						# for left_lane in
						for index in range(len(common_time)):
								# lane 0
								left_index_0_in_aslaneboundry = aiLaneBoundariesLeft_0[index]
								left_index_1_in_aslaneboundry = aiLaneBoundariesLeft_1[index]
								left_index_2_in_aslaneboundry = aiLaneBoundariesLeft_2[index]
								right_index_0_in_aslaneboundry = aiLaneBoundariesRight_0[index]
								right_index_1_in_aslaneboundry = aiLaneBoundariesRight_1[index]
								right_index_2_in_aslaneboundry = aiLaneBoundariesRight_2[index]

								for idx, asLaneBoundaryObject in asLaneBoundaryObjects.iteritems():
										if left_index_0_in_aslaneboundry == idx:
												# left_index_0_fDistanceMeter[index] = asLaneBoundaryObject.Parameters_fDistanceMeter[index]
												lanes['left_lane']['0']['Parameters_fDistanceMeter'][index] = \
														asLaneBoundaryObject.Parameters_fDistanceMeter[index]
												lanes['left_lane']['0']['Parameters_fYawAngleRad'][index] = \
														asLaneBoundaryObject.Parameters_fYawAngleRad[index]
												lanes['left_lane']['0']['ClothoidNear_fCurvature'][index] = \
														asLaneBoundaryObject.ClothoidNear_fCurvature[index]
												lanes['left_lane']['0']['ClothoidNear_fCurvatureRate'][index] = \
														asLaneBoundaryObject.ClothoidNear_fCurvatureRate[index]
												lanes['left_lane']['0']['ClothoidNear_fValidLengthMeter'][index] = \
														asLaneBoundaryObject.ClothoidNear_fValidLengthMeter[index]
												lanes['left_lane']['0']['ClothoidFar_fCurvature'][index] = \
														asLaneBoundaryObject.ClothoidFar_fCurvature[index]
												lanes['left_lane']['0']['ClothoidFar_fCurvatureRate'][index] = \
														asLaneBoundaryObject.ClothoidFar_fCurvatureRate[index]
												lanes['left_lane']['0']['ClothoidFar_fValidLengthMeter'][index] = \
														asLaneBoundaryObject.ClothoidFar_fValidLengthMeter[index]
												lanes['left_lane']['0']['ClothoidVertical_fCurvature'][index] = \
														asLaneBoundaryObject.ClothoidVertical_fCurvature[index]
												lanes['left_lane']['0']['ClothoidVertical_fCurvatureRate'][index] = \
														asLaneBoundaryObject.ClothoidVertical_fCurvatureRate[index]
												lanes['left_lane']['0']['ClothoidVertical_fValidLengthMeter'][index] = \
														asLaneBoundaryObject.ClothoidVertical_fValidLengthMeter[index]
												lanes['left_lane']['0']['Status_bAvailable'][index] = asLaneBoundaryObject.Status_bAvailable[index]

										# polyfar
										if left_index_1_in_aslaneboundry == idx:
												lanes['left_lane']['2']['Parameters_fDistanceMeter'][index] = \
														asLaneBoundaryObject.Parameters_fDistanceMeter[index]
												lanes['left_lane']['2']['Parameters_fYawAngleRad'][index] = \
														asLaneBoundaryObject.Parameters_fYawAngleRad[index]
												lanes['left_lane']['2']['ClothoidNear_fCurvature'][index] = \
														asLaneBoundaryObject.ClothoidNear_fCurvature[index]
												lanes['left_lane']['2']['ClothoidNear_fCurvatureRate'][index] = \
														asLaneBoundaryObject.ClothoidNear_fCurvatureRate[index]
												lanes['left_lane']['2']['ClothoidNear_fValidLengthMeter'][index] = \
														asLaneBoundaryObject.ClothoidNear_fValidLengthMeter[index]
												lanes['left_lane']['2']['ClothoidFar_fCurvature'][index] = \
														asLaneBoundaryObject.ClothoidFar_fCurvature[index]
												lanes['left_lane']['2']['ClothoidFar_fCurvatureRate'][index] = \
														asLaneBoundaryObject.ClothoidFar_fCurvatureRate[index]
												lanes['left_lane']['2']['ClothoidFar_fValidLengthMeter'][index] = \
														asLaneBoundaryObject.ClothoidFar_fValidLengthMeter[index]
												lanes['left_lane']['2']['ClothoidVertical_fCurvature'][index] = \
														asLaneBoundaryObject.ClothoidVertical_fCurvature[index]
												lanes['left_lane']['2']['ClothoidVertical_fCurvatureRate'][index] = \
														asLaneBoundaryObject.ClothoidVertical_fCurvatureRate[index]
												lanes['left_lane']['2']['ClothoidVertical_fValidLengthMeter'][index] = \
														asLaneBoundaryObject.ClothoidVertical_fValidLengthMeter[index]
												lanes['left_lane']['2']['Status_bAvailable'][index] = asLaneBoundaryObject.Status_bAvailable[index]

										if left_index_2_in_aslaneboundry == idx:
												lanes['left_lane']['6']['Parameters_fDistanceMeter'][index] = \
														asLaneBoundaryObject.Parameters_fDistanceMeter[index]
												lanes['left_lane']['6']['Parameters_fYawAngleRad'][index] = \
														asLaneBoundaryObject.Parameters_fYawAngleRad[index]
												lanes['left_lane']['6']['ClothoidNear_fCurvature'][index] = \
														asLaneBoundaryObject.ClothoidNear_fCurvature[index]
												lanes['left_lane']['6']['ClothoidNear_fCurvatureRate'][index] = \
														asLaneBoundaryObject.ClothoidNear_fCurvatureRate[index]
												lanes['left_lane']['6']['ClothoidNear_fValidLengthMeter'][index] = \
														asLaneBoundaryObject.ClothoidNear_fValidLengthMeter[index]
												lanes['left_lane']['6']['ClothoidFar_fCurvature'][index] = \
														asLaneBoundaryObject.ClothoidFar_fCurvature[index]
												lanes['left_lane']['6']['ClothoidFar_fCurvatureRate'][index] = \
														asLaneBoundaryObject.ClothoidFar_fCurvatureRate[index]
												lanes['left_lane']['6']['ClothoidFar_fValidLengthMeter'][index] = \
														asLaneBoundaryObject.ClothoidFar_fValidLengthMeter[index]
												lanes['left_lane']['6']['ClothoidVertical_fCurvature'][index] = \
														asLaneBoundaryObject.ClothoidVertical_fCurvature[index]
												lanes['left_lane']['6']['ClothoidVertical_fCurvatureRate'][index] = \
														asLaneBoundaryObject.ClothoidVertical_fCurvatureRate[index]
												lanes['left_lane']['6']['ClothoidVertical_fValidLengthMeter'][index] = \
														asLaneBoundaryObject.ClothoidVertical_fValidLengthMeter[index]
												lanes['left_lane']['6']['Status_bAvailable'][index] = asLaneBoundaryObject.Status_bAvailable[index]

										if right_index_0_in_aslaneboundry == idx:
												lanes['right_lane']['1']['Parameters_fDistanceMeter'][index] = \
														asLaneBoundaryObject.Parameters_fDistanceMeter[index]
												lanes['right_lane']['1']['Parameters_fYawAngleRad'][index] = \
														asLaneBoundaryObject.Parameters_fYawAngleRad[index]
												lanes['right_lane']['1']['ClothoidNear_fCurvature'][index] = \
														asLaneBoundaryObject.ClothoidNear_fCurvature[index]
												lanes['right_lane']['1']['ClothoidNear_fCurvatureRate'][index] = \
														asLaneBoundaryObject.ClothoidNear_fCurvatureRate[index]
												lanes['right_lane']['1']['ClothoidNear_fValidLengthMeter'][index] = \
														asLaneBoundaryObject.ClothoidNear_fValidLengthMeter[index]
												lanes['right_lane']['1']['ClothoidFar_fCurvature'][index] = \
														asLaneBoundaryObject.ClothoidFar_fCurvature[index]
												lanes['right_lane']['1']['ClothoidFar_fCurvatureRate'][index] = \
														asLaneBoundaryObject.ClothoidFar_fCurvatureRate[index]
												lanes['right_lane']['1']['ClothoidFar_fValidLengthMeter'][index] = \
														asLaneBoundaryObject.ClothoidFar_fValidLengthMeter[index]
												lanes['right_lane']['1']['ClothoidVertical_fCurvature'][index] = \
														asLaneBoundaryObject.ClothoidVertical_fCurvature[index]
												lanes['right_lane']['1']['ClothoidVertical_fCurvatureRate'][index] = \
														asLaneBoundaryObject.ClothoidVertical_fCurvatureRate[index]
												lanes['right_lane']['1']['ClothoidVertical_fValidLengthMeter'][index] = \
														asLaneBoundaryObject.ClothoidVertical_fValidLengthMeter[index]
												lanes['right_lane']['1']['Status_bAvailable'][index] = asLaneBoundaryObject.Status_bAvailable[
														index]

										if right_index_1_in_aslaneboundry == idx:
												lanes['right_lane']['3']['Parameters_fDistanceMeter'][index] = \
														asLaneBoundaryObject.Parameters_fDistanceMeter[index]
												lanes['right_lane']['3']['Parameters_fYawAngleRad'][index] = \
														asLaneBoundaryObject.Parameters_fYawAngleRad[index]
												lanes['right_lane']['3']['ClothoidNear_fCurvature'][index] = \
														asLaneBoundaryObject.ClothoidNear_fCurvature[index]
												lanes['right_lane']['3']['ClothoidNear_fCurvatureRate'][index] = \
														asLaneBoundaryObject.ClothoidNear_fCurvatureRate[index]
												lanes['right_lane']['3']['ClothoidNear_fValidLengthMeter'][index] = \
														asLaneBoundaryObject.ClothoidNear_fValidLengthMeter[index]
												lanes['right_lane']['3']['ClothoidFar_fCurvature'][index] = \
														asLaneBoundaryObject.ClothoidFar_fCurvature[index]
												lanes['right_lane']['3']['ClothoidFar_fCurvatureRate'][index] = \
														asLaneBoundaryObject.ClothoidFar_fCurvatureRate[index]
												lanes['right_lane']['3']['ClothoidFar_fValidLengthMeter'][index] = \
														asLaneBoundaryObject.ClothoidFar_fValidLengthMeter[index]
												lanes['right_lane']['3']['ClothoidVertical_fCurvature'][index] = \
														asLaneBoundaryObject.ClothoidVertical_fCurvature[index]
												lanes['right_lane']['3']['ClothoidVertical_fCurvatureRate'][index] = \
														asLaneBoundaryObject.ClothoidVertical_fCurvatureRate[index]
												lanes['right_lane']['3']['ClothoidVertical_fValidLengthMeter'][index] = \
														asLaneBoundaryObject.ClothoidVertical_fValidLengthMeter[index]
												lanes['right_lane']['3']['Status_bAvailable'][index] = asLaneBoundaryObject.Status_bAvailable[
														index]

										if right_index_2_in_aslaneboundry == idx:
												lanes['right_lane']['7']['Parameters_fDistanceMeter'][index] = \
														asLaneBoundaryObject.Parameters_fDistanceMeter[index]
												lanes['right_lane']['7']['Parameters_fYawAngleRad'][index] = \
														asLaneBoundaryObject.Parameters_fYawAngleRad[index]
												lanes['right_lane']['7']['ClothoidNear_fCurvature'][index] = \
														asLaneBoundaryObject.ClothoidNear_fCurvature[index]
												lanes['right_lane']['7']['ClothoidNear_fCurvatureRate'][index] = \
														asLaneBoundaryObject.ClothoidNear_fCurvatureRate[index]
												lanes['right_lane']['7']['ClothoidNear_fValidLengthMeter'][index] = \
														asLaneBoundaryObject.ClothoidNear_fValidLengthMeter[index]
												lanes['right_lane']['7']['ClothoidFar_fCurvature'][index] = \
														asLaneBoundaryObject.ClothoidFar_fCurvature[index]
												lanes['right_lane']['7']['ClothoidFar_fCurvatureRate'][index] = \
														asLaneBoundaryObject.ClothoidFar_fCurvatureRate[index]
												lanes['right_lane']['7']['ClothoidFar_fValidLengthMeter'][index] = \
														asLaneBoundaryObject.ClothoidFar_fValidLengthMeter[index]
												lanes['right_lane']['7']['ClothoidVertical_fCurvature'][index] = \
														asLaneBoundaryObject.ClothoidVertical_fCurvature[index]
												lanes['right_lane']['7']['ClothoidVertical_fCurvatureRate'][index] = \
														asLaneBoundaryObject.ClothoidVertical_fCurvatureRate[index]
												lanes['right_lane']['7']['ClothoidVertical_fValidLengthMeter'][index] = \
														asLaneBoundaryObject.ClothoidVertical_fValidLengthMeter[index]
												lanes['right_lane']['7']['Status_bAvailable'][index] = asLaneBoundaryObject.Status_bAvailable[
														index]

						# polynominal

						C0 = lanes['left_lane']['0']['Parameters_fDistanceMeter']
						C1 = lanes['left_lane']['0']['Parameters_fYawAngleRad']
						C2 = lanes['left_lane']['0']['ClothoidNear_fCurvature']
						C3 = lanes['left_lane']['0']['ClothoidNear_fCurvatureRate']
						V_raw = lanes['left_lane']['0']['ClothoidNear_fValidLengthMeter']

						left_lane = create_line(common_time, C0, C1, C2, C3, V_raw, None, None, group.winner)

						C0 = lanes['left_lane']['2']['Parameters_fDistanceMeter']
						C1 = lanes['left_lane']['2']['Parameters_fYawAngleRad']
						C2 = lanes['left_lane']['2']['ClothoidNear_fCurvature']
						C3 = lanes['left_lane']['2']['ClothoidNear_fCurvatureRate']
						V_raw = lanes['left_lane']['2']['ClothoidNear_fValidLengthMeter']

						left_left_lane = create_line(common_time, C0, C1, C2, C3, V_raw, None, None, group.winner)

						C0 = lanes['left_lane']['6']['Parameters_fDistanceMeter']
						C1 = lanes['left_lane']['6']['Parameters_fYawAngleRad']
						C2 = lanes['left_lane']['6']['ClothoidNear_fCurvature']
						C3 = lanes['left_lane']['6']['ClothoidNear_fCurvatureRate']
						V_raw = lanes['left_lane']['6']['ClothoidNear_fValidLengthMeter']

						left_left_left_lane = create_line(common_time, C0, C1, C2, C3, V_raw, None, None, group.winner)

						C0 = lanes['right_lane']['1']['Parameters_fDistanceMeter']
						C1 = lanes['right_lane']['1']['Parameters_fYawAngleRad']
						C2 = lanes['right_lane']['1']['ClothoidNear_fCurvature']
						C3 = lanes['right_lane']['1']['ClothoidNear_fCurvatureRate']
						V_raw = lanes['right_lane']['1']['ClothoidNear_fValidLengthMeter']

						right_lane = create_line(common_time, C0, C1, C2, C3, V_raw, None, None, group.winner)

						C0 = lanes['right_lane']['3']['Parameters_fDistanceMeter']
						C1 = lanes['right_lane']['3']['Parameters_fYawAngleRad']
						C2 = lanes['right_lane']['3']['ClothoidNear_fCurvature']
						C3 = lanes['right_lane']['3']['ClothoidNear_fCurvatureRate']
						V_raw = lanes['right_lane']['3']['ClothoidNear_fValidLengthMeter']

						right_right_lane = create_line(common_time, C0, C1, C2, C3, V_raw, None, None, group.winner)

						C0 = lanes['right_lane']['7']['Parameters_fDistanceMeter']
						C1 = lanes['right_lane']['7']['Parameters_fYawAngleRad']
						C2 = lanes['right_lane']['7']['ClothoidNear_fCurvature']
						C3 = lanes['right_lane']['7']['ClothoidNear_fCurvatureRate']
						V_raw = lanes['right_lane']['7']['ClothoidNear_fValidLengthMeter']

						right_right_right_lane = create_line(common_time, C0, C1, C2, C3, V_raw, None, None, group.winner)

						lines = LaneData(left_lane, right_lane, left_left_lane, right_right_lane)
						store_modules_cache(self.source, "calc_lanes_flc25_abd@aebs.fill", lines)
				else:
						logger.info("Loading abdlanes from cached data")
						lines = cached_data
				done = time.time()
				elapsed = done - start
				logger.info("ABDLanes loaded in " + str(elapsed))
				return lines


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"C:\KBData\Data\Development\PythonToolchainSupport\ContiMeasurementsSuport\mfc525_interface" \
								r"\measurements\HMC__2020-04-25_13-34-35_ABDLaneData.mat"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		flc25_lanes = manager_modules.calc('calc_lanes_flc25_abd@aebs.fill', manager)
		print flc25_lanes
