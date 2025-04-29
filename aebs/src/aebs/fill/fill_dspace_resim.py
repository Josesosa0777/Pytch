# -*- dataeval: init -*-
import ConfigParser
import logging
import math
import os
import subprocess
from collections import OrderedDict

import numpy as np
import scipy
from aebs.fill.dspace_exporter.dspace_resim_export_utils import get_absolute_distaces

from interface import iObjectFill
import matplotlib.pyplot as plt
logger = logging.getLogger('fillFLC25_CEM_TPF')

INVALID_ID = 255

DSPACE_EXE_PATH = os.path.join(os.path.dirname(__file__), "dspace_exporter", "dSpace_scenario_generator","dSpace_scenario_generator.exe")
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "dspace_exporter",  "config.cfg")

class cFill(iObjectFill):
		dep = 'fill_flc25_cem_tpf_tracks', 'calc_egomotion_resim','calc_lanes-flc25'
		def check(self):
				self.config = ConfigParser.ConfigParser()

				if self.config.read(CONFIG_PATH):
					self.pytchOutputFolder = self.config.get("ModelDeskProject", "MatlabOutputFolder")
					self.ControlDeskOutputFolder = self.config.get("ControlDeskProject", "ControlDeskOutputFolder")
					self.ControlDeskOutputFile=  self.config.get("ControlDeskProject","ControlDeskOutputFile")

				modules = self.get_modules()
				cem_tpf_tracks, _ = modules.fill("fill_flc25_cem_tpf_tracks")
				ego_orig_export = modules.fill("calc_egomotion_resim@aebs.fill")
				ego_lane_info = modules.fill("calc_lanes-flc25@aebs.fill")

				return cem_tpf_tracks, ego_orig_export, ego_lane_info

		def fill(self, cem_tpf_tracks, ego_orig_export,ego_lane_info):
				import time
				start = time.time()
				logger.info("FLC25 CEM TPF object retrieval is started, Please wait...")
				cem_tpf_objectbufferlist = {}
				for id, cem_tpf_track in cem_tpf_tracks.iteritems():
						o = {}
						o["time"] = cem_tpf_track.time
						o["id"] = np.where(cem_tpf_track.dx.mask, INVALID_ID, id)
						o["valid"] = (
												cem_tpf_track.tr_state.valid.data
												& ~cem_tpf_track.tr_state.valid.mask
								)
						object_type = np.empty(cem_tpf_track.dx.shape, dtype = "int")
						object_type[:] = 6
						car = np.where(cem_tpf_track.obj_type.car, 1, 0)
						truck = np.where(cem_tpf_track.obj_type.truck, 2, 0)
						motorcycle = np.where(cem_tpf_track.obj_type.motorcycle, 3, 0)
						pedestrian = np.where(cem_tpf_track.obj_type.pedestrian, 4, 0)
						bicycle = np.where(cem_tpf_track.obj_type.bicycle, 5, 0)
						unknown = np.where(cem_tpf_track.obj_type.unknown, 6, 0)
						point = np.where(cem_tpf_track.obj_type.point, 7, 0)
						wide = np.where(cem_tpf_track.obj_type.wide, 8, 0)
						object_type[car == 1] = 1
						object_type[truck == 2] = 2
						object_type[motorcycle == 3] = 3
						object_type[pedestrian == 4] = 4
						object_type[bicycle == 5] = 5
						object_type[unknown == 6] = 6
						object_type[point == 7] = 7
						object_type[wide == 8] = 8

						o["object_type"] = object_type
						o["alive_intervals"] = cem_tpf_track.alive_intervals

						cem_tpf_track.dx.data[cem_tpf_track.dx.mask] = 0
						o["dx"] = cem_tpf_track.dx.data
						cem_tpf_track.dy.data[cem_tpf_track.dy.mask] = 0
						o["dy"] = cem_tpf_track.dy.data
						o["ax"] = cem_tpf_track.ax.data
						o["ay"] = cem_tpf_track.ay.data
						o["vx"] = cem_tpf_track.vx.data
						o["vy"] = cem_tpf_track.vy.data
						o["height"] = cem_tpf_track.height.data
						o["width"] = cem_tpf_track.width.data
						o["length"] = cem_tpf_track.length.data
						o["dx_std"] = cem_tpf_track.dx_std.data
						o["dy_std"] = cem_tpf_track.dy_std.data
						o["range"] = cem_tpf_track.range.data
						o["angle"] = cem_tpf_track.angle.data
						o["ay_abs"] = cem_tpf_track.ay_abs.data
						o["ax_abs"] = cem_tpf_track.ax_abs.data

						# o["ax_abs"] = cem_tpf_track.ax_abs.data
						o["vx_std"] = cem_tpf_track.vx_std.data
						o["vy_std"] = cem_tpf_track.vy_std.data
						o["vx_abs"] = cem_tpf_track.vx_abs.data
						o["vy_abs"] = cem_tpf_track.vy_abs.data
						o["vx_abs_std"] = cem_tpf_track.vx_abs_std.data
						o["vy_abs_std"] = cem_tpf_track.vy_abs_std.data
						o["dz"] = cem_tpf_track.dz.data
						o["dz_std"] = cem_tpf_track.dz_std.data
						o["yaw"] = cem_tpf_track.yaw.data
						o["yaw_std"] = cem_tpf_track.yaw_std.data
						o["mov_state"] = cem_tpf_track.mov_state.join()
						o["video_conf"] = cem_tpf_track.video_conf.data
						o["measured_by"] = cem_tpf_track.measured_by.join()
						o["lane"] = cem_tpf_track.lane.join()

						objectbuffer_key = "cem_tpf_objectbuffer" + str(id)
						cem_tpf_objectbufferlist[objectbuffer_key] = o

				end = time.time()
				print("FLC25 CEM TPFObjects collected in {} sec".format(end - start))
				start = time.time()
				BUFFER_SIZE = 100
				common_time = cem_tpf_tracks.time
				l_data = len(common_time)
				filtered_objects = []
				limit = 48 #timestamps[48] - timestamps[0]
				# How to prepare fellowlist: non-overlapping objects
				# Find fellowList dimension?
				# How to decide which object goes into FellowListMDA(i).txt =>
				# Filters:
				# - Filter objects that are active for 48 time cycles
				# - Object type: car, truck, unknown
				# - Non overlapping object
				# Original measurement:
				valid_detection_mx = np.zeros(shape = [BUFFER_SIZE, l_data])
				ModelDeskType_mx = np.zeros(shape = [BUFFER_SIZE, l_data])
				laneIndex_mx = np.zeros(shape=[BUFFER_SIZE, l_data])

				filtered_dx_type_mx = np.zeros(
						shape = [BUFFER_SIZE, l_data])  # contains filtered_dx_type vector for each of the object buffers
				filtered_dy_type_mx = np.zeros(
						shape = [BUFFER_SIZE, l_data])  # contains filtered_dy_type vector for each of the object buffers

				time_unit = (common_time[l_data - 1] - common_time[0]) / l_data # Rounded to 4 decimal value
				for i in range(100): #TODO Stop debug for 23rd object
						# o = {}
						object_name = "cem_tpf_objectbuffer" + str(i)

						raw_object = cem_tpf_objectbufferlist[object_name]
						alive_intervals = raw_object["alive_intervals"]
						# Prepare masks
						valid_filter_object_mask = (raw_object["dx"] > 0) & (raw_object["video_conf"] > 0)
						for interval_start, interval_end in alive_intervals:
								alive_interval_cycles = interval_end - interval_start
								alive_ahead_cycles = len(raw_object["dx"][raw_object["dx"][interval_start:interval_end+1]>0])
								if alive_ahead_cycles <= limit:  # 48 time cycles
										valid_filter_object_mask[interval_start:interval_end] = False
								# else:
								# 	print(raw_object["time"][interval_start:interval_end][0])

						valid_object = np.array(valid_filter_object_mask, dtype = int)

						modeldesk_type = raw_object["object_type"]
						modeldesk_type[~valid_filter_object_mask] = 0

						valid_obj_type_mask = (raw_object["object_type"] == 1) | (raw_object["object_type"] == 2) | (raw_object["object_type"] == 6)
						valid_filter_object_mask = valid_filter_object_mask & valid_obj_type_mask
