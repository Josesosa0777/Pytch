# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis
def_param = interface.NullParam

devices = ("trajectory_generator_flx20_autobox", "XCP_Test")
sgs = [
{
  # "tg_driver_input_pause_button": (dev, "tg_driver_input_pause_button"),
  # "tg_driver_input_resume_button": (dev, "tg_driver_input_resume_button"),
  # "tg_driver_input_set_button": (dev, "tg_driver_input_set_button"),
  # "tg_driver_input_accel_button": (dev, "tg_driver_input_accel_button"),
  # "tg_driver_input_coast_button": (dev, "tg_driver_input_coast_button"),
  "tg_lon_planner_hmi_v_set": (dev, "tg_lon_planner_hmi_v_set"),
  "tg_lon_planner_ego_vx": (dev, "tg_lon_planner_ego_vx"),
  "tg_lon_planner_ego_ax": (dev, "tg_lon_planner_ego_ax"),
  "tg_output_arbitrated_ref_traj_st_coeffs": (dev, "tg_output_arbitrated_ref_traj_st_coeffs"),
  "tg_lon_planner_track_dx": (dev, "tg_lon_planner_track_dx"),
  "tg_lon_planner_dist_follow": (dev, "tg_lon_planner_dist_follow"),
  "tg_lon_maneuver_template_output_obj_s_t_coeffs": (dev, "tg_lon_maneuver_template_output_obj_s_t_coeffs"),
  "tg_lon_maneuver_template_output_obj_s_t_num_segments": (dev, "tg_lon_maneuver_template_output_obj_s_t_num_segments"),
} for dev in devices
]

class View(interface.iView):
  def check(self):
    group = self.source.selectSignalGroupOrEmpty(sgs)
    return group

  def fill(self, group):
    return group

  def view(self, param, group):
    kin_nav = datavis.cPlotNavigator(title="Longitudinal kinematics")
    self.sync.addClient(kin_nav)

    #buttonticks = {0: "released", 1: "pressed"}
    #button_axis = kin_nav.addAxis(ylabel="buttons", yticks=buttonticks)
    #pausetime, pausevalue, pauseunit = group.get_signal_with_unit("tg_driver_input_pause_button")
    #kin_nav.addSignal2Axis(button_axis, "tg_driver_input_pause_button", pausetime, pausevalue, unit=pauseunit)
    #reusmetime, resumevalue, resumeunit = group.get_signal_with_unit("tg_driver_input_resume_button")
    #kin_nav.addSignal2Axis(button_axis, "tg_driver_input_resume_button", reusmetime, resumevalue, unit=resumeunit)
    #settime, setvalue, setunit = group.get_signal_with_unit("tg_driver_input_set_button")
    #kin_nav.addSignal2Axis(button_axis, "tg_driver_input_set_button", settime, setvalue, unit=setunit)
    #acceltime, accelvalue, accelunit = group.get_signal_with_unit("tg_driver_input_accel_button")
    #kin_nav.addSignal2Axis(button_axis, "tg_driver_input_accel_button", acceltime, accelvalue, unit=accelunit)
    #coasttime, coastvalue, coastunit = group.get_signal_with_unit("tg_driver_input_coast_button")
    #kin_nav.addSignal2Axis(button_axis, "tg_driver_input_coast_button", coasttime, coastvalue, unit=coastunit)

    speed_axis = kin_nav.addAxis(ylabel="speed")
    vxtime, vxvalue, vxunit = group.get_signal_with_unit("tg_lon_planner_ego_vx")
    kin_nav.addSignal2Axis(speed_axis, "tg_lon_planner_ego_vx", vxtime, vxvalue, unit=vxunit)
    # axtime, axvalue, axunit = group.get_signal_with_unit("tg_lon_planner_ego_ax")
    # kin_nav.addSignal2Axis(speed_axis, "tg_lon_planner_ego_ax", axtime, axvalue, unit=axunit)
    vsettime, vsetvalue, vsetunit = group.get_signal_with_unit("tg_lon_planner_hmi_v_set")
    kin_nav.addSignal2Axis(speed_axis, "tg_lon_planner_hmi_v_set", vsettime, vsetvalue, unit=vsetunit)
    vreqtime, vreqvalue, vrequnit = group.get_signal_with_unit("tg_output_arbitrated_ref_traj_st_coeffs")
    kin_nav.addSignal2Axis(speed_axis, "tg_output_v_req", vreqtime, vreqvalue[:,4,0], unit=vrequnit)
    tvtime, tvvalue, tvunit = group.get_signal_with_unit("tg_lon_maneuver_template_output_obj_s_t_coeffs")
    kin_nav.addSignal2Axis(speed_axis, "object vx abs", tvtime, tvvalue[:,4,0], unit=tvunit)
    speed_axis.set_ylim([-5.0, 50.0])

    dist_axis = kin_nav.addAxis(ylabel="distance")
    dxtime, dxvalue, dxunit = group.get_signal_with_unit("tg_lon_maneuver_template_output_obj_s_t_coeffs")
    kin_nav.addSignal2Axis(dist_axis, "object dx", dxtime, dxvalue[:,5,0], unit=dxunit)
    time00, value00, unit00 = group.get_signal_with_unit("tg_lon_planner_dist_follow")
    kin_nav.addSignal2Axis(dist_axis, "tg_lon_planner_dist_follow", time00, value00, unit=unit00)
    dist_axis.set_ylim([-5.0, 120.0])

    axis = kin_nav.addAxis(ylabel="num. segments")
    time, value, unit = group.get_signal_with_unit("tg_lon_maneuver_template_output_obj_s_t_num_segments")
    kin_nav.addSignal2Axis(axis, "obj_s_t_num_segments", time, value, unit=unit)
    return
