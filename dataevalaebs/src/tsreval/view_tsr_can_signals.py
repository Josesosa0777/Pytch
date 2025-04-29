# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import numpy as np
import datavis

sgs  = [
{
  "TSSCurrentRegion": ("FLC_PROP1_sE8", "TSSCurrentRegion"),
  "TSSLifeTime": ("FLC_PROP1_sE8", "TSSLifeTime"),
  "TSSDetectedUoM": ("FLC_PROP1_sE8", "TSSDetectedUoM"),
  "TSSDetectedStatus": ("FLC_PROP1_sE8", "TSSDetectedStatus"),
  "TSSOverspeedAlert": ("FLC_PROP1_sE8", "TSSOverspeedAlert"),
  "TSSDetectedValue": ("FLC_PROP1_sE8", "TSSDetectedValue"),
  "AutoHighLowBeamControl": ("FLC_PROP1_sE8", "AutoHighLowBeamControl"),
},
{
  "TSSCurrentRegion": ("FLC_PROP1_E8_sE8", "FLCProp1_TSSCurrentRegion_E8"),
  "TSSDetectedStatus": ("FLC_PROP1_E8_sE8", "FLCProp1_TSSDetectedStatus_E8"),
  "TSSDetectedUoM": ("FLC_PROP1_E8_sE8", "FLCProp1_TSSDetectedUoM_E8"),
  "TSSDetectedValue": ("FLC_PROP1_E8_sE8", "FLCProp1_TSSDetectedValue_E8"),
  "TSSLifeTime": ("FLC_PROP1_E8_sE8", "FLCProp1_TSSLifeTime_E8"),
  "TSSOverspeedAlert": ("FLC_PROP1_E8_sE8", "FLCProp1_TSSOverspeedAlert_E8"),
  "AutoHighLowBeamControl": ("FLC_PROP1_E8_sE8","FLCProp1_AutoHighLowBeamCtrl_E8"),
},
{
  "TSSCurrentRegion": ("FLC_PROP1","TSSCurrentRegion_sE8"),
  "TSSDetectedStatus": ("FLC_PROP1","TSSDetectedStatus_sE8"),
  "TSSDetectedUoM": ("FLC_PROP1","TSSDetectedUoM_sE8"),
  "TSSDetectedValue": ("FLC_PROP1","TSSDetectedValue_sE8"),
  "TSSLifeTime": ("FLC_PROP1","TSSLifeTime_sE8"),
  "TSSOverspeedAlert": ("FLC_PROP1","TSSOverspeedAlert_sE8"),
  "AutoHighLowBeamControl": ("FLC_PROP1","AutoHighLowBeamControl_sE8"),
},
  {
  "TSSCurrentRegion": ("FLC_PROP1_E8","FLCProp1_TSSCurrentRegion_E8_sE8"),
  "TSSDetectedStatus": ("FLC_PROP1_E8","FLCProp1_TSSDetectedStatus_E8_sE8"),
  "TSSDetectedUoM": ("FLC_PROP1_E8","FLCProp1_TSSDetectedUoM_E8_sE8"),
  "TSSDetectedValue": ("FLC_PROP1_E8","FLCProp1_TSSDetectedValue_E8_sE8"),
  "TSSLifeTime": ("FLC_PROP1_E8","FLCProp1_TSSLifeTime_E8_sE8"),
  "TSSOverspeedAlert": ("FLC_PROP1_E8","FLCProp1_TSSOverspeedAlert_E8_sE8"),
  "AutoHighLowBeamControl": ("FLC_PROP1_E8","FLCProp1_AutoHighLowBeamCtrl_E8_sE8"),
  },
]

class View(interface.iView):
  def check(self):
    group = self.source.selectSignalGroup(sgs)
    return group

  def fill(self, group):
    return group

  def view(self, group):
    client00 = datavis.cListNavigator(title="TSR CAN Data")
    self.sync.addClient(client00 )
    if 'AutoHighLowBeamControl' in group:
      time_AutoHighLowBeamControl, value_AutoHighLowBeamControl = group.get_signal("AutoHighLowBeamControl")
      client00.addsignal("AutoHighLowBeamControl", (time_AutoHighLowBeamControl, value_AutoHighLowBeamControl), groupname="Default")
    else:
      print("Missing Signal: AutoHighLowBeamControl")
    if 'TSSCurrentRegion' in group:
      time_TSSCurrentRegion, value_TSSCurrentRegion = group.get_signal("TSSCurrentRegion")
      client00.addsignal("TSSCurrentRegion", (time_TSSCurrentRegion, value_TSSCurrentRegion), groupname="Default")
    else:
      print("Missing Signal: TSSCurrentRegion")
    if 'TSSDetectedStatus' in group:
      time_TSSDetectedStatus, value_TSSDetectedStatus = group.get_signal("TSSDetectedStatus")
      client00.addsignal("TSSDetectedStatus", (time_TSSDetectedStatus, value_TSSDetectedStatus), groupname="Default")
    else:
      print("Missing Signal: TSSDetectedStatus")
    if 'TSSDetectedUoM' in group:
      time_TSSDetectedUoM, value_TSSDetectedUoM = group.get_signal("TSSDetectedUoM")
      client00.addsignal("TSSDetectedUoM", (time_TSSDetectedUoM, value_TSSDetectedUoM), groupname="Default")
    else:
      print("Missing Signal: TSSDetectedUoM")
    if 'TSSDetectedValue' in group:
      time_TSSDetectedValue, value_TSSDetectedValue = group.get_signal("TSSDetectedValue")
      client00.addsignal("TSSDetectedValue", (time_TSSDetectedValue, value_TSSDetectedValue), groupname="Default")
    else:
      print("Missing Signal: TSSDetectedValue")
    if 'TSSLifeTime' in group:
      time_TSSLifeTime, value_TSSLifeTime = group.get_signal("TSSLifeTime")
      client00.addsignal("TSSLifeTime", (time_TSSLifeTime, value_TSSLifeTime), groupname="Default")
    else:
      print("Missing Signal: TSSLifeTime")
    if 'TSSOverspeedAlert' in group:
      time_TSSOverspeedAlert, value_TSSOverspeedAlert = group.get_signal("TSSOverspeedAlert")
      client00.addsignal("TSSOverspeedAlert", (time_TSSOverspeedAlert, value_TSSOverspeedAlert), groupname="Default")
    else:
      print("Missing Signal: TSSOverspeedAlert")
    return
