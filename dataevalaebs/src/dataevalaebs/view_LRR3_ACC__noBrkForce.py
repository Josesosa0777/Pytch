import datavis
import interface

DefParam = interface.NullParam

SignalGroups = [{"csi.VehicleData_T20.vehicleData.vehicleData.NoBrkForce_b": ("ECU", "csi.VehicleData_T20.vehicleData.vehicleData.NoBrkForce_b"),
                 "Dai_X.PRIFLAGS.w.NoBrakeForceBrs_B": ("ECU", "Dai_X.PRIFLAGS.w.NoBrakeForceBrs_B"),
                 "Dai_X.PRIFLAGS.w.NoBrakeForceRet1_B": ("ECU", "Dai_X.PRIFLAGS.w.NoBrakeForceRet1_B"),
                 "Dai_X.PRIFLAGS.w.NoBrakeForceRet2_B": ("ECU", "Dai_X.PRIFLAGS.w.NoBrakeForceRet2_B"),
                 "Dai_X.PRIFLAGS.w.NoBrakeForceRet3_B": ("ECU", "Dai_X.PRIFLAGS.w.NoBrakeForceRet3_B"),
                 "lcc.priFlags.w.BrkForceReqByACC_B": ("ECU", "lcc.priFlags.w.BrkForceReqByACC_B"),
                 "csi.DriverActions_T20.Driveractions.Driveractions.BPAct_b": ("ECU", "csi.DriverActions_T20.Driveractions.Driveractions.BPAct_b"),
                 "vlc.States_T20.StateFlags.w.DCEnable_b": ("ECU", "vlc.States_T20.StateFlags.w.DCEnable_b"),
                 "vlc.States_T20.StateFlags.w.ECEnable_b": ("ECU", "vlc.States_T20.StateFlags.w.ECEnable_b"),
                 "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE": ("ECU", "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE"),
                 "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE2": ("ECU", "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE2"),
                 "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE3": ("ECU", "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE3"),
                 "cis_x_can_signals.FoundationBrakeUseEBC5Sa0x0B_B2": ("ECU", "cis_x_can_signals.FoundationBrakeUseEBC5Sa0x0B_B2"),
                 "cos_x_can_signals.ControlModeXBRDa0x0B_B2": ("ECU", "cos_x_can_signals.ControlModeXBRDa0x0B_B2"),},]

class cView(interface.iView):
  @classmethod
  def view(cls, Param=DefParam):
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except ValueError, error:
      print __file__
      print error.message
    else:
      #
      # 1. plot window
      #
      Client = datavis.cPlotNavigator(title="noBrakeForce", figureNr=None)
      interface.Sync.addClient(Client)
      # 1. plot
      Axis = Client.addAxis(ylim=(-0.1, 1.1))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VehicleData_T20.vehicleData.vehicleData.NoBrkForce_b")
      Client.addSignal2Axis(Axis, "csi.VehicleData_T20.vehicleData.vehicleData.NoBrkForce_b", Time, Value, unit="", color='-', linewidth=2)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "Dai_X.PRIFLAGS.w.NoBrakeForceBrs_B")
      Client.addSignal2Axis(Axis, "Dai_X.PRIFLAGS.w.NoBrakeForceBrs_B", Time, Value, unit="", color='-', linewidth=1)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "Dai_X.PRIFLAGS.w.NoBrakeForceRet1_B")
      Client.addSignal2Axis(Axis, "Dai_X.PRIFLAGS.w.NoBrakeForceRet1_B", Time, Value, unit="", color='-', linewidth=1)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "Dai_X.PRIFLAGS.w.NoBrakeForceRet2_B")
      Client.addSignal2Axis(Axis, "Dai_X.PRIFLAGS.w.NoBrakeForceRet2_B", Time, Value, unit="", color='-', linewidth=0)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "Dai_X.PRIFLAGS.w.NoBrakeForceRet3_B")
      Client.addSignal2Axis(Axis, "Dai_X.PRIFLAGS.w.NoBrakeForceRet3_B", Time, Value, unit="", color='-', linewidth=0)
      # 2. plot
      Axis = Client.addAxis(ylim=(-125.0, 25.0))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE", Time, Value, unit="", factor=0.006103515625)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE2")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE2", Time, Value, unit="", factor=0.006103515625)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE3")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE3", Time, Value, unit="", factor=0.006103515625)
      # 3. plot
      Axis = Client.addAxis(ylim=(-0.1, 3.1))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cos_x_can_signals.ControlModeXBRDa0x0B_B2")
      Client.addSignal2Axis(Axis, "cos_x_can_signals.ControlModeXBRDa0x0B_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.FoundationBrakeUseEBC5Sa0x0B_B2")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.FoundationBrakeUseEBC5Sa0x0B_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.DriverActions_T20.Driveractions.Driveractions.BPAct_b")
      Client.addSignal2Axis(Axis, "csi.DriverActions_T20.Driveractions.Driveractions.BPAct_b", Time, Value, unit="")
      # 4. plot
      Axis = Client.addAxis(ylim=(-0.1, 1.1))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "lcc.priFlags.w.BrkForceReqByACC_B")
      Client.addSignal2Axis(Axis, "lcc.priFlags.w.BrkForceReqByACC_B", Time, Value, unit="", color='-', linewidth=2)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vlc.States_T20.StateFlags.w.DCEnable_b")
      Client.addSignal2Axis(Axis, "vlc.States_T20.StateFlags.w.DCEnable_b", Time, Value, unit="", color='-', linewidth=1)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vlc.States_T20.StateFlags.w.ECEnable_b")
      Client.addSignal2Axis(Axis, "vlc.States_T20.StateFlags.w.ECEnable_b", Time, Value, unit="", color='-', linewidth=1)
      pass
    pass


