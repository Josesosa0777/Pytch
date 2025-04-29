# -*- dataeval: init -*-

import interface
import measparser
import fillAC100_Target
import fillAC100_TargetFlags


SignalGroups = [] 
for i in xrange(fillAC100_Target.NoTargets):
  SignalGroup = {}
  for Name in 'tracking_flags',:
    SignalGroup[Name] = 'Targets', 'ta%d_%s' %(i, Name)
  SignalGroups.append(SignalGroup)

class cFill(fillAC100_TargetFlags.cFill):
  def init(self):
    self.GroupTypes = {'POS':          (self.get_grouptype('AC100_POSITION'),      1, 'tracking_flags'),
                       'CLOSE_TO_ACC': (self.get_grouptype('AC100_CLOSE_TO_ACC'),  2, 'tracking_flags'),
                       'BEHIND_CBR':   (self.get_grouptype('AC100_BEHIND_CBR'),    4, 'tracking_flags'),
                       'CLOSE_LOWPWR': (self.get_grouptype('AC100_CLOSE_LOWPWR'),  8, 'tracking_flags'),
                       'FREQ':         (self.get_grouptype('AC100_FREQ'),         16, 'tracking_flags')}
    pass

  def check(self):
    Groups, Errors = interface.Source._filterSignalGroups(SignalGroups)
    measparser.signalgroup.check_onevalid(Groups, Errors, 1)
    return Groups
    
