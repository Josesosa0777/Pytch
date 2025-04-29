# -*- dataeval: init -*-

import numpy as np

import interface
import measparser

N_ESR_TR = 64

Aliases = 'RANGE', 'ANGLE', 'RANGE_RATE', 'ONCOMING', 'STATUS'
GroupLen = len(Aliases) + 1

SignalGroups = []
for k in xrange(1, N_ESR_TR+1):
  SignalGroup = {'MOVING': ('ESR_TrackMotionPower', 'CAN_TX_TRACK_MOVING%02d' %k)}
  for Alias in Aliases:
    SignalGroup[Alias] = 'ESR_Track%02d' %k, 'CAN_TX_TRACK_%s_%02d' %(Alias, k)
  SignalGroups.append(SignalGroup)

class cFill(interface.iObjectFill):
  def check(self):
    Groups, Errors = interface.Source._filterSignalGroups(SignalGroups)
    measparser.signalgroup.check_onevalid(Groups, Errors, GroupLen)
    return Groups

  def fill(self, Groups):
    Signals = measparser.signalgroup.extract_signals(Groups, ObjectGroups)
    Signals = measparser.signalgroup.extract_signals(Groups)
    scaletime = interface.Source.selectScaleTime(Signals, interface.StrictlyGrowingTimeCheck)
    Objects=[]
    # loop through all tracks
    for k in xrange(1, N_ESR_TR+1):
      Group = Groups[k]
      if len(Group) != GroupLen:
        continue
      Range        = interface.Source.getSignalFromSignalGroup(Group, 'RANGE',      ScaleTime=scaletime)[1]
      AngleDeg     = interface.Source.getSignalFromSignalGroup(Group, 'ANGLE',      ScaleTime=scaletime)[1]
      AngleRad     = np.radians(AngleDeg)
      RelVelocity  = interface.Source.getSignalFromSignalGroup(Group, 'RANGE_RATE', ScaleTime=scaletime)[1]
      Oncoming     = interface.Source.getSignalFromSignalGroup(Group, 'ONCOMING',   ScaleTime=scaletime)[1]
      Status       = interface.Source.getSignalFromSignalGroup(Group, 'STATUS',     ScaleTime=scaletime)[1]
      Moving       = interface.Source.getSignalFromSignalGroup(Group, 'MOVING',     ScaleTime=scaletime)[1]
      
      o = {}
      o["label"] = "ESR_%02d" %k
      # transformation from polar to vehicle coordinates
      CosAngle = np.cos(AngleRad)
      SinAngle = np.sin(AngleRad)
      o["dx"]  =  Range * CosAngle
      o["dy"]  = -Range * SinAngle
      o["dvx"] =  RelVelocity * CosAngle
      o["dvy"] = -RelVelocity * SinAngle
      # object type is based on moving state
      o["type"] = np.where( Moving == 1, 
                            self.get_grouptype('ESR_MOV'), 
                            self.get_grouptype('ESR_STAT'))
      # Set color to red or green according to relative speed
      w = np.reshape(np.repeat(RelVelocity < 0, 3), (-1,3))
      o["color"] = np.where(
        w,
        [255, 0, 0],
        [0, 255, 0])
      #Set color to blue if object moves in opposite direction
      w = np.reshape(np.repeat(Oncoming > 0, 3), (-1, 3))
      o["color"] = np.where(w, [0, 0, 255], o["color"])
        
      Objects.append(o)
    return scaletime, Objects
