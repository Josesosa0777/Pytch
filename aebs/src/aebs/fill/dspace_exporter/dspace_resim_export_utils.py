import ConfigParser
import logging
import sys

import scipy.io
import numpy as np
import os
import subprocess
import time
from aebs.fill.dspace_exporter.readmat73 import loadmat

BUFFER_SIZE = 100
# DSPACE_EXE_PATH = os.path.join(os.path.dirname(__file__), "dSpace_scenario_generator","dSpace_scenario_generator.exe")
# CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.cfg")
DSPACE_EXE_PATH = os.path.join(os.path.dirname(__file__), "dSpace_scenario_generator","dSpace_scenario_generator.exe")
CONFIG_PATH = os.path.join(os.path.dirname(__file__),  "config.cfg")

MODELDESK_OBJECT_TYPE = {'car' : 1, 'truck' : 2, 'motorcycle':3, 'pedestrian' : 4, 'bicycle' : 5, 'unknown' : 6} # TODO check modeldesk type enums

ALL_OK = True

def getModelDeskObjectTypes(sensorObjTypes, sensorMapping):
	uniqueObjTypes = np.unique(sensorObjTypes)

	for sensorObjType in uniqueObjTypes:
		try:
			type = MODELDESK_OBJECT_TYPE[sensorMapping[sensorObjType]]
		except:
			logging.getLogger("dSpace_resim_export_utils").critical("Sensor object type={} is not include in MODELDESK_OBJECT_TYPE".format(sensorMapping[sensorObjType]))
			type = 6
		sensorObjTypes = np.where(sensorObjTypes==sensorObjType, type, sensorObjTypes)

	return sensorObjTypes

def config_setting(CONFIG_PATH):
		config = ConfigParser.ConfigParser()
		pytchOutputFolder = None
		if config.read(CONFIG_PATH):
			pytchOutputFolder = config.get("ModelDeskProject", "MatlabOutputFolder")
			ControlDeskOutputFolder = config.get("ControlDeskProject", "ControlDeskOutputFolder")
			ControlDeskOutputFile = config.get("ControlDeskProject", "ControlDeskOutputFile")
		return pytchOutputFolder, ControlDeskOutputFolder, ControlDeskOutputFile

