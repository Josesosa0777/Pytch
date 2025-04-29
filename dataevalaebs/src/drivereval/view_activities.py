# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

"""
Plots the corresponding signals of driver actions, such as:
* accelerator pedal and brake pedal position
* steering wheel angle
* turn indicator
"""

import numpy as np

import interface
import datavis

class View(interface.iView):
  def check(self):
    sgs = [{
      "accped_pos": ("EEC2_00", "EEC2_APPos1_00"),
      "accped_kickdown": ("EEC2_00", "EEC2_APkickdwnSw_00"),
      "brkped_pos": ("EBC1_0B", "EBC1_BrkPedPos_0B"),
      "brkped_switch": ("EBC1_0B", "EBC1_EBSBrkSw_0B"),
      "steer_angle": ("VDC2_0B", "VDC2_SteerWhlAngle_0B"),
      "dir_ind": ("OEL_21", "OEL_TurnSigSw_21"),
    }]
    group = self.source.selectSignalGroup(sgs)
    return group
  
  def view(self, group):
    pn = datavis.cPlotNavigator(title="Driver activities")
    
    # accel. pedal
    ax = pn.addAxis(ylabel="pos.", ylim=(-5.0, 105.0))
    time00, value00, unit00 = group.get_signal_with_unit("accped_pos")
    pn.addSignal2Axis(ax, "accel. p. pos.", time00, value00, unit=unit00)
    ax = pn.addTwinAxis(ax, ylabel="kickdown",
      ylim=(-0.5, 1.5), color='g')
    time01, value01, unit01 = group.get_signal_with_unit("accped_kickdown")
    pn.addSignal2Axis(ax, "accel. p. kickdown", time01, value01, unit=unit01)
    # brake pedal
    ax = pn.addAxis(ylabel="pos.", ylim=(-5.0, 105.0))
    time02, value02, unit02 = group.get_signal_with_unit("brkped_pos")
    pn.addSignal2Axis(ax, "brake p. pos.", time02, value02, unit=unit02)
    ax = pn.addTwinAxis(ax, ylabel="switch",
      ylim=(-0.5, 1.5), color='g')
    time03, value03, unit03 = group.get_signal_with_unit("brkped_switch")
    pn.addSignal2Axis(ax, "brake switch", time03, value03, unit=unit03)
    # steering wheel
    ax = pn.addAxis(ylabel="angle", ylim=(-100.0, 100.0))
    time04, value04, unit04 = group.get_signal_with_unit("steer_angle")
    if unit04 == "rad" or not unit04:  # assuming rad if unit is empty
      value04 = np.rad2deg(value04)
      unit04 = "deg"
    pn.addSignal2Axis(ax, "steering wheel angle", time04, value04, unit=unit04)
    # direction indicator
    yticks = {0: "none", 1: "left", 2: "right", 3: "n/a"}
    yticks = dict( (k, "(%s) %d"%(v,k)) for k, v in yticks.iteritems() )
    ax = pn.addAxis(ylabel="state", ylim=(-1.0, 4.0), yticks=yticks)
    time05, value05, unit05 = group.get_signal_with_unit("dir_ind")
    pn.addSignal2Axis(ax, "dir. indicator", time05, value05, unit=unit05)
    
    # register client
    self.sync.addClient(pn)
    return
