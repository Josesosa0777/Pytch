# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import numpy as np
import numpy.ma as ma

from primitives.bases import PrimitiveCollection
from interface import iCalc
from metatrack import MovingState, ObjectType, TrackingState
from flr20_raw_tracks_base import ObjectFromMessage, rescaleCanMessages, stoppedNstationary
from pyutils.enum import enum

NUMOFTRACKS = 62
MOVING_STATE = enum(STANDING=0, MOVING=1)
CLASSIFICATION_STATE = enum(UNKNOWN=0, TRUCK=1, CAR=2, MOTORCYCLE=3, PEDESTRIAN=11, ERROR=14, SNA=15)

# defining how a signal group will look like
SIGNAL_GROUP_TEMPLATE = {
    "x"          : ("Obj{:03d}", "DistX_Obj{:03d}"),
    "y"          : ("Obj{:03d}", "DistY_Obj{:03d}"),
    "speed_x"    : ("Obj{:03d}", "RelSpdX_Obj{:03d}"),
    "speed_y"    : ("Obj{:03d}", "RelSpdY_Obj{:03d}"),
    "class"      : ("Obj{}_add_info", "Class_Obj{:03d}"),
    "history"    : ("Obj{}_add_info", "ObsHist_Obj{:03d}"),
    "moving"     : ("Obj{}_add_info", "ObjectMoving_Obj{:03d}")
}

# Generate signal groups using the aliases
# signals is a list of dictionaries with the alias as key and
# a tuple of device name and signal name as value
signalgroups=[]
for device_number in xrange(NUMOFTRACKS):
    group={}
    for alias, (msg_name, sig_name) in SIGNAL_GROUP_TEMPLATE.iteritems():
        sig_name = sig_name.format(device_number)
        if alias in ["x", "y", "speed_x", "speed_y"]:
            # These signals are in messages with Obj000 format
            group[alias]=(msg_name.format(device_number), sig_name)
        else:
            # These signals are in messages with Obj000_001_add_info or Obj000_add_info format
            if(device_number%7 == 6):
                msg_name = msg_name.format("{:03d}").format(device_number)
            else:
                msg_name = msg_name.format("{:03d}_{:03d}")
                if((device_number/7)%2 == 0):
                    if(device_number%2 == 0):
                        msg_name = msg_name.format(device_number, device_number + 1)
                    else:
                        msg_name = msg_name.format(device_number - 1, device_number)
                else:
                    if (device_number % 2 == 0):
                        msg_name = msg_name.format(device_number - 1, device_number)
                    else:
                        msg_name = msg_name.format(device_number, device_number + 1)
            group[alias]=(msg_name, sig_name)
    signalgroups.append(group)

class ContiARS440Track(ObjectFromMessage):
    _attribs = SIGNAL_GROUP_TEMPLATE.keys()

    xoffset = 0
    yoffset = 0
    angle = 0

    def __init__(self, id, time, source, group, invalid_mask, scaletime=None):
        self._invalid_mask =invalid_mask
        self._group=group
        super(ContiARS440Track, self).__init__(id, time, None, None, scaleTime=None)
        return

    def _create(self, signalName):
        value = self._group.get_value(signalName, ScaleTime=self.time)
        mask = ~self._invalid_mask
        out=np.ma.masked_all_like(value)
        out.data[mask] = value[mask]
        out.mask &= ~mask
        return out

    def dx(self):
        return self._x + self.xoffset

    def dy(self):
        return self._y + self.yoffset

    def range(self):
        return np.sqrt(np.square(self.dx) + np.square(self.dy))

    def angle(self):
        return np.arctan2(self.dy, self.dx)

    def vx(self):
        return self._speed_x

    def vy(self):
        return self._speed_y

    def obj_type(self):
        pedestrian = self._class == CLASSIFICATION_STATE.PEDESTRIAN
        motorcycle = self._class == CLASSIFICATION_STATE.MOTORCYCLE
        car = self._class == CLASSIFICATION_STATE.CAR
        truck = self._class == CLASSIFICATION_STATE.TRUCK
        bicycle = np.zeros_like(self._class, dtype=np.bool)
        unknown = self._class == CLASSIFICATION_STATE.UNKNOWN
        dummy = np.zeros(self._moving.shape, dtype=bool)
        arr = np.ma.masked_array(dummy, mask=self.dx.mask)
        return ObjectType(unknown=unknown, pedestrian=pedestrian, motorcycle=motorcycle,
                          car=car, truck=truck, bicycle=bicycle, point=arr, wide=arr)

    def mov_state(self):
        moving = self._moving == MOVING_STATE.MOVING
        standing = self._moving == MOVING_STATE.STANDING
        stationary, stopped = stoppedNstationary(standing, moving)
        stationary = np.ma.masked_array(stationary, mask=standing.mask)
        stopped = np.ma.masked_array(stopped, mask=standing.mask)
        unknown = np.zeros(moving.shape)
        dummy = np.zeros(self._moving.shape, dtype=bool)
        arr = np.ma.masked_array(dummy, mask=self.dx.mask)
        return MovingState(stat=stationary, stopped=stopped, moving=moving, unknown=unknown, crossing=arr, crossing_left=arr, crossing_right=arr, oncoming=arr)

    def tr_state(self):
        valid = ma.masked_array(~self._x.mask, self._x.mask)
        meas = np.zeros_like(self._x, dtype=np.bool_)
        hist = ma.masked_array(self._history, self._x.mask)
        return TrackingState(valid=valid, measured=meas, hist=hist)

class Calc(iCalc):
    def check(self):
        groups = []
        for sg in signalgroups:
            groups.append(self.source.selectSignalGroup([sg]))
        return groups

    def fill(self, groups):
        common_time, _ = groups[0].get_signal("x")
        tracks = PrimitiveCollection(common_time)
        for _id, group in enumerate(groups):
            classification = group.get_value("class", ScaleTime=common_time)
            invalid_mask = np.logical_or(classification == CLASSIFICATION_STATE.ERROR,
                                         classification == CLASSIFICATION_STATE.SNA)
            if np.all(invalid_mask):
                continue
            tracks[_id] = ContiARS440Track(_id, common_time, None, group, invalid_mask,
                                           scaletime=common_time)
        return tracks


if __name__ == '__main__':
  from config.Config import init_dataeval

  meas_path = r'//file/Messdat/DAS/Conti/ARS430_ARS440_20170331/003Recorder.MDF'
  config, manager, manager_modules = init_dataeval(['-m', meas_path])
  conti = manager_modules.calc('calc_conti_ars440@aebs.fill', manager)
  dummy_id, dummy_target = conti.iteritems().next()
  print str(dummy_id) + str(type(dummy_id))
  print str(dummy_target.dx) + str(type(dummy_target.dx))
  print str(dummy_target.vx) + str(type(dummy_target.dx))