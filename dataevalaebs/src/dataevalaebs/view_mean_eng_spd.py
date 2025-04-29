# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis
def_param = interface.NullParam

sgs  = [
{
  "EBC2_MeanSpdFA_0B": ("EBC2_0B", "EBC2_MeanSpdFA_0B"),
  "EEC1_EngSpd_00": ("EEC1_00", "EEC1_EngSpd_00"),
},
]

class View(interface.iView):
  def check(self):
    group = self.source.selectSignalGroupOrEmpty(sgs)
    return group

  def fill(self, group):
    return group

  def view(self, param, group):
    client00 = datavis.cPlotNavigator(title="")
    self.sync.addClient(client00)
    axis00 = client00.addAxis()
    time00, value00, unit00 = group.get_signal_with_unit("EBC2_MeanSpdFA_0B")
    client00.addSignal2Axis(axis00, "EBC2_MeanSpdFA_0B", time00, value00, unit=unit00)
    client01 = datavis.cPlotNavigator(title="")
    self.sync.addClient(client01)
    axis01 = client01.addAxis()
    time01, value01, unit01 = group.get_signal_with_unit("EEC1_EngSpd_00")
    client01.addSignal2Axis(axis01, "EEC1_EngSpd_00", time01, value01, unit=unit01)
    return
