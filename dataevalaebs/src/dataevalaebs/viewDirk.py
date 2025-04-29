# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis
def_param = interface.NullParam

sgs   = [
{
  "DFM_red_button": ("DIRK", "DFM_red_button"),
  "DFM_green_button": ("DIRK", "DFM_green_button"),
  "DFM_Cnt_red_button": ("DIRK", "DFM_Cnt_red_button"),
  "DFM_Cnt_green_button": ("DIRK", "DFM_Cnt_green_button"),
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
    axis00 = client00.addAxis(ylim=(-1.0,4.0))
    time00, value00, unit00 = group.get_signal_with_unit("DFM_green_button")
    client00.addSignal2Axis(axis00, "DFM_green_button", time00, value00, unit=unit00, color="g")
    time01, value01, unit01 = group.get_signal_with_unit("DFM_red_button")
    client00.addSignal2Axis(axis00, "DFM_red_button", time01, value01, unit=unit01, color="r")
    axis01 = client00.addAxis()
    time02, value02, unit02 = group.get_signal_with_unit("DFM_Cnt_green_button")
    client00.addSignal2Axis(axis01, "DFM_Cnt_green_button", time02, value02, unit=unit02, color="g")
    time03, value03, unit03 = group.get_signal_with_unit("DFM_Cnt_red_button")
    client00.addSignal2Axis(axis01, "DFM_Cnt_red_button", time03, value03, unit=unit03, color="r")
    return
