# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import numpy as np
import numpy.ma as ma

from primitives.bases import PrimitiveCollection
from interface import iCalc
from metatrack import MovingState, ObjectType, TrackingState
from flr20_raw_tracks_base import findUniqueIds, TrackFromMessage, rescaleCanMessages, createRadarTrackMasks
from pyutils.enum import enum

NUM_OF_PEDOBJ = 6

MOVING_STATE = enum(NOT_DET=0, MOVING=1, MOVING_STOPPED=2, STATIC=3, CROSSING=4, ONCOMING=5)
CLASSIFICATION_STATE = enum(UNKNOWN=0, PEDESTRIAN=11, MOTORCYCLE=3, CAR=2, TRUCK=1)

DEVICES=[]
LOCATIONS = ("Main", "Left", "Right")
DIST = ("Near", "Far")
DEVICES = [l+d for l in LOCATIONS for d in DIST]
DEVICES.append("StraightStat")
DEVICES=tuple(DEVICES)
device_letters=('A', 'B', 'C', 'E', 'D', 'F', 'G')

SIGNAL_GROUP_TEMPLATE = {
    "x"         :("Obj{}_{}_1", "DistX_Obj{}"),
    "y"         :("Obj{}_{}_1", "DistY_Obj{}"),
    "speed_x"   :("Obj{}_{}_1", "SpdX_Obj{}"),
    "speed_y"   :("Obj{}_{}_1", "SpdY_Obj{}"),
    "width"     :("Obj{}_{}_1", "Width_Obj{}"),
    "track_ID"  :("Obj{}_{}_2", "Num_Obj{}"),
    "type"      :("Obj{}_{}_2", "Type_Obj{}"),
    "class"     :("Obj{}_{}_2", "Class_Obj{}")
}
SIGNAL_GROUP_TEMPLATE_PED = {
    "x"         :("PedObj{}_1", "DistX_PedObj{}"),
    "y"         :("PedObj{}_1", "DistY_PedObj{}"),
    "speed_x"   :("PedObj{}_1", "SpdX_PedObj{}"),
    "speed_y"   :("PedObj{}_1", "SpdY_PedObj{}"),
    "width"     :("PedObj{}_1", "Width_PedObj{}"),
    "track_ID"  :("PedObj{}_2", "Num_PedObj{}"),
    "type"      :("PedObj{}_2", "Type_PedObj{}"),
    "class"     :("PedObj{}_2", "Class_PedObj{}")
}

# Generate signal groups using the aliases
# signals is a list of dictionaries with the alias as key and
# a tuple of device name and signal name as value
signalgroups=[]
# the first 7 device has this format
for dev_name, dev_letter in zip(DEVICES, device_letters):
    group={}
    for alias, (msg_name, sig_name) in SIGNAL_GROUP_TEMPLATE.iteritems():
        msg_name = msg_name.format(dev_letter, dev_name)
        sig_name = sig_name.format(dev_letter)
        group[alias]=(msg_name, sig_name)
    signalgroups.append(group)
# add the remaining signals, namely PedObjs
for i in xrange(NUM_OF_PEDOBJ):
    group={}
    for alias, (msg_name, sig_name) in SIGNAL_GROUP_TEMPLATE_PED.iteritems():
        msg_name = msg_name.format(i)
        sig_name = sig_name.format(i)
        group[alias]=(msg_name, sig_name)
    signalgroups.append(group)

SensorState = [
    {
               "el"         :('SensorState_1', "AlignEl"),
               "qel"        :('SensorState_1', "AlignQualEl"),
               "progress"   :('SensorState_1', "AlignProgress"),
               "runstate"   :('SensorState_1', "AlignRunState"),
               "failstate"  :('SensorState_1', "AlignFailState")
    }
]

def create_ContiARS430_track_mask(signals, id):
    track_index = signals["track_ID"]  # Track ID
    tracking_status = signals["type"]  # Valid data
    mask = track_index.data == id  # track occurs in message
    mask &= ~track_index.mask  # data is valid
    mask &= tracking_status.data != 0
    temp1 = tracking_status.data != 6
    temp2 = tracking_status.data != 7# tracking status ok
    mask &= temp1
    mask &= temp2
    mask &= ~tracking_status.mask  # data is valid
    return mask


