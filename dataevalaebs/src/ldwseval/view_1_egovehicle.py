# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import interface
import datavis

import numpy as np
sgs  = [
{
  "VDC2_SteerWhlAngle_0B": ("VDC2_0B", "VDC2_SteerWhlAngle_0B"),
  "EBC2_MeanSpdFA_0B": ("EBC2_0B", "EBC2_MeanSpdFA_0B"),
  "estimated_road_curvature": ("General_radar_status", "estimated_road_curvature"),
  "VDC2_YawRate_0B": ("VDC2_0B", "VDC2_YawRate_0B"),
},
]

class View(interface.iView):
  def check(self):
    group = self.source.selectSignalGroup(sgs)
    return group

  def fill(self, group):
    return group

  def view(self, group):
    client00 = datavis.cPlotNavigator(title="LDWS", figureNr=None)
    self.sync.addClient(client00)



    ###AXIS00###
    ############
    axis00 = client00.addAxis()
    #tupy = (-10,10)
    #tupx=(-5,5)
    #axis00.set_ylim(tupy)  # vertical min max values of the axes
    #axis00.set_xlim(tupx)
    t_speed, speed = group.get_signal("EBC2_MeanSpdFA_0B")
    client00.addSignal2Axis(axis00, "ego speed", t_speed, speed, unit="km/h")
    axis00.set_ylim((0, 110))
    axis00.set_ylabel('[km/h]')
    ###AXIS01###
    ############
    axis01 = client00.addAxis()
    t_StrWhlAngle, StrWhlAngle = group.get_signal("VDC2_SteerWhlAngle_0B")
    StrWhlAngle = StrWhlAngle *180.0/np.pi
    client00.addSignal2Axis(axis01, "SteerWhlAngle", t_StrWhlAngle, StrWhlAngle, unit="degree")
    axis01.set_ylim((-40, 40))
    axis01.set_ylabel('[degree]')
    ###AXIS02###
    ############
    axis02 = client00.addAxis()
    t_yawrate, yawrate =  group.get_signal("VDC2_YawRate_0B")
    client00.addSignal2Axis(axis02, "yawrate", t_yawrate, yawrate, unit="rad/s")
    axis02.set_ylim((-.3, .3))
    axis02.set_ylabel('[rad/s]')
    ###AXIS03###
    ############
    axis03 = client00.addAxis()
    t_roadcurv, roadcurv = group.get_signal("estimated_road_curvature")
    client00.addSignal2Axis(axis03, "road_curvature", t_roadcurv, roadcurv, unit="m")
    axis03.set_ylim((-1500, 1500))
    axis03.set_xlabel("time [s]")
    axis03.set_ylabel('[meter]')
    return
