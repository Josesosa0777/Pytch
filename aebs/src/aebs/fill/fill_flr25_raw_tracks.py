# -*- dataeval: init -*-
# -*- coding: utf-8 -*-
import logging

import numpy as np
import numpy.ma as ma
from flr20_raw_tracks_base import ObjectFromMessage
from interface import iCalc
from measparser.signalgroup import select_allvalid_sgs
from measproc import cIntervalList
from measproc.IntervalList import maskToIntervals
from metatrack import MovingDirection, MovingState, ObjectType, TrackingState, LaneStatus
from primitives.bases import PrimitiveCollection
from pyutils.enum import enum

AOBJECT_TRACK_MESSAGE_NUM = 40
HYPOTHESIS_TRACK_MESSAGE_NUM = 12
MOTION_ST_VALS = (
		'MOVING',
		'STATIONARY',
		'ONCOMING',
		'STAT_CAND',
		'UNKNOWN',
		'CROSSING_STAT',
		'CROSSING_MOV',
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
		'POINT',
		'CAR',
		'TRUCK',
		'PEDESTRIAN',
		'MOTORCYCLE',
		'BICYCLE',
		'WIDE',
		'UNCLASSIFIED',
)

MOTION_STATUS = enum(**dict((name, n) for n, name in enumerate(MOTION_ST_VALS)))
LANE_STATUS = enum(**dict((name, n) for n, name in enumerate(LANE_ST_VALS)))
OBJ_CLASS = enum(**dict((name, n) for n, name in enumerate(OBJ_CLASS_VALS)))

signalTemplates_EmGenObjectList = (
		("EmGenObjectList", "ARS4xx_Device_DataProcCycle_EmGenObjectList_aObjectI%dI_Kinematic_fDistX"),
		("EmGenObjectList", "ARS4xx_Device_DataProcCycle_EmGenObjectList_aObjectI%dI_General_uiID"),
		("EmGenObjectList", "ARS4xx_Device_DataProcCycle_EmGenObjectList_aObjectI%dI_General_eMaintenanceState"),
		("EmGenObjectList", "ARS4xx_Device_DataProcCycle_EmGenObjectList_aObjectI%dI_General_uiLifeCycles"),
		("EmGenObjectList", "ARS4xx_Device_DataProcCycle_EmGenObjectList_aObjectI%dI_General_fLifeTime"),

		("EmGenObjectList", "ARS4xx_Device_DataProcCycle_EmGenObjectList_aObjectI%dI_Kinematic_fDistY"),
		("EmGenObjectList", "ARS4xx_Device_DataProcCycle_EmGenObjectList_aObjectI%dI_Kinematic_fVrelX"),
		("EmGenObjectList", "ARS4xx_Device_DataProcCycle_EmGenObjectList_aObjectI%dI_Kinematic_fVrelY"),
		("EmGenObjectList", "ARS4xx_Device_DataProcCycle_EmGenObjectList_aObjectI%dI_Attributes_eClassification"),
		("EmGenObjectList", "ARS4xx_Device_DataProcCycle_EmGenObjectList_aObjectI%dI_Attributes_eDynamicProperty"),
		("EmARSObjectList", "ARS4xx_Device_DataProcCycle_EmARSObjectList_aObjectI%dI_Geometry_fLength"),
		("EmARSObjectList", "ARS4xx_Device_DataProcCycle_EmARSObjectList_aObjectI%dI_Geometry_fWidth"),
		("EmGenObjectList", "ARS4xx_Device_DataProcCycle_EmGenObjectList_aObjectI%dI_Kinematic_fArelX"),
		("EmGenObjectList", "ARS4xx_Device_DataProcCycle_EmGenObjectList_aObjectI%dI_Kinematic_fArelY"),
		# ("FCTPublicObjData","ARS4xx_Device_AlgoSenCycle_FCTPublicObjData_ObjListI%dI_LaneInformation_eAssociatedLane"),
		("EmGenObjectList", "ARS4xx_Device_DataProcCycle_EmGenObjectList_aObjectI%dI_Qualifiers_uiProbabilityOfExistence"),
)

