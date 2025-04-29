# -*- dataeval: init -*-
# -*- coding: utf-8 -*-
import logging

import numpy as np
import numpy.ma as ma
from flr20_raw_tracks_base import ObjectFromMessage
from interface import iCalc
from measproc import cIntervalList
from measproc.IntervalList import maskToIntervals
from metatrack import MovingDirection, TrackingState, MaintenanceState, ARS620MovingState
from primitives.bases import PrimitiveCollection
from pyutils.enum import enum

TRACK_MESSAGE_NUM = 50

MOTION_ST_VALS = (
    'UNKNOWN',
    'MOVING',
    'ONCOMING',
    'STATIONARY',
    'STOPPED',
    'CROSSING_LEFT',
    'CROSSING_RIGHT'
)
MAINTENANCE_STATE = (
    'EMPTY',
    'NEW',
    'MEASURED',
    'PREDICTED',
    'DELETED',
    'INVALID'
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
    'OTHER_VEHICLE',
    'TL',
)

MOTION_STATUS = enum(**dict((name, n) for n, name in enumerate(MOTION_ST_VALS)))
LANE_STATUS = enum(**dict((name, n) for n, name in enumerate(LANE_ST_VALS)))
OBJ_CLASS = enum(**dict((name, n) for n, name in enumerate(OBJ_CLASS_VALS)))
MAINTENANCE_STATE = enum(**dict((name, n) for n, name in enumerate(MAINTENANCE_STATE)))

signalTemplate = (
    ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620.MOS_Cycle.MOS_ShortObjectListMeas.obj[%d].internalObjectID"),
    ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620.MOS_Cycle.MOS_ShortObjectListMeas.obj[%d].distXStD"),
    ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620.MOS_Cycle.MOS_ShortObjectListMeas.obj[%d].distYStD"),
    ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620.MOS_Cycle.MOS_ShortObjectListMeas.obj[%d].absAccelX"),
    ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620.MOS_Cycle.MOS_ShortObjectListMeas.obj[%d].absAccelY"),
    ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620.MOS_Cycle.MOS_ShortObjectListMeas.obj[%d].relAccelX"),
    ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620.MOS_Cycle.MOS_ShortObjectListMeas.obj[%d].relAccelY"),
    ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620.MOS_Cycle.MOS_ShortObjectListMeas.obj[%d].distY"),
    ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620.MOS_Cycle.MOS_ShortObjectListMeas.obj[%d].distX"),
    ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620.MOS_Cycle.MOS_ShortObjectListMeas.obj[%d].absVelX"),
    ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620.MOS_Cycle.MOS_ShortObjectListMeas.obj[%d].absVelY"),
    ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620.MOS_Cycle.MOS_ShortObjectListMeas.obj[%d].relVelX"),
    ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620.MOS_Cycle.MOS_ShortObjectListMeas.obj[%d].relVelY"),
    ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620.MOS_Cycle.MOS_ShortObjectListMeas.obj[%d].existProbability"),
    ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620.MOS_Cycle.MOS_ShortObjectListMeas.obj[%d].dynamicProperty"),
    ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620.MOS_Cycle.MOS_ShortObjectListMeas.obj[%d].length"),
    ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620.MOS_Cycle.MOS_ShortObjectListMeas.obj[%d].width"),
    ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620.MOS_Cycle.MOS_ShortObjectListMeas.obj[%d].maintenanceState"),

)

