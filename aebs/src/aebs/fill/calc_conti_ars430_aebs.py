# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import numpy as np

from interface import iCalc
from metatrack import MovingState, ObjectType
from flr20_raw_tracks_base import ObjectFromMessage
from pyutils.enum import enum

MOVING_STATE = enum(NOT_DET=0, MOVING=1, MOVING_STOPPED=2, STATIC=3, CROSSING=4, ONCOMING=5)
CLASSIFICATION_STATE = enum(UNKNOWN=0, PEDESTRIAN=11, MOTORCYCLE=3, CAR=2, TRUCK=1)

signaltemplate={
    "x"         :   ("Obj{}_{}_1", "DistX_Obj{}"),
    "y"         :   ("Obj{}_{}_1", "DistY_Obj{}"),
    "speed_x"   :   ("Obj{}_{}_1", "SpdX_Obj{}"),
    "speed_y"   :   ("Obj{}_{}_1", "SpdY_Obj{}"),
    "track_ID"  :   ("Obj{}_{}_2", "Num_Obj{}"),
    "type"      :   ("Obj{}_{}_2", "Type_Obj{}"),
    "class"     :   ("Obj{}_{}_2", "Class_Obj{}"),
    "accel_x"   :   ("Obj{}_{}_2", "Accel_X_Obj{}"),
    "coll_relev":   ("Obj{}_{}_2", "CollRelevancyObj{}"),
}

# order is important!
DEVICES=(("A", "MainNear"), ("G", "StraightStat"))

signalgroups=[]
for (dev_letter, dev) in DEVICES:
    group={}
    for alias, (message, signal) in signaltemplate.iteritems():
        group[alias]=(message.format(dev_letter, dev), signal.format(dev_letter))
    signalgroups.append(group)

SensorState = [
    {
               "el"         :('SensorState_1', "AlignEl"),
    }
]


class ContiARS430MergedTrack(ObjectFromMessage):
    """
    This track merges track A and G in a way that it takes values from A if it is valid else take from G.
    If nor A or G is present return an invalid value.
    """
    _attribs = signaltemplate.keys()

    def __init__(self, id, msgTime,  groups, scaletime=None):
        dir_corr = None
        super(ContiARS430MergedTrack, self).__init__(id, msgTime, None, dir_corr, scaletime)
        self.time = scaletime
        #order is important!
        self._groupA = groups[0]
        self._groupG = groups[1]
        typeA = self._groupA.get_value('type', ScaleTime=self._msgTime, Order='valid', InvalidValue=0)
        typeG = self._groupG.get_value('type', ScaleTime=self._msgTime, Order='valid', InvalidValue=0)
        self.maskA, self.maskG = self._createMasks(typeA, typeG)
        return

    @staticmethod
    def _createMasks(typeA, typeG):
        """
        Decide for each track where it contains valid values.
        :returns true where the value is valid
        """
        maskA  = typeA != 0
        maskA &= typeA != 6
        maskA &= typeA != 7

        maskG  = typeG != 0
        maskG &= typeG != 6
        maskG &= typeG != 7

        return maskA, maskG

    def _create(self, signame):
        """
        Take values from both groups and merges them: if A is valid take it, else if G is valid take it, else invalid
        """
        arrA = self._groupA.get_value(signame, ScaleTime=self._msgTime, Order='valid', InvalidValue=0)
        arrG = self._groupG.get_value(signame, ScaleTime=self._msgTime, Order='valid', InvalidValue=0)
        # Where track A is valid take data from there. If not applicable decide if G is valid or write invalid value.
        data = np.where(self.maskA, arrA, np.where(self.maskG, arrG, 0))
        attrib = np.ma.masked_array(data, mask=~self.valid) # masked array mask is true where the data is invalid
        return attrib

    def valid(self):
        return self.maskA | self.maskG # valid where either A or G valid

    def dx(self):
        return self._x

    def dy(self):
        return self._y

    def range(self):
        return np.sqrt(np.square(self.dx) + np.square(self.dy))

    def vx(self):
        return self._speed_x

    def vy(self):
        return self._speed_y

    def ax(self):
        return self._accel_x

    def coll_relev(self):
        return self._coll_relev

    def obj_type(self):
        pedestrian = self._class == CLASSIFICATION_STATE.PEDESTRIAN
        motorcycle = self._class == CLASSIFICATION_STATE.MOTORCYCLE
        car        = self._class == CLASSIFICATION_STATE.CAR
        truck      = self._class == CLASSIFICATION_STATE.TRUCK
        unknown    = self._class == CLASSIFICATION_STATE.UNKNOWN
        bicycle    = np.zeros_like(self._class, dtype=np.bool_)
        dummy = np.zeros(self._type.shape, dtype=bool)
        arr = np.ma.masked_array(dummy, mask=self.dx.mask)
        return ObjectType(unknown=unknown, pedestrian=pedestrian, motorcycle=motorcycle,
                          car=car, truck=truck, bicycle=bicycle, point=arr, wide=arr)

    def mov_state(self):
        moving = ((self._type == MOVING_STATE.MOVING) |
                  (self._type == MOVING_STATE.ONCOMING) |
                  (self._type == MOVING_STATE.CROSSING))
        stationary = self._type == MOVING_STATE.STATIC
        stopped = self._type == MOVING_STATE.MOVING_STOPPED
        unknown = self._type == 0
        dummy = np.zeros(self._type.shape, dtype=bool)
        arr = np.ma.masked_array(dummy, mask=self.dx.mask)
        return MovingState(stat=stationary, stopped=stopped, moving=moving, unknown=unknown, crossing=arr, crossing_left=arr, crossing_right=arr, oncoming=arr)

class Calc(iCalc):
    def check(self):
        stateGroup = self.source.selectSignalGroup(SensorState)
        groups = []
        for sg in signalgroups:
            groups.append(self.source.selectSignalGroup([sg]))
        return stateGroup, groups

    def fill(self, stategroup, groups):
        common_time, _ = stategroup.get_signal("el")
        return ContiARS430MergedTrack(0, common_time, groups, scaletime=common_time)