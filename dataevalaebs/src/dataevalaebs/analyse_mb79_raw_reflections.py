# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import numpy as np
import datavis
def_param = interface.NullParam

# PARAMETERS ---------
# radar mounting angle from vehicle x axis
r = 21
# offset of radar in x direction of the vehicle
l_off = -2.3
# number of detections to be processed
rng = 10
# --------------------

# radar internal coordinate orientation
r_off = -45
sg = {}
for i in range(1,rng+1):
  sg["CoGRange_%d"%i]= ("MB79_TARGET_DETECTION_%dB"%i, "CoGRange_%d"%i)
  sg["Azimuth_%d"%i]= ("MB79_TARGET_DETECTION_%dB"%i, "Azimuth_%d"%i)
sgs = [sg]

class View(interface.iView):
  def check(self):
    group = self.source.selectSignalGroupOrEmpty(sgs)
    return group

  def fill(self, group):
    return group

  def view(self, param, group):
    client00 = datavis.cPlotNavigator(title="")
    self.sync.addClient(client00)
    axis00 = client00.addAxis()
    client00.addSignal2Axis(axis00,"truck",np.array([0.0,16.5,16.5,0.0,0.0]),np.array([0.0,0.0,-2.5,-2.5,0.0]))
    for i in range(1,rng+1):
      time00, value00, unit00 = group.get_signal_with_unit("Azimuth_%d"%i)
      time01, value01, unit01 = group.get_signal_with_unit("CoGRange_%d"%i)
      client00.addSignal2Axis(axis00, "%d"%i, (value01*np.cos((r+r_off+value00)*np.pi/180)-l_off), (value01*np.sin((r+r_off+value00)*np.pi/180)), unit=unit01, marker='.', linestyle='None')
    return