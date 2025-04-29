# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

"""
Plot engine speed and torque

Plot also includes different torque requests/limits.
"""

import numpy as np

import interface
import datavis

sgs = [{
  "EEC1_ActEngPercTrq_00": ("EEC1_00", "EEC1_ActEngPercTrq_00"),
  "EEC1_DrivDemPercTrq_00": ("EEC1_00", "EEC1_DrivDemPercTrq_00"),
  "EEC1_ActEngPercTrqHR_00": ("EEC1_00", "EEC1_ActEngPercTrqHR_00"),
  "EEC1_EngSpd_00": ("EEC1_00", "EEC1_EngSpd_00"),
}]

optsgs = [{
  "TSC1_ReqTorqueLimit_2A_00": ("TSC1_2A_00", "TSC1_ReqTorqueLimit_2A_00"),
}]

class View(interface.iView):
  def check(self):
    group = self.source.selectSignalGroup(sgs)
    optgroup = self.source.selectLazySignalGroup(optsgs)
    return group, optgroup
  
  def view(self, group, optgroup):
    client00 = datavis.cPlotNavigator(title="Engine speed and torque")
    self.sync.addClient(client00)
    axis00 = client00.addAxis(ylim=(-5.0, 3000.0))
    time00, value00 = group.get_signal("EEC1_EngSpd_00")
    client00.addSignal2Axis(axis00, "engine speed", time00, value00, unit="rpm")
    axis01 = client00.addAxis(ylim=(-5.0, 105.0))
    time02, value02 = group.get_signal("EEC1_ActEngPercTrq_00")
    time03, value03 = group.get_signal("EEC1_ActEngPercTrqHR_00")
    client00.addSignal2Axis(axis01, "actual torque", time02, value02+value03, unit="%")
    time01, value01 = group.get_signal("EEC1_DrivDemPercTrq_00")
    client00.addSignal2Axis(axis01, "req. torque (driver)", time01, value01, unit="%")
    if "TSC1_ReqTorqueLimit_2A_00" in optgroup:
      time01, value01 = optgroup.get_signal("TSC1_ReqTorqueLimit_2A_00")
    else:
      #time01 = time01
      value01 = np.ma.masked_array(np.zeros_like(time01), True)
    client00.addSignal2Axis(axis01, "torque limit (radar)", time01, value01, unit="%")
    axis01.set_xlabel("time [s]")
    return
