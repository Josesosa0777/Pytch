# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis
def_param = interface.NullParam

sgs  = [
{
  "DM1_AmberWarnLStat_2A": ("DM1_2A", "DM1_AmberWarnLStat_2A"),
  "FLR_ErrorStatus": ("PropWarn", "FLR_ErrorStatus"),
  "ActiveFault04": ("ACC_S02", "ActiveFault04"),
  "ActiveFault03": ("ACC_S02", "ActiveFault03"),
  "ActiveFault02": ("ACC_S02", "ActiveFault02"),
  "ActiveFault01": ("ACC_S02", "ActiveFault01"),
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
    time00, value00, unit00 = group.get_signal_with_unit("FLR_ErrorStatus")
    client00.addSignal2Axis(axis00, "FLR_ErrorStatus", time00, value00, unit=unit00)
    axis01 = client00.addAxis()
    time01, value01, unit01 = group.get_signal_with_unit("DM1_AmberWarnLStat_2A")
    client00.addSignal2Axis(axis01, "DM1_AmberWarnLStat_2A", time01, value01, unit=unit01)
    axis02 = client00.addAxis()
    time02, value02, unit02 = group.get_signal_with_unit("ActiveFault01")
    client00.addSignal2Axis(axis02, "ActiveFault01", time02, value02, unit=unit02)
    time03, value03, unit03 = group.get_signal_with_unit("ActiveFault02")
    client00.addSignal2Axis(axis02, "ActiveFault02", time03, value03, unit=unit03)
    time04, value04, unit04 = group.get_signal_with_unit("ActiveFault03")
    client00.addSignal2Axis(axis02, "ActiveFault03", time04, value04, unit=unit04)
    time05, value05, unit05 = group.get_signal_with_unit("ActiveFault04")
    client00.addSignal2Axis(axis02, "ActiveFault04", time05, value05, unit=unit05)
    return
