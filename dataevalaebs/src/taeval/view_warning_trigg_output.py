# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis
import numpy as np
def_param = interface.NullParam

sgs     = [
{
  "warn_trigg_in_dx_rel_sensor": ("TA", "warn_trigg_in_dx_rel_sensor"),
  "warn_trigg_in_dy_rel_sensor": ("TA", "warn_trigg_in_dy_rel_sensor"),
  "warn_trigg_out_warning_track": ("TA", "warn_trigg_out_warning_track"),
  "warn_trigg_out_dy_hazard": ("TA", "warn_trigg_out_dy_hazard"),
  "warn_trigg_out_dy_info": ("TA", "warn_trigg_out_dy_info"),
  "warn_trigg_out_dx_hazard_front": ("TA", "warn_trigg_out_dx_hazard_front"),
  "warn_trigg_out_dx_hazard_rear": ("TA", "warn_trigg_out_dx_hazard_rear"),
  "warn_trigg_in_vx_over_gnd_sensor": ("TA", "warn_trigg_in_vx_over_gnd_sensor"),
  "warn_trigg_in_vy_over_gnd_sensor": ("TA", "warn_trigg_in_vy_over_gnd_sensor"),
  "warn_trigg_in_vx_ego_sensor": ("TA", "warn_trigg_in_vx_ego_sensor"),
  "warn_trigg_in_vy_ego_sensor": ("TA", "warn_trigg_in_vy_ego_sensor"),
  "warn_trigg_out_sys_state": ("TA", "warn_trigg_out_sys_state"),
  "warn_trigg_in_track_motion_state": ("TA", "warn_trigg_in_track_motion_state"),
  "LED_yellow": ("TA", "LED_yellow"),
  "LED_red": ("TA", "LED_red"),
  "feedbacklamp": ("TA", "feedbacklamp"),
  "speaker": ("TA", "speaker"),
},
]