# signalTemplate = (
#     ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620_MOS_Cycle_MOS_ShortObjectListMeas_obj%d_internalObjectID"),
#     ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620_MOS_Cycle_MOS_ShortObjectListMeas_obj%d_distXStD"),
#     ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620_MOS_Cycle_MOS_ShortObjectListMeas_obj%d_distYStD"),
#     ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620_MOS_Cycle_MOS_ShortObjectListMeas_obj%d_absAccelX"),
#     ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620_MOS_Cycle_MOS_ShortObjectListMeas_obj%d_absAccelY"),
#     ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620_MOS_Cycle_MOS_ShortObjectListMeas_obj%d_relAccelX"),
#     ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620_MOS_Cycle_MOS_ShortObjectListMeas_obj%d_relAccelY"),
#     ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620_MOS_Cycle_MOS_ShortObjectListMeas_obj%d_distY"),
#     ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620_MOS_Cycle_MOS_ShortObjectListMeas_obj%d_distX"),
#     ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620_MOS_Cycle_MOS_ShortObjectListMeas_obj%d_absVelX"),
#     ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620_MOS_Cycle_MOS_ShortObjectListMeas_obj%d_absVelY"),
#     ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620_MOS_Cycle_MOS_ShortObjectListMeas_obj%d_relVelX"),
#     ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620_MOS_Cycle_MOS_ShortObjectListMeas_obj%d_relVelY"),
#     ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620_MOS_Cycle_MOS_ShortObjectListMeas_obj%d_existProbability"),
#     ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620_MOS_Cycle_MOS_ShortObjectListMeas_obj%d_dynamicProperty"),
#     ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620_MOS_Cycle_MOS_ShortObjectListMeas_obj%d_length"),
#     ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620_MOS_Cycle_MOS_ShortObjectListMeas_obj%d_width"),
#     ("ARS620.MOS_Cycle.MOS_ShortObjectListMeas", "ARS620_MOS_Cycle_MOS_ShortObjectListMeas_obj%d_maintenanceState"),
# )


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
                # array_signal = signalTemplate[1].split('[')
                # if len(array_signal) == 2:
                #     array_value = array_signal[1].split(',')[1][:-1]
                #     shortName = array_signal[0].split('_')[-1] + array_value
                # else:
                shortName = signalTemplate[1].split('.')[-1]
            messageGroup1[shortName] = (signalTemplate[0], fullName)
        signalDict.append(messageGroup1)
        messageGroups.append(signalDict)
    return messageGroups


messageGroups = createMessageGroups(TRACK_MESSAGE_NUM, signalTemplate)


