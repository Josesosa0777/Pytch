# -*- dataeval: init -*-
from interface.Interfaces import iCalc

class Calc(iCalc):
  WARNING = 1

  group = [
    ('LDW_LaneDeparture_Left', ('Camera_Prop_Warn', 'LDW_LaneDeparture_Left')),
    ('LDW_LaneDeparture_Right', ('Camera_Prop_Warn', 'LDW_LaneDeparture_Right')),
  ]
  def check(self):
    group = self.get_source().selectSignalGroup([dict(self.group)])
    return group

  def fill(self, group):
    t, left_warning = group.get_signal('LDW_LaneDeparture_Left')
    right_warning = group.get_value('LDW_LaneDeparture_Right', ScaleTime=t)
    warning = (left_warning == self.WARNING) | (right_warning == self.WARNING)
    return t, warning


