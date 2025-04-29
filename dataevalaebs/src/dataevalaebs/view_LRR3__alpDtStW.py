import datavis
import interface

DefParam = interface.NullParam

SignalGroups = [{"csi.VehicleData_T20.alpDtSteeringWheel": ("ECU", "csi.VehicleData_T20.alpDtSteeringWheel"),
                 "cis_x_can_signals.alpSteeringWheelVDC2Sa0xFF": ("ECU", "cis_x_can_signals.alpSteeringWheelVDC2Sa0xFF"),
                 "bpc.VehicleBus4csi_T20.tAbsRecvTimeSteeringWheelAngle": ("ECU", "bpc.VehicleBus4csi_T20.tAbsRecvTimeSteeringWheelAngle"),
                 "Dai_X.alpStWheel": ("ECU", "Dai_X.alpStWheel"),
                 "Dai_X.alpStWheelK1": ("ECU", "Dai_X.alpStWheelK1"),
                 "Dai_X.tAlpStWheel": ("ECU", "Dai_X.tAlpStWheel"),
                 "Dai_X.tAlpStWheelK1": ("ECU", "Dai_X.tAlpStWheelK1"),
                 "SteeringWheelAngle": ("VDC2", "SteeringWheelAngle"),},]

class cView(interface.iView):
  @classmethod
  def view(cls, Param=DefParam):
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except ValueError, error:
      print __file__
      print error.message
    else:
      # 1. plot window
      Client = datavis.cPlotNavigator(title="Measurement", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VehicleData_T20.alpDtSteeringWheel")
      Client.addSignal2Axis(Axis, "csi.VehicleData_T20.alpDtSteeringWheel", Time, Value, unit="rad/s", color=".-", linewidth=1)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "SteeringWheelAngle")
      Client.addSignal2Axis(Axis, "SteeringWheelAngle VDC2", Time, Value, unit="rad", color=".-", linewidth=1)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.alpSteeringWheelVDC2Sa0xFF")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.alpSteeringWheelVDC2Sa0xFF", Time, Value, unit="rad", color="-", linewidth=0)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "Dai_X.alpStWheel")
      Client.addSignal2Axis(Axis, "Dai_X.alpStWheel", Time, Value, unit="rad", factor=64, color=".-", linewidth=1)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "Dai_X.alpStWheelK1")
      Client.addSignal2Axis(Axis, "Dai_X.alpStWheelK1", Time, Value, unit="rad", factor=64, color=".-", linewidth=1)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "bpc.VehicleBus4csi_T20.tAbsRecvTimeSteeringWheelAngle")
      Client.addSignal2Axis(Axis, "bpc.VehicleBus4csi_T20.tAbsRecvTimeSteeringWheelAngle", Time, Value, unit="s", color="-", linewidth=0)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "Dai_X.tAlpStWheel")
      Client.addSignal2Axis(Axis, "Dai_X.tAlpStWheel", Time, Value, unit="s", factor=0.03125, color=".-", linewidth=1)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "Dai_X.tAlpStWheelK1")
      Client.addSignal2Axis(Axis, "Dai_X.tAlpStWheelK1", Time, Value, unit="s", factor=0.03125, color=".-", linewidth=1)
      # Calculations
      plotTime = interface.Source.getSignalFromSignalGroup(Group, "Dai_X.alpStWheel")[0]
      alpStWDelta = (interface.Source.getSignalFromSignalGroup(Group, "Dai_X.alpStWheel")[1] - interface.Source.getSignalFromSignalGroup(Group, "Dai_X.alpStWheelK1")[1]) * 64
      tAlpStWDelta = (interface.Source.getSignalFromSignalGroup(Group, "Dai_X.tAlpStWheel")[1] - interface.Source.getSignalFromSignalGroup(Group, "Dai_X.tAlpStWheelK1")[1]) * 0.03125
      alpDtStWCalc = alpStWDelta / tAlpStWDelta
      # 2. plot window
      Client = datavis.cPlotNavigator(title="Offline calculation", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VehicleData_T20.alpDtSteeringWheel")
      Client.addSignal2Axis(Axis, "csi.VehicleData_T20.alpDtSteeringWheel", Time, Value, unit="rad/s", color="-", linewidth=1)
      Client.addSignal2Axis(Axis, "alpDtSteeringWheelCalc", plotTime, alpDtStWCalc, unit="rad", color=".-", linewidth=1)
      Axis = Client.addAxis()
      Client.addSignal2Axis(Axis, "deltaAlpSteeringWheelCalc", plotTime, alpStWDelta, unit="rad", color=".-", linewidth=1)
      Axis = Client.addAxis()
      Client.addSignal2Axis(Axis, "deltaTAlpSteeringWheelCalc", plotTime, tAlpStWDelta, unit="s", color=".-", linewidth=1)
      pass
    pass


