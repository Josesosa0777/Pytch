import datavis
import interface

DefParam = interface.NullParam

SignalGroups = [{"csi.VehicleData_T20.psiDt": ("ECU", "csi.VehicleData_T20.psiDt"),
                 "evi.General_T20.psiDtOpt": ("ECU", "evi.General_T20.psiDtOpt"),
                 "evi.Rta_TC.psiDtOffTotal": ("ECU", "evi.Rta_TC.psiDtOffTotal"),
                 "evi.General_T20.vxvRef": ("ECU", "evi.General_T20.vxvRef"),
                 "csi.VelocityData_T20.vxwflRaw": ("ECU", "csi.VelocityData_T20.vxwflRaw"),
                 "csi.VelocityData_T20.vxwfrRaw": ("ECU", "csi.VelocityData_T20.vxwfrRaw"),
                 "csi.VelocityData_T20.vxwrlRaw": ("ECU", "csi.VelocityData_T20.vxwrlRaw"),
                 "csi.VelocityData_T20.vxwrrRaw": ("ECU", "csi.VelocityData_T20.vxwrrRaw"),},]

class cView(interface.iView):
  @classmethod
  def view(cls, Param=DefParam):
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except ValueError, error:
      print __file__
      print error.message
    else:
      Client = datavis.cPlotNavigator(title="PN", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VehicleData_T20.psiDt")
      Client.addSignal2Axis(Axis, "csi.VehicleData_T20.psiDt", Time, Value, unit="1/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "evi.General_T20.psiDtOpt")
      Client.addSignal2Axis(Axis, "evi.General_T20.psiDtOpt", Time, Value, unit="1/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "evi.Rta_TC.psiDtOffTotal")
      Client.addSignal2Axis(Axis, "evi.Rta_TC.psiDtOffTotal", Time, Value, unit="1/s")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "evi.General_T20.vxvRef")
      Client.addSignal2Axis(Axis, "evi.General_T20.vxvRef", Time, Value, unit="m/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VelocityData_T20.vxwflRaw")
      Client.addSignal2Axis(Axis, "csi.VelocityData_T20.vxwflRaw", Time, Value, unit="m/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VelocityData_T20.vxwfrRaw")
      Client.addSignal2Axis(Axis, "csi.VelocityData_T20.vxwfrRaw", Time, Value, unit="m/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VelocityData_T20.vxwrlRaw")
      Client.addSignal2Axis(Axis, "csi.VelocityData_T20.vxwrlRaw", Time, Value, unit="m/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VelocityData_T20.vxwrrRaw")
      Client.addSignal2Axis(Axis, "csi.VelocityData_T20.vxwrrRaw", Time, Value, unit="m/s")
      pass
    pass


