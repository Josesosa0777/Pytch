# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis
def_param = interface.NullParam

sgs  = [
{
  "EBC2_MeanSpdFA_0B": ("EBC2_0B", "EBC2_MeanSpdFA_0B"),
  "TSRSpeedLimit": ("PropWarn", "TSRSpeedLimit"),
  "XBRUS_TSC1TorqueLimit_2A": ("XBRUS_2A", "XBRUS_TSC1TorqueLimit_2A"),
  "TSR_Warning_Flag": ("PropWarn", "TSR_Warning_Flag"),
  "XBRUS_TSC1StartStop_2A": ("XBRUS_2A", "XBRUS_TSC1StartStop_2A"),
  "Speed_Sign_Life": ("Camera_Prop_Warn", "Speed_Sign_Life"),
  "Traffic_Sign_Type": ("Camera_Prop_State_E8", "Traffic_Sign_Type"),
  "NewSpeedSignDetected": ("Camera_Prop_Warn", "NewSpeedSignDetected"),
},
]

class View(interface.iView):
  def check(self):
    group = self.source.selectSignalGroup(sgs)
    return group

  def fill(self, group):
    return group

  def view(self, param, group):
    view_client = datavis.cPlotNavigator(title="TSR Warning", figureNr=None)

    axis00 = view_client.addAxis(ylim=(-5.0, 95.0))
    time00, value00, unit00 = group.get_signal_with_unit("TSRSpeedLimit")
    view_client.addSignal2Axis(axis00, "TSRSpeedLimit", time00, value00, unit=unit00)
    time01, value01, unit01 = group.get_signal_with_unit("EBC2_MeanSpdFA_0B")
    view_client.addSignal2Axis(axis00, "EBC2_MeanSpdFA_0B", time01, value01, unit=unit01)

    axis01 = view_client.addAxis()
    time02, value02, unit02 = group.get_signal_with_unit("TSR_Warning_Flag")
    view_client.addSignal2Axis(axis01, "TSR_Warning_Flag", time02, value02, unit=unit02)
    time03, value03, unit03 = group.get_signal_with_unit("NewSpeedSignDetected")
    view_client.addSignal2Axis(axis01, "NewSpeedSignDetected", time03, value03, unit=unit03)

    axis02 = view_client.addAxis()
    time04, value04, unit04 = group.get_signal_with_unit("Traffic_Sign_Type")
    view_client.addSignal2Axis(axis02, "Traffic_Sign_Type", time04, value04, unit=unit04)

    axis03 = view_client.addAxis()
    time05, value05, unit05 = group.get_signal_with_unit("Speed_Sign_Life")
    view_client.addSignal2Axis(axis03, "Speed_Sign_Life", time05, value05, unit=unit05)

    axis04 = view_client.addAxis()
    time06, value06, unit06 = group.get_signal_with_unit("XBRUS_TSC1StartStop_2A")
    view_client.addSignal2Axis(axis04, "XBRUS_TSC1StartStop_2A", time06, value06, unit=unit06)
    time07, value07, unit07 = group.get_signal_with_unit("XBRUS_TSC1TorqueLimit_2A")
    view_client.addSignal2Axis(axis04, "XBRUS_TSC1TorqueLimit_2A", time07, value07, unit=unit07)
    
    self.sync.addClient(view_client)
    return
