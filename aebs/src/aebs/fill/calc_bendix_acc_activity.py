# -*- dataeval: init -*-
from interface.Interfaces import iCalc

class Calc(iCalc):
  CTRL_MODE = 2
  ACCEL_DEMAND_LIMIT = -0.5
  INVALID_AUDIBLE_FEEDBACK = 5

  group = [
    ('AudibleFeedback', ('PropWarn-98FF102A-1-', 'AudibleFeedback')),
    ('XBR_ControlMode', ('XBRUS_2A', 'XBRUS_ControlMode_2A')),
    ("XBR_AccelDemand", ("XBRUS_2A", "XBRUS_AccelDemand_2A")),
  ]
  group1 = [
    ('AudibleFeedback', ('PropWarn', 'AudibleFeedback')),
    ('XBR_ControlMode', ('XBRUS_2A', 'XBRUS_ControlMode_2A')),
    ("XBR_AccelDemand", ("XBRUS_2A", "XBRUS_AccelDemand_2A")),
  ]
  def check(self):
    group = self.source.selectSignalGroup([dict(self.group), dict(self.group1)])
    return group

  def fill(self, group):
    t, ctrl_mode = group.get_signal('XBR_ControlMode')
    accel_demand = group.get_value('XBR_AccelDemand', ScaleTime=t)
    acc_activity =  (ctrl_mode == self.CTRL_MODE)\
                  & (accel_demand <= self.ACCEL_DEMAND_LIMIT)
    no_aebs_activity =   group.get_value('AudibleFeedback', ScaleTime=t)\
                      != self.INVALID_AUDIBLE_FEEDBACK

    activity = acc_activity & no_aebs_activity
    return t, activity

