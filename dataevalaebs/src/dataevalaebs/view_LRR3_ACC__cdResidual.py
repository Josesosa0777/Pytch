import datavis
import interface

DefParam = interface.NullParam

SignalGroups = [{"lcc.cdResidualF": ("ECU", "lcc.cdResidualF"),
                 "lcc.cdResidualHyst": ("ECU", "lcc.cdResidualHyst"),
                 "vlc.Mea_T20.cdResidual": ("ECU", "vlc.Mea_T20.cdResidual"),
                 "ptc.fxvTracMeas": ("ECU", "ptc.fxvTracMeas"),
                 "ptc.fxvTracPhaseCor": ("ECU", "ptc.fxvTracPhaseCor"),
                 "ptc.fxvTracPhaseCorF": ("ECU", "ptc.fxvTracPhaseCorF"),
                 "evi.General_T20.axvRef": ("ECU", "evi.General_T20.axvRef"),
                 "csi.VehicleData_T20.vehicleData.vehicleData.NoBrkForce_b": ("ECU", "csi.VehicleData_T20.vehicleData.vehicleData.NoBrkForce_b"),
                 "tra.pubFlags.w.ShiftInProgress_B": ("ECU", "tra.pubFlags.w.ShiftInProgress_B"),},]

class cView(interface.iView):
  @classmethod
  def view(cls, Param=DefParam):
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except ValueError, error:
      print __file__
      print error.message
    else:
      Client = datavis.cPlotNavigator(title="cdResidual", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis(ylim=(-1.0, 1.0))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "lcc.cdResidualF")
      Client.addSignal2Axis(Axis, "lcc.cdResidualF", Time, Value, unit="m/s^2", color='-', linewidth=1)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "lcc.cdResidualHyst")
      Client.addSignal2Axis(Axis, "lcc.cdResidualHyst", Time, Value, unit="m/s^2", color='-', linewidth=1)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vlc.Mea_T20.cdResidual")
      Client.addSignal2Axis(Axis, "vlc.Mea_T20.cdResidual", Time, Value, unit="m/s^2", color=':', linewidth=1)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ptc.fxvTracMeas")
      Client.addSignal2Axis(Axis, "ptc.fxvTracMeas", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ptc.fxvTracPhaseCor")
      Client.addSignal2Axis(Axis, "ptc.fxvTracPhaseCor", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ptc.fxvTracPhaseCorF")
      Client.addSignal2Axis(Axis, "ptc.fxvTracPhaseCorF", Time, Value, unit="", color='-', linewidth=2)
      Axis = Client.addAxis(ylim=(-3.0, 2.0))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "evi.General_T20.axvRef")
      Client.addSignal2Axis(Axis, "evi.General_T20.axvRef", Time, Value, unit="m/s^2")
      Axis = Client.addAxis(ylim=(-0.1, 1.1))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "tra.pubFlags.w.ShiftInProgress_B")
      Client.addSignal2Axis(Axis, "tra.pubFlags.w.ShiftInProgress_B", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VehicleData_T20.vehicleData.vehicleData.NoBrkForce_b")
      Client.addSignal2Axis(Axis, "csi.VehicleData_T20.vehicleData.vehicleData.NoBrkForce_b", Time, Value, unit="")
      pass
    pass