signalTemplates_EmGenObjectListh5 = (
		("ARS4xx Device.DataProcCycle.EmGenObjectList", "ARS4xx_Device_DataProcCycle_EmGenObjectList_aObject%d_Kinematic_fDistX"),
		("ARS4xx Device.DataProcCycle.EmGenObjectList", "ARS4xx_Device_DataProcCycle_EmGenObjectList_aObject%d_General_uiID"),
		("ARS4xx Device.DataProcCycle.EmGenObjectList", "ARS4xx_Device_DataProcCycle_EmGenObjectList_aObject%d_General_eMaintenanceState"),
		("ARS4xx Device.DataProcCycle.EmGenObjectList", "ARS4xx_Device_DataProcCycle_EmGenObjectList_aObject%d_General_uiLifeCycles"),
		("ARS4xx Device.DataProcCycle.EmGenObjectList", "ARS4xx_Device_DataProcCycle_EmGenObjectList_aObject%d_General_fLifeTime"),
		("ARS4xx Device.DataProcCycle.EmGenObjectList", "ARS4xx_Device_DataProcCycle_EmGenObjectList_aObject%d_Kinematic_fDistY"),
		("ARS4xx Device.DataProcCycle.EmGenObjectList", "ARS4xx_Device_DataProcCycle_EmGenObjectList_aObject%d_Kinematic_fVrelX"),
		("ARS4xx Device.DataProcCycle.EmGenObjectList", "ARS4xx_Device_DataProcCycle_EmGenObjectList_aObject%d_Kinematic_fVrelY"),
		("ARS4xx Device.DataProcCycle.EmGenObjectList", "ARS4xx_Device_DataProcCycle_EmGenObjectList_aObject%d_Attributes_eClassification"),
		("ARS4xx Device.DataProcCycle.EmGenObjectList", "ARS4xx_Device_DataProcCycle_EmGenObjectList_aObject%d_Attributes_eDynamicProperty"),
		("ARS4xx Device.DataProcCycle.EmARSObjectList", "ARS4xx_Device_DataProcCycle_EmARSObjectList_aObject%d_Geometry_fLength"),
		("ARS4xx Device.DataProcCycle.EmARSObjectList", "ARS4xx_Device_DataProcCycle_EmARSObjectList_aObject%d_Geometry_fWidth"),
		("ARS4xx Device.DataProcCycle.EmGenObjectList", "ARS4xx_Device_DataProcCycle_EmGenObjectList_aObject%d_Kinematic_fArelX"),
		("ARS4xx Device.DataProcCycle.EmGenObjectList", "ARS4xx_Device_DataProcCycle_EmGenObjectList_aObject%d_Kinematic_fArelY"),
		("ARS4xx Device.DataProcCycle.EmGenObjectList", "ARS4xx_Device_DataProcCycle_EmGenObjectList_aObject%d_Qualifiers_uiProbabilityOfExistence"),
)

signalTemplates_pFCTCDHypotheses = (
		("pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_HypothesisI%dI_eEBADynProp"),
		("pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_HypothesisI%dI_eEBAInhibitionMask"),
		("pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_HypothesisI%dI_eEBAObjMovDir"),
		("pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_HypothesisI%dI_eEBAObjectClass"),
		("pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_HypothesisI%dI_eSensorSource"),
		("pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_HypothesisI%dI_eType"),
		("pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_HypothesisI%dI_fArelX"),
		("pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_HypothesisI%dI_fArelY"),
		("pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_HypothesisI%dI_fClosingVelocity"),
		("pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_HypothesisI%dI_fDistX"),
		("pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_HypothesisI%dI_fDistY"),
		("pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_HypothesisI%dI_fHypothesisLifetime"),
		("pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_HypothesisI%dI_fLatNecAccel"),
		("pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_HypothesisI%dI_fLongNecAccel"),
		("pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_HypothesisI%dI_fTTBAcute"),
		("pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_HypothesisI%dI_fTTBPre"),
		("pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_HypothesisI%dI_fTTC"),
		("pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_HypothesisI%dI_fTTC2"),
		("pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_HypothesisI%dI_fTTC3"),
		("pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_HypothesisI%dI_fTTC4"),
		("pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_HypothesisI%dI_fTTSAcute"),
		("pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_HypothesisI%dI_fTTSPre"),
		("pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_HypothesisI%dI_fVrelX"),
		("pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_HypothesisI%dI_fVrelY"),
		("pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_HypothesisI%dI_uiHypothesisProbability"),
		("pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_HypothesisI%dI_uiObjectProbability"),
		("pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_HypothesisI%dI_uiObjectRef"),
)

