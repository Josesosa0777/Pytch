# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis
def_param = interface.NullParam

sgs  = [
{
  "FOV_count_left": ("General_radar_status", "FOV_count_left"),
  "SIB1_FOV_error": ("General_radar_status", "SIB1_FOV_error"),
  "FOV_count_centre": ("General_radar_status", "FOV_count_centre"),
  "FOV_count_right": ("General_radar_status", "FOV_count_right"),
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
    time00, value00, unit00 = group.get_signal_with_unit("FOV_count_left")
    client00.addSignal2Axis(axis00, "FOV_count_left", time00, value00, unit=unit00)
    axis01 = client00.addAxis()
    time01, value01, unit01 = group.get_signal_with_unit("FOV_count_centre")
    client00.addSignal2Axis(axis01, "FOV_count_centre", time01, value01, unit=unit01)
    axis02 = client00.addAxis()
    time02, value02, unit02 = group.get_signal_with_unit("FOV_count_right")
    client00.addSignal2Axis(axis02, "FOV_count_right", time02, value02, unit=unit02)
    axis03 = client00.addAxis()
    time03, value03, unit03 = group.get_signal_with_unit("SIB1_FOV_error")
    client00.addSignal2Axis(axis03, "SIB1_FOV_error", time03, value03, unit=unit03)
    return
