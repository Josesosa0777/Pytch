# -*- dataeval: init -*-
# -*- coding: utf-8 -*-
import logging

import numpy as np
import numpy.ma as ma
from flr20_raw_tracks_base import ObjectFromMessage
from interface import iCalc
from measproc import cIntervalList
from measproc.IntervalList import maskToIntervals
from metatrack import BlinkerStatus, BrakeLightStatus, LaneStatus, MovingDirection, MovingState, ObjectType, \
		TrackingState
from primitives.bases import PrimitiveCollection
from pyutils.enum import enum

TRACK_MESSAGE_NUM = 20

MOTION_ST_VALS = (
		'MOVING',
		'STATIONARY',
		'ONCOMING',
		'CROSSING_LEFT',
		'CROSSING_RIGHT',
		'UNKNOWN',
		'STOPPED',
)

LANE_ST_VALS = (
		'UNKNOWN',
		'FAR_LEFT',
		'LEFT',
		'EGO',
		'RIGHT',
		'FAR_RIGHT',
)

OBJ_CLASS_VALS = (
		'NONE',
		'UNKNOWN',
		'CAR',
		'TRUCK',
		'PEDESTRIAN',
		'CYCLIST',
		'MOTORBIKE',
		'MAX_VALUE',
)
BRAKE_LIGHT_VALS = (
		'UNKNOWN',
		'NO_BRAKING',
		'REGULAR_BRAKING',
		'HEAVY_BREAKING',
		'SNA',
)
INDICATOR_VALS = (
		'UNKNOWN',
		'NO_FLASHING',
		'FLASHING_LEFT',
		'FLASHING_RIGHT',
		'HAZARD_FLASHING',
)

MOTION_STATUS = enum(**dict((name, n) for n, name in enumerate(MOTION_ST_VALS)))
LANE_STATUS = enum(**dict((name, n) for n, name in enumerate(LANE_ST_VALS)))
OBJ_CLASS = enum(**dict((name, n) for n, name in enumerate(OBJ_CLASS_VALS)))
BRAKE_LIGHT_ST = enum(**dict((name, n) for n, name in enumerate(BRAKE_LIGHT_VALS)))
INDICATOR_ST = enum(**dict((name, n) for n, name in enumerate(INDICATOR_VALS)))

signalTemplate = (
		("EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObjectI%dI_General_uiID"),
		("EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObjectI%dI_Kinematic_fAabsX"),
		("EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObjectI%dI_Kinematic_fAabsXStd"),
		("EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObjectI%dI_Kinematic_fAabsY"),
		("EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObjectI%dI_Kinematic_fAabsYStd"),
		("EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObjectI%dI_Kinematic_fArelX"),
		("EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObjectI%dI_Kinematic_fArelXStd"),
		("EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObjectI%dI_Kinematic_fArelY"),
		("EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObjectI%dI_Kinematic_fArelYStd"),
		("EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObjectI%dI_Kinematic_fDistX"),
		("EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObjectI%dI_Kinematic_fDistXStd"),
		("EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObjectI%dI_Kinematic_fDistY"),
		("EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObjectI%dI_Kinematic_fDistYStd"),
		("EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObjectI%dI_Kinematic_fVabsX"),
		("EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObjectI%dI_Kinematic_fVabsXStd"),
		("EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObjectI%dI_Kinematic_fVabsY"),
		("EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObjectI%dI_Kinematic_fVabsYStd"),
		("EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObjectI%dI_Kinematic_fVrelX"),
		("EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObjectI%dI_Kinematic_fVrelXStd"),
		("EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObjectI%dI_Kinematic_fVrelY"),
		("EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObjectI%dI_Kinematic_fVrelYStd"),
		("EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObjectI%dI_Qualifiers_uiProbabilityOfExistence"),
		("EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObjectI%dI_Attributes_eClassification"),
		("EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObjectI%dI_Attributes_eDynamicProperty"),
		("EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObjectI%dI_Attributes_uiClassConfidence"),
		("EmCamObjectList", "MFC5xx_Device_EM_EmCamObjectList_aObjectI%dI_Attributes_eAssociatedLane"),
		("EmCamObjectList", "MFC5xx_Device_EM_EmCamObjectList_aObjectI%dI_Attributes_eStatusBrakeLight"),
		("EmCamObjectList", "MFC5xx_Device_EM_EmCamObjectList_aObjectI%dI_Attributes_eStatusTurnIndicator"),
		("EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObjectI%dI_Qualifiers_eEbaObjClass"),
		("EmCamObjectList", "MFC5xx_Device_EM_EmCamObjectList_aObjectI%dI_Kinematic_fYaw"),
		("EmCamObjectList", "MFC5xx_Device_EM_EmCamObjectList_aObjectI%dI_Kinematic_fYawStd"),
		("EmCamObjectList", "MFC5xx_Device_EM_EmCamObjectList_aObjectI%dI_Kinematic_fDistZ"),
		("EmCamObjectList", "MFC5xx_Device_EM_EmCamObjectList_aObjectI%dI_Kinematic_fDistZStd"),
		("EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObjectI%dI_General_eMaintenanceState"),
		("EmCamObjectList","MFC5xx_Device_EM_EmCamObjectList_aObjectI%dI_Geometry_fWidth"),
		("EmCamObjectList","MFC5xx_Device_EM_EmCamObjectList_aObjectI%dI_Geometry_fLength"),
		("EmCamObjectList","MFC5xx_Device_EM_EmCamObjectList_aObjectI%dI_Geometry_fHeight"),
		("EmCamObjectList","MFC5xx_Device_EM_EmCamObjectList_aObjectI%dI_Attributes_uiAssociatedLaneConfidence"),

)

