# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis
def_param = interface.NullParam

sgs  = [
{
  "sensor_blind_detected": ("General_radar_status", "sensor_blind_detected"),
  "sensor_blindness": ("General_radar_status", "sensor_blindness"),
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
    time00, value00, unit00 = group.get_signal_with_unit("sensor_blind_detected")
    client00.addSignal2Axis(axis00, "sensor_blind_detected", time00, value00, unit=unit00)
    axis01 = client00.addAxis()
    time01, value01, unit01 = group.get_signal_with_unit("sensor_blindness")
    client00.addSignal2Axis(axis01, "sensor_blindness", time01, value01, unit=unit01)
    return