signalTemplates_pFCTCDHypothesesh5= (
		("ARS4xx Device.AlgoSenCycle.pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_Hypothesis%d_eEBADynProp"),
		("ARS4xx Device.AlgoSenCycle.pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_Hypothesis%d_eEBAInhibitionMask"),
		("ARS4xx Device.AlgoSenCycle.pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_Hypothesis%d_eEBAObjMovDir"),
		("ARS4xx Device.AlgoSenCycle.pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_Hypothesis%d_eEBAObjectClass"),
		("ARS4xx Device.AlgoSenCycle.pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_Hypothesis%d_eSensorSource"),
		("ARS4xx Device.AlgoSenCycle.pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_Hypothesis%d_eType"),
		("ARS4xx Device.AlgoSenCycle.pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_Hypothesis%d_fArelX"),
		("ARS4xx Device.AlgoSenCycle.pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_Hypothesis%d_fArelY"),
		("ARS4xx Device.AlgoSenCycle.pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_Hypothesis%d_fClosingVelocity"),
		("ARS4xx Device.AlgoSenCycle.pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_Hypothesis%d_fDistX"),
		("ARS4xx Device.AlgoSenCycle.pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_Hypothesis%d_fDistY"),
		("ARS4xx Device.AlgoSenCycle.pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_Hypothesis%d_fHypothesisLifetime"),
		("ARS4xx Device.AlgoSenCycle.pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_Hypothesis%d_fLatNecAccel"),
		("ARS4xx Device.AlgoSenCycle.pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_Hypothesis%d_fLongNecAccel"),
		("ARS4xx Device.AlgoSenCycle.pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_Hypothesis%d_fTTBAcute"),
		("ARS4xx Device.AlgoSenCycle.pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_Hypothesis%d_fTTBPre"),
		("ARS4xx Device.AlgoSenCycle.pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_Hypothesis%d_fTTC"),
		("ARS4xx Device.AlgoSenCycle.pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_Hypothesis%d_fTTC2"),
		("ARS4xx Device.AlgoSenCycle.pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_Hypothesis%d_fTTC3"),
		("ARS4xx Device.AlgoSenCycle.pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_Hypothesis%d_fTTC4"),
		("ARS4xx Device.AlgoSenCycle.pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_Hypothesis%d_fTTSAcute"),
		("ARS4xx Device.AlgoSenCycle.pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_Hypothesis%d_fTTSPre"),
		("ARS4xx Device.AlgoSenCycle.pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_Hypothesis%d_fVrelX"),
		("ARS4xx Device.AlgoSenCycle.pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_Hypothesis%d_fVrelY"),
		("ARS4xx Device.AlgoSenCycle.pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_Hypothesis%d_uiHypothesisProbability"),
		("ARS4xx Device.AlgoSenCycle.pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_Hypothesis%d_uiObjectProbability"),
		("ARS4xx Device.AlgoSenCycle.pFCTCDHypotheses", "ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_Hypothesis%d_uiObjectRef"),
)