signalTemplatesh5 = (
		("MFC5xx Device.EM.EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObject%d_General_uiID"),
		("MFC5xx Device.EM.EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObject%d_Kinematic_fAabsX"),
		("MFC5xx Device.EM.EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObject%d_Kinematic_fAabsXStd"),
		("MFC5xx Device.EM.EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObject%d_Kinematic_fAabsY"),
		("MFC5xx Device.EM.EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObject%d_Kinematic_fAabsYStd"),
		("MFC5xx Device.EM.EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObject%d_Kinematic_fArelX"),
		("MFC5xx Device.EM.EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObject%d_Kinematic_fArelXStd"),
		("MFC5xx Device.EM.EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObject%d_Kinematic_fArelY"),
		("MFC5xx Device.EM.EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObject%d_Kinematic_fArelYStd"),
		("MFC5xx Device.EM.EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObject%d_Kinematic_fDistX"),
		("MFC5xx Device.EM.EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObject%d_Kinematic_fDistXStd"),
		("MFC5xx Device.EM.EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObject%d_Kinematic_fDistY"),
		("MFC5xx Device.EM.EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObject%d_Kinematic_fDistYStd"),
		("MFC5xx Device.EM.EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObject%d_Kinematic_fVabsX"),
		("MFC5xx Device.EM.EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObject%d_Kinematic_fVabsXStd"),
		("MFC5xx Device.EM.EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObject%d_Kinematic_fVabsY"),
		("MFC5xx Device.EM.EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObject%d_Kinematic_fVabsYStd"),
		("MFC5xx Device.EM.EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObject%d_Kinematic_fVrelX"),
		("MFC5xx Device.EM.EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObject%d_Kinematic_fVrelXStd"),
		("MFC5xx Device.EM.EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObject%d_Kinematic_fVrelY"),
		("MFC5xx Device.EM.EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObject%d_Kinematic_fVrelYStd"),
		("MFC5xx Device.EM.EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObject%d_Qualifiers_uiProbabilityOfExistence"),
		("MFC5xx Device.EM.EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObject%d_Attributes_eClassification"),
		("MFC5xx Device.EM.EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObject%d_Attributes_eDynamicProperty"),
		("MFC5xx Device.EM.EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObject%d_Attributes_uiClassConfidence"),
		("MFC5xx Device.EM.EmCamObjectList", "MFC5xx_Device_EM_EmCamObjectList_aObject%d_Attributes_eAssociatedLane"),
		("MFC5xx Device.EM.EmCamObjectList", "MFC5xx_Device_EM_EmCamObjectList_aObject%d_Attributes_eStatusBrakeLight"),
		("MFC5xx Device.EM.EmCamObjectList", "MFC5xx_Device_EM_EmCamObjectList_aObject%d_Attributes_eStatusTurnIndicator"),
		("MFC5xx Device.EM.EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObject%d_Qualifiers_eEbaObjClass"),
		("MFC5xx Device.EM.EmCamObjectList", "MFC5xx_Device_EM_EmCamObjectList_aObject%d_Kinematic_fYaw"),
		("MFC5xx Device.EM.EmCamObjectList", "MFC5xx_Device_EM_EmCamObjectList_aObject%d_Kinematic_fYawStd"),
		("MFC5xx Device.EM.EmCamObjectList", "MFC5xx_Device_EM_EmCamObjectList_aObject%d_Kinematic_fDistZ"),
		("MFC5xx Device.EM.EmCamObjectList", "MFC5xx_Device_EM_EmCamObjectList_aObject%d_Kinematic_fDistZStd"),
		("MFC5xx Device.EM.EmGenObjectList", "MFC5xx_Device_EM_EmGenObjectList_aObject%d_General_eMaintenanceState"),
		("MFC5xx Device.EM.EmCamObjectList","MFC5xx_Device_EM_EmCamObjectList_aObject%d_Geometry_fWidth"),
		("MFC5xx Device.EM.EmCamObjectList","MFC5xx_Device_EM_EmCamObjectList_aObject%d_Geometry_fLength"),
		("MFC5xx Device.EM.EmCamObjectList","MFC5xx_Device_EM_EmCamObjectList_aObject%d_Geometry_fHeight"),
		("MFC5xx Device.EM.EmCamObjectList","MFC5xx_Device_EM_EmCamObjectList_aObject%d_Attributes_uiAssociatedLaneConfidence"),

)

