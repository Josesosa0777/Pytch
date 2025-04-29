# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import numpy as np
import numpy.ma as ma

from primitives.bases import PrimitiveCollection
from interface import iCalc
from measparser.signalgroup import select_allvalid_sgs
from metatrack import MovingState, ObjectType, TrackingState
from flr20_raw_tracks_base import findUniqueIds, TrackFromMessage, rescaleCanMessages, createRadarTrackMasks, \
                                  stoppedNstationary
from pyutils.enum import enum

MSG_NUM = 63

# Object_Interface_10A
# Object_ID_10                        ID number
# ax_m_s_s_10               [m/s^2]   absolute acceleration
# ay_m_s_s_10               [m/s^2]   absolute acceleration
# x_m_10                    [m]       Object X relative position in car coordinate system
# y_m_10                    [m]       Object Y relative position in car coordinate system
# PredictionAge_10          [s]       Age of the prediction
#
#
# Object_Interface_10B
# vx_m_s_10                 [m/s]     Relative velocity
# vy_m_s_10                 [m/s]     Relative velocity
# Classification_10                   Object classification
# TrackAge_10               [s]       Age of the track
#
#
# Object_Interface_10C
# Length_m_10               [m]       Length of the object
# Width_m_10                [m]       Width of the object
# MotionType_10                       The motion type defines, if an object is stationary or moving
# ReferencePoint_10                   Defines the position of the reference point
#                                     with respect to a box representation of the object
#                                     (defined by length, width, orientation, and reference point)
# ExistenceProbability_10             Existence probability
#
#
# Object_Interface_10D
# Orientation_rad_10        [rad]     Object orientation in host vehicle coordinate system
# YawRate_rad_s_10          [rad/s]   Yaw rate
#
#
#
# Object_Interface_Header_1
# NumObject                           Number of Transmitted Objects
# DetectionRange            [m]       Maximum Detection Range
# HostSpeed                 [m/s]     Host vehicle speed
# HostYawRate               [rad/s]   Host vehicle yaw rate

MOVING_STATE = enum(UNKNOWN=0, STATIC=1, DYNAMIC=2)
CLASSIFICATION_STATE = enum(UNKNOWN=0, PEDESTRIAN=1, MOTORCYCLE=2, CAR=3, TRUCK=4, BICYCLE=5)
VALID_STATE = enum(INVALID=0, VALID=1)

signals = {
    "Object_Interface_%(k)dA": ("Object_ID_%(k)d", "ax_m_s_s_%(k)d", "ay_m_s_s_%(k)d",
                                "x_m_%(k)d", "y_m_%(k)d", "PredictionAge_%(k)d"),

    "Object_Interface_%(k)dB": ("vx_m_s_%(k)d", "vy_m_s_%(k)d", "ClassificationQuality_%(k)d",
                                "Classification_%(k)d", "Classification_Age_%(k)d", "TrackAge_%(k)d"),

    "Object_Interface_%(k)dC": ("Length_m_%(k)d", "Width_m_%(k)d", "LengthQuality_%(k)d",
                                "WidthQuality_%(k)d", "MotionType_%(k)d", "ReferencePoint_%(k)d",
                                "ExistenceProbability_%(k)d"),

    "Object_Interface_%(k)dD": ("Orientation_rad_%(k)d", "OrientationQuality_%(k)d", "YawRateQuality_%(k)d",
                                "YawRate_rad_s_%(k)d", "Cov_a_x_%(k)d"),

    "Object_Interface_%(k)dE": ("Cov_a_xy_%(k)d", "Cov_a_y_%(k)d",
                                "Cov_v_x_%(k)d", "Cov_v_xy_%(k)d"),

    "Object_Interface_%(k)dF": ("Cov_v_y_%(k)d", "Cov_x_%(k)d",
                                "Cov_y_%(k)d", "Cov_xy_%(k)d"),
}

GROUP_LENGTH = sum(len(value) for value in signals.itervalues())

alias_template = []
for message in signals.itervalues():
    for signal in message:
        alias, _ = signal.rsplit('_%(k)d')
        alias_template.append(alias)


def create_message_groups(sgs_templates):
    """
    :Parameters:
        sgs_templates: dict
            {"MessageName<str>: (SignalName1<str>, ..., SignalNameN<str>)"}
    :Return:
        MessageGroups: list
            [
             {Alias1<str>: (DeviceName<str>, SignalName1<str>), ..., AliasN<str>: (DeviceName<str>, SignalNameN<str>)},
             {Alias1<str>: (DeviceName<str>, SignalName1<str>), ..., AliasN<str>: (DeviceName<str>, SignalNameN<str>)},
             ...
            ]
    """
    message_groups = []
    for m in xrange(1, MSG_NUM + 1):
        signal_group = {}
        for key, value in sgs_templates.iteritems():
            dev = key % {'k': m}
            for v in value:
                shortname = "_".join(v.split("_")[:-1])
                sig = v % {'k': m}
                signal_group[shortname] = (dev, sig)
        message_groups.append(signal_group)
    return message_groups


