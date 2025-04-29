# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis
def_param = interface.NullParam

sgs  = [
{
  "ACD_b_ctl": ("ACC_S04", "ACD_b_ctl"),
  "actual_vehicle_speed": ("General_radar_status", "actual_vehicle_speed"),
  "ACC1_DistanceOfForwardVehicle_2A": ("ACC1_2A", "ACC1_DistanceOfForwardVehicle_2A"),
  "LCM_n_pcnt_eng_out": ("ACC_S04", "LCM_n_pcnt_eng_out"),
  "LCG_a_xbr_out": ("ACC_S05", "LCG_a_xbr_out"),
},
]

class View(interface.iView):
  def check(self):
    group = self.source.selectSignalGroup(sgs)
    return group

  def fill(self, group):
    return group

  def view(self, param, group):
    plot_nav = datavis.cPlotNavigator(title="", figureNr=None)
    self.sync.addClient(plot_nav)
    
    
    axis_distance_m = plot_nav.addAxis()
    time00, value00, unit00 = group.get_signal_with_unit("ACC1_DistanceOfForwardVehicle_2A")
    plot_nav.addSignal2Axis(axis_distance_m, "ACC1_DistanceOfForwardVehicle_2A", time00, value00, unit=unit00)
    
    
    axis_hv_speed_ms = plot_nav.addAxis()
    time01, value01, unit01 = group.get_signal_with_unit("actual_vehicle_speed")
    plot_nav.addSignal2Axis(axis_hv_speed_ms, "actual_vehicle_speed", time01, value01, unit=unit01)
    
    
    axis_decel_xbr_ms2 = plot_nav.addAxis()
    time02, value02, unit02 = group.get_signal_with_unit("LCG_a_xbr_out")
    plot_nav.addSignal2Axis(axis_decel_xbr_ms2, "LCG_a_xbr_out", time02, value02, unit=unit02)
    
    
    axis_eng_pcnt = plot_nav.addAxis()
    time03, value03, unit03 = group.get_signal_with_unit("LCM_n_pcnt_eng_out")
    plot_nav.addSignal2Axis(axis_eng_pcnt, "LCM_n_pcnt_eng_out", time03, value03, unit=unit03)
    
    
    axis_jolt_dem_ms3 = plot_nav.addAxis()
    time04, value04, unit04 = group.get_signal_with_unit("ACD_b_ctl")
    plot_nav.addSignal2Axis(axis_jolt_dem_ms3, "ACD_b_ctl", time04, value04, unit=unit04)
    return
