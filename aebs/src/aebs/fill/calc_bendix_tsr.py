# -*- dataeval: init -*-
from interface.Interfaces import iCalc

class Calc(iCalc):
  TSR_WARNING_TRIGGER = 0
  
  group = [('TSR_Warning_Flag', ("PropWarn-98FF102A-1-", "TSR_Warning_Flag"))]
  group1 = [('TSR_Warning_Flag', ("PropWarn", "TSR_Warning_Flag"))]

  def check(self):
    group = self.source.selectSignalGroup([dict(self.group), dict(self.group1)])
    return group

  def fill(self, group):
    t, tsr_warning = group.get_signal('TSR_Warning_Flag')
    trigger = (tsr_warning == self.TSR_WARNING_TRIGGER)
    return t, trigger
    