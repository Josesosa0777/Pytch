# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis
def_param = interface.NullParam

sgs     = [
{
  "tracking_in_Azimuth": ("TA", "tracking_in_Azimuth"),
  "Azimuth_3": ("MB79_TARGET_DETECTION_3B", "Azimuth_3"),
  "Azimuth_1": ("MB79_TARGET_DETECTION_1B", "Azimuth_1"),
  "Azimuth_5": ("MB79_TARGET_DETECTION_5B", "Azimuth_5"),
},
]

class View(interface.iView):
  def check(self):
    group = self.source.selectSignalGroupOrEmpty(sgs)
    return group

  def fill(self, group):
    return group

  def view(self, param, group):
    client00 = datavis.cPlotNavigator(title="MB79 detection azimuth")
    self.sync.addClient(client00)
    axis00 = client00.addAxis()
    time00, value00, unit00 = group.get_signal_with_unit("Azimuth_1")
    client00.addSignal2Axis(axis00, "Azimuth_1", time00, value00, unit=unit00)
    time01, value01, unit01 = group.get_signal_with_unit("tracking_in_Azimuth")
    client00.addSignal2Axis(axis00, "tracking_in_Azimuth_1", time01, value01[:,0], unit=unit01)
    axis01 = client00.addAxis()
    time02, value02, unit02 = group.get_signal_with_unit("Azimuth_3")
    client00.addSignal2Axis(axis01, "Azimuth_3", time02, value02, unit=unit02)
    client00.addSignal2Axis(axis01, "tracking_in_Azimuth_3", time01, value01[:,1], unit=unit01)
    axis02 = client00.addAxis()
    time03, value03, unit03 = group.get_signal_with_unit("Azimuth_5")
    client00.addSignal2Axis(axis02, "Azimuth_5", time03, value03, unit=unit03)
    client00.addSignal2Axis(axis02, "tracking_in_Azimuth_5", time01, value01[:,2], unit=unit01)
    return