class View(interface.iView):
  def check(self):
    group = self.source.selectSignalGroupOrEmpty(sgs)
    return group

  def fill(self, group):
    return group

  def view(self, param, group):
    kwargs1 = {'lw': 0, 'marker': '.'}
    client00 = datavis.cPlotNavigator(title="")
    self.sync.addClient(client00)
    axis00 = client00.addAxis(ylim=(-0.5,4.5))
    axis01 = client00.addAxis(ylim=(-15.5,5.5))
    axis02 = client00.addAxis(ylim=(-0.5,7.5))
    axis03 = client00.addAxis(ylim=(-5.5,5.5))
    axis04 = client00.addAxis()
    
    time00, value00, unit00 = group.get_signal_with_unit("warn_trigg_out_warning_track")
    time01, value01, unit01 = group.get_signal_with_unit("warn_trigg_in_dx_rel_sensor")
    time02, value02, unit02 = group.get_signal_with_unit("warn_trigg_in_dy_rel_sensor")
    time03, value03, unit03 = group.get_signal_with_unit("warn_trigg_out_dy_hazard")
    time04, value04, unit04 = group.get_signal_with_unit("warn_trigg_out_dy_info")
    time05, value05, unit05 = group.get_signal_with_unit("warn_trigg_out_dx_hazard_front")
    time06, value06, unit06 = group.get_signal_with_unit("warn_trigg_out_dx_hazard_rear")
    
    time07, value07, unit07 = group.get_signal_with_unit("warn_trigg_in_vx_over_gnd_sensor")
    time08, value08, unit08 = group.get_signal_with_unit("warn_trigg_in_vy_over_gnd_sensor")
    time09, value09, unit09 = group.get_signal_with_unit("warn_trigg_in_vx_ego_sensor")
    time10, value10, unit10 = group.get_signal_with_unit("warn_trigg_in_vy_ego_sensor")

    time11, value11, unit11 = group.get_signal_with_unit("warn_trigg_out_sys_state")
    time12, value12, unit12 = group.get_signal_with_unit("warn_trigg_in_track_motion_state")

    time13, value13, unit13 = group.get_signal_with_unit("feedbacklamp")
    time14, value14, unit14 = group.get_signal_with_unit("LED_yellow")
    time15, value15, unit15 = group.get_signal_with_unit("LED_red")
    time16, value16, unit16 = group.get_signal_with_unit("speaker")
    
    time_size, target_size = value01.shape

    pos_x = []
    pos_y = []
    rel_vx = []
    rel_vy = []
    track_vx = []
    track_vy = []
    abs_v = []
    mot_state = []
    for j in xrange(time_size):
      if value00[j] > 0:
        i = value00[j] - 1
        pos_x.append(value01[j,i])
        pos_y.append(value02[j,i])
        rel_vx.append(value07[j,i] - value09[j])
        rel_vy.append(value08[j,i] - value10[j])
        track_vx.append(value07[j,i])
        track_vy.append(value08[j,i])
        abs_v.append(((value07[j,i]**2.0)+(value08[j,i]**2.0))**0.5)
        mot_state.append(value12[j,i])
      else:
        pos_x.append(2000.0)
        pos_y.append(-2000.0)
        rel_vx.append(2000.0)
        rel_vy.append(2000.0)
        track_vx.append(2000.0)
        track_vy.append(2000.0)
        abs_v.append(2000.0)
        mot_state.append(0)
        
    client00.addSignal2Axis(axis04, "warn_trigg_out_warning_track", time00, value00, unit=unit00, **kwargs1)

    client00.addSignal2Axis(axis00, "feedbacklamp", time13, value13, unit=unit13)
    client00.addSignal2Axis(axis00, "LED_yellow", time14, value14*2.0, unit=unit14)
    client00.addSignal2Axis(axis00, "LED_red", time15, value15*3.0, unit=unit15)
    client00.addSignal2Axis(axis00, "speaker", time16, value16*4.0, unit=unit16)
    client00.addSignal2Axis(axis00, "warn_trigg_out_sys_state", time11, value11/4.0, unit=unit11, **kwargs1)
    client00.addSignal2Axis(axis04, "warn_trigg_out_sys_state", time11, value11, unit=unit11)
    
    warn_pos_x = np.asarray(pos_x)
    warn_pos_y = np.asarray(pos_y)
    client00.addSignal2Axis(axis01, "warn_trigg_in_dx", time01, warn_pos_x, unit=unit01, **kwargs1)
    client00.addSignal2Axis(axis01, "warn_trigg_out_dx_hazard_front", time05, value05, unit=unit05)
    client00.addSignal2Axis(axis01, "warn_trigg_out_dx_hazard_rear", time06, value06, unit=unit06)

    client00.addSignal2Axis(axis02, "warn_trigg_in_dy", time02, warn_pos_y, unit=unit02, **kwargs1)
    client00.addSignal2Axis(axis02, "warn_trigg_out_dy_hazard", time03, value03, unit=unit03)
    client00.addSignal2Axis(axis02, "warn_trigg_out_dy_info", time04, value04, unit=unit04)

    warn_vx = np.asarray(rel_vx)
    warn_vy = np.asarray(rel_vy)
    warn_v_abs = np.asarray(abs_v)
    gnd_vx = np.asarray(track_vx)
    gnd_vy = np.asarray(track_vy)
    motion = np.asarray(mot_state)

    client00.addSignal2Axis(axis03, "warn_track_vx_gnd", time09, gnd_vx, unit=unit09, **kwargs1)
    client00.addSignal2Axis(axis03, "warn_track_vy_gnd", time10, gnd_vy, unit=unit10, **kwargs1)
    client00.addSignal2Axis(axis03, "warn_track_motion_state", time12, motion, unit=unit12)
    client00.addSignal2Axis(axis03, "vx_ego_sensor", time09, value09, unit=unit09)
    client00.addSignal2Axis(axis03, "vy_ego_sensor", time10, value10, unit=unit10)
    
    return
