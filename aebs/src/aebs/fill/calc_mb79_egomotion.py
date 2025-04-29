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

  def check(self):
    sgs = [{
      'vx':          ('Object_Interface_Header_1', 'HostSpeed'),
      'yawrate_deg': ('Object_Interface_Header_1', 'HostYawRate'),
    }]
    group = self.source.selectSignalGroup(sgs)
    return group

  def fill(self, group):
    time = group.get_time("vx")
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
    d_vx = np.gradient(vx)
    d_t = np.gradient(time)
    ax = np.where(d_t > 0.0, d_vx/d_t, 0.0)
    # return value
    ego_motion = EgoMotion(time, vx, yaw_rate, ax)
    return ego_motion