def create_mb79_track_mask(signals, id):
    track_index = signals["Object_ID"]      # Track ID
    tracking_status = signals["TrackAge"]   # Valid data
    mask = track_index.data == id           # track occurs in message
    mask &= ~track_index.mask               # data is valid
    mask &= tracking_status.data != 0       # tracking status ok
    mask &= ~tracking_status.mask           # data is valid
    return mask


class MB79Track(TrackFromMessage):
    _attribs = tuple(alias for alias in alias_template)

    # coordinate frame position and orientation --> transformation from center of gravity to front bumper
    dx0 = 4.0
    dy0 = 0.0
    angle0 = np.deg2rad(30.0)

    def __init__(self, _id, msg_time, msg_masks, source, optgroups, dir_corr, ego,
                 scaleTime=None, **kwargs):
        TrackFromMessage.__init__(self, _id, msg_time, msg_masks, source, optgroups, dir_corr,
                                  scaleTime=scaleTime, **kwargs)
        self._ego = ego
        self.offset_angle = self.angle0 + np.pi / 2
        return

    def rescale(self, scaleTime, **kwargs):
        ego = self._ego.rescale(scaleTime, **kwargs)
        cls = self.__class__
        return cls(self._id, self._msgTime, self._msgMasks, self._source,
                   self._groups, self._dirCorr, ego, scaleTime=scaleTime, **kwargs)

    def id(self):
        return self._Object_ID

    def dx(self):
        return self._x_m - self.dx0

    def dy(self):
        return self._y_m - self.dy0

    def range(self):
        return np.sqrt(np.square(self.dx) + np.square(self.dy))

    def angle(self):
        return np.arctan2(self.dy, self.dx)

    def vx(self):
        return self._vx_m_s

    def vy(self):
        return self._vy_m_s

    def ax(self):
        return self._ax_m_s_s

    def ay(self):
        return self._ay_m_s_s

    def orientation(self):
        return self._Orientation_rad

    def obj_type(self):
        unknown = self._Classification == CLASSIFICATION_STATE.UNKNOWN
        pedestrian = self._Classification == CLASSIFICATION_STATE.PEDESTRIAN
        motorcycle = self._Classification == CLASSIFICATION_STATE.MOTORCYCLE
        car = self._Classification == CLASSIFICATION_STATE.CAR
        truck = self._Classification == CLASSIFICATION_STATE.TRUCK
        bicycle = self._Classification == CLASSIFICATION_STATE.BICYCLE
        dummy = np.zeros(self._MotionType.shape, dtype=bool)
        arr = np.ma.masked_array(dummy, mask=self.dx.mask)
        return ObjectType(unknown=unknown, pedestrian=pedestrian, motorcycle=motorcycle,
                          car=car, truck=truck, bicycle=bicycle, point=arr, wide=arr)

    def yaw_rate(self):
        return self._YawRate_rad_s

    def ref_point(self):
        return self._ReferencePoint

    def length(self):
        return self._Length_m

    def width(self):
        return self._Width_m

    def mov_state(self):
        moving = self._MotionType == MOVING_STATE.DYNAMIC
        standing = self._MotionType == MOVING_STATE.STATIC
        stationary, stopped = stoppedNstationary(standing, moving)
        stationary = np.ma.masked_array(stationary, mask=standing.mask)
        stopped = np.ma.masked_array(stopped, mask=standing.mask)
        unknown = self._MotionType == MOVING_STATE.UNKNOWN
        dummy = np.zeros(self._MotionType.shape, dtype=bool)
        arr = np.ma.masked_array(dummy, mask=self.dx.mask)
        return MovingState(stat=stationary, stopped=stopped, moving=moving, unknown=unknown, crossing=arr, crossing_left=arr, crossing_right=arr, oncoming=arr)

    def tr_state(self):
        valid = ma.masked_array(~self._x_m.mask, self._x_m.mask)
        meas = self._PredictionAge == 0
        hist = self._TrackAge > 0
        return TrackingState(valid=valid, measured=meas, hist=hist)


class Calc(iCalc):
    obj_factory = MB79Track

    dep = "calc_mb79_egomotion",

    def check(self):

        ego = self.modules.fill(self.dep[0])

        groups = create_message_groups(signals)
        filtgroups = self.source.filterSignalGroups(groups)  # , Verbose=True)
        optgroups = select_allvalid_sgs(filtgroups, GROUP_LENGTH)

        return optgroups, ego

    def fill(self, optgroups, ego):
        common_time = ego.time

        tracks = PrimitiveCollection(common_time)

        sg_names = ["Object_ID", "TrackAge"]

        messages = rescaleCanMessages(common_time, self.source, optgroups, names=sg_names)

        ids = [message['Object_ID'].compressed() for message in messages.itervalues()]
        unique_ids = findUniqueIds(ids)

        track_masks = self.createRadarTrackMasks(messages, unique_ids, create_mb79_track_mask)

        # TODO: check for y coord axis direction correction
        dir_corr = 1

        for _id, msg_masks in track_masks.iteritems():
            tracks[_id] = self.obj_factory(_id, common_time, msg_masks, self.source, optgroups, dir_corr, ego)

        return tracks

    @staticmethod
    def createRadarTrackMasks(messages, ids, callback):
        return createRadarTrackMasks(messages, ids, callback)
