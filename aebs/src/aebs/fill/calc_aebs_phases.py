# -*- dataeval: init -*-

import sys

from measproc.IntervalList import maskToIntervals, intervalsToMask
from primitives.aebs import AebsPhases
import interface


def intersect_first(outer_mask, inner_mask):
  """
  Intersect two masks such that every interval in the result mask will
  contain only the first interval of the inner mask within an interval
  of the outer mask.
  
  Example:
  
  outer:      ___________           ___________     ___
          0 0 1 1 1 1 1 1 0 0 0 0 0 1 1 1 1 1 1 0 0 1 1 0
  inner:          ___         ___     _   ___
          0 0 0 0 1 1 0 0 0 0 1 1 0 0 1 0 1 1 0 0 0 0 0 0
  result:         ___                 _
          0 0 0 0 1 1 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0
  """
  outer_intvals = maskToIntervals(outer_mask)
  inner_intvals = maskToIntervals(inner_mask)
  result_intvals = []
  for outer_start, outer_end in outer_intvals:
    for inner_start, inner_end in inner_intvals:
      if outer_start <= inner_start <= outer_end:
        result_intvals.append((inner_start, min(inner_end, outer_end)))
        break  # add max. one interval
  result_mask = intervalsToMask(result_intvals, outer_mask.size)
  return result_mask

def intersect_first_extended(outer_mask, inner_mask):
  """
  Intersect two masks such that every interval in the result mask will
  contain only the first interval of the inner mask within an interval
  of the outer mask, extended to the outer intervals' closing boundaries.
  
  Example:
  
  outer:      ___________           ___________     ___
          0 0 1 1 1 1 1 1 0 0 0 0 0 1 1 1 1 1 1 0 0 1 1 0
  inner:          ___         ___     _   ___
          0 0 0 0 1 1 0 0 0 0 1 1 0 0 1 0 1 1 0 0 0 0 0 0
  result:         _______             _________
          0 0 0 0 1 1 1 1 0 0 0 0 0 0 1 1 1 1 1 0 0 0 0 0
  """
  outer_intvals = maskToIntervals(outer_mask)
  inner_intvals = maskToIntervals(inner_mask)
  result_intvals = []
  for outer_start, outer_end in outer_intvals:
    for inner_start, inner_end in inner_intvals:
      if outer_start <= inner_start <= outer_end:
        result_intvals.append((inner_start, outer_end))  # extended to the end
        break
  result_mask = intervalsToMask(result_intvals, outer_mask.size)
  return result_mask


EXP_UNITS = {
  'xbr': ('m/s^2', 'm/s2', 'm/ss'),
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
  group = [
    ('XBR_AccelDemand', ('XBR_FD', 'XBRUS_AccelDemand_FD')),
    ('Acoustical', ('PropWarn_FD', 'AcousticalWarning_FD')),
    ('Optical', ('PropWarn_FD', 'OpticalWarning_FD')),
  ]
  XBR_ACTIVE = 1e-5
  XBR_PARTIAL = -2.0
  XBR_EMRGENCY = -4.0
  def check(self):
    group = self.get_source().selectSignalGroup([dict(self.group)])
    return group
  
  def fill(self, group):
    time, xbr, xbr_unit = group.get_signal_with_unit('XBR_AccelDemand')
    #check_unit('xbr', xbr_unit)
    acoustical = group.get_value('Acoustical', ScaleTime=time).astype(bool)
    optical = group.get_value('Optical', ScaleTime=time).astype(bool)
    # warning phase
    warning = acoustical & (xbr <= self.XBR_ACTIVE) & (xbr >= self.XBR_PARTIAL)
    warning = intersect_first(acoustical, warning)
    # braking
    # partial braking phase
    partial = acoustical & (xbr < self.XBR_PARTIAL) & (xbr >= self.XBR_EMRGENCY)
    #        & (diff(xbr) == 0)
    partial = intersect_first(acoustical, partial)
    # emergency braking phase
    emergency =  acoustical & (xbr < self.XBR_EMRGENCY)
    #          & until[(vx_ego > 0) & (dx_obj > 0)]
    emergency = intersect_first_extended(acoustical & (xbr <= -self.XBR_ACTIVE),
                                         emergency)
    # in-crash braking phase
    incrash = (~acoustical) & (xbr < self.XBR_EMRGENCY)
    # | from[(vx_ego <= 0) | (dx_obj<=0)]
    # & (diff(xbr) == 0)
    phases = AebsPhases(
      time,
      warning, partial, emergency, incrash,
      acoustical, optical
    )
    return phases
