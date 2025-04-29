import datavis
import interface

DefParam = interface.NullParam

SignalGroups = [{"vlc.States_T20.StateFlags.w.TracInterrupt_b": ("ECU", "vlc.States_T20.StateFlags.w.TracInterrupt_b"),
                 "tra.pubFlags.w.ShiftInProgress_B": ("ECU", "tra.pubFlags.w.ShiftInProgress_B"),
                 "csi.DriverActions_T20.Driveractions.Driveractions.CPAct_b": ("ECU", "csi.DriverActions_T20.Driveractions.Driveractions.CPAct_b"),
                 "cis_x_can_signals.TMShiftInProcessETC1Sa0x03_B2": ("ECU", "cis_x_can_signals.TMShiftInProcessETC1Sa0x03_B2"),
                 "csi.DriverActions_T20.Driveractions.Driveractions.ShiftInProgress_b": ("ECU", "csi.DriverActions_T20.Driveractions.Driveractions.ShiftInProgress_b"),
                 "csi.GearInfo_T20.TMRatio": ("ECU", "csi.GearInfo_T20.TMRatio"),
                 "tra.tmRatio": ("ECU", "tra.tmRatio"),
                 "tra.StateTracInterrupt": ("ECU", "tra.StateTracInterrupt"),
                 "evi.General_T20.vxvRef": ("ECU", "evi.General_T20.vxvRef"),
                 "csi.VehicleData_T20.nMot": ("ECU", "csi.VehicleData_T20.nMot"),},]

class cView(interface.iView):
  @classmethod
  def view(cls, Param=DefParam):
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except ValueError, error:
      print __file__
      print error.message
    else:
      Client = datavis.cPlotNavigator(title="Traction interruption", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vlc.States_T20.StateFlags.w.TracInterrupt_b")
      Client.addSignal2Axis(Axis, "vlc.States_T20.StateFlags.w.TracInterrupt_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "tra.pubFlags.w.ShiftInProgress_B")
      Client.addSignal2Axis(Axis, "tra.pubFlags.w.ShiftInProgress_B", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.DriverActions_T20.Driveractions.Driveractions.CPAct_b")
      Client.addSignal2Axis(Axis, "csi.DriverActions_T20.Driveractions.Driveractions.CPAct_b", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.TMShiftInProcessETC1Sa0x03_B2")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.TMShiftInProcessETC1Sa0x03_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.DriverActions_T20.Driveractions.Driveractions.ShiftInProgress_b")
      Client.addSignal2Axis(Axis, "csi.DriverActions_T20.Driveractions.Driveractions.ShiftInProgress_b", Time, Value, unit="")
      Axis = Client.addAxis(ylim=(0.0,100.0))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.GearInfo_T20.TMRatio")
      Client.addSignal2Axis(Axis, "csi.GearInfo_T20.TMRatio", Time, Value, unit="", factor=0.0078125)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "tra.tmRatio")
      Client.addSignal2Axis(Axis, "tra.tmRatio", Time, Value, unit="N/Nm")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "tra.StateTracInterrupt")
      Client.addSignal2Axis(Axis, "tra.StateTracInterrupt", Time, Value, unit="")
      Axis = Client.addAxis(ylim=(0.0,2500.0))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VehicleData_T20.nMot")
      Client.addSignal2Axis(Axis, "csi.VehicleData_T20.nMot", Time, Value, unit="1/min")
      Axis = Client.addAxis(ylim=(0.0,30.0))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "evi.General_T20.vxvRef")
      Client.addSignal2Axis(Axis, "evi.General_T20.vxvRef", Time, Value, unit="m/s")
      pass
    pass