# TODO re-define entire logic while debugging matlab script
def get_absolute_distaces(controldesk_mat_file_path, pytchOutputFolder):
		global ALL_OK
		if not ALL_OK:
			return False
		# Loading the fused data
		controldesk_matfile_obj = loadmat(controldesk_mat_file_path)
		if controldesk_matfile_obj:
				mat_file_variable = os.path.splitext(os.path.basename(controldesk_mat_file_path))[0]
				controldesk_matfile_obj = controldesk_matfile_obj[mat_file_variable]
		end = controldesk_matfile_obj['Y'][0]['Data'].size

		FellowDistance_orig_4 = {}  # ModelDesk table vectors, all detections separated (each detection correpsponds
		# to a fellow)
		FellowLateralOffset_orig_4 = {}
		ASMTime_4 = {}
		SegmentTimeLength_4 = {}
		signal_present_4 = {}  # Time stamps where detection is present, separated
		FellowType_4 = {}

		Delay_4 = {}
		Delay_44 = {}

		BUFFER_ROW_SIZE = (len(controldesk_matfile_obj["Y"]) - 2) / 2
		BUFFER_COL_SIZE = controldesk_matfile_obj['Y'][0]['Data'][107:].size
		FILTERED_BUFFER_ROW_SIZE = 0
		for nnn in range(BUFFER_ROW_SIZE):
				if np.count_nonzero(controldesk_matfile_obj["Y"][nnn]["Data"]) != 0:
						FILTERED_BUFFER_ROW_SIZE += 1

		ASMTime_orig = np.zeros(shape = [FILTERED_BUFFER_ROW_SIZE, BUFFER_COL_SIZE])
		FellowLateralOffset_orig = np.zeros(shape = [FILTERED_BUFFER_ROW_SIZE, BUFFER_COL_SIZE])
		FellowDistance_orig = np.zeros(shape = [FILTERED_BUFFER_ROW_SIZE, BUFFER_COL_SIZE])
		ModelDeskType_orig = np.zeros(shape = [FILTERED_BUFFER_ROW_SIZE, BUFFER_COL_SIZE])

		# Movement data of the fellow vehicles
		for nnn in range(BUFFER_ROW_SIZE):
				if np.count_nonzero(controldesk_matfile_obj["Y"][nnn]["Data"]) != 0:
						ASMTime_orig[nnn, :] = controldesk_matfile_obj['Y'][len(controldesk_matfile_obj['Y'])-1]['Data'][107:end]
						FellowLateralOffset_orig[nnn, :] = controldesk_matfile_obj['Y'][nnn]['Data'][107:end]
						FellowDistance_orig[nnn, :] = controldesk_matfile_obj['Y'][nnn + BUFFER_ROW_SIZE]['Data'][107:end]
		ASMTime = ASMTime_orig
		# Generating the new array of the fellow vehicle order
		nn = 0
		time_unit = controldesk_matfile_obj["Y"][-1]["Data"][-1]/ len(controldesk_matfile_obj['Y'][len(controldesk_matfile_obj['Y']) - 1]['Data'])
		FellowOrder = np.zeros(len(FellowDistance_orig))


		for ii in range(FILTERED_BUFFER_ROW_SIZE):
				mm =0
				# nn = 1; needed for FellowDistance_orig_4_struct...
				mlast = 0
				END_COUNT = len(FellowDistance_orig[ii, :])  # TODO can be taken out of loop
				# Generating cell arrays containing all detections separated
				if FellowDistance_orig[ii][0] != 0:  # Fellow Object detected from begining of interval
						mfirst = 0
						while (mm < END_COUNT - 1) and (FellowDistance_orig[ii][mm + 1] != 0):
								mm = mm + 1
						mlast = mm
						FellowDistance_orig_4[nn] = FellowDistance_orig[ii][mfirst:mlast]
						FellowLateralOffset_orig_4[nn] = FellowLateralOffset_orig[ii][mfirst:mlast]
						ASMTime_4[nn] = ASMTime_orig[0, 0:mm - mfirst + 1] #ASMTime[0, 0:mm - mfirst + 1]
						# Delay_4[nn] = 0
						SegmentTimeLength_4[nn] = mm * time_unit
						Delay_44[nn] = 0
						signal_present_4[nn] = range(mfirst, mlast + 1, 1)
						# FellowType_4[nn] = np.bincount(np.array(ModelDeskType_orig[ii][mfirst:mm], dtype = int)).argmax()
						FellowType_4[nn] = 1
						FellowOrder[ii] = FellowOrder[ii] + 1
						mm = mm + 1
						nn = nn + 1

				while mm < END_COUNT - 1:
						if FellowDistance_orig[ii][mm] == 0 and FellowDistance_orig[ii][mm + 1] != 0:
								mfirst = mm + 1
								while (mm < END_COUNT - 1) and (FellowDistance_orig[ii][mm + 1] != 0):
										mm = mm + 1
								Delay_44[nn] = (mfirst - mlast) * time_unit
								mlast = mm
								FellowDistance_orig_4[nn] = FellowDistance_orig[ii, mfirst:mlast]
								FellowLateralOffset_orig_4[nn] = FellowLateralOffset_orig[ii, mfirst:mlast]
								ASMTime_4[nn] = ASMTime_orig[0, 0:mm - mfirst + 1]

								SegmentTimeLength_4[nn] = (mlast - mfirst) * time_unit
								signal_present_4[nn] = range(mfirst, mlast + 1, 1)
								# FellowType_4[nn] = np.bincount(np.array(ModelDeskType_orig[ii][mfirst:mm], dtype = int)).argmax()
								FellowType_4[nn] = 1
								FellowOrder[ii] = FellowOrder[ii] + 1
								mm = mm + 1
								nn = nn + 1
						else:
								mm = mm + 1


		# Exporting the ModelDesk table of the fellow vehicles to a MAT file
		for nnn in range(0, len(ASMTime_4.keys())):
				ASMTime = ASMTime_4[nnn]
				FellowDistance = FellowDistance_orig_4[nnn]
				FellowLateralOffset = FellowLateralOffset_orig_4[nnn]
				FellowDict = {}
				if len(FellowDistance) < len(ASMTime):
						ASMTime = ASMTime[1:]
				FellowDict['ASMTime'] = ASMTime
				FellowDict['FellowPosition'] = FellowDistance
				FellowDict['FellowLateralOffset'] = FellowLateralOffset
				FelloMovementName = "FellowMovement" + str(nnn) + ".mat"
				scipy.io.savemat(os.path.join(pytchOutputFolder, FelloMovementName), FellowDict)

		fileID_6 = open(os.path.join(pytchOutputFolder, 'FellowOrder.txt'), 'w')
		for element in FellowOrder:
				fileID_6.write('{}\n'.format(int(element)))
		fileID_6.close()

		fileID_6 = open(os.path.join(pytchOutputFolder, 'SegmentTimeLength_4.txt'), 'w')
		for element in SegmentTimeLength_4.values():
				fileID_6.write('{}\n'.format(element))
		fileID_6.close()

		fileID_6 = open(os.path.join(pytchOutputFolder, 'Delay_MD.txt'), 'w')
		for element in Delay_44.values():
				fileID_6.write('{}\n'.format(element))
		fileID_6.close()


