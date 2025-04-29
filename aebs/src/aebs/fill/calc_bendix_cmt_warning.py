# -*- dataeval: init -*-
from interface.Interfaces import iCalc

class Calc(iCalc):
  AUDIBLE_FEEDBACK = 5
  CM_SYSTEM_STATUS = 2
  AEB_STATE = 3

  group = [
    ('AudibleFeedback', ('PropWarn-98FF102A-1-', 'AudibleFeedback')),
    #("AEB_state", ("ACC_S09", "AEB_state")),
    ("cm_system_status", ("General_radar_status", "cm_system_status")),
  ]
  group1 = [
    ('AudibleFeedback', ('PropWarn', 'AudibleFeedback')),
    #("AEB_state", ("ACC_S09", "AEB_state")),
    ("cm_system_status", ("General_radar_status", "cm_system_status")),
  ]
  def check(self):
    group = self.source.selectSignalGroup([dict(self.group), dict(self.group1)])
    return group

  def fill(self, group):
    t, audio_warning = group.get_signal('AudibleFeedback')
    #aeb_state = group.get_value('AEB_state', ScaleTime=t)
    cm_system_status = group.get_value('cm_system_status', ScaleTime=t)
    warning = ((   (cm_system_status >= self.CM_SYSTEM_STATUS) )# | (aeb_state >= self.AEB_STATE))
             & (audio_warning >= self.AUDIBLE_FEEDBACK) )
    
    return t, warning

