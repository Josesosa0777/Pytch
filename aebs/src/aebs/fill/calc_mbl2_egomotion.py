# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import sys

import numpy as np

from primitives.egomotion import EgoMotion
import interface


EXP_UNITS = {
  'yawrate_radar_deg': (u'\u00B0/s', u'�/s'),  # degree/s
  'yawrate_ref':       ('rad/s',),
  'yawrate_deg':       (u'\u00B0/s', u'�/s'),  # degree/s
  'vx':                ('m/s',),
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
  dep = ('calc_mbl2_common_time',)

  def check(self):
    sgs = [{
      'vx':          ('MBM_VEHICLEDATA1_r', 'usVehicleSpeed'),
      'yawrate_deg': ('MBM_VEHICLEDATA1_r', 'usYawRate'),
    }]
    optsgs = [{
      'ax': ('MBM_VEHICLEDATA2_r', 'nLongAcc_cm_per_sqr_s'),
    }]
    group = self.source.selectSignalGroup(sgs)
    optgroup = self.source.selectLazySignalGroup(optsgs)
    return group, optgroup

  def fill(self, group, optgroup):
    time = self.modules.fill('calc_mbl2_common_time')
    rescale_kwargs = {'ScaleTime': time, 'Order': 'valid'}
    # vx
    _, vx, unit_vx = group.get_signal_with_unit('vx', **rescale_kwargs)
    #check_unit('vx', unit_vx)
    # yaw rate
    _, yawrate_deg, unit_yawrate = \
      group.get_signal_with_unit('yawrate_deg', **rescale_kwargs)
    #check_unit('yawrate_deg', unit_yawrate)
    yaw_rate = np.deg2rad(yawrate_deg)

    # ax
    if 'ax' in optgroup:
      ax = optgroup.get_value('ax', **rescale_kwargs)
    else:
      self.logger.debug(
        "'vehicle_reference_acceleration' not available; calculating ax")
      d_vx = np.gradient(vx)
      d_t = np.gradient(time)
      ax = np.where(d_t > 0.0, d_vx/d_t, 0.0)
    # return value
    ego_motion = EgoMotion(time, vx, yaw_rate, ax)
    return ego_motion
