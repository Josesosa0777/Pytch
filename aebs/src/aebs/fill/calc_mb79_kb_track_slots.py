# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import numpy as np

from primitives.bases import PrimitiveCollection
from interface import iCalc
from metatrack import MovingState, TrackingState
from flr20_raw_tracks_base import TrackFromMessage
from pyutils.enum import enum

MOTION_STATE = enum(UNKNOWN=0, STATIONARY=1, STOPPED=2, MOVING=3)
TRACK_STATUS = enum(INVALID=0, INITIALIZED=1, TENTATIVE=2, ESTABLISHED=3)

NUM_OF_TRACKS = 20

signals = [{
    # checkpoint 1.6 - velocity signal naming corrected
    "XRelPosVeh":           ("TA", "tracking_out_XRelPosVeh"),
    "YRelPosVeh":           ("TA", "tracking_out_YRelPosVeh"),
    "XRelVelocity":         ("TA", "tracking_out_XRelVelocity"),
    "XAbsVelocity":         ("TA", "tracking_out_XAbsVelocity"),
    "YRelVelocity":         ("TA", "tracking_out_YRelVelocity"),
    "YAbsVelocity":         ("TA", "tracking_out_YAbsVelocity"),
    "ObjMotionState":       ("TA", "tracking_out_ObjMotionState"),
    "GatingRectangle":      ("TA", "tracking_out_GatingRectangle"),
    "YRelPosVehRightSide":  ("TA", "tracking_out_YRelPosVehRightSide"),
    "Orientation":          ("TA", "tracking_out_Orientation"),
    "TrackStatus":          ("TA", "tracking_out_TrackStatus"),
},
{
    # checkpoint 1.4 - velocity signal interpretation changed, but naming not updated
    "XRelPosVeh":           ("TA", "tracking_out_XRelPosVeh"),
    "YRelPosVeh":           ("TA", "tracking_out_YRelPosVeh"),
    "XRelVelocity":         ("TA", "tracking_out_XAbsVelocity"),
    "XAbsVelocity":         ("TA", "tracking_out_XDiffVelocity"),
    "YRelVelocity":         ("TA", "tracking_out_YAbsVelocity"),
    "YAbsVelocity":         ("TA", "tracking_out_YDiffVelocity"),
    "ObjMotionState":       ("TA", "tracking_out_ObjMotionState"),
    "GatingRectangle":      ("TA", "tracking_out_GatingRectangle"),
    "YRelPosVehRightSide":  ("TA", "tracking_out_YRelPosVehRightSide"),
    "Orientation":          ("TA", "tracking_out_Orientation"),
    "TrackStatus":          ("TA", "tracking_out_TrackStatus"),
}]


class KBTracks(TrackFromMessage):
    _attribs = tuple(signals[0].keys())

    # coordinate frame position and orientation --> transformation from center of gravity to front bumper
    dx0 = 2.69
    dy0 = 0.0

    def __init__(self, id, common_time, group, invalid_mask, **kwargs):
        dir_corr = None  # no direction correction
        source = None  # source unnecessary as signals can be loaded directly from signal group
        super(KBTracks, self).__init__(id, common_time, True, source, None, dir_corr, **kwargs)
        self._group = group
        self._invalid_mask = invalid_mask
        return

    def _create(self, signalName):
        arr = self._group.get_value(signalName)
        arr = arr[:, self._id]
        arr_copy = arr.copy() # arr is read-only
        arr_copy[self._invalid_mask] = 0 # set zero as invalid value
        out = np.ma.masked_array(arr_copy, self._invalid_mask)
        # out = self._rescale(arr) # TODO: rescale method
        return out

    def id(self):
        # TODO: id attribute (might be different over time) when signal available
        raise NotImplementedError

    def dx(self):
        return self._XRelPosVeh - self.dx0

    def dy(self):
        return self._YRelPosVeh - self.dy0

    def range(self):
        return np.sqrt(np.square(self.dx) + np.square(self.dy))

    def angle(self):
        return np.arctan2(self.dy, self.dx)

    def vx(self):
        return self._XRelVelocity

    def vy(self):
        return self._YRelVelocity

    def vx_abs(self):
        return self._XAbsVelocity

    def vy_abs(self):
        return self._YAbsVelocity

    def mov_state(self):
        moving = self._ObjMotionState == MOTION_STATE.MOVING
        stationary = self._ObjMotionState == MOTION_STATE.STATIONARY
        stopped = self._ObjMotionState == MOTION_STATE.STOPPED
        unknown = self._ObjMotionState == MOTION_STATE.UNKNOWN
        dummy = np.zeros(self._ObjMotionState.shape, dtype=bool)
        arr = np.ma.masked_array(dummy, mask=self.dx.mask)
        return MovingState(stat=stationary, stopped=stopped, moving=moving, unknown=unknown, crossing=arr, crossing_left=arr, crossing_right=arr, oncoming=arr)

    def tr_state(self):
        valid = np.ma.masked_array(~self._invalid_mask, self._invalid_mask)
        meas = None # TODO
        hist = self._TrackStatus == TRACK_STATUS.ESTABLISHED
        return TrackingState(valid=valid, measured=meas, hist=hist)


class Calc(iCalc):
    def check(self):
        group = self.source.selectSignalGroup(signals)
        return group

    def fill(self, group):
        common_time, status_signal = group.get_signal("TrackStatus")
        dx = group.get_value("XRelPosVeh")
        tracks = PrimitiveCollection(common_time)
        for tr_slot in range(NUM_OF_TRACKS):
            invalid_mask = (status_signal[:,tr_slot] == TRACK_STATUS.INVALID) | (dx[:,tr_slot] > 1000)
            if np.all(invalid_mask):
                continue
            tracks[tr_slot] = KBTracks(tr_slot, common_time, group, invalid_mask)
        return tracks
