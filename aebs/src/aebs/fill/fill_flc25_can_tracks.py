# -*- dataeval: init -*-
# -*- coding: utf-8 -*-
import logging

import numpy as np
import numpy.ma as ma
from metatrack import ObjectFromMessage
from interface import iCalc
from measproc import cIntervalList
from measproc.IntervalList import maskToIntervals
from metatrack import MovingDirection, MovingState, ObjectType, \
    TrackingState, MeasuredBy
from primitives.bases import PrimitiveCollection
from pyutils.enum import enum

TRACK_MESSAGE_NUM = 6

MOTION_ST_VALS = (
    'UNKNOWN',
    'MOVING',
    'ONCOMING',
    'CROSSING',
    'STATIONARY',
    'STOPPED',
)

OBJ_CLASS_VALS = (
    'UNCLASSIFIED',
    'POINT',
    'WIDE',
    'MOTORCYCLE',
    'CAR_OR_VAN',
    'TRUCK_OR_COACH',
)

MEASURED_BY_VALS = (
    'NO_OBJECT',
    'RADAR_ONLY',
    'CAMERA_ONLY',
    'RADAR_CAMERA_CONFIRMED',
)
MOTION_STATUS = enum(**dict((name, n) for n, name in enumerate(MOTION_ST_VALS)))
OBJ_CLASS = enum(**dict((name, n) for n, name in enumerate(OBJ_CLASS_VALS)))
MEASURED_BY_ST = enum(**dict((name, n) for n, name in enumerate(MEASURED_BY_VALS)))
signalTemplate = (
    ("Track%d_A", "TrackId"),
    ("Track%d_A", "TrackWidth"),
    ("Track%d_A", "TrackingState"),
    ("Track%d_A", "Classification"),
    ("Track%d_A", "Confidence"),
    ("Track%d_A", "CutInCutOut"),
    ("Track%d_A", "DynState"),
    ("Track%d_A", "FusionState"),
    ("Track%d_B", "RelAccX"),
    ("Track%d_B", "RelVelX"),
    ("Track%d_B", "RelVelY"),
    ("Track%d_C", "RelAccY"),
    ("Track%d_C", "RelDistX"),
    ("Track%d_C", "RelDistY"),
)


def createMessageGroups(MESSAGE_NUM, signalTemplates):
    messageGroups = []
    for m in xrange(1, MESSAGE_NUM + 1):
        messageGroup = {}
        for signalTemplate in signalTemplates:
            fullName = signalTemplate[1]
            shortName = signalTemplate[1]
            messageGroup[shortName] = (signalTemplate[0] % m, fullName)
        messageGroups.append(messageGroup)
    return messageGroups


messageGroups = createMessageGroups(TRACK_MESSAGE_NUM, signalTemplate)


