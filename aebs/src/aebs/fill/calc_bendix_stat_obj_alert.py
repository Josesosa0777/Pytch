# -*- dataeval: init -*-
from interface.Interfaces import iCalc

class Calc(iCalc):
  AUDIBLE_FEEDBACK = 2
  FDA_LIGHT_STRIP_CTRL = 3

  group = [
    ('AudibleFeedback', ('PropWarn-98FF102A-1-', 'AudibleFeedback')),
    ('FDALightStripControl', ('PropWarn-98FF102A-1-', 'FDALightStripControl')),
  ]
  group1 = [
    ('AudibleFeedback', ('PropWarn', 'AudibleFeedback')),
    ('FDALightStripControl', ('PropWarn', 'FDALightStripControl')),
  ]
  def check(self):
    group = self.source.selectSignalGroup([dict(self.group), dict(self.group1)])
    return group

  def fill(self, group):
    t, audio_warning = group.get_signal('AudibleFeedback')
    light_warning = group.get_value('FDALightStripControl', ScaleTime=t)
    warning =  (audio_warning == self.AUDIBLE_FEEDBACK)\
             & (light_warning == self.FDA_LIGHT_STRIP_CTRL)
    return t, warning

