"""
:Organization: Knorr-Bremse SfN GmbH T/CES3.2 (BU2) Budapest Schwieberdingen T/CES3.2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""
import datavis
import measparser
import interface

DefParam = interface.NullParam

SignalGroups = [{"BrakePedalPosition": ("EBC1", "BrakePedalPosition"),
                 "Dam_x._.InitialDriverOverride_b": ("ECU", "Dam_x._.InitialDriverOverride_b"),
                 "EBSBrakeSwitch": ("EBC1", "EBSBrakeSwitch"),
                 "ParkingBrakeSwitch": ("CCVS", "ParkingBrakeSwitch"),
                 "SteeringWheelAngle": ("VDC2-98F009FE", "SteeringWheelAngle"),
                 "csi.DriverActions_TC.Driveractions.Driveractions.DriverOverride_b": ("ECU", "csi.DriverActions_TC.Driveractions.Driveractions.DriverOverride_b"),
                 "csi.DriverActions_TC.fak1uGPPos": ("ECU", "csi.DriverActions_TC.fak1uGPPos"),
                 "lca.TimeIndicatorLeft": ("ECU", "lca.TimeIndicatorLeft"),
                 "lca.TimeIndicatorRight": ("ECU", "lca.TimeIndicatorRight"),},]

class cView(interface.iView):
  @classmethod
  def view(Sync, cls, Param=DefParam): 
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except measparser.signalgroup.SignalGroupError, error:
      print __file__
      print error.message
    else:
      #################
      #Driver override#
      #################
      Client = datavis.cPlotNavigator(title="driver_override", figureNr=105)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.DriverActions_TC.Driveractions.Driveractions.DriverOverride_b")
      Client.addSignal2Axis(Axis, "DrvOverride", Time, Value, unit="bool")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "Dam_x._.InitialDriverOverride_b")
      Client.addSignal2Axis(Axis, "InitialDrvOverride", Time, Value, unit="bool")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.DriverActions_TC.fak1uGPPos")
      Client.addSignal2Axis(Axis, "GPPos", Time, Value, unit="%")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "BrakePedalPosition")
      Client.addSignal2Axis(Axis, "BrakePedalPosition", Time, Value, unit="%")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "EBSBrakeSwitch")
      Client.addSignal2Axis(Axis, "EBSBrakeSwitch", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ParkingBrakeSwitch")
      Client.addSignal2Axis(Axis, "ParkingBrakeSwitch", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "SteeringWheelAngle")
      Client.addSignal2Axis(Axis, "SteeringWheelAngle", Time, Value, unit="rad")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "lca.TimeIndicatorLeft")
      Client.addSignal2Axis(Axis, "indic_left", Time, Value, unit="")    
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "lca.TimeIndicatorRight")
      return []

