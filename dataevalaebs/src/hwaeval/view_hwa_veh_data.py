# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis
def_param = interface.NullParam

sgs  = [
{
  "debug_CANin_TCO1_VehicleSpeed":            ("XCP_Test", "debug_CANin_TCO1_VehicleSpeed"),
  "debug_CANin_VDC2_LongitudinalAcc":         ("XCP_Test", "debug_CANin_VDC2_LongitudinalAcc"),
  "debug_CANin_ADMA_Misc_Distance_Travelled": ("XCP_Test", "debug_CANin_ADMA_Misc_Distance_Travelled"),
  "debug_CANin_VDC2_LateralAcceleration":     ("XCP_Test", "debug_CANin_VDC2_LateralAcceleration"),
  "debug_CANin_VDC2_YawRate":                 ("XCP_Test", "debug_CANin_VDC2_YawRate"),
  # alias: (devicename, signalname),
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
    time00, value00, unit00 = group.get_signal_with_unit("debug_CANin_ADMA_Misc_Distance_Travelled")
    client00.addSignal2Axis(axis00, "Travelled distance", time00, value00, unit=unit00)
    axis01 = client00.addAxis()
    time01, value01, unit01 = group.get_signal_with_unit("debug_CANin_VDC2_LateralAcceleration")
    client00.addSignal2Axis(axis01, "Lateral Acceleration", time01, value01, unit=unit01)
    time02, value02, unit02 = group.get_signal_with_unit("debug_CANin_VDC2_LongitudinalAcc")
    client00.addSignal2Axis(axis01, "Longitudinal Acceleration", time02, value02, unit=unit02)
    axis02 = client00.addAxis()
    time03, value03, unit03 = group.get_signal_with_unit("debug_CANin_VDC2_YawRate")
    client00.addSignal2Axis(axis02, "Yaw Rate", time03, value03, unit=unit03)
    axis03 = client00.addAxis()
    time04, value04, unit04 = group.get_signal_with_unit("debug_CANin_TCO1_VehicleSpeed")
    client00.addSignal2Axis(axis03, "Vehicle Speed", time04, value04, unit=unit04)
    return
