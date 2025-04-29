# -*- dataeval: init -*-

import interface
import measparser
import fillAC100_Target
import fillAC100_TargetFlags

SignalGroups = [] 
for i in xrange(fillAC100_Target.NoTargets):
  SignalGroup = {}
  for Name in 'target_status',:
    SignalGroup[Name] = 'Targets', 'ta%d_%s' %(i, Name)
  SignalGroups.append(SignalGroup)

class cFill(fillAC100_TargetFlags.cFill):
  def init(self):
    self.GroupTypes = {'UNCONF':  (self.get_grouptype('AC100_UNCONF'),  0, 'target_status'),
                       'PARTIAL': (self.get_grouptype('AC100_PARTIAL'), 1, 'target_status'),
                       'SHADED':  (self.get_grouptype('AC100_SHADED'),  2, 'target_status'),
                       'CONF':    (self.get_grouptype('AC100_CONF'),    3, 'target_status')}

  def check(self):
    Groups, Errors = interface.Source._filterSignalGroups(SignalGroups)
    measparser.signalgroup.check_onevalid(Groups, Errors, 1)
    return Groups
