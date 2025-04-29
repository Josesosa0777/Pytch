# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import interface
import datavis

sgs = [
{
  "covi": ("General_radar_status", "covi"),
  "SIB2_COVI_error": ("General_radar_status", "SIB2_COVI_error"),
  "FOV_count_left": ("General_radar_status", "FOV_count_left"),
  "sensor_blind_detected": ("General_radar_status", "sensor_blind_detected"),
  "number_of_targets": ("General_radar_status", "number_of_targets"),
  "dfil": ("General_radar_status", "dfil"),
  "number_of_tracks": ("General_radar_status", "number_of_tracks"),
  "yawrate_offset": ("General_radar_status", "yawrate_offset"),
  "SIB1_FOV_error": ("General_radar_status", "SIB1_FOV_error"),
  "FOV_count_centre": ("General_radar_status", "FOV_count_centre"),
  "cal_yaw_offset": ("General_radar_status", "cal_yaw_offset"),
  "FOV_count_right": ("General_radar_status", "FOV_count_right"),
  "sensor_blindness": ("General_radar_status", "sensor_blindness"),
},
]

class View(interface.iView):
  def check(self):
    group = self.source.selectSignalGroupOrEmpty(sgs)
    return group

  def view(self, group):
    client00 = datavis.cPlotNavigator(title="FLR21 sensor check")
    self.sync.addClient(client00)
    axis00 = client00.addAxis()
    time00, value00, unit00 = group.get_signal_with_unit("dfil")
    client00.addSignal2Axis(axis00, "dfil", time00, value00, unit=unit00)
    axis01 = client00.addAxis()
    time01, value01, unit01 = group.get_signal_with_unit("covi")
    client00.addSignal2Axis(axis01, "covi", time01, value01, unit=unit01)
    time02, value02, unit02 = group.get_signal_with_unit("SIB2_COVI_error")
    client00.addSignal2Axis(axis01, "SIB2_COVI_error", time02, value02, unit=unit02)
    axis02 = client00.addAxis()
    time03, value03, unit03 = group.get_signal_with_unit("cal_yaw_offset")
    client00.addSignal2Axis(axis02, "cal_yaw_offset", time03, value03, unit=unit03)
    time04, value04, unit04 = group.get_signal_with_unit("yawrate_offset")
    client00.addSignal2Axis(axis02, "yawrate_offset", time04, value04, unit=unit04)
    axis03 = client00.addAxis()
    time05, value05, unit05 = group.get_signal_with_unit("sensor_blindness")
    client00.addSignal2Axis(axis03, "sensor_blindness", time05, value05, unit=unit05)
    time06, value06, unit06 = group.get_signal_with_unit("sensor_blind_detected")
    client00.addSignal2Axis(axis03, "sensor_blind_detected", time06, value06, unit=unit06)
    axis04 = client00.addAxis()
    time07, value07, unit07 = group.get_signal_with_unit("FOV_count_left")
    client00.addSignal2Axis(axis04, "FOV_count_left", time07, value07, unit=unit07)
    time08, value08, unit08 = group.get_signal_with_unit("FOV_count_centre")
    client00.addSignal2Axis(axis04, "FOV_count_centre", time08, value08, unit=unit08)
    time09, value09, unit09 = group.get_signal_with_unit("FOV_count_right")
    client00.addSignal2Axis(axis04, "FOV_count_right", time09, value09, unit=unit09)
    time10, value10, unit10 = group.get_signal_with_unit("SIB1_FOV_error")
    client00.addSignal2Axis(axis04, "SIB1_FOV_error", time10, value10, unit=unit10)
    axis05 = client00.addAxis()
    time11, value11, unit11 = group.get_signal_with_unit("number_of_targets")
    client00.addSignal2Axis(axis05, "number_of_targets", time11, value11, unit=unit11)
    time12, value12, unit12 = group.get_signal_with_unit("number_of_tracks")
    client00.addSignal2Axis(axis05, "number_of_tracks", time12, value12, unit=unit12)
    return