def createMessageGroups_EmGenObjectList(MESSAGE_NUM, signalTemplates):
		messageGroups = []
		for m in xrange(MESSAGE_NUM):
				messageGroup = {}
				signalDict = []
				for signalTemplate in signalTemplates:
						fullName = signalTemplate[1] % m
						shortName = signalTemplate[1].split('_')[-1]
						messageGroup[shortName] = (signalTemplate[0], fullName)
				signalDict.append(messageGroup)
				messageGroup2 = {}
				for signalTemplate in signalTemplates_EmGenObjectListh5:
						fullName = signalTemplate[1] % m
						shortName = signalTemplate[1].split('_')[-1]
						messageGroup2[shortName] = (signalTemplate[0], fullName)
				signalDict.append(messageGroup2)
				messageGroups.append(signalDict)
		return messageGroups


def createMessageGroups_pFCTCDHypotheses(MESSAGE_NUM, signalTemplates):
		messageGroups = []
		for m in xrange(MESSAGE_NUM):
				messageGroup = {}
				signalDict = []
				for signalTemplate in signalTemplates:
						fullName = signalTemplate[1] % m
						shortName = signalTemplate[1].split('_')[-1]
						messageGroup[shortName] = (signalTemplate[0], fullName)
				signalDict.append(messageGroup)
				messageGroup2 = {}
				for signalTemplate in signalTemplates_pFCTCDHypothesesh5:
						fullName = signalTemplate[1] % m
						shortName = signalTemplate[1].split('_')[-1]
						messageGroup2[shortName] = (signalTemplate[0], fullName)
				signalDict.append(messageGroup2)
				messageGroups.append(signalDict)
		return messageGroups


def getHypothesisObjects(hypothesis_objects, common_time):
		hypo_groups = {}
		# iterate through RawTrackObjects
		for track_index in range(AOBJECT_TRACK_MESSAGE_NUM):
				ttc = np.zeros(len(common_time))
				# iterate through common time
				for time_index in range(0, len(common_time)):
						for hypothesis_index, hypothesis_object in enumerate(hypothesis_objects):
								if hypothesis_object["uiObjectRef"][time_index] != 0 and hypothesis_object["uiObjectRef"][
										time_index] == track_index:
										ttc[time_index] = hypothesis_object["fTTC"][time_index]
				hypo_groups["ttc_" + str(track_index)] = ttc
		return hypo_groups


messageGroups_EmGenObjectList = createMessageGroups_EmGenObjectList(AOBJECT_TRACK_MESSAGE_NUM, signalTemplates_EmGenObjectList)
messageGroups_pFCTCDHypotheses = createMessageGroups_pFCTCDHypotheses(HYPOTHESIS_TRACK_MESSAGE_NUM, signalTemplates_pFCTCDHypotheses)


