# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis
def_param = interface.NullParam

sgs  = [
{
  "XBRUS_AccelDemand_2A": ("XBRUS_2A", "XBRUS_AccelDemand_2A"),
  "ttc_cw": ("General_radar_status", "ttc_cw"),
  "tr0_radar_confidence": ("Tracks", "tr0_radar_confidence"),
  "tr0_range": ("Tracks", "tr0_range"),
  "AEB_state": ("ACC_S09", "AEB_state"),
  "ACC1_SpeedOfForwardVehicle_2A": ("ACC1_2A", "ACC1_SpeedOfForwardVehicle_2A"),
  "cm_system_status": ("General_radar_status", "cm_system_status"),
  "AudibleFeedback": ("PropWarn", "AudibleFeedback"),
  "tr0_video_confidence": ("Tracks", "tr0_video_confidence"),
  "VDC2_LongAccel_0B": ("VDC2_0B", "VDC2_LongAccel_0B"),
  "WheelBasedVehicleSpeed": ("CCVS", "WheelBasedVehicleSpeed"),
},
]

class View(interface.iView):
  def check(self):
    group = self.source.selectSignalGroup(sgs)
    return group

  def fill(self, group):
    return group

  def view(self, param, group):
    client00 = datavis.cPlotNavigator(title="", figureNr=None)
    self.sync.addClient(client00)
    axis00 = client00.addAxis()
    time00, value00, unit00 = group.get_signal_with_unit("cm_system_status")
    client00.addSignal2Axis(axis00, "cm_system_status", time00, value00, unit=unit00)
    time01, value01, unit01 = group.get_signal_with_unit("AEB_state")
    client00.addSignal2Axis(axis00, "AEB_state", time01, value01, unit=unit01)
    time02, value02, unit02 = group.get_signal_with_unit("AudibleFeedback")
    client00.addSignal2Axis(axis00, "AudibleFeedback", time02, value02, unit=unit02)
    axis01 = client00.addAxis()
    time03, value03, unit03 = group.get_signal_with_unit("XBRUS_AccelDemand_2A")
    client00.addSignal2Axis(axis01, "XBRUS_AccelDemand_2A", time03, value03, unit=unit03)
    time04, value04, unit04 = group.get_signal_with_unit("VDC2_LongAccel_0B")
    client00.addSignal2Axis(axis01, "VDC2_LongAccel_0B", time04, value04, unit=unit04)
    axis02 = client00.addAxis()
    time05, value05, unit05 = group.get_signal_with_unit("ttc_cw")
    client00.addSignal2Axis(axis02, "ttc_cw", time05, value05, unit=unit05)
    axis03 = client00.addAxis()
    time06, value06, unit06 = group.get_signal_with_unit("WheelBasedVehicleSpeed")
    client00.addSignal2Axis(axis03, "WheelBasedVehicleSpeed", time06, value06, unit=unit06)
    time07, value07, unit07 = group.get_signal_with_unit("ACC1_SpeedOfForwardVehicle_2A")
    client00.addSignal2Axis(axis03, "ACC1_SpeedOfForwardVehicle_2A", time07, value07, unit=unit07)
    axis04 = client00.addAxis()
    time08, value08, unit08 = group.get_signal_with_unit("tr0_range")
    client00.addSignal2Axis(axis04, "tr0_range", time08, value08, unit=unit08)
    axis05 = client00.addAxis()
    time09, value09, unit09 = group.get_signal_with_unit("tr0_radar_confidence")
    client00.addSignal2Axis(axis05, "tr0_radar_confidence", time09, value09, unit=unit09)
    time10, value10, unit10 = group.get_signal_with_unit("tr0_video_confidence")
    client00.addSignal2Axis(axis05, "tr0_video_confidence", time10, value10, unit=unit10)
    return
