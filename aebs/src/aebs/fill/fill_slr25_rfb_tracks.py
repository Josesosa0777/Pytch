# -*- dataeval: init -*-
# -*- coding: utf-8 -*-
import logging

import numpy as np
import numpy.ma as ma
from flr20_raw_tracks_base import ObjectFromMessage
from interface import iCalc
from measproc import cIntervalList
from measproc.IntervalList import maskToIntervals
from metatrack import MovingDirection, MovingState, ObjectType, TrackingState, SlrObjectType
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

OBJ_CLASS_VALS = (
    "POINT",
    "CAR",
    "TRUCK",
    "PEDESTRIAN",
    "MOTORCYCLE",
    "BICYCLE",
    "WIDE",
    "MIRROR",
    "MULTIPLE",
    "INITIALIZED",
    "UNCLASSIFIED",
)

MOTION_STATUS = enum(**dict((name, n) for n, name in enumerate(MOTION_ST_VALS)))
OBJ_CLASS = enum(**dict((name, n) for n, name in enumerate(OBJ_CLASS_VALS)))

signalTemplate = (

    ("FCTCustomOutputData",
     "SRR520_RightFrontBackwards_AlgoSenCycle_FCTCustomOutputData_CustObjDataI%dI_Attributes_eDynamicProp"),
    ("FCTCustomOutputData",
     "SRR520_RightFrontBackwards_AlgoSenCycle_FCTCustomOutputData_CustObjDataI%dI_Attributes_eObjType"),
    ("FCTCustomOutputData",
     "SRR520_RightFrontBackwards_AlgoSenCycle_FCTCustomOutputData_CustObjDataI%dI_Attributes_fObjLength"),
    ("FCTCustomOutputData",
     "SRR520_RightFrontBackwards_AlgoSenCycle_FCTCustomOutputData_CustObjDataI%dI_Attributes_fObjWidth"),
    ("FCTCustomOutputData",
     "SRR520_RightFrontBackwards_AlgoSenCycle_FCTCustomOutputData_CustObjDataI%dI_Attributes_fProbOfExist"),
    ("FCTCustomOutputData",
     "SRR520_RightFrontBackwards_AlgoSenCycle_FCTCustomOutputData_CustObjDataI%dI_Attributes_uiLifetime"),
    ("FCTCustomOutputData",
     "SRR520_RightFrontBackwards_AlgoSenCycle_FCTCustomOutputData_CustObjDataI%dI_General_uOutObjID"),
    ("FCTCustomOutputData",
     "SRR520_RightFrontBackwards_AlgoSenCycle_FCTCustomOutputData_CustObjDataI%dI_Kinematics_fArelX"),
    ("FCTCustomOutputData",
     "SRR520_RightFrontBackwards_AlgoSenCycle_FCTCustomOutputData_CustObjDataI%dI_Kinematics_fArelXStd"),
    ("FCTCustomOutputData",
     "SRR520_RightFrontBackwards_AlgoSenCycle_FCTCustomOutputData_CustObjDataI%dI_Kinematics_fArelY"),
    ("FCTCustomOutputData",
     "SRR520_RightFrontBackwards_AlgoSenCycle_FCTCustomOutputData_CustObjDataI%dI_Kinematics_fArelYStd"),
    ("FCTCustomOutputData",
     "SRR520_RightFrontBackwards_AlgoSenCycle_FCTCustomOutputData_CustObjDataI%dI_Kinematics_fDistX"),
    ("FCTCustomOutputData",
     "SRR520_RightFrontBackwards_AlgoSenCycle_FCTCustomOutputData_CustObjDataI%dI_Kinematics_fDistXStd"),
    ("FCTCustomOutputData",
     "SRR520_RightFrontBackwards_AlgoSenCycle_FCTCustomOutputData_CustObjDataI%dI_Kinematics_fDistY"),
    ("FCTCustomOutputData",
     "SRR520_RightFrontBackwards_AlgoSenCycle_FCTCustomOutputData_CustObjDataI%dI_Kinematics_fDistYStd"),
    ("FCTCustomOutputData",
     "SRR520_RightFrontBackwards_AlgoSenCycle_FCTCustomOutputData_CustObjDataI%dI_Kinematics_fVabs"),
    ("FCTCustomOutputData",
     "SRR520_RightFrontBackwards_AlgoSenCycle_FCTCustomOutputData_CustObjDataI%dI_Kinematics_fVrelX"),
    ("FCTCustomOutputData",
     "SRR520_RightFrontBackwards_AlgoSenCycle_FCTCustomOutputData_CustObjDataI%dI_Kinematics_fVrelXStd"),
    ("FCTCustomOutputData",
     "SRR520_RightFrontBackwards_AlgoSenCycle_FCTCustomOutputData_CustObjDataI%dI_Kinematics_fVrelY"),
    ("FCTCustomOutputData",
     "SRR520_RightFrontBackwards_AlgoSenCycle_FCTCustomOutputData_CustObjDataI%dI_Kinematics_fVrelYStd"),

)
signalTemplateh5 = (
    ("SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData",
     "SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData.CustObjData[%d].Attributes.eDynamicProp"),
    ("SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData",
     "SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData.CustObjData[%d].Attributes.eObjType"),
    ("SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData",
     "SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData.CustObjData[%d].Attributes.fObjLength"),
    ("SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData",
     "SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData.CustObjData[%d].Attributes.fObjWidth"),
    ("SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData",
     "SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData.CustObjData[%d].Attributes.fProbOfExist"),
    ("SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData",
     "SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData.CustObjData[%d].Attributes.uiLifetime"),
    ("SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData",
     "SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData.CustObjData[%d].General.uOutObjID"),
    ("SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData",
     "SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData.CustObjData[%d].Kinematics.fArelX"),
    ("SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData",
     "SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData.CustObjData[%d].Kinematics.fArelXStd"),
    ("SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData",
     "SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData.CustObjData[%d].Kinematics.fArelY"),
    ("SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData",
     "SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData.CustObjData[%d].Kinematics.fArelYStd"),
    ("SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData",
     "SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData.CustObjData[%d].Kinematics.fDistX"),
    ("SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData",
     "SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData.CustObjData[%d].Kinematics.fDistXStd"),
    ("SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData",
     "SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData.CustObjData[%d].Kinematics.fDistY"),
    ("SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData",
     "SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData.CustObjData[%d].Kinematics.fDistYStd"),
    ("SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData",
     "SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData.CustObjData[%d].Kinematics.fVabs"),
    ("SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData",
     "SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData.CustObjData[%d].Kinematics.fVrelX"),
    ("SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData",
     "SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData.CustObjData[%d].Kinematics.fVrelXStd"),
    ("SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData",
     "SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData.CustObjData[%d].Kinematics.fVrelY"),
    ("SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData",
     "SRR520_RightFrontBackwards.AlgoSenCycle.FCTCustomOutputData.CustObjData[%d].Kinematics.fVrelYStd"),

)

