# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import interface
import datavis

import numpy as np
sgs  = [
{
  "Me_Line_Changed_Left_B": ("Video_Lane_Left_B", "Me_Line_Changed_Left_B"),
  "Me_Line_Changed_Right_B": ("Video_Lane_Right_B", "Me_Line_Changed_Right_B"),
  "FLI2_LaneTrackingStatusLeft": ("FLI2_E8", "FLI2_LaneTrackingStatusLeft"),
  "FLI2_LaneTrackingStatusRight": ("FLI2_E8", "FLI2_LaneTrackingStatusRight"),  
  "C0_Left_A": ("Video_Lane_Left_A", "C0_Left_A"),
  "C1_Left_A": ("Video_Lane_Left_A", "C1_Left_A"),  
  "C2_Left_A": ("Video_Lane_Left_A", "C2_Left_A"),  
  "C3_Left_A": ("Video_Lane_Left_A", "C3_Left_A"), 
  "C0_Right_A": ("Video_Lane_Right_A", "C0_Right_A"),   
  "C1_Right_A": ("Video_Lane_Right_A", "C1_Right_A"),
  "C2_Right_A": ("Video_Lane_Right_A", "C2_Right_A"),
  "C3_Right_A": ("Video_Lane_Right_A", "C3_Right_A")
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

    t_Crossing_left, Crossing_left = group.get_signal("Me_Line_Changed_Left_B")
    t_Crossing_right, Crossing_right = group.get_signal("Me_Line_Changed_Right_B")
    t_LDW_tracking_left, LDW_tracking_left = group.get_signal("FLI2_LaneTrackingStatusLeft")
    t_LDW_tracing_right, LDW_tracking_right = group.get_signal("FLI2_LaneTrackingStatusRight")
    t_c0_left, c0_left = group.get_signal("C0_Left_A")
    t_c1_left, c1_left = group.get_signal("C1_Left_A")
    t_c2_left, c2_left = group.get_signal("C2_Left_A")
    t_c3_left, c3_left = group.get_signal("C3_Left_A")
    t_c0_right, c0_right = group.get_signal("C0_Right_A")
    t_c1_right, c1_right = group.get_signal("C1_Right_A")
    t_c2_right, c2_right = group.get_signal("C2_Right_A")
    t_c3_right, c3_right = group.get_signal("C3_Right_A")

    ###AXIS00###
    ############
    axis00 = client00.addAxis()
    client00.addSignal2Axis(axis00, "Ldw_tracking_left", t_LDW_tracking_left, LDW_tracking_left, unit="")
    client00.addSignal2Axis(axis00, "Ldw_tracking_right", t_LDW_tracing_right, LDW_tracking_right, unit="", offset=2, displayscaled=False)
    client00.addSignal2Axis(axis00, "Line_Changed_left", t_Crossing_left, Crossing_left, unit="", offset=4, displayscaled=False)
    client00.addSignal2Axis(axis00, "Line_Changed_right", t_Crossing_right, Crossing_right, unit=" ", offset=6, displayscaled=False)
    axis00.set_yticklabels(['','OFF','ON','OFF','ON','OFF','ON','OFF','ON'])
    ###AXIS01###
    ############
    axis01 = client00.addAxis()
    client00.addSignal2Axis(axis01, "c0_left", t_c0_left, c0_left, unit="m")
    client00.addSignal2Axis(axis01, "c0_right", t_c0_right, c0_right, unit="m")
    ###AXIS02###
    ############
    axis02 = client00.addAxis()
    client00.addSignal2Axis(axis02, "c1_left", t_c1_left, c1_left, unit="rad")
    client00.addSignal2Axis(axis02, "c1_right", t_c1_right, c1_right, unit="rad")
    ###AXIS03###
    ############
    axis03 = client00.addAxis()
    client00.addSignal2Axis(axis03, "c2_left", t_c2_left, c2_left, unit="rad/s")
    client00.addSignal2Axis(axis03, "c2_right", t_c2_right, c2_right, unit="rad/s")
    axis03.set_ylim((-0.2,0.2))
    ###AXIS04###
    ############
    axis04 = client00.addAxis()
    client00.addSignal2Axis(axis04, "c3_left", t_c3_left, c3_left, unit="rad/s^2")
    client00.addSignal2Axis(axis04, "c3_right", t_c3_right, c3_right, unit="rad/s^2")
    axis04.set_ylim((-0.2,0.2))
    return