class Ars620Track(ObjectFromMessage):
    attribs = []
    for signalTemplate in signalTemplate:
        fullName = signalTemplate[1]
        if "fPosX" in fullName or "fPosY" in fullName:
            full_position_string = fullName.split('_aShapePointCoordinatesI')[1]
            pos_index, pos_string = full_position_string.split('I_')
            shortName = pos_string + pos_index
        else:
            # array_signal = signalTemplate[1].split('[')
            # if len(array_signal) == 2:
            #     array_value = array_signal[1].split(',')[1][:-1]
            #     shortName = array_signal[0].split('_')[-1] + array_value
            # else:
            shortName = signalTemplate[1].split('.')[-1]
        attribs.append(shortName)

    _attribs = tuple(attribs)
    _special_methods = 'alive_intervals'

    def __init__(self, id, time, source, group, invalid_mask, scaletime=None):
        self._invalid_mask = invalid_mask
        self._group = group
        super(Ars620Track, self).__init__(id, time, None, None, scaleTime=None)
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
        arr = np.ma.masked_array(data, mask=self._distX.mask)
        return arr

    def dx(self):
        return self._distX

    def general_uid(self):
        return self._internalObjectID

    def dx_std(self):
        return self._distXStD

    def dy(self):
        return self._distY

    def dy_std(self):
        return self._distYStD

    def range(self):
        return np.sqrt(np.square(self.dx) + np.square(self.dy))

    def angle(self):
        return np.arctan2(self.dy, self.dx)

    def ax_abs(self):
        return self._absAccelX

    def ay_abs(self):
        return self._absAccelY

    def ax(self):
        return self._relAccelX

    def ay(self):
        return self._relAccelY

    def vx_abs(self):
        return self._absVelX

    def vy_abs(self):
        return self._absVelY

    def vx(self):
        return self._relVelX

    def vy(self):
        return self._relVelY

    def width(self):
        return self._Width

    def length(self):
        return self._length

    def video_conf(self):
        return self._existProbability

    def ttc(self):
        with np.errstate(divide='ignore'):
            ttc = np.where(self.vx < -1e-3,  # avoid too large (meaningless) values
                           -self.dx / self.vx,
                           np.inf)
        return ttc

    def invttc(self):
        return 1. / self.ttc

    def maintenance_state(self):
        empty = self._maintenanceState == MAINTENANCE_STATE.EMPTY
        new = self._maintenanceState == MAINTENANCE_STATE.NEW

        measured = self._maintenanceState == MAINTENANCE_STATE.MEASURED
        predicted = self._maintenanceState == MAINTENANCE_STATE.PREDICTED
        deleted = self._maintenanceState == MAINTENANCE_STATE.DELETED

        invalid = self._maintenanceState == MAINTENANCE_STATE.INVALID

        return MaintenanceState(empty=empty, new=new, measured=measured, predicted=predicted, deleted=deleted,
                                invalid=invalid)

    def mov_dir(self):
        crossing_left = self._dynamicProperty == MOTION_STATUS.CROSSING_LEFT
        crossing_right = self._dynamicProperty == MOTION_STATUS.CROSSING_RIGHT

        stationary = self._dynamicProperty == MOTION_STATUS.STATIONARY
        stopped = self._dynamicProperty == MOTION_STATUS.STOPPED
        unknown = self._dynamicProperty == MOTION_STATUS.UNKNOWN

        ongoing = self._dynamicProperty == MOTION_STATUS.MOVING
        oncoming = self._dynamicProperty == MOTION_STATUS.ONCOMING
        undefined = (unknown | stationary | stopped)
        dummy = np.zeros(self._dynamicProperty.shape, dtype=bool)
        arr = np.ma.masked_array(dummy, mask=self._distX.mask)
        return MovingDirection(oncoming=oncoming, ongoing=ongoing, undefined=undefined, crossing=arr,
                               crossing_left=crossing_left, crossing_right=crossing_right)

    def mov_state(self):
        crossing_left = self._dynamicProperty == MOTION_STATUS.CROSSING_LEFT
        crossing_right = self._dynamicProperty == MOTION_STATUS.CROSSING_RIGHT
        moving = self._dynamicProperty == MOTION_STATUS.MOVING
        oncoming = self._dynamicProperty == MOTION_STATUS.ONCOMING
        stationary = self._dynamicProperty == MOTION_STATUS.STATIONARY
        stopped = self._dynamicProperty == MOTION_STATUS.STOPPED
        unknown = self._dynamicProperty == MOTION_STATUS.UNKNOWN
        dummy = np.zeros(self._dynamicProperty.shape, dtype=bool)
        arr = np.ma.masked_array(dummy, mask=self._distX.mask)
        return ARS620MovingState(unknown=unknown, moving=moving, oncoming=oncoming, stat=stationary, stopped=stopped,
                                 crossing_left=crossing_left, crossing_right=crossing_right)

    def tr_state(self):
        valid = ma.masked_array(~self._distX.mask, self._distX.mask)
        meas = np.ones_like(valid)
        hist = np.ones_like(valid)
        for st, end in maskToIntervals(~self._distX.mask):
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
            object_id = group.get_value("internalObjectID", ScaleTime=common_time)
            invalid_mask = (np.isnan(object_id))
            #						if np.all(invalid_mask):
            #								continue
            VALID_FLAG = True
            tracks[_id] = Ars620Track(_id, common_time, self.source, group, invalid_mask, scaletime=common_time)
        if not VALID_FLAG:
            logging.warning("Error: {} :Measurement does not contain ARS620 object data".format(self.source.FileName))
        return tracks, signals


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\evaluation\pytch2_eval\rrec2mf4\mf4_eval\2025-02-18\mi5id5649__2025-02-18_13-15-53.mf4"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    tracks = manager_modules.calc('fill_flc25_ars620_tracks@aebs.fill', manager)
    print(tracks)
# print(tracks[0][0].fusion_quality)
# print(tracks)
