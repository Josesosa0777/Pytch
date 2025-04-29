# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis
def_param = interface.NullParam

sgs   = [
{
  "EEC1_SACtrlDeviceEngCntrl_00": ("EEC1_00", "EEC1_SACtrlDeviceEngCntrl_00"),
  "TSC1_RegSpeedConditions_0B_00": ("TSC1_0B_00", "TSC1_RegSpeedConditions_0B_00"),
  "TSC1_ControlPurpose_0B_00": ("TSC1_0B_00", "TSC1_ControlPurpose_0B_00"),
  "XBRUS_TSC1TorqueLimit_2A": ("XBRUS_2A", "XBRUS_TSC1TorqueLimit_2A"),
  "EEC1_DrivDemPercTrq_00": ("EEC1_00", "EEC1_DrivDemPercTrq_00"),
  "EEC1_ActEngPercTrq_00": ("EEC1_00", "EEC1_ActEngPercTrq_00"),
  "TSC1_ReqTorqueLimit_0B_00": ("TSC1_0B_00", "TSC1_ReqTorqueLimit_0B_00"),
  "TSC1_Priority_0B_00": ("TSC1_0B_00", "TSC1_Priority_0B_00"),
  "TSC1_OverrideControlMode_0B_00": ("TSC1_0B_00", "TSC1_OverrideControlMode_0B_00"),
  "XBRUS_TSC1StartStop_2A": ("XBRUS_2A", "XBRUS_TSC1StartStop_2A"),
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
    time00, value00, unit00 = group.get_signal_with_unit("XBRUS_TSC1TorqueLimit_2A")
    client00.addSignal2Axis(axis00, "XBRUS_TSC1TorqueLimit_2A", time00, value00, unit=unit00)
    time01, value01, unit01 = group.get_signal_with_unit("EEC1_ActEngPercTrq_00")
    client00.addSignal2Axis(axis00, "EEC1_ActEngPercTrq_00", time01, value01, unit=unit01)
    time02, value02, unit02 = group.get_signal_with_unit("EEC1_DrivDemPercTrq_00")
    client00.addSignal2Axis(axis00, "EEC1_DrivDemPercTrq_00", time02, value02, unit=unit02)
    time03, value03, unit03 = group.get_signal_with_unit("TSC1_ReqTorqueLimit_0B_00")
    client00.addSignal2Axis(axis00, "TSC1_ReqTorqueLimit_0B_00", time03, value03, unit=unit03)
    axis01 = client00.addAxis()
    time04, value04, unit04 = group.get_signal_with_unit("EEC1_SACtrlDeviceEngCntrl_00")
    client00.addSignal2Axis(axis01, "EEC1_SACtrlDeviceEngCntrl_00", time04, value04, unit=unit04)
    axis02 = client00.addAxis()
    time05, value05, unit05 = group.get_signal_with_unit("TSC1_OverrideControlMode_0B_00")
    client00.addSignal2Axis(axis02, "TSC1_OverrideControlMode_0B_00", time05, value05, unit=unit05)
    axis03 = client00.addAxis()
    time06, value06, unit06 = group.get_signal_with_unit("TSC1_RegSpeedConditions_0B_00")
    client00.addSignal2Axis(axis03, "TSC1_RegSpeedConditions_0B_00", time06, value06, unit=unit06)
    axis04 = client00.addAxis()
    time07, value07, unit07 = group.get_signal_with_unit("TSC1_Priority_0B_00")
    client00.addSignal2Axis(axis04, "TSC1_Priority_0B_00", time07, value07, unit=unit07)
    axis05 = client00.addAxis()
    time08, value08, unit08 = group.get_signal_with_unit("TSC1_ControlPurpose_0B_00")
    client00.addSignal2Axis(axis05, "TSC1_ControlPurpose_0B_00", time08, value08, unit=unit08)
    axis06 = client00.addAxis()
    time10, value10, unit10 = group.get_signal_with_unit("XBRUS_TSC1StartStop_2A")
    client00.addSignal2Axis(axis06, "XBRUS_TSC1StartStop_2A", time10, value10, unit=unit10)
    return
