# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

from measparser import signalproc
import interface
import datavis
import numpy as np
from aebs_c import AEBS_C_wrapper #= imp.load_dynamic('AEBS_C_wrapper', r'C:\KBData\Sandboxes\aebs_c\cython\release\AEBS_C_wrapper.pyd')
def_param = interface.NullParam

sgs  = [
{
  "AccAccelDemand": ("CCP", "kbaebsInaebs.AccAccelDemand"),
  "AccAccelDemandMin": ("CCP", "kbaebsInaebs.AccAccelDemandMin"),
  "AccInControl_b": ("CCP", "kbaebsInaebs.AccInControl_b"),
  "AccObjectIsSame_b": ("CCP", "kbaebsInaebs.AccObjectIsSame_b"),
  "AdditionalSensorAssociated_b": ("CCP", "kbaebsInaebs.AdditionalSensorAssociated_b"),
  "BPAct_b": ("CCP", "kbaebsInaebs.BPAct_b"),
  "BPPos": ("CCP", "kbaebsInaebs.BPPos"),
  "CMAllowEntry_b": ("CCP", "kbaebsInaebs.CMAllowEntry_b"),
  "CMBAllowEntry_b": ("CCP", "kbaebsInaebs.CMBAllowEntry_b"),
  "CMBCancel_b": ("CCP", "kbaebsInaebs.CMBCancel_b"),
  "CMCancel_b": ("CCP", "kbaebsInaebs.CMCancel_b"),
  "CWAllowEntry_b": ("CCP", "kbaebsInaebs.CWAllowEntry_b"),
  "CWCancel_b": ("CCP", "kbaebsInaebs.CWCancel_b"),
  "ControlledIrrevOffRaised_b": ("CCP", "kbaebsInaebs.ControlledIrrevOffRaised_b"),
  "ControlledRevOffRaised_b": ("CCP", "kbaebsInaebs.ControlledRevOffRaised_b"),
  "DirIndL_b": ("CCP", "kbaebsInaebs.DirIndL_b"),
  "DirIndR_b": ("CCP", "kbaebsInaebs.DirIndR_b"),
  "DriveInvDir_b": ("CCP", "kbaebsInaebs.DriveInvDir_b"),
  "Drive_b": ("CCP", "kbaebsInaebs.Drive_b"),
  "DriverActivationDemand_b": ("CCP", "kbaebsInaebs.DriverActivationDemand_b"),
  "EngineSpeed": ("CCP", "kbaebsInaebs.EngineSpeed"),
  "FusionOperational_b": ("CCP", "kbaebsInaebs.FusionOperational_b"),
  "GPKickdown_B": ("CCP", "kbaebsInaebs.GPKickdown_B"),
  "GPPos": ("CCP", "kbaebsInaebs.GPPos"),
  "ReverseGearDetected_b": ("CCP", "kbaebsInaebs.ReverseGearDetected_b"),
  "PlatformReady_b": ("CCP", "kbaebsInaebs.PlatformReady_b"),
  "NotClassified_b": ("CCP", "kbaebsInaebs.NotClassified_b"),
  "Stand_b": ("CCP", "kbaebsInaebs.Stand_b"),
  "StoppedInvDir_b": ("CCP", "kbaebsInaebs.StoppedInvDir_b"),
  "Stopped_b": ("CCP", "kbaebsInaebs.Stopped_b"),
  
  "Valid_b": ("CCP", "kbaebsInaebs.Valid_b"),
  "aRef": ("CCP", "kbaebsInaebs.aRef"),
  "axv": ("CCP", "kbaebsInaebs.axv"),
  "vRef": ("CCP", "kbaebsInaebs.vRef"),
  "vxv": ("CCP", "kbaebsInaebs.vxv"),
  "vyv": ("CCP", "kbaebsInaebs.vyv"),
  "dt": ("CCP", "kbaebsInaebs.dt"),
  "dxv": ("CCP", "kbaebsInaebs.dxv"),
  "dyv": ("CCP", "kbaebsInaebs.dyv"),
  "alpSteeringWheel": ("CCP", "kbaebsInaebs.alpSteeringWheel"),
},
]
sgs_resim = [
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
  "GPKickdown_B": ("kbaebsInput", "GPKickdown_B"),
  "GPPos": ("kbaebsInput", "GPPos"),
  "ReverseGearDetected_b": ("kbaebsInput", "ReverseGearDetected_b"),
  "PlatformReady_b": ("kbaebsInput", "PlatformReady_b"),
  "NotClassified_b": ("kbaebsInput", "NotClassified_b"),
  "Stand_b": ("kbaebsInput", "Stand_b"),
  "StoppedInvDir_b": ("kbaebsInput", "StoppedInvDir_b"),
  "Stopped_b": ("kbaebsInput", "Stopped_b"),
  
  "Valid_b": ("kbaebsInput", "Valid_b"),
  "aRef": ("kbaebsInput", "aRef"),
  "axv": ("kbaebsInput", "axv"),
  "vRef": ("kbaebsInput", "vRef"),
  "vxv": ("kbaebsInput", "vxv"),
  "vyv": ("kbaebsInput", "vyv"),
  "dt": ("kbaebsInput", "dt"),
  "dxv": ("kbaebsInput", "dxv"),
  "dyv": ("kbaebsInput", "dyv"),
  "alpSteeringWheel": ("kbaebsInput", "alpSteeringWheel"),
},
]
class View(interface.iView):
  channels = "main","resim"
  def check(self):
    group = self.get_source("main").selectSignalGroupOrEmpty(sgs)
    group_resim = self.get_source("resim").selectSignalGroupOrEmpty(sgs_resim)
    return group, group_resim

  def fill(self, group, group_resim):
    return group, group_resim

  def view(self, param, group, group_resim):
    title = "CCP vs resimulation inputs"
    
    for name in sgs[0]:
      pn = datavis.cPlotNavigator(title=title)
      self.sync.addClient(pn)
      axis = pn.addAxis()
      time, value, unit = group.get_signal_with_unit(name)
      time_resim, value_resim, unit_resim = group_resim.get_signal_with_unit(name)
      
      time_c = np.array(time) # create copy to avoid interference with cache
      time_c -= (time[0]-time_resim[0]) # offset compensation
      
      if name in AEBS_C_wrapper.kbaebsInputSt_t_norms:
        value = AEBS_C_wrapper.FixedPointArray(value, name).float_value #pn.addSignal2Axis(axis, name, time, AEBS_C_wrapper.FixedPointArray(value, name).float_value, unit=unit)
      pn.addSignal2Axis(axis, name, time_c, value, unit=unit)
      pn.addSignal2Axis(axis, name+" resim", time_resim, value_resim, unit=unit_resim)
      
      _, value_rescale = signalproc.rescale(time_c, value, time_resim)
      value_err = np.array(value_resim-value_rescale)
      axis = pn.addAxis()
      pn.addSignal2Axis(axis, name+" error", time_resim, value_err, unit=unit)
    #AEBS_C_wrapper.FixedPointArray(value, name).float_value
    return