signalTemplate_2 = {
    "BSD4_LatDispMIORightSide_D0": ("CAN_MFC_Public_BSD4_D0", "BSD4_LatDispMIORightSide_D0"),
    "BSD4_LonDispMIORightSide_D0": ("CAN_MFC_Public_BSD4_D0", "BSD4_LonDispMIORightSide_D0"),
}


def createMessageGroups(MESSAGE_NUM, signalTemplates):
    messageGroups = []
    for m in xrange(MESSAGE_NUM):
        messageGroup1 = {}
        signalDict = []
        for signalTemplate in signalTemplates:
            fullName = signalTemplate[1] % m
            shortName = fullName.split('_')[-1]
            messageGroup1[shortName] = (signalTemplate[0], fullName)
        messageGroup2 = {}
        for signalTemplate in signalTemplateh5:
            fullName = signalTemplate[1] % m
            shortName = fullName.split('.')[-1]
            messageGroup2[shortName] = (signalTemplate[0], fullName)
        for key, signals in signalTemplate_2.iteritems():
            messageGroup1[key] = signals
            messageGroup2[key] = signals
        signalDict.append(messageGroup1)
        signalDict.append(messageGroup2)
        messageGroups.append(signalDict)
    return messageGroups


messageGroups = createMessageGroups(TRACK_MESSAGE_NUM, signalTemplate)