class ContiARS430Track(TrackFromMessage):
    _attribs = SIGNAL_GROUP_TEMPLATE.keys()

    def __init__(self, id, time, source, groups, masks, scaletime=None):
        dir_corr = None
        super(ContiARS430Track, self).__init__(id, time, masks, source, groups, dir_corr, scaleTime=scaletime)
        return

    def which(self):
        # Making an array with the same size as the first mask
        out = np.full_like(self._msgMasks[self._msgMasks.keys()[0]], -1, dtype=np.int8)
        # tracknum is the number of the group in the signalgroups list
        # this is why it's possible to label objects this way
        for tracknum, mask in self._msgMasks.iteritems():
            out[mask]=tracknum
        # update device letters with the six pedestrian objects
        all_device_letters = device_letters + ('P', 'P', 'P', 'P', 'P', 'P')
        out = [all_device_letters[index] if index!=-1 else '' for index in out]
        return out

    def dx(self):
        return self._x

    def dy(self):
        return self._y

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
        bicycle = np.zeros_like(self._class, dtype=np.bool_)
        unknown = self._class == CLASSIFICATION_STATE.UNKNOWN
        dummy = np.zeros(self._type.shape, dtype=bool)
        arr = np.ma.masked_array(dummy, mask=self.dx.mask)
        return ObjectType(unknown=unknown, pedestrian=pedestrian, motorcycle=motorcycle,
                          car=car, truck=truck, bicycle=bicycle, point=arr, wide=arr)

    def width(self):
        return self._width

    def mov_state(self):
        moving = (self._type == MOVING_STATE.MOVING) | (self._type == MOVING_STATE.ONCOMING) |\
                 (self._type == MOVING_STATE.CROSSING)
        stationary = self._type == MOVING_STATE.STATIC
        stopped = self._type == MOVING_STATE.MOVING_STOPPED
        unknown = self._type == 0
        dummy = np.zeros(self._type.shape, dtype=bool)
        arr = np.ma.masked_array(dummy, mask=self.dx.mask)
        return MovingState(stat=stationary, stopped=stopped, moving=moving, unknown=unknown, crossing=arr, crossing_left=arr, crossing_right=arr, oncoming=arr)

    def tr_state(self):
        valid = ma.masked_array(~self._x.mask, self._x.mask)
        meas = np.zeros_like(self._x, dtype=np.bool_)
        hist = np.zeros_like(self._x, dtype=np.bool_)
        return TrackingState(valid=valid, measured=meas, hist=hist)

class Calc(iCalc):
    def check(self):
        stateGroup = self.source.selectSignalGroup(SensorState)
        groups = []
        for sg in signalgroups:
            groups.append(self.source.selectSignalGroup([sg]))
        return stateGroup, groups

    def fill(self, stategroup, groups):
        common_time, _ = stategroup.get_signal("el")
        # find all unique tracks in all groups
        SGS_NAMES=['track_ID','type']
        messages = rescaleCanMessages(common_time, self.source, groups, names=SGS_NAMES)
        ids = [message['track_ID'].compressed() for message in messages.itervalues()]
        unique_ids = findUniqueIds(ids)
        track_masks=createRadarTrackMasks(messages, unique_ids, create_ContiARS430_track_mask)
        tracks = PrimitiveCollection(common_time)

        for _id, msg_masks in track_masks.iteritems():
            tracks[_id] = ContiARS430Track(_id, common_time, self.source, groups, msg_masks,
                                           scaletime=common_time)

        return tracks


if __name__ == '__main__':
  from config.Config import init_dataeval

  meas_path = r'C:\KBData\ContiARS430\DAF__2017-03-06_18-14-02.mf4'
  config, manager, manager_modules = init_dataeval(['-m', meas_path])
  conti = manager_modules.calc('calc_conti_ars430@aebs.fill', manager)
  dummy_id, dummy_target = conti.iteritems().next()
  print str(dummy_id) + str(type(dummy_id))
  print str(dummy_target.dx) + str(type(dummy_target.dx))
  print str(dummy_target.vx) + str(type(dummy_target.dx))