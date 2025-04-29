# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis
def_param = interface.NullParam

sgs  = [
{
  "covi": ("General_radar_status", "covi"),
  "SIB2_COVI_error": ("General_radar_status", "SIB2_COVI_error"),
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
    time00, value00, unit00 = group.get_signal_with_unit("SIB2_COVI_error")
    client00.addSignal2Axis(axis00, "SIB2_COVI_error", time00, value00, unit=unit00)
    axis01 = client00.addAxis()
    time01, value01, unit01 = group.get_signal_with_unit("covi")
    client00.addSignal2Axis(axis01, "covi", time01, value01, unit=unit01)
    return
