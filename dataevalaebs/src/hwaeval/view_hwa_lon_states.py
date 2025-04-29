# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis
def_param = interface.NullParam

devices = ("trajectory_generator_flx20_autobox", "XCP_Test")
sgs = [
{
  "tg_lon_planner_feasible": (dev, "tg_lon_planner_feasible"),
  "tg_lon_planner_collision_possible": (dev, "tg_lon_planner_collision_possible"),
  "tg_lon_planner_takeover_request": (dev, "tg_lon_planner_takeover_request"),
  "tg_coordinator_lon_ctrl_state": (dev, "tg_coordinator_lon_ctrl_state"),
  "tg_updater_lon_traj_status": (dev, "tg_updater_lon_traj_status"),
  "tg_output_lon_replan_status": (dev, "tg_output_lon_replan_status"),
  "tg_lon_planner_follow_object_reaching_mode": (dev, "tg_lon_planner_object_reaching_mode"),
  "tg_lon_planner_longitudinal_planner_mode": (dev, "tg_lon_planner_lon_planner_mode"),
} for dev in devices
]

class View(interface.iView):
  def check(self):
    group = self.source.selectSignalGroupOrEmpty(sgs)
    return group

  def fill(self, group):
    return group

  def view(self, param, group):
    states_nav = datavis.cPlotNavigator(title="Longitudinal states")
    self.sync.addClient(states_nav)

    stateticks = {0: "false", 1: "true"}
    states_axis = states_nav.addAxis(ylabel="states", yticks=stateticks)
    feasibletime, feasiblevalue, feasibleunit = group.get_signal_with_unit("tg_lon_planner_feasible")
    states_nav.addSignal2Axis(states_axis, "tg_lon_planner_feasible", feasibletime, feasiblevalue, unit=feasibleunit)
    cptime, vpvalue, cpunit = group.get_signal_with_unit("tg_lon_planner_collision_possible")
    states_nav.addSignal2Axis(states_axis, "tg_lon_planner_collision_possible", cptime, vpvalue, unit=cpunit)
    trtime, trvalue, trunit = group.get_signal_with_unit("tg_lon_planner_takeover_request")
    states_nav.addSignal2Axis(states_axis, "tg_lon_planner_takeover_request", trtime, trvalue, unit=trunit)

    replanticks = {0: "START_OPT", 1: "START_HERE", 2: "START_PREV", 3: "CONT_PREV", 4: "OFF"}
    replan_axis = states_nav.addAxis(ylabel="replan status", yticks=replanticks)
    replantime, replanvalue, replanunit = group.get_signal_with_unit("tg_output_lon_replan_status")
    states_nav.addSignal2Axis(replan_axis, "tg_output_lon_replan_status", replantime, replanvalue, unit=replanunit)

    statusticks = {0: "VALID", 1: "INVALID", 2: "ERROR", 3: "NOT AVAILABLE"}
    trajaxis = states_nav.addAxis(ylabel="trajectory status", yticks=statusticks)
    time13, value13, unit13 = group.get_signal_with_unit("tg_updater_lon_traj_status")
    states_nav.addSignal2Axis(trajaxis, "tg_updater_lon_traj_status", time13, value13, unit=unit13)

    ctrlticks = {0: "OFF", 1: "ON", 2: "OVERRIDE", 3: "PAUSE"}
    ctrlaxis = states_nav.addAxis(ylabel="lon control state", yticks=ctrlticks)
    ctrltime, ctrlvalue, ctrlunit = group.get_signal_with_unit("tg_coordinator_lon_ctrl_state")
    states_nav.addSignal2Axis(ctrlaxis, "tg_coordinator_lon_ctrl_state", ctrltime, ctrlvalue, unit=ctrlunit)

    reachticks = {0: "None", 1: "MinJerk", 2: "SatFollow", 3: "Takeover", 4: "BangBang", 5: "Delay"}
    reach_axis = states_nav.addAxis(ylabel="reaching_mode", yticks=reachticks)
    reachtime, reachvalue, reachunit = group.get_signal_with_unit("tg_lon_planner_follow_object_reaching_mode")
    states_nav.addSignal2Axis(reach_axis, "tg_lon_planner_follow_object_reaching_mode", reachtime, reachvalue, unit=reachunit)

    modeticks = {0: "?", 1: "ObjectFollowing", 2: "SetspeedReaching", 3: "SetspeedTravelling", 4: "ObjectReaching"}
    mode_axis = states_nav.addAxis(ylabel="planner_mode", yticks=modeticks)
    modetime, modevalue, modeunit = group.get_signal_with_unit("tg_lon_planner_longitudinal_planner_mode")
    states_nav.addSignal2Axis(mode_axis, "tg_lon_planner_longitudinal_planner_mode", modetime, modevalue, unit=modeunit)

    return
