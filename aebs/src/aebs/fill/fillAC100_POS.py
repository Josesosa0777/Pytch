# -*- dataeval: init -*-

import numpy

import interface
import measproc
import measparser
import fillAC100

SignalGroups = []
Alias = 'acc_track_info'
for k in xrange(fillAC100.N_AC100_TR):
  Group = {Alias: ('Tracks', 'tr%d_%s' %(k, Alias))}
  SignalGroups.append(Group)

class cFill(interface.iObjectFill):
  dep = 'fillAC100',
  def check(self):
    Groups, Errors = interface.Source._filterSignalGroups(SignalGroups)
    measparser.signalgroup.check_onevalid(Groups, Errors, 1)
    return Groups

  def fill(self, Groups):
    Keys = 'dx', 'dy', 'vx', 'vy', 'ax', 'type', 'color', 'id', 'stand'
    Time, AC100Objects = interface.Objects.fill('fillAC100')
    Ref = AC100Objects[0]
    InfoObjects = measproc.Object.initObjects(('ACC', 'IIV', 'NIV_L', 'NIV_R'), Ref, Keys, type=self.get_grouptype('NONE_TYPE'))
    # Filter the AC100 ojects
    for Object in AC100Objects:
      Track = Object['track']
      Group = Groups[Track]
      # Get the track info
      Time, InfoV = interface.Source.getSignalFromSignalGroup(Group, Alias, ScaleTime=Time)
      # NIV_L and NIV_R has the same value (3)
      # They can be present at the same time
      # Classification will be done via dy
      InfoObject = InfoObjects['NIV_L']
      Mask = InfoV == 3
      Reserved = InfoObject['type'] == self.get_grouptype('AC100_NIV_L')
      Intruder = Mask & Reserved
      Winner = InfoObject['dy'][Intruder] < Object['dy'][Intruder]
      Loser = numpy.logical_not(Winner)
      Object2Left = Mask.copy()
      Object2Left[Intruder][Loser] = False
      Object2Right = numpy.zeros_like(Mask)
      Object2Right[Intruder][Loser] = True
      Left2Right = numpy.zeros_like(Mask)
      Left2Right[Intruder][Winner] = True
      # Fill the info objects
      CopyRules = ((self.get_grouptype('AC100_ACC'),   InfoV == 1,   Object,               InfoObjects['ACC']),
                   (self.get_grouptype('AC100_IIV'),   InfoV == 2,   Object,               InfoObjects['IIV']),
                   (self.get_grouptype('AC100_NIV_R'), Object2Right, Object,               InfoObjects['NIV_R']),
                   (self.get_grouptype('AC100_NIV_R'), Left2Right,   InfoObjects['NIV_L'], InfoObjects['NIV_R']),
                   (self.get_grouptype('AC100_NIV_L'), Object2Left,  Object,               InfoObjects['NIV_L']))
      for Type, Mask, Source, Target in CopyRules:
        measproc.Object.copyObject(Source, Target, Mask, Keys, type=Type)
      Objects = measproc.Object.listObjects(InfoObjects)
    return Time, Objects