class Flc25CanTrack(ObjectFromMessage):
    _attribs = tuple(tmpl[1] for tmpl in signalTemplate)
    _special_methods = 'alive_intervals'

    def __init__(self, id, time, source, group, invalid_mask, scaletime=None):
        self._invalid_mask = invalid_mask
        self._group = group
        super(Flc25CanTrack, self).__init__(id, time, None, None, scaleTime=None)
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
        arr = np.ma.masked_array(data, mask=self._RelDistX.mask)
        return arr

    def dx(self):
        return self._RelDistX

    def dy(self):
        return self._RelDistY

    def range(self):
        return np.sqrt(np.square(self.dx) + np.square(self.dy))

    def angle(self):
        return np.arctan2(self.dy, self.dx)

    def vx(self):
        return self._RelVelX

    def vy(self):
        return self._RelVelY

    def ax(self):
        return self._RelAccX

    def ay(self):
        return self._RelAccY

    def width(self):
        return self._TrackWidth

    def video_conf(self):
        return self._Confidence

    def ttc(self):
        with np.errstate(divide='ignore'):
            ttc = np.where(self.vx < -1e-3,  # avoid too large (meaningless) values
                           -self.dx / self.vx,
                           np.inf)
        return ttc

    def invttc(self):
        return 1. / self.ttc

    def mov_dir(self):
        crossing = self._DynState == MOTION_STATUS.CROSSING

        stationary = self._DynState == MOTION_STATUS.STATIONARY
        stopped = self._DynState == MOTION_STATUS.STOPPED
        unknown = self._DynState == MOTION_STATUS.UNKNOWN

        ongoing = self._DynState == MOTION_STATUS.MOVING
        oncoming = self._DynState == MOTION_STATUS.ONCOMING
        undefined = unknown | stationary | stopped
        dummy = np.zeros(self._Classification.shape, dtype=bool)
        arr = np.ma.masked_array(dummy, mask=self._RelDistX.mask)
        return MovingDirection(oncoming=oncoming, ongoing=ongoing, undefined=undefined, crossing=crossing,
                               crossing_left=arr, crossing_right=arr)

    def obj_type(self):
        point = self._Classification == OBJ_CLASS.POINT
        wide = self._Classification == OBJ_CLASS.WIDE
        unclassified = self._Classification == OBJ_CLASS.UNCLASSIFIED
        motorcycle = self._Classification == OBJ_CLASS.MOTORCYCLE
        car = self._Classification == OBJ_CLASS.CAR_OR_VAN
        truck = self._Classification == OBJ_CLASS.TRUCK_OR_COACH
        # dummy data
        dummy = np.zeros(self._Classification.shape, dtype=bool)
        arr = np.ma.masked_array(dummy, mask=self._RelDistX.mask)
        return ObjectType(unknown=unclassified, pedestrian=arr, motorcycle=motorcycle, car=car,
                          truck=truck,
                          bicycle=arr, point=point, wide=wide)

    def mov_state(self):
        crossing = self._DynState == MOTION_STATUS.CROSSING
        moving = self._DynState == MOTION_STATUS.MOVING
        oncoming = self._DynState == MOTION_STATUS.ONCOMING
        stationary = self._DynState == MOTION_STATUS.STATIONARY
        stopped = self._DynState == MOTION_STATUS.STOPPED
        unknown = self._DynState == MOTION_STATUS.UNKNOWN
        dummy = np.zeros(self._Classification.shape, dtype=bool)
        arr = np.ma.masked_array(dummy, mask=self._RelDistX.mask)
        return MovingState(stat=stationary, stopped=stopped, moving=moving, unknown=unknown, crossing=crossing,
                           crossing_left=arr, crossing_right=arr, oncoming=oncoming)

    def tr_state(self):
        valid = ma.masked_array(~self._RelDistX.mask, self._RelDistX.mask)
        meas = np.ones_like(valid)
        hist = np.ones_like(valid)
        for st, end in maskToIntervals(~self._RelDistX.mask):
            if st != 0:
                hist[st] = False
        return TrackingState(valid=valid, measured=meas, hist=hist)

    def alive_intervals(self):
        new = self.tr_state.valid & ~self.tr_state.hist
        validIntervals = cIntervalList.fromMask(self.time, self.tr_state.valid)
        newIntervals = cIntervalList.fromMask(self.time, new)
        alive_intervals = validIntervals.split(st for st, _ in newIntervals)
        return alive_intervals

    def measured_by(self):
        no_info = self._FusionState == MEASURED_BY_ST.NO_OBJECT
        radar_only = self._FusionState == MEASURED_BY_ST.RADAR_ONLY
        camera_only = self._FusionState == MEASURED_BY_ST.CAMERA_ONLY
        fused = self._FusionState == MEASURED_BY_ST.RADAR_CAMERA_CONFIRMED
        # dummy data
        dummy = np.zeros(self._FusionState.shape, dtype=bool)
        arr = np.ma.masked_array(dummy, mask=self._RelDistX.mask)
        return MeasuredBy(none=no_info, prediction=arr, radar_only=radar_only, camera_only=camera_only, fused=fused)

    def tracking_state(self):
        return self._TrackingState

    def cut_in_cut_out(self):
        return self._CutInCutOut


class Calc(iCalc):
    dep = 'calc_common_time-flc25',

    def check(self):
        modules = self.get_modules()
        source = self.get_source()
        commonTime = modules.fill(self.dep[0])
        groups = []
        for sg in messageGroups:
            groups.append(source.selectSignalGroup([sg]))
        return groups, commonTime

    def fill(self, groups, common_time):
        tracks = PrimitiveCollection(common_time)
        signals = messageGroups
        VALID_FLAG = False
        for _id, group in enumerate(groups):
            object_id = group.get_value("TrackId", ScaleTime=common_time)
            invalid_mask = (object_id == 254) | (np.isnan(object_id))
#            if np.all(invalid_mask):
#                continue
            VALID_FLAG = True
            tracks[_id] = Flc25CanTrack(_id, common_time, self.source, group, invalid_mask, scaletime=common_time)
        if not VALID_FLAG:
            logging.warning("Error: {} :Measurement does not contain CAN object data".format(self.source.FileName))
        return tracks, signals


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\Data\Development\PythonToolchainSupport\ContiMeasurementsSuport\hmc_issue\UnknownTruckId__2021-02-18_07-31-46.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    tracks = manager_modules.calc('fill_flc25_can_tracks@aebs.fill', manager)
    print(tracks)
