# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import interface
import datavis
from aebs_c import AEBS_C_wrapper
import numpy as np

sgsccp  = [
{
  "dxv": ("CCP", "kbaebsInaebs.dxv"),
  "vRef": ("CCP", "kbaebsInaebs.vRef"),
  "vxv": ("CCP", "kbaebsInaebs.vxv"),
  "aRef": ("CCP", "kbaebsInaebs.aRef"),
  "axv": ("CCP", "kbaebsInaebs.axv"),
  "dyv": ("CCP", "kbaebsInaebs.dyv"),
  "vyv": ("CCP", "kbaebsInaebs.vyv"),
},
]
sgs  = [
{
  "dxv": ("kbaebsInput", "dxv"),
  "vRef": ("kbaebsInput", "vRef"),
  "vxv": ("kbaebsInput", "vxv"),
  "aRef": ("kbaebsInput", "aRef"),
  "axv": ("kbaebsInput", "axv"),
  "dyv": ("kbaebsInput", "dyv"),
  "vyv": ("kbaebsInput", "vyv"),
},
]

class View(interface.iView):

  def check(self):
    self.ccp_available = "vRef" in self.source.selectSignalGroupOrNone(sgsccp)
    if self.ccp_available:
      group = self.source.selectSignalGroup(sgsccp)
    else:
      group = self.source.selectSignalGroup(sgs)
    return group

  def fill(self, group):
    return group

  def view(self, group):
    inp = {}
    for name in group:
      value = group.get_value(name)
      if (name in AEBS_C_wrapper.kbaebsInputSt_t_norms) and self.ccp_available:
        value = AEBS_C_wrapper.FixedPointArray(value, name).float_value
      inp[name] = value
    client00 = datavis.cPlotNavigator(title="")
    self.sync.addClient(client00)
    axis00 = client00.addAxis()
    time00, value00, unit00 = group.get_signal_with_unit("dxv")
    mask = inp["dxv"] > 255.0
    inp["dxv"] = np.ma.masked_array(inp["dxv"], mask=mask)
    client00.addSignal2Axis(axis00, "dxv", time00, inp["dxv"], unit="m")
    axis01 = client00.addAxis()
    time01, value01, unit01 = group.get_signal_with_unit("vRef")
    client00.addSignal2Axis(axis01, "vRef", time01, inp["vRef"]*3.6, unit="kph")
    inp["vxv"] = np.ma.masked_array(inp["vxv"], mask=mask)
    time02, value02, unit02 = group.get_signal_with_unit("vxv")
    client00.addSignal2Axis(axis01, "vxv", time02, inp["vxv"]*3.6, unit="kph")
    axis02 = client00.addAxis()
    time03, value03, unit03 = group.get_signal_with_unit("aRef")
    client00.addSignal2Axis(axis02, "aRef", time03, inp["aRef"], unit="m/s2")
    inp["axv"] = np.ma.masked_array(inp["axv"], mask=mask)
    time04, value04, unit04 = group.get_signal_with_unit("axv")
    client00.addSignal2Axis(axis02, "axv", time04, inp["axv"], unit="m/s2")
    axis03 = client00.addAxis()
    inp["dyv"] = np.ma.masked_array(inp["dyv"], mask=mask)
    time05, value05, unit05 = group.get_signal_with_unit("dyv")
    client00.addSignal2Axis(axis03, "dyv", time05, inp["dyv"], unit="m")
    axis03 = client00.addTwinAxis(axis03)
    inp["vyv"] = np.ma.masked_array(inp["vyv"], mask=mask)
    time06, value06, unit06 = group.get_signal_with_unit("vyv")
    client00.addSignal2Axis(axis03, "vyv", time06, inp["vyv"]*3.6, unit="kph", color = 'g')
    return