def createMessageGroups(MESSAGE_NUM, signalTemplates):
		messageGroups = []
		for m in xrange(MESSAGE_NUM):
				messageGroup1 = {}
				signalDict = []
				for signalTemplate in signalTemplates:
						fullName = signalTemplate[1] % m
						if "fPosX" in fullName or "fPosY" in fullName:
								full_position_string = fullName.split('_aShapePointCoordinatesI')[1]
								pos_index, pos_string = full_position_string.split('I_')
								shortName = pos_string + pos_index
						else:
								array_signal = signalTemplate[1].split('[')
								if len(array_signal) == 2:
										array_value = array_signal[1].split(',')[1][:-1]
										shortName = array_signal[0].split('_')[-1] + array_value
								else:
										shortName = signalTemplate[1].split('_')[-1]

						messageGroup1[shortName] = (signalTemplate[0], fullName)
				signalDict.append(messageGroup1)

				
				messageGroup2 = {}
				for signalTemplateh5 in signalTemplatesh5:
						fullName = signalTemplateh5[1] % m
						if "fPosX" in fullName or "fPosY" in fullName:
								full_position_string = fullName.split('_aShapePointCoordinatesI')[1]
								pos_index, pos_string = full_position_string.split('I_')
								shortName = pos_string + pos_index
						else:
								array_signal = signalTemplateh5[1].split('[')
								if len(array_signal) == 2:
										array_value = array_signal[1].split(',')[1][:-1]
										shortName = array_signal[0].split('_')[-1] + array_value
								else:
										shortName = signalTemplateh5[1].split('_')[-1]

						messageGroup2[shortName] = (signalTemplateh5[0], fullName)
				signalDict.append(messageGroup2)
				messageGroups.append(signalDict)
		return messageGroups


messageGroups = createMessageGroups(TRACK_MESSAGE_NUM, signalTemplate)


