# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis
def_param = interface.NullParam

sgs  = [
{
  "AccAccelDemand": ("kbaebsInput", "AccAccelDemand"),
  "AccAccelDemandMin": ("kbaebsInput", "AccAccelDemandMin"),
  "AccInControl_b": ("kbaebsInput", "AccInControl_b"),
  "AccObjectIsSame_b": ("kbaebsInput", "AccObjectIsSame_b"),
  "AdditionalSensorAssociated_b": ("kbaebsInput", "AdditionalSensorAssociated_b"),
  "BPAct_b": ("kbaebsInput", "BPAct_b"),
  "BPPos": ("kbaebsInput", "BPPos"),
  "CMAllowEntry_b": ("kbaebsInput", "CMAllowEntry_b"),
  "CMBAllowEntry_b": ("kbaebsInput", "CMBAllowEntry_b"),
  "CMBCancel_b": ("kbaebsInput", "CMBCancel_b"),
  "CMCancel_b": ("kbaebsInput", "CMCancel_b"),
  "CWAllowEntry_b": ("kbaebsInput", "CWAllowEntry_b"),
  "CWCancel_b": ("kbaebsInput", "CWCancel_b"),
  "ControlledIrrevOffRaised_b": ("kbaebsInput", "ControlledIrrevOffRaised_b"),
  "ControlledRevOffRaised_b": ("kbaebsInput", "ControlledRevOffRaised_b"),
  "DirIndL_b": ("kbaebsInput", "DirIndL_b"),
  "DirIndR_b": ("kbaebsInput", "DirIndR_b"),
  "DriveInvDir_b": ("kbaebsInput", "DriveInvDir_b"),
  "Drive_b": ("kbaebsInput", "Drive_b"),
  "DriverActivationDemand_b": ("kbaebsInput", "DriverActivationDemand_b"),
  "EngineSpeed": ("kbaebsInput", "EngineSpeed"),
  "FusionOperational_b": ("kbaebsInput", "FusionOperational_b"),
  "ReverseGearDetected_b": ("kbaebsInput", "ReverseGearDetected_b"),
  "PlatformReady_b": ("kbaebsInput", "PlatformReady_b"),
  "NotClassified_b": ("kbaebsInput", "NotClassified_b"),
  "Stand_b": ("kbaebsInput", "Stand_b"),
  "StoppedInvDir_b": ("kbaebsInput", "StoppedInvDir_b"),
  "Stopped_b": ("kbaebsInput", "Stopped_b"),
  "TORSitSubjective_b": ("kbaebsInput", "TORSitSubjective_b"),
  "Valid_b": ("kbaebsInput", "Valid_b"),
  "aRef": ("kbaebsInput", "aRef"),
  "axv": ("kbaebsInput", "axv"),
  "vRef": ("kbaebsInput", "vRef"),
  "vxv": ("kbaebsInput", "vxv"),
  "vyv": ("kbaebsInput", "vyv"),
  "dt": ("kbaebsInput", "dt"),
  "dxv": ("kbaebsInput", "dxv"),
  "dyv": ("kbaebsInput", "dyv"),
  "t": ("kbaebsInput", "t"),
  "alpSteeringWheel": ("kbaebsInput", "alpSteeringWheel"),
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
    time00, value00, unit00 = group.get_signal_with_unit("AccAccelDemand")
    client00.addSignal2Axis(axis00, "AccAccelDemand", time00, value00, unit=unit00)
    time01, value01, unit01 = group.get_signal_with_unit("AccAccelDemandMin")
    client00.addSignal2Axis(axis00, "AccAccelDemandMin", time01, value01, unit=unit01)
    axis01 = client00.addAxis()
    time02, value02, unit02 = group.get_signal_with_unit("AccInControl_b")
    client00.addSignal2Axis(axis01, "AccInControl_b", time02, value02, unit=unit02)
    time03, value03, unit03 = group.get_signal_with_unit("AccObjectIsSame_b")
    client00.addSignal2Axis(axis01, "AccObjectIsSame_b", time03, value03, unit=unit03)
    time04, value04, unit04 = group.get_signal_with_unit("AdditionalSensorAssociated_b")
    client00.addSignal2Axis(axis01, "AdditionalSensorAssociated_b", time04, value04, unit=unit04)
    axis02 = client00.addAxis()
    time05, value05, unit05 = group.get_signal_with_unit("BPAct_b")
    client00.addSignal2Axis(axis02, "BPAct_b", time05, value05, unit=unit05)
    time06, value06, unit06 = group.get_signal_with_unit("BPPos")
    client00.addSignal2Axis(axis02, "BPPos", time06, value06, unit=unit06)
    axis03 = client00.addAxis()
    time07, value07, unit07 = group.get_signal_with_unit("CMAllowEntry_b")
    client00.addSignal2Axis(axis03, "CMAllowEntry_b", time07, value07, unit=unit07)
    time08, value08, unit08 = group.get_signal_with_unit("CMBAllowEntry_b")
    client00.addSignal2Axis(axis03, "CMBAllowEntry_b", time08, value08, unit=unit08)
    time09, value09, unit09 = group.get_signal_with_unit("CMBCancel_b")
    client00.addSignal2Axis(axis03, "CMBCancel_b", time09, value09, unit=unit09)
    time10, value10, unit10 = group.get_signal_with_unit("CMCancel_b")
    client00.addSignal2Axis(axis03, "CMCancel_b", time10, value10, unit=unit10)
    time11, value11, unit11 = group.get_signal_with_unit("CWAllowEntry_b")
    client00.addSignal2Axis(axis03, "CWAllowEntry_b", time11, value11, unit=unit11)
    time12, value12, unit12 = group.get_signal_with_unit("CWCancel_b")
    client00.addSignal2Axis(axis03, "CWCancel_b", time12, value12, unit=unit12)
    time13, value13, unit13 = group.get_signal_with_unit("ControlledIrrevOffRaised_b")
    client00.addSignal2Axis(axis03, "ControlledIrrevOffRaised_b", time13, value13, unit=unit13)
    time14, value14, unit14 = group.get_signal_with_unit("ControlledRevOffRaised_b")
    client00.addSignal2Axis(axis03, "ControlledRevOffRaised_b", time14, value14, unit=unit14)
    axis04 = client00.addAxis()
    time15, value15, unit15 = group.get_signal_with_unit("DirIndL_b")
    client00.addSignal2Axis(axis04, "DirIndL_b", time15, value15, unit=unit15)
    time16, value16, unit16 = group.get_signal_with_unit("DirIndR_b")
    client00.addSignal2Axis(axis04, "DirIndR_b", time16, value16, unit=unit16)
    time17, value17, unit17 = group.get_signal_with_unit("DriveInvDir_b")
    client00.addSignal2Axis(axis04, "DriveInvDir_b", time17, value17, unit=unit17)
    time18, value18, unit18 = group.get_signal_with_unit("Drive_b")
    client00.addSignal2Axis(axis04, "Drive_b", time18, value18, unit=unit18)
    time19, value19, unit19 = group.get_signal_with_unit("DriverActivationDemand_b")
    client00.addSignal2Axis(axis04, "DriverActivationDemand_b", time19, value19, unit=unit19)
    axis05 = client00.addAxis()
    time20, value20, unit20 = group.get_signal_with_unit("EngineSpeed")
    client00.addSignal2Axis(axis05, "EngineSpeed", time20, value20, unit=unit20)
    time21, value21, unit21 = group.get_signal_with_unit("FusionOperational_b")
    client00.addSignal2Axis(axis05, "FusionOperational_b", time21, value21, unit=unit21)
    time22, value22, unit22 = group.get_signal_with_unit("ReverseGearDetected_b")
    client00.addSignal2Axis(axis05, "ReverseGearDetected_b", time22, value22, unit=unit22)
    time23, value23, unit23 = group.get_signal_with_unit("PlatformReady_b")
    client00.addSignal2Axis(axis05, "PlatformReady_b", time23, value23, unit=unit23)
    axis06 = client00.addAxis()
    time24, value24, unit24 = group.get_signal_with_unit("NotClassified_b")
    client00.addSignal2Axis(axis06, "NotClassified_b", time24, value24, unit=unit24)
    time25, value25, unit25 = group.get_signal_with_unit("Stand_b")
    client00.addSignal2Axis(axis06, "Stand_b", time25, value25, unit=unit25)
    time26, value26, unit26 = group.get_signal_with_unit("StoppedInvDir_b")
    client00.addSignal2Axis(axis06, "StoppedInvDir_b", time26, value26, unit=unit26)
    time27, value27, unit27 = group.get_signal_with_unit("Stopped_b")
    client00.addSignal2Axis(axis06, "Stopped_b", time27, value27, unit=unit27)
    time28, value28, unit28 = group.get_signal_with_unit("TORSitSubjective_b")
    client00.addSignal2Axis(axis06, "TORSitSubjective_b", time28, value28, unit=unit28)
    time29, value29, unit29 = group.get_signal_with_unit("Valid_b")
    client00.addSignal2Axis(axis06, "Valid_b", time29, value29, unit=unit29)
    axis07 = client00.addAxis()
    time30, value30, unit30 = group.get_signal_with_unit("aRef")
    client00.addSignal2Axis(axis07, "aRef", time30, value30, unit=unit30)
    time31, value31, unit31 = group.get_signal_with_unit("axv")
    client00.addSignal2Axis(axis07, "axv", time31, value31, unit=unit31)
    time32, value32, unit32 = group.get_signal_with_unit("vRef")
    client00.addSignal2Axis(axis07, "vRef", time32, value32, unit=unit32)
    time33, value33, unit33 = group.get_signal_with_unit("vxv")
    client00.addSignal2Axis(axis07, "vxv", time33, value33, unit=unit33)
    time34, value34, unit34 = group.get_signal_with_unit("vyv")
    client00.addSignal2Axis(axis07, "vyv", time34, value34, unit=unit34)
    axis08 = client00.addAxis()
    time35, value35, unit35 = group.get_signal_with_unit("dt")
    client00.addSignal2Axis(axis08, "dt", time35, value35, unit=unit35)
    time36, value36, unit36 = group.get_signal_with_unit("dxv")
    client00.addSignal2Axis(axis08, "dxv", time36, value36, unit=unit36)
    time37, value37, unit37 = group.get_signal_with_unit("dyv")
    client00.addSignal2Axis(axis08, "dyv", time37, value37, unit=unit37)
    time38, value38, unit38 = group.get_signal_with_unit("t")
    client00.addSignal2Axis(axis08, "t", time38, value38, unit=unit38)
    axis09 = client00.addAxis()
    time39, value39, unit39 = group.get_signal_with_unit("alpSteeringWheel")
    client00.addSignal2Axis(axis09, "alpSteeringWheel", time39, value39, unit=unit39)
    return