def preprocess_dspace_resimulation_data(SelectedObjectBuffers, common_time, ResimStartTime, ResimEndtTime,
																				measurementFilePath,logger):
		global ALL_OK
		if not ALL_OK :
			return False
		start = time.time()
		cem_tpf_objectbufferdict = prepare_object_buffers(SelectedObjectBuffers, common_time)
		# common_time = get_common_time(measurementFilePath)
		ego_orig_export = get_egomotion(measurementFilePath)

		l_data = len(common_time)
		filtered_objects = []
		limit = 48

		valid_detection_mx = np.zeros(shape = [BUFFER_SIZE, l_data])
		ModelDeskType_mx = np.zeros(shape = [BUFFER_SIZE, l_data])
		filtered_dx_type_mx = np.zeros(
						shape = [BUFFER_SIZE, l_data])  # contains filtered_dx_type vector for each of the object buffers
		filtered_dy_type_mx = np.zeros(
						shape = [BUFFER_SIZE, l_data])  # contains filtered_dy_type vector for each of the object buffers

		time_unit = (common_time[l_data - 1] - common_time[0]) / l_data
		for id, objectDict in cem_tpf_objectbufferdict.iteritems():
				i = id
				alive_intervals = objectDict['alive_intervals']
				if len(alive_intervals)==0:
						continue

				# Prepare masks
				valid_filter_object_mask = (objectDict["dx"] > 0) & (objectDict["video_conf"] > 0)
				for interval_start, interval_end in alive_intervals:
						alive_interval_cycles = interval_end - interval_start
						alive_ahead_cycles = len(objectDict["dx"][objectDict["dx"][interval_start:interval_end + 1] > 0])
						if alive_ahead_cycles <= limit:  # 48 time cycles
								valid_filter_object_mask[interval_start:interval_end] = False

				valid_object = np.array(valid_filter_object_mask, dtype = int)
				# objectDict["object_type"][:] = 1 #TODO Check why object type info missing
				modeldesk_type = objectDict["object_type"]
				modeldesk_type[~valid_filter_object_mask] = 0
				valid_obj_type_mask = (objectDict["object_type"] == 1) | (objectDict["object_type"] == 2) | (
								objectDict["object_type"] == 6)
				valid_filter_object_mask = valid_filter_object_mask & valid_obj_type_mask
				# Obj_type: 8377=2
				objectDict["dx"][~valid_filter_object_mask] = 0
				objectDict["dy"][~valid_filter_object_mask] = 0

				# o["ModelDeskType"] = modeldesk_type
				# o["dx"] = raw_object["dx"]
				# o["dy"] = raw_object["dy"]
				filtered_dx_type_mx[i, :] = objectDict["dx"]
				filtered_dy_type_mx[i, :] = objectDict["dy"]
				ModelDeskType_mx[i, :] = modeldesk_type
				valid_detection_mx[i, :] = valid_object
		# filtered_objects.append(o)

		count = 0
		valid_objectbuffer = np.zeros(shape = BUFFER_SIZE)
		for kk in range(0, BUFFER_SIZE):  # TODO 23rd buffer has all zeros: Check it out
				if np.count_nonzero(filtered_dx_type_mx[kk, :]) == 0:
						valid_objectbuffer[kk] = -1
				else:
						count = count + 1
						valid_objectbuffer[kk] = kk



		# TODO ego_orig_export +  cem_tpf_buffers
		# TODO in matlab script they did not rescaled ego: Here after rescaling results may differ
		ego_orig_export_tmp = ego_orig_export.rescale(common_time)
		# Handling the detection of different fellow vehicles for selected time segment

		# time interval of the simulation
		# max(0, Time.searchsorted(Time, side='right')-1)
		startPoint = max(0, common_time.searchsorted(ResimStartTime, side = 'right') - 1)  # video time 1.614694009e9;
		endPoint = max(0, common_time.searchsorted(ResimEndtTime, side = 'right') - 1) +1  # video time 1.614694062e9;

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

		FellowDistanceTemp = np.zeros(shape = [BUFFER_SIZE, endPoint - startPoint])
		FellowLateralOffsetTemp = np.zeros(shape = [BUFFER_SIZE, endPoint - startPoint])
		ModelDeskTypeTemp = np.zeros(shape = [BUFFER_SIZE, endPoint - startPoint])

		for ii in range(0, BUFFER_SIZE):
				FellowDistanceTemp[ii, :] = filtered_dx_type_mx[ii, startPoint: endPoint]
				FellowLateralOffsetTemp[ii, :] = filtered_dy_type_mx[ii, startPoint: endPoint]
				EgoSpeedTemp = ego_orig_export_tmp.vx[startPoint:endPoint]  # TODO in matlab script they did not rescaled ego
				ModelDeskTypeTemp[ii, :] = ModelDeskType_mx[ii, startPoint: endPoint]

				end = len(ASMTimeTemp) - 1
				# Shifting arrays if consecutive time is same
				for j in range(0, len(ASMTimeTemp) - 1):
						if (j != len(ASMTimeTemp)):
								if ASMTimeTemp[j] == ASMTimeTemp[j + 1]:
										ASMTimeTemp[j:  end -1] = ASMTimeTemp[j + 1: end]
										ASMTimeTemp[end] = 0
										FellowDistanceTemp[ii, j: end - 1] = FellowDistanceTemp[ii, j + 1: end]
										FellowDistanceTemp[ii, end] = 0
										FellowLateralOffsetTemp[ii, j: end - 1] = FellowLateralOffsetTemp[ii, j + 1: end]
										FellowLateralOffsetTemp[ii, end] = 0
										EgoSpeedTemp[j: end - 1] = EgoSpeedTemp[j + 1: end]
										EgoSpeedTemp[end] = 0
										ModelDeskTypeTemp[ii, j: end - 1] = ModelDeskTypeTemp[ii, j + 1: end]
										ModelDeskTypeTemp[ii, end] = 0
				ASMTime = np.zeros(shape = np.count_nonzero(ASMTimeTemp_1) + 1)
				EgoSpeed_orig = np.zeros(shape = np.count_nonzero(ASMTimeTemp_1) + 1)

				j = 1
				# Copy cleaned data to orig: left-shifted non-zeros corresponding ASMTime elements
				FellowDistance_orig[ii][0] = FellowDistanceTemp[ii, 0]
				FellowLateralOffset_orig[ii][0] = FellowLateralOffsetTemp[ii, 0]
				EgoSpeed_orig[0] = EgoSpeedTemp[0]
				ModelDeskType_orig[ii][0] = ModelDeskTypeTemp[ii, 0]
				while ASMTimeTemp_1[j] != 0:
						ASMTime[j] = ASMTimeTemp_1[j]
						FellowDistance_orig[ii][j] = FellowDistanceTemp[ii, j]
						FellowLateralOffset_orig[ii][j] = FellowLateralOffsetTemp[ii, j]
						EgoSpeed_orig[j] = EgoSpeedTemp[j]
						ModelDeskType_orig[ii][j] = ModelDeskTypeTemp[ii, j]
						j = j + 1

				mm = 1
				mlast = 0
				END_COUNT = len(FellowDistance_orig[ii, :])  # TODO can be taken out of loop
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
						signal_present_4[nn] = range(mfirst, mlast + 1, 1)
						FellowType_4[nn] = np.bincount(np.array(ModelDeskType_orig[ii][mfirst:mm], dtype = int)).argmax()
						mm = mm + 1
						nn = nn + 1
				while mm < END_COUNT - 1:
						if FellowDistance_orig[ii][mm] == 0 and FellowDistance_orig[ii][mm + 1] != 0:
								mfirst = mm + 1
								while (mm < END_COUNT - 1) and (FellowDistance_orig[ii][mm + 1] != 0):
										mm = mm + 1
								mlast = mm
								FellowDistance_orig_4[nn] = FellowDistance_orig[ii][mfirst:mlast]
								FellowLateralOffset_orig_4[nn] = FellowLateralOffset_orig[ii][mfirst:mlast]
								ASMTime_4[nn] = ASMTime[1:mm - mfirst + 1]

								SegmentTimeLength_4[nn] = (mlast - mfirst) * time_unit
								# Delay_4[nn] = mfirst * time_unit
								signal_present_4[nn] = range(mfirst,  mlast + 1, 1)
								FellowType_4[nn] = np.bincount(np.array(ModelDeskType_orig[ii][mfirst:mm], dtype = int)).argmax()
								mm = mm + 1
								nn = nn + 1
						else:
								mm = mm + 1


				if np.sum(FellowDistance_orig[ii][:]) != 0:
						FellowsToModelDesk.append(ii)  # ToDO

				EgoTimeLength = (endPoint - startPoint) * time_unit
		end = time.time()
		logger.info("dSpace inputs prepared in {} sec".format(end - start))
		start = time.time()
		pytchOutputFolder, ControlDeskOutputFolder, ControlDeskOutputFile = config_setting(CONFIG_PATH)
		try:
			if not os.path.exists(pytchOutputFolder):
					os.makedirs(pytchOutputFolder)
			if not os.path.exists(ControlDeskOutputFolder):
					os.makedirs(ControlDeskOutputFolder)
			ego_start_found = False
			model_files = os.listdir(pytchOutputFolder)
			for name in model_files:
				if "EgoStart.mat" not in name:
					os.remove(os.path.join(pytchOutputFolder,name))
				else:
					ego_start_found = True
			if not ego_start_found:
				logger.error("EgoStart.mat is missing at location {}".format(pytchOutputFolder))
				ALL_OK = False
				return

			control_files = os.listdir(ControlDeskOutputFolder)
			for name in control_files:
					os.remove(os.path.join(ControlDeskOutputFolder,name))

			# os.remove(ControlDeskOutputFile)

		except Exception as e:
			logger.error("It looks like given folder and project paths are incorrect.\n"
				  "{}\n{}\n{}\n, please update below configuration file with correct paths:\n {}"
				  .format(pytchOutputFolder,ControlDeskOutputFolder,
										ControlDeskOutputFile, CONFIG_PATH))

			logger.warning(str(e))
			ALL_OK = False
			return
		ASMvDesired = 3.6 * EgoSpeed_orig
		EgoDict = {}
		EgoDict['ASMTime'] = ASMTime
		EgoDict['ASMvDesired'] = ASMvDesired
		scipy.io.savemat(os.path.join(pytchOutputFolder, 'EgoMovement.mat'), EgoDict)

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
				scipy.io.savemat(os.path.join(pytchOutputFolder, FelloMovementName), FellowDict)

		# Grouping of non - overlapping(time and type) detections
		FellowList = dict({0: {0}})
		FellowListUnion = dict({0: set(signal_present_4[0])})
		FellowTypeUnion = dict({0: {FellowType_4[0]}})
		for j in range(1, len(signal_present_4)):
				jj = 0
				while (jj < len(FellowListUnion)):
						if sum(FellowListUnion[jj].intersection(signal_present_4[j])) == 0 and \
										sum(FellowTypeUnion[jj].intersection({FellowType_4[j]})) != 0:  # TODO FellowType_4 convert to set
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
						firstElement[hh][gg] = signal_present_4[ind][0]  # TODO
				sortedIndexes = sorted(range(len(firstElement[hh])), key = firstElement[hh].__getitem__)
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
				indd01 = FellowListModelDesk[z][0]  # TODO 0 or 1
				Delay_7[z][0] = (signal_present_4[indd01][0] - 1) * time_unit
				Segment_Time_Length[z][0] = SegmentTimeLength_4[indd01]
				for zz in range(1, len(FellowListModelDesk[z])):
						indd1 = FellowListModelDesk[z][zz]
						indd2 = FellowListModelDesk[z][zz - 1]
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
				fileID_string[aa] = open(os.path.join(pytchOutputFolder, 'FellowListMDA{}.txt'.format(str(aa))), 'w')
				for element in FellowListMDA:
						fileID_string[aa].write('{}\n'.format(element))
				fileID_string[aa].close()
		fileID_2 = open(os.path.join(pytchOutputFolder, 'SegmentTimeLength_4.txt'), 'w')
		SegmentTimeLength_4_List = [element for list1 in Segment_Time_Length.values() for element in list1]
		for element in SegmentTimeLength_4_List:
				fileID_2.write('{}\n'.format(element))
		fileID_2.close()

		fileID_4 = open(os.path.join(pytchOutputFolder, 'EgoTimeLength.txt'), 'w')
		fileID_4.write('{}\n'.format(EgoTimeLength))
		fileID_4.close()

		FellowListDim = len(FellowList)
		fileID_5 = open(os.path.join(pytchOutputFolder, 'FellowListDim.txt'), 'w')
		fileID_5.write('{}\n'.format(FellowListDim))
		fileID_5.close()

		fileID_6 = open(os.path.join(pytchOutputFolder, 'Delay_MD.txt'), 'w')
		Delay_MD_list = [element for list1 in Delay_7.values() for element in list1]
		for element in Delay_MD_list:
				if element < 0:
						element = 0
				fileID_6.write('{}\n'.format(element))
		fileID_6.close()

		FellowType = FellowTypeUnion.values()
		fileID_7 = open(os.path.join(pytchOutputFolder, 'FellowType.txt'), 'w')
		for element in FellowType:
				fileID_7.write('{}\n'.format(list(element)[0]))
		fileID_7.close()

		end = time.time()
		logger.info("Time taken to write results into output files: {} sec".format(end - start))

		start = time.time()
		updateModelDeskScenario(logger)
		end = time.time()
		logger.info("Time taken to update modeldesk parameters: {} sec".format(end - start))

		start = time.time()
		updateControlDeskScenario(logger)
		end = time.time()
		logger.info("Time taken to update controldesk parameters: {} sec".format(end - start))

		controldesk_mat_file_path = ControlDeskOutputFile
		get_absolute_distaces(controldesk_mat_file_path, ControlDeskOutputFolder)

		start = time.time()
		updateModelDeskAbsScenario(logger)
		end = time.time()
		logger.info("Time taken to update modeldesk with absolute distance parameters: {} sec".format(end - start))