class Flc25EmTrack(ObjectFromMessage):
		attribs = []
		for signalTemplate in signalTemplate:
				fullName = signalTemplate[1]
				if "fPosX" in fullName or "fPosY" in fullName:
						full_position_string = fullName.split('_aShapePointCoordinatesI')[1]
						pos_index, pos_string = full_position_string.split('I_')
						shortName = pos_string + pos_index
				else:
						array_signal = signalTemplate[1].split('[')
						if len(array_signal) == 2:
								array_value = array_signal[1].split(',')[1][:-1]
								shortName = array_signal[0].split('_')[-1] + array_value
						else:
								shortName = signalTemplate[1].split('_')[-1]
				attribs.append(shortName)

		_attribs = tuple(attribs)
		_special_methods = 'alive_intervals'

		def __init__(self, id, time, source, group, invalid_mask, scaletime = None):
				self._invalid_mask = invalid_mask
				self._group = group
				super(Flc25EmTrack, self).__init__(id, time, None, None, scaleTime = None)
				return

		def _create(self, signalName):
				value = self._group.get_value(signalName, ScaleTime = self.time)
				mask = ~self._invalid_mask
				out = np.ma.masked_all_like(value)
				out.data[mask] = value[mask]
				out.mask &= ~mask
				return out

		def id(self):
				data = np.repeat(np.uint8(self._id), self.time.size)
				arr = np.ma.masked_array(data, mask = self._fDistX.mask)
				return arr

		def dx(self):
				return self._fDistX

		def dx_std(self):
				return self._fDistXStd

		def dy(self):
				return self._fDistY

		def dy_std(self):
				return self._fDistYStd

		def range(self):
				return np.sqrt(np.square(self.dx) + np.square(self.dy))

		def angle(self):
				return np.arctan2(self.dy, self.dx)

		def ay(self):
				return self._fArelY

		def ay_abs(self):
				return self._fAabsY

		def ax(self):
				return self._fArelX

		def ax_abs(self):
				return self._fAabsX

		def vx(self):
				return self._fVrelX

		def vx_abs(self):
				return self._fVabsX

		def vy(self):
				return self._fVrelY

		def vy_abs(self):
				return self._fVabsY

		def vx_abs_std(self):
				return self._fVabsXStd

		def vy_abs_std(self):
				return self._fVabsYStd

		def dz(self):
				return self._fDistZ

		def dz_std(self):
				return self._fDistZStd

		def yaw(self):
				return self._fYaw

		def yaw_std(self):
				return self._fYawStd

		def height(self):
				return self._fHeight

		def width(self):
				return self._fWidth

		def length(self):
				return self._fLength

		def ttc(self):
				with np.errstate(divide = 'ignore'):
						ttc = np.where(self.vx < -1e-3,  # avoid too large (meaningless) values
													 -self.dx / self.vx,
													 np.inf)
				return ttc

		def invttc(self):
				return 1. / self.ttc

		def mov_dir(self):
				crossing_left = self._eDynamicProperty == MOTION_STATUS.CROSSING_LEFT
				crossing_right = self._eDynamicProperty == MOTION_STATUS.CROSSING_RIGHT

				stationary = self._eDynamicProperty == MOTION_STATUS.STATIONARY
				stopped = self._eDynamicProperty == MOTION_STATUS.STOPPED
				unknown = self._eDynamicProperty == MOTION_STATUS.UNKNOWN

				ongoing = self._eDynamicProperty == MOTION_STATUS.MOVING
				oncoming = self._eDynamicProperty == MOTION_STATUS.ONCOMING
				undefined = (unknown | stationary | stopped)
				# dummy data
				dummy = np.zeros(self._eDynamicProperty.shape, dtype = bool)
				arr = np.ma.masked_array(dummy, mask = self._fDistX.mask)
				return MovingDirection(oncoming = oncoming, ongoing = ongoing, undefined = undefined, crossing=arr, crossing_left=crossing_left,crossing_right=crossing_right)

		def obj_type(self):
				none_type = self._eEbaObjClass == OBJ_CLASS.NONE
				car = self._eEbaObjClass == OBJ_CLASS.CAR
				truck = self._eEbaObjClass == OBJ_CLASS.TRUCK
				pedestrian = self._eEbaObjClass == OBJ_CLASS.PEDESTRIAN
				motorbike = self._eEbaObjClass == OBJ_CLASS.MOTORBIKE
				cyclist = self._eEbaObjClass == OBJ_CLASS.CYCLIST
				unknown = self._eEbaObjClass == OBJ_CLASS.UNKNOWN
				unknown_max_value = self._eEbaObjClass == 255
				undefined = (none_type | unknown | unknown_max_value)
				dummy = np.zeros(self._eDynamicProperty.shape, dtype = bool)
				arr = np.ma.masked_array(dummy, mask = self._fDistX.mask)
				return ObjectType(unknown = undefined, pedestrian = pedestrian, motorcycle = motorbike, car = car,
													truck = truck,
													bicycle = cyclist, point=arr,wide=arr)

		def mov_state(self):
				crossing_left = self._eDynamicProperty == MOTION_STATUS.CROSSING_LEFT
				crossing_right = self._eDynamicProperty == MOTION_STATUS.CROSSING_RIGHT
				moving = self._eDynamicProperty == MOTION_STATUS.MOVING
				oncoming = self._eDynamicProperty == MOTION_STATUS.ONCOMING
				stationary = self._eDynamicProperty == MOTION_STATUS.STATIONARY
				stopped = self._eDynamicProperty == MOTION_STATUS.STOPPED
				unknown = self._eDynamicProperty == MOTION_STATUS.UNKNOWN
				# dummy data
				dummy = np.zeros(self._eDynamicProperty.shape, dtype = bool)
				arr = np.ma.masked_array(dummy, mask = self._fDistX.mask)
				return MovingState(stat = stationary, stopped = stopped, moving = moving, unknown = unknown,crossing=arr, crossing_left=crossing_left,crossing_right=crossing_right, oncoming=oncoming)

		def tr_state(self):
				valid = ma.masked_array(~self._fDistX.mask, self._fDistX.mask)
				meas = self._eMaintenanceState == 2
				hist = np.ones_like(valid)
				for st, end in maskToIntervals(self._eMaintenanceState == 1):
						if st != 0:
								hist[st] = False
				return TrackingState(valid = valid, measured = meas, hist = hist)

		def lane(self):
				same = self._eAssociatedLane == LANE_STATUS.EGO
				left = self._eAssociatedLane == LANE_STATUS.LEFT
				right = self._eAssociatedLane == LANE_STATUS.RIGHT
				uncorr_left = self._eAssociatedLane == LANE_STATUS.FAR_LEFT
				uncorr_right = self._eAssociatedLane == LANE_STATUS.FAR_RIGHT
				unknown = self._eAssociatedLane == LANE_STATUS.UNKNOWN
				lane = LaneStatus(same = same, left = left, right = right, uncorr_left = uncorr_left,
													uncorr_right = uncorr_right, unknown = unknown)
				return lane

		def brake_light(self):
				unknown_breaking = self._eStatusBrakeLight == BRAKE_LIGHT_ST.UNKNOWN
				no_breaking = self._eStatusBrakeLight == BRAKE_LIGHT_ST.NO_BRAKING
				regular_breaking = self._eStatusBrakeLight == BRAKE_LIGHT_ST.REGULAR_BRAKING
				heavy_breaking = self._eStatusBrakeLight == BRAKE_LIGHT_ST.HEAVY_BREAKING
				sna = self._eStatusBrakeLight == BRAKE_LIGHT_ST.HEAVY_BREAKING
				unknown = (unknown_breaking | sna)
				on = (regular_breaking | heavy_breaking)
				return BrakeLightStatus(on=on, off=no_breaking, unknown=unknown)

		def blinker(self):
				unknwon_blinker = self._eStatusTurnIndicator == INDICATOR_ST.UNKNOWN
				off = self._eStatusTurnIndicator == INDICATOR_ST.NO_FLASHING
				left = self._eStatusTurnIndicator == INDICATOR_ST.FLASHING_LEFT
				right = self._eStatusTurnIndicator == INDICATOR_ST.FLASHING_RIGHT
				both = self._eStatusTurnIndicator == INDICATOR_ST.HAZARD_FLASHING
				return BlinkerStatus(off=off, left=left, right=right, both=both, unknown=unknwon_blinker)

		def video_conf(self):
				return self._uiProbabilityOfExistence

		def lane_conf(self):
				return self._uiAssociatedLaneConfidence

		def alive_intervals(self):
				new = self.tr_state.valid & ~self.tr_state.hist
				validIntervals = cIntervalList.fromMask(self.time, self.tr_state.valid)
				newIntervals = cIntervalList.fromMask(self.time, new)
				alive_intervals = validIntervals.split(st for st, _ in newIntervals)
				return alive_intervals


class Calc(iCalc):
		dep = 'calc_common_time-flc25',

		def check(self):
				modules = self.get_modules()
				source = self.get_source()
				commonTime = modules.fill(self.dep[0])
				groups = []
				for sg in messageGroups:
						groups.append(source.selectSignalGroup(sg))
				return groups, commonTime

		def fill(self, groups, common_time):
				tracks = PrimitiveCollection(common_time)
				signals = messageGroups
				VALID_FLAG = False
				for _id, group in enumerate(groups):
						object_id = group.get_value("uiID", ScaleTime = common_time)
						invalid_mask = (object_id == 255) | (np.isnan(object_id))
#						if np.all(invalid_mask):
#								continue
						VALID_FLAG = True
						tracks[_id] = Flc25EmTrack(_id, common_time, self.source, group, invalid_mask, scaletime = common_time)
				if not VALID_FLAG:
						logging.warning("Error: {} :Measurement does not contain EM object data".format(self.source.FileName))
				return tracks , signals


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"\\pu2w6474\shared-drive\measurements\new_meas_09_11_21\mi5id787__2021-10-28_00-03-59.h5"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		tracks, signals = manager_modules.calc('fill_flc25_em_tracks@aebs.fill', manager)
		print(signals)
		print(tracks)
