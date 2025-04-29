# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

"""
Plots the basic vehicle motion data (speed, acceleration, yaw rate).
"""

import numpy as np

import interface
import datavis

class View(interface.iView):
  dep = 'calc_j1939_egomotion@aebs.fill',
  
  def view(self):
    pn = datavis.cPlotNavigator(title="Ego vehicle motion data")
    
    ego_motion = self.modules.fill(self.dep[0])
    t = ego_motion.time
    # speed
    ax = pn.addAxis(ylabel="speed", ylim=(-5.0, 105.0))
    pn.addSignal2Axis(ax, "speed", t, 3.6 * ego_motion.vx, unit="km/h")
    # yaw rate
    ax = pn.addAxis(ylabel="yaw rate", ylim=(-12.0, 12.0))
    pn.addSignal2Axis(ax, "yaw rate",
      t, np.rad2deg(ego_motion.yaw_rate), unit="deg/s")
    # acceleration
    ax = pn.addAxis(ylabel="acceleration", ylim=(-11.0, 11.0))
    pn.addSignal2Axis(ax, "acceleration", t, ego_motion.ax, unit="m/s^2")
    
    # register client
    self.sync.addClient(pn)
    return
