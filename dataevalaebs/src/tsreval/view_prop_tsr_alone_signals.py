# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import numpy as np
import datavis

sgs  = [
  {
    "TSR_SpeedLimit1_E8_sE8": ("PropTSRAlone_E8", "TSR_SpeedLimit1_E8_sE8"),
    "TSR_SpeedLimit1Supplementary_E8_sE8": ("PropTSRAlone_E8", "TSR_SpeedLimit1Supplementary_E8_sE8"),
    "TSR_SpeedLimit2_E8_sE8": ("PropTSRAlone_E8", "TSR_SpeedLimit2_E8_sE8"),
    "TSR_SpeedLimitElectronic_E8_sE8": ("PropTSRAlone_E8", "TSR_SpeedLimitElectronic_E8_sE8"),
    "TSR_NoPassingRestriction_E8_sE8": ("PropTSRAlone_E8", "TSR_NoPassingRestriction_E8_sE8"),
    "TSR_CountryCode_E8_sE8": ("PropTSRAlone_E8","TSR_CountryCode_E8_sE8"),
  }
]

class View(interface.iView):
  def check(self):
    group = self.source.selectSignalGroup(sgs)
    return group

  def fill(self, group):
    return group

  def view(self, group):
    pn = datavis.cPlotNavigator(title="PropTSRAlone Signal Data")
    self.sync.addClient(pn )
    axis00 = pn.addAxis(ylabel="PropTSRAlone Signal", )
    if 'TSR_SpeedLimit1_E8_sE8' in group:
      time_AutoHighLowBeamControl, value_AutoHighLowBeamControl = group.get_signal("TSR_SpeedLimit1_E8_sE8")
      pn.addSignal2Axis(axis00, "SpeedLimit1", time_AutoHighLowBeamControl, value_AutoHighLowBeamControl,linewidth=1.5, )
    else:
      print("Missing Signal: TSR_SpeedLimit1_E8_sE8")

    if 'TSR_SpeedLimit1Supplementary_E8_sE8' in group:
      time_TSSCurrentRegion, value_TSSCurrentRegion = group.get_signal("TSR_SpeedLimit1Supplementary_E8_sE8")
      pn.addSignal2Axis(axis00, "SpeedLimit1Supplementary", time_TSSCurrentRegion, value_TSSCurrentRegion,linewidth=1.5, )
    else:
      print("Missing Signal: TSR_SpeedLimit1Supplementary_E8_sE8")

    if 'TSR_SpeedLimit2_E8_sE8' in group:
      time_TSSDetectedStatus, value_TSSDetectedStatus = group.get_signal("TSR_SpeedLimit2_E8_sE8")
      pn.addSignal2Axis(axis00, "SpeedLimit2", time_TSSDetectedStatus, value_TSSDetectedStatus, linewidth=1.5, )
    else:
      print("Missing Signal: TSR_SpeedLimit2_E8_sE8")

    if 'TSR_SpeedLimitElectronic_E8_sE8' in group:
      time_TSSDetectedUoM, value_TSSDetectedUoM = group.get_signal("TSR_SpeedLimitElectronic_E8_sE8")
      pn.addSignal2Axis(axis00, "SpeedLimitElectronic", time_TSSDetectedUoM, value_TSSDetectedUoM,linewidth=1.5, )
    else:
      print("Missing Signal: TSR_SpeedLimitElectronic_E8_sE8")

    if 'TSR_NoPassingRestriction_E8_sE8' in group:
      time_TSSDetectedValue, value_TSSDetectedValue = group.get_signal("TSR_NoPassingRestriction_E8_sE8")
      pn.addSignal2Axis(axis00, "NoPassingRestriction", time_TSSDetectedValue, value_TSSDetectedValue, linewidth=1.5, )
    else:
      print("Missing Signal: TSR_NoPassingRestriction_E8_sE8")

    if 'TSR_CountryCode_E8_sE8' in group:
      time_TSSDetectedValue, value_TSSDetectedValue = group.get_signal("TSR_CountryCode_E8_sE8")
      pn.addSignal2Axis(axis00, "CountryCode", time_TSSDetectedValue, value_TSSDetectedValue,
                        linewidth=1.5, )
    else:
      print("Missing Signal: TSR_CountryCode_E8_sE8")

    return
