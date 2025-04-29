# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis
def_param = interface.NullParam

sgs  = [
{
  "tg_output_reference_traj_approx_c0": ("XCP_Test", "tg_output_reference_traj_approx_c0"),
  "tg_output_reference_traj_approx_c1": ("XCP_Test", "tg_output_reference_traj_approx_c1"),
  "tg_lon_planner_ego_vx": ("XCP_Test", "tg_lon_planner_ego_vx"),
  "tg_output_reference_traj_approx_c2": ("XCP_Test", "tg_output_reference_traj_approx_c2"),
  "tg_lon_planner_ego_ax": ("XCP_Test", "tg_lon_planner_ego_ax"),
  "tg_lon_planner_lon_planner_mode": ("XCP_Test", "tg_lon_planner_lon_planner_mode"),
  "tg_lon_planner_object_reaching_mode": ("XCP_Test", "tg_lon_planner_object_reaching_mode"),
},
]

class View(interface.iView):
  def check(self):
    group = self.source.selectSignalGroupOrEmpty(sgs)
    return group

  def fill(self, group):
    return group

  def view(self, param, group):
    client00 = datavis.cPlotNavigator(title="Longitudinal trajectory")
    self.sync.addClient(client00)
    axis00 = client00.addAxis()
    time00, value00, unit00 = group.get_signal_with_unit("tg_output_reference_traj_approx_c0")
    client00.addSignal2Axis(axis00, "tg_output_reference_traj_approx_c0", time00, value00, unit=unit00)
    axis01 = client00.addAxis()
    time01, value01, unit01 = group.get_signal_with_unit("tg_output_reference_traj_approx_c1")
    client00.addSignal2Axis(axis01, "tg_output_reference_traj_approx_c1", time01, value01, unit=unit01)
    time02, value02, unit02 = group.get_signal_with_unit("tg_lon_planner_ego_vx")
    client00.addSignal2Axis(axis01, "tg_lon_planner_ego_vx", time02, value02, unit=unit02)
    axis02 = client00.addAxis()
    time03, value03, unit03 = group.get_signal_with_unit("tg_output_reference_traj_approx_c2")
    client00.addSignal2Axis(axis02, "tg_output_reference_traj_approx_c2", time03, value03*2.0, unit=unit03)  # x2
    time04, value04, unit04 = group.get_signal_with_unit("tg_lon_planner_ego_ax")
    client00.addSignal2Axis(axis02, "tg_lon_planner_ego_ax", time04, value04, unit=unit04)
    
    ticks = {0: "None", 1: "ObjectFollowing", 2: "DCSetSpeedReaching", 3: "SetSpeedTraveling", 4: "SetSpeedReaching", 5: "ObjectReaching"}
    axis03 = client00.addAxis(yticks=ticks)
    time05, value05, unit05 = group.get_signal_with_unit("tg_lon_planner_lon_planner_mode")
    client00.addSignal2Axis(axis03, "tg_lon_planner_lon_planner_mode", time05, value05, unit=unit05)
    ticks = {0: "None", 1: "MinJerk", 2: "TempTraj", 3: "BangBang", 4: "DelayIntervention"}
    axis04 = client00.addAxis(yticks=ticks)
    time06, value06, unit06 = group.get_signal_with_unit("tg_lon_planner_object_reaching_mode")
    client00.addSignal2Axis(axis04, "tg_lon_planner_object_reaching_mode", time06, value06, unit=unit06)
    return
