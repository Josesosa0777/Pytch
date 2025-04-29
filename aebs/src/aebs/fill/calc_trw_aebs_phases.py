# -*- dataeval: init -*-

import sys

import numpy as np

from primitives.aebs import AebsPhases
import interface
from aebs.fill.calc_aebs_phases import intersect_first, intersect_first_extended


EXP_UNITS = {
  'xbr': ('m/s^2', 'm/s2', 'm/ss', u'm/s\xb2'),
}

def check_unit(alias, unit):
  """
  Check whether the signal's physical unit is the expected one or not.
  Raise AssertionError in the latter case.
  """
  if unit == '':
    print >> sys.stderr, "Unit check not possible for %s." % alias
    return
  if unit not in EXP_UNITS[alias]:
    raise AssertionError('unexpected unit for %s: %s' % (alias, unit))
  return


class Calc(interface.iCalc):
  dep = ('calc_flr20_common_time',)

  group = [
    ('cm_system_status', ('General_radar_status', 'cm_system_status')),
    ('XBR_AccelDemand', ('General_radar_status', 'cm_deceleration_demand')),
    ('hmi_warning', ('General_radar_status', 'cm_collision_warning')),
  ]

  XBR_ACTIVE = 1e-5
  XBR_PARTIAL = -2.0
  XBR_EMRGENCY = -4.0
  CM_WARNING = 2
  CM_BRAKING = 3

  def check(self):
    group = self.get_source().selectSignalGroup([dict(self.group)])
    return group

  def fill(self, group):
    time = self.get_modules().fill('calc_flr20_common_time')
    rescale_kwargs = {'ScaleTime': time, 'Order': 'valid'}
    _, xbr, xbr_unit = group.get_signal_with_unit('XBR_AccelDemand', **rescale_kwargs)
    #check_unit('xbr', xbr_unit)
    acoustical = group.get_value('hmi_warning', **rescale_kwargs).astype(bool)
    optical = np.array(acoustical)
    mode = group.get_value('cm_system_status', **rescale_kwargs)
    if mode.size > 0:
      mode = np.append(mode[1:], 0)  # left shift needed (#739)
    warning = mode == self.CM_WARNING

    braking = mode == self.CM_BRAKING
    # partial braking phase
    partial = braking & (xbr < self.XBR_PARTIAL) & (xbr >= self.XBR_EMRGENCY)
    #        & (diff(xbr) == 0)
    partial = intersect_first(braking, partial)
    # emergency braking phase
    emergency = braking & (xbr < self.XBR_EMRGENCY)
    #          & until[(vx_ego > 0) & (dx_obj > 0)]
    emergency = intersect_first_extended(braking & (xbr <= -self.XBR_ACTIVE),
                                         emergency)
    # in-crash braking phase
    incrash = np.zeros_like(time, dtype=bool)  # TODO: implement

    # return value
    phases = AebsPhases(
      time,
      warning, partial, emergency, incrash,
      acoustical, optical
    )
    return phases
