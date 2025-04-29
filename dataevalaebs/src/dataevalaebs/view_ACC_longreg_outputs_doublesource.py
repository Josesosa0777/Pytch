# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

# Important : Run scan before usage.

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
  channels = "main", "rail" 
  def check(self):
    group = self.source.selectSignalGroup(sgs)
    return group

  def fill(self, group):
    return group

  def view(self, param, group):
    rail_source = self.get_source("rail")
    meas_source = self.get_source("main")
    plot_nav = datavis.cPlotNavigator(title="", figureNr=None)
    self.sync.addClient(plot_nav)
    
    
    axis_distance_m = plot_nav.addAxis()
    time00, value00 =           meas_source.getSignalFromSignalGroup(group, "ACC1_DistanceOfForwardVehicle_2A")
    time00_rail, value00_rail = rail_source.getSignalFromSignalGroup(group, "ACC1_DistanceOfForwardVehicle_2A")
    plot_nav.addSignal2Axis(axis_distance_m, "ACC1_IV_Distance (MEAS)", time00, value00, unit='m')
    plot_nav.addSignal2Axis(axis_distance_m, "ACC1_IV_Distance (RAIL)", time00_rail, value00_rail, unit='m')
    
    axis_hv_speed_ms = plot_nav.addAxis()
    time01, value01 =           meas_source.getSignalFromSignalGroup(group, "actual_vehicle_speed")
    time01_rail, value01_rail = rail_source.getSignalFromSignalGroup(group, "actual_vehicle_speed")
    plot_nav.addSignal2Axis(axis_hv_speed_ms, "actual_vehicle_speed (MEAS)", time01, value01, unit='m/s')
    plot_nav.addSignal2Axis(axis_hv_speed_ms, "actual_vehicle_speed (RAIL)", time01_rail, value01_rail, unit='m/s')
    
    axis_decel_xbr_ms2 = plot_nav.addAxis()
    time02, value02 =           meas_source.getSignalFromSignalGroup(group, "LCG_a_xbr_out")
    time02_rail, value02_rail = rail_source.getSignalFromSignalGroup(group, "LCG_a_xbr_out")
    plot_nav.addSignal2Axis(axis_decel_xbr_ms2, "LCG_a_xbr_out (MEAS)", time02, value02, unit='m/s^2')
    plot_nav.addSignal2Axis(axis_decel_xbr_ms2, "LCG_a_xbr_out (RAIL)", time02_rail, value02_rail, unit='m/s^2')
    
    
    axis_eng_pcnt = plot_nav.addAxis()
    time03, value03 =           meas_source.getSignalFromSignalGroup(group, "LCM_n_pcnt_eng_out")
    time03_rail, value03_rail = rail_source.getSignalFromSignalGroup(group, "LCM_n_pcnt_eng_out")
    plot_nav.addSignal2Axis(axis_eng_pcnt, "LCM_n_pcnt_eng_out (MEAS)", time03, value03, unit='%')
    plot_nav.addSignal2Axis(axis_eng_pcnt, "LCM_n_pcnt_eng_out (RAIL)", time03_rail, value03_rail, unit='%')
    
    axis_jolt_dem_ms3 = plot_nav.addAxis()
    time04, value04 =           meas_source.getSignalFromSignalGroup(group, "ACD_b_ctl")
    time04_rail, value04_rail = rail_source.getSignalFromSignalGroup(group, "ACD_b_ctl")
    plot_nav.addSignal2Axis(axis_jolt_dem_ms3, "ACD_b_ctl (MEAS)", time04, value04, unit='m/s^3')
    plot_nav.addSignal2Axis(axis_jolt_dem_ms3, "ACD_b_ctl (RAIL)", time04_rail, value04_rail, unit='m/s^3')
    return
