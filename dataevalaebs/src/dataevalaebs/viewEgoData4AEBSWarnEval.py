import sys

import numpy

import datavis
import interface
from measparser.signalgroup import SignalGroupError

DefParam = interface.NullParam

deviceNames = "MRR1plus", "RadarFC", "ECU"

sensorSignalGroups = []
for device in deviceNames:
  sensorSignalGroup = {"vx_ego": (device, "evi.General_TC.vxvRef"),
                       "YR_ego": (device, "evi.General_TC.psiDtOpt")}
  sensorSignalGroups.append(sensorSignalGroup)
sensorSignalGroups.append({"vx_ego": ("General_radar_status", "actual_vehicle_speed"),
                           "YR_ego": ("General_radar_status", "cvd_yawrate")})

mrfSignalGroups = []
for device in deviceNames:
  mrfSignalGroup = {"Relevant.dxv": (device, "Mrf._.PssObjectDebugInfo.dxv")}
  mrfSignalGroups.append(mrfSignalGroup)
mrfSignalGroups.append({"Relevant.dxv": ("Tracks", "tr0_range")})
class cView(interface.iView):
  def check(self):
    sensorGroup = interface.Source.selectSignalGroup(sensorSignalGroups)
    return sensorGroup
    
  def fill(self, sensorGroup):
    return sensorGroup
  
  @classmethod
  def view(cls, Param, sensorGroup):
    try:
      mrfGroup = interface.Source.selectSignalGroup(mrfSignalGroups)
    except SignalGroupError:
      mrfGroup = None
    Client = datavis.cPlotNavigator(title="PN", figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis()
    Time, Value = interface.Source.getSignalFromSignalGroup(sensorGroup, "vx_ego")
    Client.addSignal2Axis(Axis, "vx_Ego", Time, 3.6*Value, unit="km/h")
    Axis = Client.addAxis()
    Time, Value = interface.Source.getSignalFromSignalGroup(sensorGroup, "YR_ego")
    # The yaw rate in AC100 General_radar_status is in deg/sec, should be converted to rad/sec!
    if interface.Source.getShortDeviceName(sensorGroup['YR_ego'][0]) == 'General_radar_status':
      print >> sys.stderr, "YR_ego in message General_radar_status converted to rad/sec"
      Value = Value * numpy.pi / 180.0
    Client.addSignal2Axis(Axis, "YR_Ego", Time, Value, unit='1/s')
    if mrfGroup is not None:  
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(mrfGroup, "Relevant.dxv")
      Unit = interface.Source.getPhysicalUnitFromSignalGroup(mrfGroup, "Relevant.dxv")
      Client.addSignal2Axis(Axis, "dx", Time, Value, unit=Unit)
  