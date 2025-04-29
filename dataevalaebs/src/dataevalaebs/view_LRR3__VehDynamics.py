import datavis
import interface

DefParam = interface.NullParam

SignalGroups = [{"csi.VehicleData_T20.vehicleData.vehicleData.ABSActive_b": ("ECU", "csi.VehicleData_T20.vehicleData.vehicleData.ABSActive_b"),
                 "csi.VehicleData_T20.vehicleData.vehicleData.ASRActive_b": ("ECU", "csi.VehicleData_T20.vehicleData.vehicleData.ASRActive_b"),
                 "csi.VehicleData_T20.vehicleData.vehicleData.ESPActive_b": ("ECU", "csi.VehicleData_T20.vehicleData.vehicleData.ESPActive_b"),
                 "csi.VehicleData_T20.vehicleData.vehicleData.MSRActive_b": ("ECU", "csi.VehicleData_T20.vehicleData.vehicleData.MSRActive_b"),
                 "csi.VehicleData_T20.vehicleData.vehicleData.VDCActive_b": ("ECU", "csi.VehicleData_T20.vehicleData.vehicleData.VDCActive_b"),
                 "csi.VelocityData_T20.vxwflRaw": ("ECU", "csi.VelocityData_T20.vxwflRaw"),
                 "csi.VelocityData_T20.vxwfrRaw": ("ECU", "csi.VelocityData_T20.vxwfrRaw"),
                 "csi.VelocityData_T20.vxwrlRaw": ("ECU", "csi.VelocityData_T20.vxwrlRaw"),
                 "csi.VelocityData_T20.vxwrrRaw": ("ECU", "csi.VelocityData_T20.vxwrrRaw"),
                 "csi.VehicleData_T20.psiDt": ("ECU", "csi.VehicleData_T20.psiDt"),},]

class cView(interface.iView):
  @classmethod
  def view(cls, Param=DefParam):
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except ValueError, error:
      print __file__
      print error.message
    else:
      Client = datavis.cPlotNavigator(title="Vehicle dynamics", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis(ylim=(-0.1,1.1))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VehicleData_T20.vehicleData.vehicleData.ABSActive_b")
      Client.addSignal2Axis(Axis, "csi.VehicleData_T20.vehicleData.vehicleData.ABSActive_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VehicleData_T20.vehicleData.vehicleData.ASRActive_b")
      Client.addSignal2Axis(Axis, "csi.VehicleData_T20.vehicleData.vehicleData.ASRActive_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VehicleData_T20.vehicleData.vehicleData.ESPActive_b")
      Client.addSignal2Axis(Axis, "csi.VehicleData_T20.vehicleData.vehicleData.ESPActive_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VehicleData_T20.vehicleData.vehicleData.MSRActive_b")
      Client.addSignal2Axis(Axis, "csi.VehicleData_T20.vehicleData.vehicleData.MSRActive_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VehicleData_T20.vehicleData.vehicleData.VDCActive_b")
      Client.addSignal2Axis(Axis, "csi.VehicleData_T20.vehicleData.vehicleData.VDCActive_b", Time, Value, unit="")
      Axis = Client.addAxis(ylim=(0.0,30.0))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VelocityData_T20.vxwflRaw")
      Client.addSignal2Axis(Axis, "csi.VelocityData_T20.vxwflRaw", Time, Value, unit="m/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VelocityData_T20.vxwfrRaw")
      Client.addSignal2Axis(Axis, "csi.VelocityData_T20.vxwfrRaw", Time, Value, unit="m/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VelocityData_T20.vxwrlRaw")
      Client.addSignal2Axis(Axis, "csi.VelocityData_T20.vxwrlRaw", Time, Value, unit="m/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VelocityData_T20.vxwrrRaw")
      Client.addSignal2Axis(Axis, "csi.VelocityData_T20.vxwrrRaw", Time, Value, unit="m/s")
      Axis = Client.addAxis(ylim=(-0.05, 0.05))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VehicleData_T20.psiDt")
      Client.addSignal2Axis(Axis, "csi.VehicleData_T20.psiDt", Time, Value, unit="1/s")
      pass
    pass