# Obj_type: 8377=2
						raw_object["dx"][~valid_filter_object_mask] = 0
						raw_object["dy"][~valid_filter_object_mask] = 0

						laneIndex = raw_object["lane"]
						laneIndex[~valid_filter_object_mask] = 0
						# o["ModelDeskType"] = modeldesk_type
						# o["dx"] = raw_object["dx"]
						# o["dy"] = raw_object["dy"]
						filtered_dx_type_mx[i, :] = raw_object["dx"]
						filtered_dy_type_mx[i, :] = raw_object["dy"]
						ModelDeskType_mx[i, :] = modeldesk_type
						valid_detection_mx[i, :] = valid_object
						laneIndex_mx[i, :] = laneIndex
						# filtered_objects.append(o)

				count = 0
				valid_objectbuffer = np.zeros(shape = BUFFER_SIZE)
				for kk in range(0, BUFFER_SIZE): #TODO 23rd buffer has all zeros: Check it out
						if np.count_nonzero(filtered_dx_type_mx[kk, :]) == 0:
								valid_objectbuffer[kk] = -1
						else:
								count = count + 1
								valid_objectbuffer[kk] = kk

				#TODO: Just for verification:
				# Counting the number of object buffers that contain valid instances
				# np.bincount(np.array(ModelDeskTypeTemp, dtype = int))
				# detection_count = np.zeros_like(common_time)
				# for m in range(0, l_data):
				# 		xx = filtered_dx_type_mx[:, m]
				# 		# detection_count[m] = len(np.argwhere(xx >0))
				# 		detection_count[m] = len(np.argwhere(xx>0)) #TODO np.count_nonzero(xx)  # len(nonzeros(xx(xx>0)))
				# detection_count1 = np.zeros_like(common_time)
				# for m in range(0, l_data):
				# 		xx = filtered_dy_type_mx[:, m]
				# 		# detection_count[m] = len(np.argwhere(xx >0))
				# 		detection_count1[m] = len(np.argwhere(xx > 0))
				#
				# detection_count2 = np.zeros_like(common_time)
				# for m in range(0, l_data):
				# 		xx = ModelDeskType_mx[:, m]
				# 		# detection_count[m] = len(np.argwhere(xx >0))
				# 		detection_count2[m] = len(np.argwhere(xx > 0))
				#
				# detection_count3 = np.zeros_like(common_time)
				# for m in range(0, l_data):
				# 		xx = valid_detection_mx[:, m]
				# 		# detection_count[m] = len(np.argwhere(xx >0))
				# 		detection_count3[m] = len(np.argwhere(xx > 0))
				# print(detection_count)

				# TODO ego_orig_export +  cem_tpf_buffers
				# TODO in matlab script they did not rescaled ego: Here after rescaling results may differ
				ego_orig_export_tmp = ego_orig_export.rescale(cem_tpf_tracks.time)
				# Handling the detection of different fellow vehicles for selected time segment

				# time interval of the simulation
				startPoint = 3515
				endPoint = 5335

				FellowDistance_orig_4 = {}  # ModelDesk table vectors, all detections separated (each detection correpsponds
				# to a fellow)
				FellowLateralOffset_orig_4 = {}
				ASMTime_4 = {}
				SegmentTimeLength_4 = {}
				signal_present_4 = {}  # Time stamps where detection is present, separated
				FellowType_4 = {}
				Delay = np.zeros(shape = [BUFFER_SIZE, endPoint - startPoint])

				FellowsToModelDesk = []

				nn = 0
				count_temp = 0

				# Setting the start point to 0 s
				ASMTimeTemp = (common_time[startPoint:endPoint] - common_time[startPoint])
				ASMTimeTemp_1 = (common_time[startPoint:endPoint] - common_time[startPoint])
				end = len(ASMTimeTemp_1) - 1
				for j in range(0, len(ASMTimeTemp_1) - 1):
						if (j != len(ASMTimeTemp_1)):
								if ASMTimeTemp_1[j] == ASMTimeTemp_1[j + 1]:
										ASMTimeTemp_1[j:  end - 1] = ASMTimeTemp_1[j + 1: end]
										ASMTimeTemp_1[end] = 0
				for i in range(len(ASMTimeTemp_1) - 1):
						if ASMTimeTemp_1[i] == ASMTimeTemp_1[i + 1]:
								ASMTimeTemp_1[i + 1:] = 0
								break

				FellowDistance_orig = np.zeros(shape = [BUFFER_SIZE, np.count_nonzero(ASMTimeTemp_1) + 1])
				FellowLateralOffset_orig = np.zeros(shape = [BUFFER_SIZE, np.count_nonzero(ASMTimeTemp_1) + 1])
				ModelDeskType_orig = np.zeros(shape = [BUFFER_SIZE, np.count_nonzero(ASMTimeTemp_1) + 1])
				laneIndexTemp_orig = np.zeros(shape=[BUFFER_SIZE, np.count_nonzero(ASMTimeTemp_1) + 1])
				EgoLateralOffset_orig = np.zeros(shape=np.count_nonzero(ASMTimeTemp_1) + 1)
				EgoLateralOffsetLeft_orig = np.zeros(shape=np.count_nonzero(ASMTimeTemp_1) + 1)
				EgoLateralOffsetRight_orig = np.zeros(shape=np.count_nonzero(ASMTimeTemp_1) + 1)

				FellowDistanceTemp = np.zeros(shape = [BUFFER_SIZE, endPoint - startPoint])
				FellowLateralOffsetTemp = np.zeros(shape = [BUFFER_SIZE, endPoint - startPoint])
				ModelDeskTypeTemp = np.zeros(shape = [BUFFER_SIZE, endPoint - startPoint])
				laneIndexTemp = np.zeros(shape=[BUFFER_SIZE, endPoint - startPoint])

				for ii in range(0, BUFFER_SIZE):
						FellowDistanceTemp[ii, :] = filtered_dx_type_mx[ii, startPoint: endPoint]
						FellowLateralOffsetTemp[ii, :] = filtered_dy_type_mx[ii, startPoint: endPoint]
						EgoSpeedTemp = ego_orig_export_tmp.vx[startPoint:endPoint] #TODO in matlab script they did not rescaled ego
						ModelDeskTypeTemp[ii, :] = ModelDeskType_mx[ii, startPoint: endPoint]
						EgoLateralOffsetTemp = abs(ego_lane_info.right_line.c0[startPoint:endPoint]) - 2.0
						EgoLateralOffsetLeftTemp = ego_lane_info.left_line.c0[startPoint:endPoint]
						EgoLateralOffsetRightTemp = ego_lane_info.right_line.c0[startPoint:endPoint]
						laneIndexTemp[ii, :] = laneIndex_mx[ii, startPoint:endPoint]

						end = len(ASMTimeTemp) - 1
						# Shifting arrays if consecutive time is same
						for j in range(0, len(ASMTimeTemp) - 1):
								if (j != len(ASMTimeTemp)):
										if ASMTimeTemp[j] == ASMTimeTemp[j + 1]:
												ASMTimeTemp[j:  end - 1] = ASMTimeTemp[j + 1: end]
												ASMTimeTemp[end] = 0
												FellowDistanceTemp[ii, j: end - 1] = FellowDistanceTemp[ii, j + 1: end]
												FellowDistanceTemp[ii, end] = 0
												FellowLateralOffsetTemp[ii, j: end - 1] = FellowLateralOffsetTemp[ii, j + 1: end]
												FellowLateralOffsetTemp[ii, end] = 0
												EgoSpeedTemp[j: end - 1] = EgoSpeedTemp[j + 1: end]
												EgoSpeedTemp[end] = 0
												EgoLateralOffsetTemp[j:end - 1] = EgoLateralOffsetTemp[j + 1:end]
												EgoLateralOffsetTemp[end] = 0
												EgoLateralOffsetLeftTemp[j:end - 1] = EgoLateralOffsetLeftTemp[
																					  j + 1:end]
												EgoLateralOffsetLeftTemp[end] = 0
												EgoLateralOffsetRightTemp[j:end - 1] = EgoLateralOffsetRightTemp[
																					   j + 1:end]
												EgoLateralOffsetRightTemp[end] = 0

												ModelDeskTypeTemp[ii, j: end - 1] = ModelDeskTypeTemp[ii, j + 1: end]
												ModelDeskTypeTemp[ii, end] = 0
												laneIndexTemp[ii, j:end - 1] = laneIndexTemp[ii, j + 1:end]
												laneIndexTemp[ii, end] = 0

						ASMTime = np.zeros(shape = np.count_nonzero(ASMTimeTemp_1) + 1)
						EgoSpeed_orig = np.zeros(shape = np.count_nonzero(ASMTimeTemp_1) + 1)

						j = 1
						# Copy cleaned data to orig: left-shifted non-zeros corresponding ASMTime elements
						FellowDistance_orig[ii][0] = FellowDistanceTemp[ii, 0]
						FellowLateralOffset_orig[ii][0] = FellowLateralOffsetTemp[ii, 0]
						EgoSpeed_orig[0] = EgoSpeedTemp[0]
						EgoLateralOffset_orig[0] = EgoLateralOffsetTemp[0]

						ModelDeskType_orig[ii][0] = ModelDeskTypeTemp[ii, 0]
						laneIndexTemp_orig[ii][0] = laneIndexTemp[ii, 0]

						while ASMTimeTemp_1[j] != 0:
								ASMTime[j] = ASMTimeTemp_1[j]
								FellowDistance_orig[ii][j] = FellowDistanceTemp[ii, j]
								FellowLateralOffset_orig[ii][j] = FellowLateralOffsetTemp[ii, j]
								EgoSpeed_orig[j] = EgoSpeedTemp[j]
								ModelDeskType_orig[ii][j] = ModelDeskTypeTemp[ii, j]
								EgoLateralOffset_orig[j] = EgoLateralOffsetTemp[j]
								EgoLateralOffsetLeft_orig[j] = EgoLateralOffsetLeftTemp[j]
								EgoLateralOffsetRight_orig[j] = EgoLateralOffsetRightTemp[j]

								laneIndexTemp_orig[ii][j] = laneIndexTemp[ii, j]

								j = j + 1

						mm = 1
						mlast = 0
						END_COUNT = len(FellowDistance_orig[ii, :]) #TODO can be taken out of loop

						if FellowDistance_orig[ii][0] != 0:  # Fellow Object detected from begining of interval
								mfirst = 0
								try:
										while (mm < END_COUNT - 1) and (FellowDistance_orig[ii][mm + 1] != 0):
												mm = mm + 1
								except:
										print("mm : {}".format(mm))
										print("FellowDistance_orig shape : {}".format(FellowDistance_orig.shape))
								mlast = mm
								FellowDistance_orig_4[nn] = FellowDistance_orig[ii][mfirst:mlast]
								FellowLateralOffset_orig_4[nn] = FellowLateralOffset_orig[ii][mfirst:mlast]
								ASMTime_4[nn] = ASMTime[0:mm - mfirst + 1]
								# Delay_4[nn] = 0
								SegmentTimeLength_4[nn] = mm * time_unit
								Delay[nn] = 0
								signal_present_4[nn] = range(mfirst, mlast, 1)
								FellowType_4[nn] = np.bincount(np.array(ModelDeskType_orig[ii][mfirst:mm], dtype = int)).argmax()
								mm = mm + 1
								nn = nn + 1

						while mm < END_COUNT - 1:
								if FellowDistance_orig[ii][mm] == 0 and FellowDistance_orig[ii][mm + 1] != 0:
										#TODO  ii
										mfirst = mm + 1
										while (mm < END_COUNT - 1) and (FellowDistance_orig[ii][mm + 1] != 0):
												mm = mm + 1
										mlast = mm
										FellowDistance_orig_4[nn] = FellowDistance_orig[ii][mfirst:mlast]
										FellowLateralOffset_orig_4[nn] = FellowLateralOffset_orig[ii][mfirst:mlast]
										ASMTime_4[nn] = ASMTime[1:mm - mfirst + 1]

										SegmentTimeLength_4[nn] = (mlast - mfirst) * time_unit
										# Delay_4[nn] = mfirst * time_unit
										signal_present_4[nn] = range(mfirst, mlast, 1)
										FellowType_4[nn] = np.bincount(np.array(ModelDeskType_orig[ii][mfirst:mm], dtype = int)).argmax()
										mm = mm + 1
										nn = nn + 1
								else:
										mm = mm + 1
						if np.sum(FellowDistance_orig[ii][:]) != 0:
								FellowsToModelDesk.append(ii)  # ToDO

						EgoTimeLength = (endPoint - startPoint) * time_unit
				end = time.time()
				print("dSpace inputs prepared in {} sec".format(end-start))
				start = time.time()
				if not os.path.exists(self.pytchOutputFolder):
					os.makedirs(self.pytchOutputFolder)
				ego_lane = np.ones_like(EgoLateralOffsetLeft_orig)

				for i in range(1, len(EgoLateralOffsetLeft_orig) - 1):
					if (EgoLateralOffsetLeft_orig[i] < 0.1) and (EgoLateralOffsetLeft_orig[i - 1] < 1) and (
							EgoLateralOffsetLeft_orig[i - 1] != EgoLateralOffsetLeft_orig[i]) and (
							EgoLateralOffsetRight_orig[i] < -3):
						ego_lane[i + 1] = ego_lane[i] + 1
					elif (EgoLateralOffsetLeft_orig[i] < 0.1) and EgoLateralOffsetLeft_orig[i - 1] > 3 and (
							EgoLateralOffsetLeft_orig[i - 1] != EgoLateralOffsetLeft_orig[i]) and (
							EgoLateralOffsetLeft_orig[i] > -0.1):
						ego_lane[i + 1] = ego_lane[i] - 1
					else:
						ego_lane[i + 1] = ego_lane[i]

				ASMvDesired = 3.6 * EgoSpeed_orig
				ASMLaneIndex = ego_lane
				ASMLateralOffset = EgoLateralOffset_orig

				EgoDict = {}
				EgoDict['ASMTime'] = ASMTime
				# EgoDict['ASMLaneIndex'] = ASMLaneIndex
				# EgoDict['ASMLateralOffset'] = ASMLateralOffset
				EgoDict['ASMvDesired'] = ASMvDesired
				scipy.io.savemat(os.path.join(self.pytchOutputFolder,'EgoMovement.mat'), EgoDict)

				ASMTIMEEGO = ASMTime

				for nnn in range(0, len(ASMTime_4.keys())):
						ASMTime = ASMTime_4[nnn]
						FellowDistance = FellowDistance_orig_4[nnn]
						FellowLateralOffset = FellowLateralOffset_orig_4[nnn]
						FellowDict = {}
						if len(FellowDistance) < len(ASMTime):
								ASMTime = ASMTime[len(ASMTime) - len(FellowDistance):]
						FellowDict['ASMTime'] = ASMTime
						FellowDict['FellowDistance'] = FellowDistance
						FellowDict['FellowLateralOffset'] = FellowLateralOffset
						FelloMovementName = "FellowMovement" + str(nnn) + ".mat"
						scipy.io.savemat(os.path.join(self.pytchOutputFolder,FelloMovementName), FellowDict)


				# Grouping of non - overlapping(time and type) detections
				FellowList = dict({0: {0}})
				FellowListUnion = dict({0: set(signal_present_4[0])})
				FellowTypeUnion = dict({0: {FellowType_4[0]}})
				for j in range(1, len(signal_present_4)):
						jj = 0
						while(jj < len(FellowListUnion)):
								if sum(FellowListUnion[jj].intersection(signal_present_4[j])) == 0 and \
												sum(FellowTypeUnion[jj].intersection({FellowType_4[j]})) != 0: #TODO FellowType_4 convert to set
										FellowList[jj] = FellowList[jj].union([j])
										FellowListUnion[jj] = FellowListUnion[jj].union(signal_present_4[j])
										FellowTypeUnion[jj] = FellowTypeUnion[jj].union({FellowType_4[j]})
										break
								else:
										jj = jj + 1

						if jj == len(FellowListUnion):
								FellowList[jj] = {j}
								FellowListUnion[jj] = []
								FellowListUnion[jj] = set(signal_present_4[j])
								FellowTypeUnion[jj] = []
								FellowTypeUnion[jj] = {FellowType_4[j]}
				# Sorting fellows that were grouped in the same group (above) in the order of their appearance
				firstElement = {}
				for i in range(len(FellowList)):
						firstElement[i] = [0] * len(FellowList[i])
				sorderedList = []
				FellowListModelDesk = []
				for hh in range(len(FellowList.keys())):
						for gg in range(len(FellowList[hh])):
								ind = list(FellowList[hh])[gg]
								firstElement[hh][gg] = signal_present_4[ind][0] #TODO
						sortedIndexes = sorted(range(len(firstElement[hh])),key=firstElement[hh].__getitem__)
						sorderedList.append(sorted(firstElement[hh]))
						modelDeskSortedList = []
						for idx in sortedIndexes:
								modelDeskSortedList.append(list(FellowList[hh])[idx])
						FellowListModelDesk.append(modelDeskSortedList)
						"""
						[sortedList{hh},I{hh}] = sort(firstElement{hh});
            FellowListModelDesk{hh} = FellowList{hh}(I{hh});
            """

				# Calculating delay time for each fellow (the time after which they appear)
				Delay_7 = {}
				Segment_Time_Length = {}
				for i in range(len(FellowListModelDesk)):
						Delay_7[i] = [0] * len(FellowListModelDesk[i])
						Segment_Time_Length[i] = [0] * len(FellowListModelDesk[i])

				for z in range(len(FellowListModelDesk)):
						indd01 = FellowListModelDesk[z][0] #TODO 0 or 1
						Delay_7[z][0] = (signal_present_4[indd01][0] - 1)* time_unit
						Segment_Time_Length[z][0] = SegmentTimeLength_4[indd01]
						for zz in range(1, len(FellowListModelDesk[z])):
								indd1 = FellowListModelDesk[z][zz]
								indd2 = FellowListModelDesk[z][zz -1]
								Delay_7[z][zz] = (signal_present_4[indd1][0] - signal_present_4[indd2][-1]) * time_unit
								Segment_Time_Length[z][zz] = SegmentTimeLength_4[indd1]

				# for a in range(len(FellowList)):
				# 		FellowListMD = FellowList[a]
				# 		FellowListMDDict = {}
				# 		FellowListMDDict['FellowListMD'] = list(FellowListMD)
				# 		FellowListName = "FellowList" + str(a) + ".mat"
				# 		scipy.io.savemat(os.path.join(self.pytchOutputFolder,FellowListName), FellowListMDDict)

				fileID_string = {}
				for aa in range(len(FellowListModelDesk)):
						FellowListMDA = FellowListModelDesk[aa]
						fileID_string[aa] = open(os.path.join(self.pytchOutputFolder,'FellowListMDA{}.txt'.format(str(aa))), 'w')
						for element in FellowListMDA:
								fileID_string[aa].write('{}\n'.format(element))
						fileID_string[aa].close()

				# fileID_1 = open(os.path.join(self.pytchOutputFolder,'FellowsToModelDeskList.txt'), 'w')
				# for element in FellowsToModelDesk:
				# 		fileID_1.write('{}\n'.format(element))
				# fileID_1.close()

				fileID_2 = open(os.path.join(self.pytchOutputFolder,'SegmentTimeLength_4.txt'), 'w')
				SegmentTimeLength_4_List = [element for list1 in Segment_Time_Length.values() for element in list1]
				for element in SegmentTimeLength_4_List:
						fileID_2.write('{}\n'.format(element))
				fileID_2.close()

				fileID_4 = open(os.path.join(self.pytchOutputFolder,'EgoTimeLength.txt'), 'w')
				fileID_4.write('{}\n'.format(EgoTimeLength))
				fileID_4.close()

				FellowListDim = len(FellowList)
				fileID_5 = open(os.path.join(self.pytchOutputFolder,'FellowListDim.txt'), 'w')
				fileID_5.write('{}\n'.format(FellowListDim))
				fileID_5.close()

				fileID_6 = open(os.path.join(self.pytchOutputFolder,'Delay_MD.txt'), 'w')
				Delay_MD_list = [element for list1 in Delay_7.values() for element in list1]
				for element in Delay_MD_list:
						if element < 0:
								element = 0
						fileID_6.write('{}\n'.format(element))
				fileID_6.close()

				FellowType = FellowType_4.values()
				fileID_7 = open(os.path.join(self.pytchOutputFolder, 'FellowType.txt'), 'w')
				for element in FellowType:
						fileID_7.write('{}\n'.format(element))
				fileID_7.close()

				end = time.time()
				print("Time taken to write results into output files: {} sec".format(end-start))
				# logger.info("FLC25 CEM TPF object retrieval is completed in " + str(elapsed) + " seconds")
				start = time.time()
				self.updateModelDeskScenario()
				end = time.time()
				print("Time taken to update modeldesk parameters: {} sec".format(end - start))

				start = time.time()
				self.updateControlDeskScenario()
				end = time.time()
				print("Time taken to update controldesk parameters: {} sec".format(end - start))

				# Getting absolute distances considering we have control-desk recording
				# controldesk_mat_file_path, common_time, pytchOutputFolder
				if not os.path.exists(self.ControlDeskOutputFolder):
					os.makedirs(self.ControlDeskOutputFolder)
				controldesk_mat_file_path = self.ControlDeskOutputFile
				get_absolute_distaces(controldesk_mat_file_path,self.ControlDeskOutputFolder)

				start = time.time()
				self.updateModelDeskAbsScenario()
				end = time.time()
				print("Time taken to update modeldesk parameters: {} sec".format(end - start))

				return

		def updateModelDeskScenario(self):
			if CONFIG_PATH != "" and DSPACE_EXE_PATH != "":
				command = DSPACE_EXE_PATH + " " + CONFIG_PATH + " " + "--modeldesk"
				process = subprocess.Popen(command, stdout=subprocess.PIPE)
				stdout = process.communicate()[0]
				logger.info(stdout)
			else:
				logger.info("No cfg input provided")

			return

		def updateControlDeskScenario(self):
			if CONFIG_PATH != "" and DSPACE_EXE_PATH != "":
				command = DSPACE_EXE_PATH + " " + CONFIG_PATH + " " + "--controldesk"
				process = subprocess.Popen(command, stdout=subprocess.PIPE)
				stdout = process.communicate()[0]
				logger.info(stdout)
			else:
				logger.info("No cfg input provided")

			return

		def updateModelDeskAbsScenario(self):
			if CONFIG_PATH != "" and DSPACE_EXE_PATH != "":
				command = DSPACE_EXE_PATH + " " + CONFIG_PATH + " " + "--modeldesk_abs"
				process = subprocess.Popen(command, stdout=subprocess.PIPE)
				stdout = process.communicate()[0]
				logger.info(stdout)
			else:
				logger.info("No cfg input provided")

			return

		def filterObjects(self, objectBuffer):  # Returns filters objects considering valid alive(48 time cycles) intervals
				pass

		def prepareModelDeskInputs(self):  # Prepares text files, fellow objects
				"""
				Hello Akshata, Hello Datta,

				As I mentioned before, the python script builds up the scenario in a way,
				that fellows that are not present at the same time are grouped in the ModelDesk scenario.
				This is necessary because ModelDesk can handle only 30 fellows.

				To overcome this limitation we had to reinitialize the fellows in the scenario.
				Obviously, only detections (fellows) that appearance do not overlap in time
				and have the same type can belong to the same fellow in ModelDesk.

				The matlab array FellowListSorted contains the grouped order of detections (fellows)
				as shown on the figure below. Each group contains fellows that appearances do not overlap
				in time in the order of their appearance.

				====================================== Text Files ========================================
				The following txt files are required to run the python script:

				FellowListMDA(i).txt contains the i. element of FellowListSorted
				(the list of the i. group of fellows) as shown on the figure below.

				FellowListDim.txt: number of groups (ModelDesk fellows). (Maximum 30 allowed)

				DelayMD.txt: the length of time interval before a fellow appears
				(for each detection in the original order of detections). In the case of reinitialized
				fellows this is the time that passes after the previous fellow disappears.

				SegmentTimeLength_4.txt: the length of the time interval for that a detection (fellow)
				is present (for each detection in the original order of detections).

				FellowType.txt: type of detected fellows in the original order of detections.

				EgoTimeLength.txt: the length of the time interval for that the ego vehicle is present.
				This equals the length of the time segment that was selected for the simulation.

				I hope the above is useful to you. Please feel free to contact me if you have any further questions.

				"""

				pass


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"C:\Users\wattamwa\Desktop\measurements\dSpace_Exporter\HMC-QZ-STR__2021-03-02_13-57-57.h5"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		manager_modules.calc('fill_dspace_resim@aebs.fill', manager)
