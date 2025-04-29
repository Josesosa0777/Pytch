# -*- dataeval: init -*-

import numpy

import interface
import measproc
import measparser
from calc_flr20_egomotion import is_left_positive

NoTargets = 10
Aliases = 'angle_MSB',\
          'angle_LSB',\
          'relative_velocitiy',\
          'range',\
          'power'

GroupLen = len(Aliases)
SignalGroups = []
for i in xrange(NoTargets):
  SignalGroup = {}
  for Name in Aliases:
    SignalGroup[Name] = 'Targets', 'ta%d_%s' %(i, Name)
  SignalGroups.append(SignalGroup)

class cFill(interface.iObjectFill):
  def check(self):
    Groups, Errors = interface.Source._filterSignalGroups(SignalGroups)
    measparser.signalgroup.check_onevalid(Groups, Errors, GroupLen)
    return Groups

  def fill(self, Groups):
    Signals = measparser.signalgroup.extract_signals(Groups)
    Time = interface.Source.selectScaleTime(Signals, interface.StrictlyGrowingTimeCheck)
    dirCorr = 1.0 if is_left_positive(interface.Source) else -1.0
    TargetObjects = {}
    for target, Group in enumerate(Groups):
      if len(Group) != GroupLen:
        continue
      Object = dict(target=target)
      Time, AngleLSB = interface.Source.getSignalFromSignalGroup(Group, 'angle_LSB', ScaleTime=Time)
      Time, AngleMSB = interface.Source.getSignalFromSignalGroup(Group, 'angle_MSB', ScaleTime=Time)
      Angle = dirCorr * numpy.radians(AngleMSB+AngleLSB)
      Cos = numpy.cos(Angle)
      Sin = numpy.sin(Angle)
      Time, Range = interface.Source.getSignalFromSignalGroup(Group, 'range', ScaleTime=Time)
      Object['dx'] = Cos * Range
      Object['dy'] = Sin * Range
      Time, RelVel = interface.Source.getSignalFromSignalGroup(Group, 'relative_velocitiy', ScaleTime=Time)
      Object['dvx'] = RelVel
      Object['type'] = numpy.zeros(Time.size, dtype=int) + self.get_grouptype('NONE_TYPE')
      Object['color'] = numpy.zeros((Time.size, 3), dtype=int)
      Object['color'][:,0] = 255
      Object['color'][:,2] = 255
      Time, Power = interface.Source.getSignalFromSignalGroup(Group, 'power', ScaleTime=Time)
      Object['alpha'] = Power / 255.0
      Label = 'AC100_Target_%d' %target
      TargetObjects[Label] = Object
    Objects = measproc.Object.listObjects(TargetObjects)
    return Time, Objects