class ContiFLR25Track(ObjectFromMessage):
		_attribs = tuple(tmpl[1].split('_')[-1] for tmpl in signalTemplates_EmGenObjectList)
		_hypo_attribs = ("ttc",)
		_attribs = _attribs + _hypo_attribs

		_special_methods = 'alive_intervals'

		def __init__(self, id, time, source, group, hypo_groups, invalid_mask, scaletime = None):
				self._invalid_mask = invalid_mask
				self._group = group
				self._hypo_groups = hypo_groups
				super(ContiFLR25Track, self).__init__(id, time, None, None, scaleTime = None)
				return

		def _create(self, signalName):
				if signalName in self._hypo_attribs:
						value = self._hypo_groups[signalName + "_" + str(self._id)]
				else:
						value = self._group.get_value(signalName, ScaleTime = self.time)

				mask = ~self._invalid_mask
				out = np.ma.masked_all_like(value)
				out.data[mask] = value[mask]
				out.mask &= ~mask
				return out

		def id(self):
				data = np.repeat(np.uint8(self._id), self.time.size)
				arr = np.ma.masked_array(data, mask = self.dx.mask)
				return arr

		def dx(self):
				return self._fDistX

		def dy(self):
				return self._fDistY

		def range(self):
				return np.sqrt(np.square(self.dx) + np.square(self.dy))

		def angle(self):
				return np.arctan2(self.dy, self.dx)

		def vx(self):
				return self._fVrelX

		def vy(self):
				return self._fVrelY

		def ax(self):
				return self._fArelX

		def ay(self):
				return self._fArelY

		def length(self):
				return self._fLength

		def width(self):
				return self._fWidth

		def ttc(self):
				return self._ttc

		def invttc(self):
				return 1. / self.ttc

		def radar_conf(self):
				return self._uiProbabilityOfExistence

		def mov_dir(self):
				crossing_stationary = self._eDynamicProperty == MOTION_STATUS.CROSSING_STAT
				crossing_moving = self._eDynamicProperty == MOTION_STATUS.CROSSING_MOV

				stationary = self._eDynamicProperty == MOTION_STATUS.STATIONARY
				stat_cand = self._eDynamicProperty == MOTION_STATUS.STAT_CAND
				stopped = self._eDynamicProperty == MOTION_STATUS.STOPPED
				unknown = self._eDynamicProperty == MOTION_STATUS.UNKNOWN

				ongoing = self._eDynamicProperty == MOTION_STATUS.MOVING
				oncoming = self._eDynamicProperty == MOTION_STATUS.ONCOMING
				undefined = (unknown | stationary | stopped | stat_cand | crossing_stationary)
				crossing = crossing_moving
				# dummy data
				dummy = np.zeros(self._eDynamicProperty.shape, dtype = bool)
				arr = np.ma.masked_array(dummy, mask = self._fDistX.mask)
				return MovingDirection(oncoming = oncoming, ongoing = ongoing, undefined = undefined, crossing = crossing, crossing_left=arr,crossing_right=arr)

		def obj_type(self):
				point = self._eClassification == OBJ_CLASS.POINT
				car = self._eClassification == OBJ_CLASS.CAR
				truck = self._eClassification == OBJ_CLASS.TRUCK
				pedestrian = self._eClassification == OBJ_CLASS.PEDESTRIAN
				motorcycle = self._eClassification == OBJ_CLASS.MOTORCYCLE
				bicycle = self._eClassification == OBJ_CLASS.BICYCLE
				wide = self._eClassification == OBJ_CLASS.WIDE
				unclassified = self._eClassification == OBJ_CLASS.UNCLASSIFIED
				unknown = (unclassified)

				return ObjectType(unknown = unknown, pedestrian = pedestrian, motorcycle = motorcycle, car = car,
													truck = truck,
													bicycle = bicycle, point = point, wide =wide)

		MOVING_STATE = enum(MOVING = 0, STATIONARY = 1, ONCOMING = 2, STAT_CAND = 3, UNKNOWN = 4, CROSSING_STAT = 5,
												CROSSING_MOV = 6, STOPPED = 7)

		def mov_state(self):
				crossing_stationary = self._eDynamicProperty == MOTION_STATUS.CROSSING_STAT
				crossing_moving = self._eDynamicProperty == MOTION_STATUS.CROSSING_MOV

				stationary = self._eDynamicProperty == MOTION_STATUS.STATIONARY
				stat_cand = self._eDynamicProperty == MOTION_STATUS.STAT_CAND
				stopped = self._eDynamicProperty == MOTION_STATUS.STOPPED
				unknown = self._eDynamicProperty == MOTION_STATUS.UNKNOWN

				moving = self._eDynamicProperty == MOTION_STATUS.MOVING
				oncoming = self._eDynamicProperty == MOTION_STATUS.ONCOMING
				stationary_objects = (crossing_stationary | stationary | stat_cand)
				# dummy data
				dummy = np.zeros(self._eDynamicProperty.shape, dtype = bool)
				arr = np.ma.masked_array(dummy, mask = self._fDistX.mask)
				return MovingState(stat = stationary_objects, stopped = stopped, moving = moving, unknown = unknown,
													 crossing = crossing_moving, crossing_left=arr,crossing_right=arr, oncoming = oncoming)

		def lane(self):
				same = self._eAssociatedLane == LANE_STATUS.EGO
				left = self._eAssociatedLane == LANE_STATUS.LEFT
				right = self._eAssociatedLane == LANE_STATUS.RIGHT
				uncorr_left = self._eAssociatedLane == LANE_STATUS.FAR_LEFT
				uncorr_right = self._eAssociatedLane == LANE_STATUS.FAR_RIGHT
				unknown_lane = self._eAssociatedLane == LANE_STATUS.UNKNOWN
				return LaneStatus(same = same, left = left, right = right, uncorr_left = uncorr_left,
													uncorr_right = uncorr_right, unknown = unknown_lane)

		def tr_state(self):
				valid = ma.masked_array(~self._fDistX.mask, self._fDistX.mask)
				meas = self._eMaintenanceState == 2
				hist = np.ones_like(valid)
				for st, end in maskToIntervals(self._eMaintenanceState == 1):
						if st != 0:
								hist[st] = False
				return TrackingState(valid = valid, measured = meas, hist = hist)

		def alive_intervals(self):
				new = self.tr_state.valid & ~self.tr_state.hist
				validIntervals = cIntervalList.fromMask(self.time, self.tr_state.valid)
				newIntervals = cIntervalList.fromMask(self.time, new)
				alive_intervals = validIntervals.split(st for st, _ in newIntervals)
				return alive_intervals


