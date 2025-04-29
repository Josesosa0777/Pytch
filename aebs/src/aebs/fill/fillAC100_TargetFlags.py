# -*- dataeval: init -*-

import interface
import measproc
import measparser
import fillAC100_Target

Aliases = 'target_flags_LSB', 'target_flags_MSB'
GroupLen = len(Aliases)
SignalGroups = []
for i in xrange(fillAC100_Target.NoTargets):
  SignalGroup = {}
  for Name in Aliases:
    SignalGroup[Name] = 'Targets', 'ta%d_%s' %(i, Name)
  SignalGroups.append(SignalGroup)

class cFill(interface.iObjectFill):
  dep = 'fillAC100_Target',
  def init(self):
    self.GroupTypes = {'STAT':         (self.get_grouptype('AC100_STAT_TARGET'),   1, 'target_flags_LSB'),
                       'AMBIGOUS':     (self.get_grouptype('AC100_AMBIGUOUS'),     2, 'target_flags_LSB'),
                       'WEAK_DET':     (self.get_grouptype('AC100_WEAK_DET'),      4, 'target_flags_LSB'),
                       'WEAK_PARTNER': (self.get_grouptype('AC100_WEAK_PARTNER') , 8, 'target_flags_LSB'),
                       'PHI_ERROR':    (self.get_grouptype('AC100_PHI_ERROR'),     1, 'target_flags_MSB')}
    pass

  def check(self):
    Groups, Errors = interface.Source._filterSignalGroups(SignalGroups)
    measparser.signalgroup.check_onevalid(Groups, Errors, GroupLen)
    return Groups

  def fill(self, Groups):
    Keys = 'dx', 'dy', 'color', 'alpha', 'type'
    Time, Targets = interface.Objects.fill('fillAC100_Target')
    Objects = measproc.Object.initObjects(self. GroupTypes, Targets[0], Keys, type=self.get_grouptype('NONE_TYPE'))
    Signals = {}
    for Target in Targets:
      i = Target['target']
      Group = Groups[i]
      for Type, Value, Alias in self.GroupTypes.itervalues():
        Time, Signals[Alias] = interface.Source.getSignalFromSignalGroup(Group, Alias, ScaleTime=Time)
      for Flag, (Type, Value, Alias) in self.GroupTypes.iteritems():
        Signal = Signals[Alias]
        Mask = Signal == Value
        measproc.Object.copyObject(Target, Objects[Flag], Mask, Keys, type=Type)
    Objects = measproc.Object.listObjects(Objects)
    return Time, Objects
