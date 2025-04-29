# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis
def_param = interface.NullParam

sgs  = [
{
  "tg_output_lon_replan_status": ("trajectory_generator_flx20_autobox", "tg_output_lon_replan_status"),
  "tg_lon_planner_longitudinal_planner_mode": ("trajectory_generator_flx20_autobox", "tg_lon_planner_longitudinal_planner_mode"),
  "tg_driver_input_accel_button": ("trajectory_generator_flx20_autobox", "tg_driver_input_accel_button"),
  "tg_lon_planner_hmi_v_set": ("trajectory_generator_flx20_autobox", "tg_lon_planner_hmi_v_set"),
  "tg_lon_planner_ego_vx": ("trajectory_generator_flx20_autobox", "tg_lon_planner_ego_vx"),
  "tg_output_arbitrated_ref_traj_st_coeffs": ("trajectory_generator_flx20_autobox", "tg_output_arbitrated_ref_traj_st_coeffs"),
},
]

class View(interface.iView):
  def check(self):
    group = self.source.selectSignalGroupOrEmpty(sgs)
    return group

  def fill(self, group):
    return group

  def view(self, param, group):
    ss_nav = datavis.cPlotNavigator(title="Longitudinal states")
    self.sync.addClient(ss_nav)

    replanticks = {0: "START_OPT", 1: "START_HERE", 2: "START_PREV", 3: "CONT_PREV", 4: "OFF"}
    replan_axis = ss_nav.addAxis(ylabel="replan status", yticks=replanticks)
    replantime, replanvalue, replanunit = group.get_signal_with_unit("tg_output_lon_replan_status")
    ss_nav.addSignal2Axis(replan_axis, "tg_output_lon_replan_status", replantime, replanvalue, unit=replanunit)

    modeticks = {0: "Object2", 1: "Object1", 2: "SetspeedReaching", 3: "SetspeedTravelling"}
    mode_axis = ss_nav.addAxis(ylabel="planner_mode", yticks=modeticks)
    modetime, modevalue, modeunit = group.get_signal_with_unit("tg_lon_planner_longitudinal_planner_mode")
    ss_nav.addSignal2Axis(mode_axis, "tg_lon_planner_longitudinal_planner_mode", modetime, modevalue, unit=modeunit)

    buttonticks = {0: "released", 1: "pushed"}
    button_axis = ss_nav.addAxis(ylabel="buttons", yticks=buttonticks)
    acceltime, accelvalue, accelunit = group.get_signal_with_unit("tg_driver_input_accel_button")
    ss_nav.addSignal2Axis(button_axis, "tg_driver_input_accel_button", acceltime, accelvalue, unit=accelunit)

    speed_axis = ss_nav.addAxis(ylabel="speed")
    vxtime, vxvalue, vxunit = group.get_signal_with_unit("tg_lon_planner_ego_vx")
    ss_nav.addSignal2Axis(speed_axis, "tg_lon_planner_ego_vx", vxtime, vxvalue, unit=vxunit)
    vsettime, vsetvalue, vsetunit = group.get_signal_with_unit("tg_lon_planner_hmi_v_set")
    ss_nav.addSignal2Axis(speed_axis, "tg_lon_planner_hmi_v_set", vsettime, vsetvalue, unit=vsetunit)
    vreqtime, vreqvalue, vrequnit = group.get_signal_with_unit("tg_output_arbitrated_ref_traj_st_coeffs")
    ss_nav.addSignal2Axis(speed_axis, "tg_output_v_req", vreqtime, vreqvalue[:,4,0], unit=vrequnit)
    
    return
