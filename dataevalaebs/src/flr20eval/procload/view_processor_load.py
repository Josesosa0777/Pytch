# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis
def_param = interface.NullParam

sgs  = [
{
  "MinimumMainStack": ("ACC_S03", "MinimumMainStack"),
  "KBAEBSRuntimeWorst": ("ACC_S03", "KBAEBSRuntimeWorst"),
  "number_of_targets": ("General_radar_status", "number_of_targets"),
  "KBAEBSRuntimeCurrent": ("ACC_S03", "KBAEBSRuntimeCurrent"),
  "AEBS1_AEBSState_2A": ("AEBS1_2A", "AEBS1_AEBSState_2A"),
  "number_of_tracks": ("General_radar_status", "number_of_tracks"),
  "CurrentProcessorLoad": ("ACC_S03", "CurrentProcessorLoad"),
  "tr0_CW_track": ("Tracks", "tr0_CW_track"),
  "MaximumProcessorLoad": ("ACC_S03", "MaximumProcessorLoad"),
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
    time00, value00, unit00 = group.get_signal_with_unit("CurrentProcessorLoad")
    client00.addSignal2Axis(axis00, "CurrentProcessorLoad", time00, value00, unit=unit00)
    time01, value01, unit01 = group.get_signal_with_unit("MaximumProcessorLoad")
    client00.addSignal2Axis(axis00, "MaximumProcessorLoad", time01, value01, unit=unit01)
    axis01 = client00.addAxis()
    time02, value02, unit02 = group.get_signal_with_unit("KBAEBSRuntimeCurrent")
    client00.addSignal2Axis(axis01, "KBAEBSRuntimeCurrent", time02, value02, unit=unit02)
    time03, value03, unit03 = group.get_signal_with_unit("KBAEBSRuntimeWorst")
    client00.addSignal2Axis(axis01, "KBAEBSRuntimeWorst", time03, value03, unit=unit03)
    axis02 = client00.addAxis()
    time04, value04, unit04 = group.get_signal_with_unit("MinimumMainStack")
    client00.addSignal2Axis(axis02, "MinimumMainStack", time04, value04, unit=unit04)
    axis03 = client00.addAxis()
    time05, value05, unit05 = group.get_signal_with_unit("number_of_targets")
    client00.addSignal2Axis(axis03, "number_of_targets", time05, value05, unit=unit05)
    time06, value06, unit06 = group.get_signal_with_unit("number_of_tracks")
    client00.addSignal2Axis(axis03, "number_of_tracks", time06, value06, unit=unit06)
    axis04 = client00.addAxis()
    time07, value07, unit07 = group.get_signal_with_unit("tr0_CW_track")
    client00.addSignal2Axis(axis04, "tr0_CW_track", time07, value07, unit=unit07)
    axis05 = client00.addAxis()
    time08, value08, unit08 = group.get_signal_with_unit("AEBS1_AEBSState_2A")
    client00.addSignal2Axis(axis05, "AEBS1_AEBSState_2A", time08, value08, unit=unit08)
    return
