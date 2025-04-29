# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis
def_param = interface.NullParam

sgs  = [
{
  "CCVS_ClutchSwitch_00": ("CCVS1_00", "CCVS_ClutchSwitch_00"),
  "EEC1_EngSpd_00": ("EEC1_00", "EEC1_EngSpd_00"),
  "TSC1_OverrideControlMode_2A_00": ("TSC1_2A_00", "TSC1_OverrideControlMode_2A_00"),
  "TSC1_ControlPurpose_2A_00": ("TSC1_2A_00", "TSC1_ControlPurpose_2A_00"),
  "EEC1_DrivDemPercTrq_00": ("EEC1_00", "EEC1_DrivDemPercTrq_00"),
  "TSC1_ReqTorqueLimit_2A_00": ("TSC1_2A_00", "TSC1_ReqTorqueLimit_2A_00"),
  "EEC1_ActEngPercTrq_00": ("EEC1_00", "EEC1_ActEngPercTrq_00"),
  "EEC2_APPos1_00": ("EEC2_00", "EEC2_APPos1_00"),
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
    time00, value00, unit00 = group.get_signal_with_unit("TSC1_ReqTorqueLimit_2A_00")
    client00.addSignal2Axis(axis00, "TSC1_ReqTorqueLimit_2A_00", time00, value00, unit=unit00)
    axis01 = client00.addAxis()
    time01, value01, unit01 = group.get_signal_with_unit("TSC1_OverrideControlMode_2A_00")
    client00.addSignal2Axis(axis01, "TSC1_OverrideControlMode_2A_00", time01, value01, unit=unit01)
    time02, value02, unit02 = group.get_signal_with_unit("TSC1_ControlPurpose_2A_00")
    client00.addSignal2Axis(axis01, "TSC1_ControlPurpose_2A_00", time02, value02, unit=unit02)
    axis02 = client00.addAxis()
    time03, value03, unit03 = group.get_signal_with_unit("EEC1_ActEngPercTrq_00")
    client00.addSignal2Axis(axis02, "EEC1_ActEngPercTrq_00", time03, value03, unit=unit03)
    time04, value04, unit04 = group.get_signal_with_unit("EEC1_DrivDemPercTrq_00")
    client00.addSignal2Axis(axis02, "EEC1_DrivDemPercTrq_00", time04, value04, unit=unit04)
    axis03 = client00.addAxis()
    time05, value05, unit05 = group.get_signal_with_unit("CCVS_ClutchSwitch_00")
    client00.addSignal2Axis(axis03, "CCVS_ClutchSwitch_00", time05, value05, unit=unit05)
    axis04 = client00.addAxis()
    time06, value06, unit06 = group.get_signal_with_unit("EEC2_APPos1_00")
    client00.addSignal2Axis(axis04, "EEC2_APPos1_00", time06, value06, unit=unit06)
    axis05 = client00.addAxis()
    time07, value07, unit07 = group.get_signal_with_unit("EEC1_EngSpd_00")
    client00.addSignal2Axis(axis05, "EEC1_EngSpd_00", time07, value07, unit=unit07)
    return