def updateModelDeskScenario(logger):
		if CONFIG_PATH != "" and DSPACE_EXE_PATH != "":
				command = DSPACE_EXE_PATH + " " + CONFIG_PATH + " " + "--modeldesk"
				process = subprocess.Popen(command, stdout = subprocess.PIPE)
				stdout = process.communicate()[0]
				logger.info(stdout)
		else:
				logger.warning("No cfg input provided")

		return

def updateControlDeskScenario(logger):
	if CONFIG_PATH != "" and DSPACE_EXE_PATH != "":
		command = DSPACE_EXE_PATH + " " + CONFIG_PATH + " " + "--controldesk"
		process = subprocess.Popen(command, stdout=subprocess.PIPE)
		stdout = process.communicate()[0]
		logger.info(stdout)
	else:
		logger.warning("No cfg input provided")

	return
def updateModelDeskAbsScenario(logger):
	if CONFIG_PATH != "" and DSPACE_EXE_PATH != "":
		command = DSPACE_EXE_PATH + " " + CONFIG_PATH + " " + "--modeldesk_abs"
		process = subprocess.Popen(command, stdout=subprocess.PIPE)
		stdout = process.communicate()[0]
		logger.info(stdout)
	else:
		logger.warning("No cfg input provided")

def prepare_object_buffers(SelectedObjectBuffers, common_time):
		sensorMapping = []
		try:
			sensorMapping = SelectedObjectBuffers.values()[0]["extraData"]['obj_type_mapping'][0]
		except:
			sensorMapping = {
				0: 'Car', 1: 'Truck', 2: 'Motorcycle', 3: 'Pedestrian', 4: 'Bicycle', 5: 'Unknown', 6: 'point',
				7: 'wide'
			}
		cem_tpf_objectbufferlist = {}
		for i in range(100):
				o = {}
				o["time"] = np.zeros_like(common_time)
				o["dx"] = np.zeros_like(common_time)
				o["dy"] = np.zeros_like(common_time)
				o["alive_intervals"] = []
				o["video_conf"] = np.zeros_like(common_time)
				o["object_type"] = np.zeros_like(common_time)
				cem_tpf_objectbufferlist[i] = o


		for key, value in SelectedObjectBuffers.iteritems():

				id = int(key.split("_")[-2])
				start = value['time'][0]
				end = value['time'][-1]
				start_idx = max(0, common_time.searchsorted(start, side = 'right') - 1)
				end_idx = start_idx + len(value[u'longitudinal_distance'])
				cem_tpf_objectbufferlist[id]['dx'][start_idx:end_idx] = value[u'longitudinal_distance']
				cem_tpf_objectbufferlist[id]['dy'][start_idx:end_idx] = value[u'lateral_distance']
				cem_tpf_objectbufferlist[id]['alive_intervals'].append((start_idx,end_idx,))
				cem_tpf_objectbufferlist[id]['video_conf'][start_idx:end_idx] = value['extraData']['video_conf']
				cem_tpf_objectbufferlist[id]['object_type'][start_idx:end_idx] = getModelDeskObjectTypes(value['extraData'][u'obj_type'], sensorMapping)
				cem_tpf_objectbufferlist[id]['time'] = common_time

		return cem_tpf_objectbufferlist


def get_egomotion(measurement_file_path):
		from config.Config import init_dataeval
		meas_path = measurement_file_path
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		ego_motion = manager_modules.calc('calc_egomotion_resim@aebs.fill', manager)
		return ego_motion

# def get_common_time(measurement_file_path):
# 		from config.Config import init_dataeval
# 		meas_path = measurement_file_path
# 		config, manager, manager_modules = init_dataeval(['-m', meas_path])
# 		common_time = manager_modules.calc('calc_common_time-flc25@aebs.fill', manager)
# 		return common_time

if __name__ == "__main__":
		controldesk_mat_file_path = r"C:\KBData\exp1_.mat"
		pytchOutputFolder = r"E:\TCI_Akshata\output\tmp"
		get_absolute_distaces(controldesk_mat_file_path, pytchOutputFolder)