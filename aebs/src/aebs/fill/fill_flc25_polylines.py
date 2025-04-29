# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

from interface import iCalc
import numpy as np
import logging
import time
from pyutils.cache_manager import get_modules_cache, store_modules_cache, is_modules_cache_available

logger = logging.getLogger('fill_flc25_polylines')
class Calc(iCalc):
		dep = 'fill_flc25_line_attributes', 'fill_flc25_lane_hypotheses', 'fill_flc25_linear_objects', 'fill_flc25_geometries_lines', 'calc_common_time-flc25'

		def check(self):
				start = time.time()
				line_attributes = []
				lane_hypotheses = []
				linear_objects = []
				geometries_lines = []
				commonTime = []
				start_cache_load = time.time()
				cached_data = get_modules_cache(self.source, "fill_flc25_polylines@aebs.fill")
				if cached_data is None:
						line_attributes=[]
						logger.info("Loading road model fusion(point cloud) from measurement, Please wait... (Note: This can take longer based on file size)")
						modules = self.get_modules()
						commonTime = modules.fill(self.dep[4])
						# logger.info("Getting Line attributes from road model fusion, Please wait...")
						# line_attributes = modules.fill(self.dep[0])
						logger.info("Getting Lane hypothesis from road model fusion, Please wait...")
						lane_hypotheses = modules.fill(self.dep[1])
						logger.info("Getting Linear objects from road model fusion, Please wait...")
						linear_objects = modules.fill(self.dep[2])
						logger.info("Getting Geometries lines from road model fusion, Please wait...")
						geometries_lines = modules.fill(self.dep[3])
						done = time.time()
						elapsed = done - start
						logger.info("Road model fusion(point cloud) is loaded in " + str(elapsed))
				else:
						logger.info("Polyline data is loaded from cache in " + str(time.time() - start_cache_load))

				return line_attributes, lane_hypotheses, linear_objects, geometries_lines, commonTime, cached_data

		def fill(self, line_attributes, lane_hypotheses, linear_objects, geometries_lines, common_time, cached_data):
				start = time.time()
				if cached_data is None:
						logger.info("Post processing road model fusion data to run in Python Toolchain, Please wait...")
						ego_centerLineList = []
						ego_leftLineList = []
						ego_rightLineList = []
						# Ego's left side
						egoleft_leftLineList = []
						egoleft_rightLineList = []
						egoleftleft_leftLineList = []
						egoleftleft_rightLineList = []
						# Ego's right side
						egoright_leftLineList = []
						egoright_rightLineList = []
						egorightright_leftLineList = []
						egorightright_rightLineList = []
						lanes = np.zeros((len(common_time), 5), dtype=object)

						for index_sample in range(len(common_time)):
								LanesHypotheses = lane_hypotheses[index_sample]
								egoLaneIndex = LanesHypotheses['egoLaneIndex']
								if egoLaneIndex >=0 and egoLaneIndex < 5:
										Lines = geometries_lines[index_sample]
										for lane_index, lane in LanesHypotheses["lanes"].items():
												single_lane = {}

												leftBoundaryParts = lane['leftBoundaryParts']
												rightBoundaryParts = lane['rightBoundaryParts']

												LinearObjects = linear_objects[index_sample]

												leftLine = None
												left_combinedgeometry_array = {}
												left_combinedgeometry_array['x'] = np.array([])
												left_combinedgeometry_array['y'] = np.array([])
												left_combinedgeometry_array['y_var'] = np.array([])
												for left_boundary_index in leftBoundaryParts:
														geometry_line = LinearObjects[left_boundary_index]['geometry_line']
														geometry_from = LinearObjects[left_boundary_index]['geometry_from']
														geometry_to = LinearObjects[left_boundary_index]['geometry_to']
														geometry_array = Lines[geometry_line]
														left_combinedgeometry_array['x'] = np.concatenate((left_combinedgeometry_array['x'], geometry_array['x'][geometry_from:geometry_to+1]), axis = 0)
														left_combinedgeometry_array['y'] = np.concatenate(
																		(left_combinedgeometry_array['y'], geometry_array['y'][geometry_from:geometry_to + 1]),
																		axis = 0)
														left_combinedgeometry_array['y_var'] = np.concatenate(
																		(left_combinedgeometry_array['y_var'], geometry_array['y_var'][geometry_from:geometry_to + 1]),
																		axis = 0)
												leftLine = left_combinedgeometry_array

												rightLine = None
												right_combinedgeometry_array = {}
												right_combinedgeometry_array['x'] = np.array([])
												right_combinedgeometry_array['y'] = np.array([])
												right_combinedgeometry_array['y_var'] = np.array([])
												for right_boundary_index in rightBoundaryParts:
														geometry_line = LinearObjects[right_boundary_index]['geometry_line']
														geometry_from = LinearObjects[right_boundary_index]['geometry_from']
														geometry_to = LinearObjects[right_boundary_index]['geometry_to']
														geometry_array = Lines[geometry_line]
														right_combinedgeometry_array['x'] = np.concatenate((right_combinedgeometry_array['x'], geometry_array['x'][geometry_from:geometry_to+1]), axis = 0)
														right_combinedgeometry_array['y'] = np.concatenate(
																		(right_combinedgeometry_array['y'], geometry_array['y'][geometry_from:geometry_to + 1]),
																		axis = 0)
														right_combinedgeometry_array['y_var'] = np.concatenate(
																		(right_combinedgeometry_array['y_var'], geometry_array['y_var'][geometry_from:geometry_to + 1]),
																		axis = 0)
												rightLine = right_combinedgeometry_array

												single_lane['leftLine'] = leftLine
												single_lane['rightLine'] = rightLine
												lanes[index_sample, lane["id"]] = single_lane

								if LanesHypotheses["lanes"]:
										egoLaneInfo = LanesHypotheses["lanes"][egoLaneIndex]
										lanes[index_sample, egoLaneIndex]["lane_info"] = "ego_lane"
										lanes[index_sample, egoLaneIndex]['centerLine'] = Lines[egoLaneInfo["centerLine"]]
										ego_centerLineList.append((lanes[index_sample, egoLaneIndex]["centerLine"]["x"], lanes[index_sample, egoLaneIndex]["centerLine"]["y"]))
										ego_leftLine = (lanes[index_sample, egoLaneIndex]["leftLine"]["x"], lanes[index_sample, egoLaneIndex]["leftLine"]["y"])
										ego_leftLineList.append(ego_leftLine)
										ego_rightLine = (lanes[index_sample, egoLaneIndex]["rightLine"]["x"], lanes[index_sample, egoLaneIndex]["rightLine"]["y"])
										ego_rightLineList.append(ego_rightLine)
										if egoLaneInfo["leftLane"] != 5:
												egoLeftLaneIndex = egoLaneInfo["leftLane"]
												egoLeftLaneInfo = LanesHypotheses["lanes"][egoLeftLaneIndex]
												lanes[index_sample, egoLeftLaneIndex]["lane_info"] = "left_lane"

												egoleft_leftLineList.append((lanes[index_sample, egoLeftLaneIndex]["leftLine"]["x"], lanes[index_sample, egoLeftLaneIndex]["leftLine"]["y"]))
												egoleft_rightLineList.append((lanes[index_sample, egoLeftLaneIndex]["rightLine"]["x"], lanes[index_sample, egoLeftLaneIndex]["rightLine"]["y"]))
												if egoLeftLaneInfo["leftLane"] != 5:
														egoLeftLeftLaneIndex = egoLeftLaneInfo["leftLane"]
														lanes[index_sample, egoLeftLeftLaneIndex]["lane_info"] = "leftleft_lane"
														egoleftleft_leftLineList.append((lanes[index_sample, egoLeftLeftLaneIndex]["leftLine"]["x"], lanes[index_sample, egoLeftLeftLaneIndex]["leftLine"]["y"]))
														egoleftleft_rightLineList.append((lanes[index_sample, egoLeftLeftLaneIndex]["rightLine"]["x"], lanes[index_sample, egoLeftLeftLaneIndex]["rightLine"]["y"]))
												else:
														egoleftleft_leftLineList.append(np.zeros_like(np.array((np.array([0.0]), np.array([0.0])))))
														egoleftleft_rightLineList.append(np.zeros_like(np.array((np.array([0.0]), np.array([0.0])))))
										else:
												egoleft_leftLineList.append(np.zeros_like(np.array((np.array([0.0]), np.array([0.0])))))
												egoleft_rightLineList.append(np.zeros_like(np.array((np.array([0.0]), np.array([0.0])))))
												egoleftleft_leftLineList.append(np.zeros_like(np.array((np.array([0.0]), np.array([0.0])))))
												egoleftleft_rightLineList.append(np.zeros_like(np.array((np.array([0.0]), np.array([0.0])))))
										if egoLaneInfo["rightLane"] != 5:
												egoRightLaneIndex = egoLaneInfo["rightLane"]
												egoRightLaneInfo = LanesHypotheses["lanes"][egoRightLaneIndex]
												lanes[index_sample, egoRightLaneIndex]["lane_info"] = "right_lane"
												egoright_leftLineList.append((lanes[index_sample, egoRightLaneIndex]["leftLine"]["x"], lanes[index_sample, egoRightLaneIndex]["leftLine"]["y"]))
												egoright_rightLineList.append((lanes[index_sample, egoRightLaneIndex]["rightLine"]["x"], lanes[index_sample, egoRightLaneIndex]["rightLine"]["y"]))
												if egoRightLaneInfo["rightLane"] != 5:
														egoRightRightLaneIndex = egoRightLaneInfo["rightLane"]
														lanes[index_sample, egoRightRightLaneIndex]["lane_info"] = "rightright_lane"
														egorightright_leftLineList.append((lanes[index_sample, egoRightRightLaneIndex]["leftLine"]["x"], lanes[index_sample, egoRightRightLaneIndex]["leftLine"]["y"]))
														egorightright_rightLineList.append((lanes[index_sample, egoRightRightLaneIndex]["rightLine"]["x"], lanes[index_sample, egoRightRightLaneIndex]["rightLine"]["y"]))
												else:
														egorightright_leftLineList.append(np.zeros_like(np.array((np.array([0.0]), np.array([0.0])))))
														egorightright_rightLineList.append(np.zeros_like(np.array((np.array([0.0]), np.array([0.0])))))
										else:
												egoright_leftLineList.append(np.zeros_like(np.array((np.array([0.0]), np.array([0.0])))))
												egoright_rightLineList.append(np.zeros_like(np.array((np.array([0.0]), np.array([0.0])))))
												egorightright_leftLineList.append(np.zeros_like(np.array((np.array([0.0]), np.array([0.0])))))
												egorightright_rightLineList.append(np.zeros_like(np.array((np.array([0.0]), np.array([0.0])))))
								else:
										ego_centerLineList.append(np.zeros_like(np.array((np.array([0.0]), np.array([0.0])))))
										ego_leftLineList.append(np.zeros_like(np.array((np.array([0.0]), np.array([0.0])))))
										ego_rightLineList.append(np.zeros_like(np.array((np.array([0.0]), np.array([0.0])))))
										# Ego's left side
										egoleft_leftLineList.append(np.zeros_like(np.array((np.array([0.0]), np.array([0.0])))))
										egoleft_rightLineList.append(np.zeros_like(np.array((np.array([0.0]), np.array([0.0])))))
										egoleftleft_leftLineList.append(np.zeros_like(np.array((np.array([0.0]), np.array([0.0])))))
										egoleftleft_rightLineList.append(np.zeros_like(np.array((np.array([0.0]), np.array([0.0])))))
										# Ego's right side
										egoright_leftLineList.append(np.zeros_like(np.array((np.array([0.0]), np.array([0.0])))))
										egoright_rightLineList.append(np.zeros_like(np.array((np.array([0.0]), np.array([0.0])))))
										egorightright_leftLineList.append(np.zeros_like(np.array((np.array([0.0]), np.array([0.0])))))
										egorightright_rightLineList.append(np.zeros_like(np.array((np.array([0.0]), np.array([0.0])))))
						all_lines = {}

						all_lines["ego_leftLine"] = np.array(ego_leftLineList)
						all_lines["ego_centerLine"] = np.array(ego_centerLineList)
						all_lines["ego_rightLine"] = np.array(ego_rightLineList)
						# Ego's left side
						all_lines["egoleft_leftLine"] = np.array(egoleft_leftLineList)
						all_lines["egoleft_rightLine"] = np.array(egoleft_rightLineList)
						all_lines["egoleftleft_leftLine"] = np.array(egoleftleft_leftLineList)
						all_lines["egoleftleft_rightLine"] = np.array(egoleftleft_rightLineList)
						# Ego's right side
						all_lines["egoright_leftLine"] = np.array(egoright_leftLineList)
						all_lines["egoright_rightLine"] = np.array(egoright_rightLineList)
						all_lines["egorightright_leftLine"] = np.array(egorightright_leftLineList)
						all_lines["egorightright_rightLine"] = np.array(egorightright_rightLineList)
						store_modules_cache(self.source, "fill_flc25_polylines@aebs.fill", (all_lines, common_time))
				else:
						logger.info("Loading polylines from cached data")
						all_lines,common_time = cached_data
				done = time.time()
				elapsed = done - start
				logger.info("Post processing road model fusion is completed in " + str(elapsed))
				return all_lines, common_time


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"C:\KBData\Data\Development\PythonToolchainSupport\ContiMeasurementsSuport\mfc525_interface\measurements\2020-08-20\NY00__2020-08-20_13-52-08.mat"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		tracks = manager_modules.calc('fill_flc25_polylines@aebs.fill', manager)
		print(tracks)