class Slr25Tracks(ObjectFromMessage):
    attribs = []
    for signalTemplate in signalTemplateh5:
        fullName = signalTemplate[1]
        shortName = fullName.split('.')[-1]
        attribs.append(shortName)

    _attribs = tuple(attribs)
    _special_methods = 'alive_intervals'

    def __init__(self, id, time, source, group, invalid_mask, scaletime=None):
        self._invalid_mask = invalid_mask
        self._group = group
        super(Slr25Tracks, self).__init__(id, time, None, None, scaleTime=None)
        return

    def _create(self, signalName):
        value = self._group.get_value(signalName, ScaleTime=self.time)
        mask = ~self._invalid_mask
        out = np.ma.masked_all_like(value)
        out.data[mask] = value[mask]
        out.mask &= ~mask
        return out

    def id(self):
        data = np.repeat(np.uint8(self._id), self.time.size)
        arr = np.ma.masked_array(data, mask=self._fDistX.mask)
        return arr

    def dx(self):
        return self._fDistX

    def dx_std(self):
        return self._fDistXStd

    def dy(self):
        return self._fDistY

    def dy_std(self):
        return self._fDistYStd

    def life_time(self):
        return self._uiLifetime

    def range(self):
        return np.sqrt(np.square(self.dx) + np.square(self.dy))

    def angle(self):
        return np.arctan2(self.dy, self.dx)

    def ay(self):
        return self._fArelY

    def ay_std(self):
        return self._fArelYStd

    def ax(self):
        return self._fArelX

    def ax_std(self):
        return self._fArelXStd

    def vx(self):
        return self._fVrelX

    def vx_std(self):
        return self._fVrelXStd

    def vx_abs(self):
        return self._fVabs

    def vy(self):
        return self._fVrelY

    def vy_std(self):
        return self._fVrelYStd

    def width(self):
        return self._fObjWidth

    def length(self):
        return self._fObjLength

    def video_conf(self):
        return self._fProbOfExist

    def ttc(self):
        with np.errstate(divide='ignore'):
            ttc = np.where(self.vx < -1e-3,  # avoid too large (meaningless) values
                           -self.dx / self.vx,
                           np.inf)
        return ttc

    def invttc(self):
        return 1. / self.ttc

    def mov_dir(self):
        crossing_left = self._eDynamicProp == MOTION_STATUS.CROSSING_LEFT
        crossing_right = self._eDynamicProp == MOTION_STATUS.CROSSING_RIGHT

        stationary = self._eDynamicProp == MOTION_STATUS.STATIONARY
        stopped = self._eDynamicProp == MOTION_STATUS.STOPPED
        unknown = self._eDynamicProp == MOTION_STATUS.UNKNOWN

        ongoing = self._eDynamicProp == MOTION_STATUS.MOVING
        oncoming = self._eDynamicProp == MOTION_STATUS.ONCOMING
        undefined = (unknown | stationary | stopped)
        dummy = np.zeros(self._eDynamicProp.shape, dtype=bool)
        arr = np.ma.masked_array(dummy, mask=self._fDistX.mask)
        return MovingDirection(oncoming=oncoming, ongoing=ongoing, undefined=undefined, crossing=arr,
                               crossing_left=crossing_left, crossing_right=crossing_right)

    def obj_type(self):
        point = self._eObjType == OBJ_CLASS.POINT
        car = self._eObjType == OBJ_CLASS.CAR
        truck = self._eObjType == OBJ_CLASS.TRUCK
        pedestrian = self._eObjType == OBJ_CLASS.PEDESTRIAN
        motorcycle = self._eObjType == OBJ_CLASS.MOTORCYCLE
        bicycle = self._eObjType == OBJ_CLASS.BICYCLE
        wide = self._eObjType == OBJ_CLASS.WIDE
        unclassified = self._eObjType == OBJ_CLASS.UNCLASSIFIED
        mirror = self._eObjType == OBJ_CLASS.MIRROR
        initialized = self._eObjType == OBJ_CLASS.INITIALIZED
        multiple = self._eObjType == OBJ_CLASS.MULTIPLE
        unknown = unclassified

        return SlrObjectType(unknown=unknown, pedestrian=pedestrian, motorcycle=motorcycle, car=car,
                             truck=truck, bicycle=bicycle, point=point, wide=wide,
                             mirror=mirror, multiple=multiple, initialized=initialized)

    def mov_state(self):
        crossing_left = self._eDynamicProp == MOTION_STATUS.CROSSING_LEFT
        crossing_right = self._eDynamicProp == MOTION_STATUS.CROSSING_RIGHT
        moving = self._eDynamicProp == MOTION_STATUS.MOVING
        oncoming = self._eDynamicProp == MOTION_STATUS.ONCOMING
        stationary = self._eDynamicProp == MOTION_STATUS.STATIONARY
        stopped = self._eDynamicProp == MOTION_STATUS.STOPPED
        unknown = self._eDynamicProp == MOTION_STATUS.UNKNOWN
        dummy = np.zeros(self._eDynamicProp.shape, dtype=bool)
        arr = np.ma.masked_array(dummy, mask=self._fDistX.mask)
        return MovingState(stat=stationary, stopped=stopped, moving=moving, unknown=unknown, crossing=arr,
                           crossing_left=crossing_left, crossing_right=crossing_right, oncoming=oncoming)

    def tr_state(self):
        valid = ma.masked_array(~self._fDistX.mask, self._fDistX.mask)
        meas = np.ones_like(valid)
        hist = np.ones_like(valid)
        for st, end in maskToIntervals(~self._fDistX.mask):
            if st != 0:
                hist[st] = False
        return TrackingState(valid=valid, measured=meas, hist=hist)

    def alive_intervals(self):
        new = self.tr_state.valid & ~self.tr_state.hist
        validIntervals = cIntervalList.fromMask(self.time, self.tr_state.valid)
        newIntervals = cIntervalList.fromMask(self.time, new)
        alive_intervals = validIntervals.split(st for st, _ in newIntervals)
        return alive_intervals