class Calc(iCalc):
		dep = 'calc_common_time-flr25',

		def check(self):
				modules = self.get_modules()
				source = self.get_source()
				commonTime = modules.fill(self.dep[0])
				groups_EmGenObjectList = []
				groups_pFCTCDHypotheses =[]
				for sg in messageGroups_EmGenObjectList:
						groups_EmGenObjectList.append(self.source.selectSignalGroup(sg))
				for sg in messageGroups_pFCTCDHypotheses:
						groups_pFCTCDHypotheses.append(self.source.selectSignalGroup(sg))
				optgroups_pFCTCDHypotheses = select_allvalid_sgs(groups_pFCTCDHypotheses,
																												 len(messageGroups_pFCTCDHypotheses[0][0]))
				return groups_EmGenObjectList, commonTime, optgroups_pFCTCDHypotheses

		def fill(self, groups, common_time, groups_pFCTCDHypotheses):
				tracks = PrimitiveCollection(common_time)
				VALID_FLAG = False
				# Create List of Hypothesis objects
				HypothesisObjects = []
				for k, group in enumerate(groups_pFCTCDHypotheses):
						HypothesisObject = dict(track = k)
						HypothesisObject["time"] = common_time
						HypothesisObject["eEBADynProp"] = \
								self.source.getSignalFromSignalGroup(group, "eEBADynProp", ScaleTime = common_time)[1]
						HypothesisObject["fDieEBAInhibitionMaskstY"] = \
								self.source.getSignalFromSignalGroup(group, "eEBAInhibitionMask", ScaleTime = common_time)[1]
						HypothesisObject["eEBAObjMovDir"] = \
								self.source.getSignalFromSignalGroup(group, "eEBAObjMovDir", ScaleTime = common_time)[1]
						HypothesisObject["eEBAObjectClass"] = \
								self.source.getSignalFromSignalGroup(group, "eEBAObjectClass", ScaleTime = common_time)[1]
						HypothesisObject["eSensorSource"] = \
								self.source.getSignalFromSignalGroup(group, "eSensorSource", ScaleTime = common_time)[1]
						HypothesisObject["eType"] = self.source.getSignalFromSignalGroup(group, "eType", ScaleTime =
						common_time)[1]
						HypothesisObject["fArelX"] = self.source.getSignalFromSignalGroup(group, "fArelX", ScaleTime =
						common_time)[
								1]
						HypothesisObject["fArelY"] = self.source.getSignalFromSignalGroup(group, "fArelY", ScaleTime =
						common_time)[
								1]
						HypothesisObject["fClosingVelocity"] = \
								self.source.getSignalFromSignalGroup(group, "fClosingVelocity", ScaleTime = common_time)[1]
						HypothesisObject["fDistX"] = self.source.getSignalFromSignalGroup(group, "fDistX", ScaleTime =
						common_time)[
								1]
						HypothesisObject["fDistY"] = self.source.getSignalFromSignalGroup(group, "fDistY", ScaleTime =
						common_time)[
								1]
						HypothesisObject["fHypothesisLifetime"] = \
								self.source.getSignalFromSignalGroup(group, "fHypothesisLifetime", ScaleTime = common_time)[1]
						HypothesisObject["fLatNecAccel"] = \
								self.source.getSignalFromSignalGroup(group, "fLatNecAccel", ScaleTime = common_time)[1]
						HypothesisObject["fLongNecAccel"] = \
								self.source.getSignalFromSignalGroup(group, "fLongNecAccel", ScaleTime = common_time)[1]
						HypothesisObject["fTTBAcute"] = \
								self.source.getSignalFromSignalGroup(group, "fTTBAcute", ScaleTime = common_time)[1]
						HypothesisObject["fTTBPre"] = \
								self.source.getSignalFromSignalGroup(group, "fTTBPre", ScaleTime = common_time)[1]
						HypothesisObject["fTTC"] = self.source.getSignalFromSignalGroup(group, "fTTC", ScaleTime = common_time)[1]
						HypothesisObject["fTTC2"] = self.source.getSignalFromSignalGroup(group, "fTTC2", ScaleTime =
						common_time)[1]
						HypothesisObject["fTTC3"] = self.source.getSignalFromSignalGroup(group, "fTTC3", ScaleTime =
						common_time)[1]
						HypothesisObject["fTTSAcute"] = \
								self.source.getSignalFromSignalGroup(group, "fTTSAcute", ScaleTime = common_time)[1]
						HypothesisObject["fTTSPre"] = \
								self.source.getSignalFromSignalGroup(group, "fTTSPre", ScaleTime = common_time)[1]
						HypothesisObject["fVrelX"] = self.source.getSignalFromSignalGroup(group, "fVrelX", ScaleTime =
						common_time)[
								1]
						HypothesisObject["fVrelY"] = self.source.getSignalFromSignalGroup(group, "fVrelY", ScaleTime =
						common_time)[
								1]
						HypothesisObject["uiHypothesisProbability"] = \
								self.source.getSignalFromSignalGroup(group, "uiHypothesisProbability", ScaleTime = common_time)[1]
						HypothesisObject["uiObjectProbability"] = \
								self.source.getSignalFromSignalGroup(group, "uiObjectProbability", ScaleTime = common_time)[1]
						HypothesisObject["uiObjectRef"] = \
								self.source.getSignalFromSignalGroup(group, "uiObjectRef", ScaleTime = common_time)[1]
						HypothesisObjects.append(HypothesisObject)

				hypo_groups = getHypothesisObjects(HypothesisObjects, common_time)
				for _id, (group, hypo_group) in enumerate(zip(groups, hypo_groups)):
						object_id = group.get_value("uiID", ScaleTime = common_time)
						invalid_mask = (object_id == 254) | (np.isnan(object_id))
#						if np.all(invalid_mask):
#								continue
						VALID_FLAG = True
						tracks[_id] = ContiFLR25Track(_id, common_time, None, group, hypo_groups, invalid_mask,
																					scaletime = common_time)
				if not VALID_FLAG:
						logging.warning("Error: {} :Measurement does not contain FLR25 object data".format(self.source.FileName))
				return tracks


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"\\pu2w6474\shared-drive\transfer\shubham\measurements\ARS4xx_new_dcnvt_h5_format\New folder\mi5id787__2021-06-09_06-40-32.h5"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		conti = manager_modules.calc('fill_flr25_raw_tracks@aebs.fill', manager)
		print(conti)
