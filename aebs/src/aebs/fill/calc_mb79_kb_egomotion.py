# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import numpy as np

from primitives.egomotion import EgoMotion
import interface


class Calc(interface.iCalc):

  def check(self):
    sgs = [{
      'vx':      ('TA', 'tracking_in_FrontAxleSpeed'),
      'yawrate': ('TA', 'tracking_in_YawRate'),
    }]
    optsgs = [{
      "vx": ("TA", "warn_trigg_in_vref"),
    }]

    group = self.source.selectLazySignalGroup(sgs)
    optgroup = self.source.selectLazySignalGroup(optsgs)
    return group, optgroup

  def fill(self, group, optgroup):
    # vx
    v_group = group if "vx" in group else optgroup
    time, vx, unit_vx = v_group.get_signal_with_unit('vx')
    # yaw rate
    _, yawrate, unit_yawrate = group.get_signal_with_unit('yawrate')
    yaw_rate = np.deg2rad(yawrate)
    # ax
    d_vx = np.gradient(vx)
    d_t = np.gradient(time)
    ax = np.where(d_t > 0.0, d_vx/d_t, 0.0)
    # return value
    return EgoMotion(time, vx, yaw_rate, ax)