class Calc(iCalc):
    dep = 'calc_common_time-slr25',

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
            object_id = group.get_value("uOutObjID", ScaleTime=common_time)
            LatDispMIORightSide = group.get_value('BSD4_LatDispMIORightSide_D0', ScaleTime=common_time)
            LonDispMIORightSide = group.get_value('BSD4_LonDispMIORightSide_D0', ScaleTime=common_time)
            invalid_mask = (object_id == 255) | (np.isnan(object_id))
            #						if np.all(invalid_mask):
            #								continue
            VALID_FLAG = True
            tracks[_id] = Slr25Tracks(_id, common_time, self.source, group, invalid_mask, scaletime=common_time)
            tracks['BSD4_LatDispMIORightSide_D0'] = LatDispMIORightSide
            tracks['BSD4_LonDispMIORightSide_D0'] = LonDispMIORightSide
        if not VALID_FLAG:
            logging.warning(
                "Error: {} :Measurement does not contain SLR25_RFB object data".format(self.source.FileName))
        return tracks, signals


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\evaluation\pytch2_eval\slr_eval\test\2024-08-28\mi5id5506__2024-08-28_14-51-16.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    tracks, signals = manager_modules.calc('fill_slr25_rfb_tracks@aebs.fill', manager)
    print(tracks)
    print(signals)
