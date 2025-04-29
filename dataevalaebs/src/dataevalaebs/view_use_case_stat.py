# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis
def_param = interface.NullParam

sgs  = [
{
  "tr0_CW_track": ("Tracks", "tr0_CW_track"),
  "Longitudinal_Distance_3_A": ("Video_Object_3_A", "Longitudinal_Distance_3_A"),
  "tr0_radar_confidence": ("Tracks", "tr0_radar_confidence"),
  "AEBS1_AEBSState_2A": ("AEBS1_2A", "AEBS1_AEBSState_2A"),
  "AEBS1_CollisionWarningLevel_2A": ("AEBS1_2A", "AEBS1_CollisionWarningLevel_2A"),
  "tr0_range": ("Tracks", "tr0_range"),
  "kbaebsInaebs.AdditionalSensorAssociated_b": ("CCP", "kbaebsInaebs.AdditionalSensorAssociated_b"),
  "Longitudinal_Distance_0_A": ("Video_Object_0_A", "Longitudinal_Distance_0_A"),
  "Longitudinal_Distance_2_A": ("Video_Object_2_A", "Longitudinal_Distance_2_A"),
  "tr0_video_confidence": ("Tracks", "tr0_video_confidence"),
  "Longitudinal_Distance_1_A": ("Video_Object_1_A", "Longitudinal_Distance_1_A"),
  "XBR_ExtAccelDem_2A": ("XBR_2A", "XBR_ExtAccelDem_2A"),
},
]

class cView(interface.iView):
  def check(self):
    group = self.source.selectSignalGroup(sgs)
    return group

  def fill(self, group):
    return group

  def view(self, param, group):
    client00 = datavis.cPlotNavigator(title="", figureNr=None)
    self.sync.addClient(client00)
    axis00 = client00.addAxis()
    time00, value00, unit00 = group.get_signal_with_unit("tr0_CW_track")
    client00.addSignal2Axis(axis00, "tr0_CW_track", time00, value00, unit=unit00)
    axis01 = client00.addAxis()
    time01, value01, unit01 = group.get_signal_with_unit("tr0_radar_confidence")
    client00.addSignal2Axis(axis01, "tr0_radar_confidence", time01, value01, unit=unit01)
    time02, value02, unit02 = group.get_signal_with_unit("tr0_video_confidence")
    client00.addSignal2Axis(axis01, "tr0_video_confidence", time02, value02, unit=unit02)
    axis02 = client00.addAxis()
    time03, value03, unit03 = group.get_signal_with_unit("tr0_range")
    client00.addSignal2Axis(axis02, "tr0_range", time03, value03, unit=unit03)
    axis03 = client00.addAxis()
    time04, value04, unit04 = group.get_signal_with_unit("XBR_ExtAccelDem_2A")
    client00.addSignal2Axis(axis03, "XBR_ExtAccelDem_2A", time04, value04, unit=unit04)
    axis04 = client00.addAxis()
    time05, value05, unit05 = group.get_signal_with_unit("AEBS1_AEBSState_2A")
    client00.addSignal2Axis(axis04, "AEBS1_AEBSState_2A", time05, value05, unit=unit05)
    time05, value11, unit11 = group.get_signal_with_unit("AEBS1_CollisionWarningLevel_2A")
    client00.addSignal2Axis(axis04, "AEBS1_CollisionWarningLevel_2A", time05, value11, unit=unit11)
    axis05 = client00.addAxis()
    time06, value06, unit06 = group.get_signal_with_unit("Longitudinal_Distance_0_A")
    client00.addSignal2Axis(axis05, "Longitudinal_Distance_0_A", time06, value06, unit=unit06)
    time07, value07, unit07 = group.get_signal_with_unit("Longitudinal_Distance_1_A")
    client00.addSignal2Axis(axis05, "Longitudinal_Distance_1_A", time07, value07, unit=unit07)
    time08, value08, unit08 = group.get_signal_with_unit("Longitudinal_Distance_2_A")
    client00.addSignal2Axis(axis05, "Longitudinal_Distance_2_A", time08, value08, unit=unit08)
    time09, value09, unit09 = group.get_signal_with_unit("Longitudinal_Distance_3_A")
    client00.addSignal2Axis(axis05, "Longitudinal_Distance_3_A", time09, value09, unit=unit09)
    axis06 = client00.addAxis()
    time10, value10, unit10 = group.get_signal_with_unit("kbaebsInaebs.AdditionalSensorAssociated_b")
    client00.addSignal2Axis(axis06, "kbaebsInaebs.AdditionalSensorAssociated_b", time10, value10, unit=unit10)
    return
