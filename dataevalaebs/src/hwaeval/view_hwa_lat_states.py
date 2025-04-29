# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis
def_param = interface.NullParam

sgs  = [
{
  "tg_output_lat_replan_status": ("trajectory_generator_flx20_autobox", "tg_output_lat_replan_status"),
  "tg_updater_lat_traj_status": ("trajectory_generator_flx20_autobox", "tg_updater_lat_traj_status"),
  "tg_coordinator_lat_ctrl_state": ("trajectory_generator_flx20_autobox", "tg_coordinator_lat_ctrl_state"),
  "tg_lat_planner_centerline_learned": ("trajectory_generator_flx20_autobox", "tg_lat_planner_centerline_learned"),
  "tg_driver_input_pause_button": ("trajectory_generator_flx20_autobox", "tg_driver_input_pause_button"),
  "tg_driver_input_resume_button": ("trajectory_generator_flx20_autobox", "tg_driver_input_resume_button"),
},
]

class View(interface.iView):
  def check(self):
    group = self.source.selectSignalGroupOrEmpty(sgs)
    return group

  def fill(self, group):
    return group

  def view(self, param, group):
    states_nav = datavis.cPlotNavigator(title="Lateral states")
    self.sync.addClient(states_nav)

    buttonticks = {0: "released", 1: "pressed"}
    button_axis = states_nav.addAxis(ylabel="buttons", yticks=buttonticks)
    pausetime, pausevalue, pauseunit = group.get_signal_with_unit("tg_driver_input_pause_button")
    states_nav.addSignal2Axis(button_axis, "tg_driver_input_pause_button", pausetime, pausevalue, unit=pauseunit)
    reusmetime, resumevalue, resumeunit = group.get_signal_with_unit("tg_driver_input_resume_button")
    states_nav.addSignal2Axis(button_axis, "tg_driver_input_resume_button", reusmetime, resumevalue, unit=resumeunit)

    replanticks = {0: "START_OPT", 1: "START_HERE", 2: "START_PREV", 3: "CONT_PREV", 4: "OFF"}
    replan_axis = states_nav.addAxis(ylabel="replan status", yticks=replanticks)
    replantime, replanvalue, replanunit = group.get_signal_with_unit("tg_output_lat_replan_status")
    states_nav.addSignal2Axis(replan_axis, "tg_output_lat_replan_status", replantime, replanvalue, unit=replanunit)

    statusticks = {0: "VALID", 1: "INVALID", 2: "ERROR", 3: "NOT AVAILABLE"}
    trajaxis = states_nav.addAxis(ylabel="trajectory status", yticks=statusticks)
    time13, value13, unit13 = group.get_signal_with_unit("tg_updater_lat_traj_status")
    states_nav.addSignal2Axis(trajaxis, "tg_updater_lat_traj_status", time13, value13, unit=unit13)

    ctrlticks = {0: "OFF", 1: "ON", 2: "OVERRIDE", 3: "PAUSE"}
    ctrlaxis = states_nav.addAxis(ylabel="lon control state", yticks=ctrlticks)
    ctrltime, ctrlvalue, ctrlunit = group.get_signal_with_unit("tg_coordinator_lat_ctrl_state")
    states_nav.addSignal2Axis(ctrlaxis, "tg_coordinator_lat_ctrl_state", ctrltime, ctrlvalue, unit=ctrlunit)

    center_axis = states_nav.addAxis(ylabel="learned centerline")
    centertime, centervalue, centerunit = group.get_signal_with_unit("tg_lat_planner_centerline_learned")
    states_nav.addSignal2Axis(center_axis, "tg_lat_planner_centerline_learned", centertime, centervalue, unit=centerunit)

    return
