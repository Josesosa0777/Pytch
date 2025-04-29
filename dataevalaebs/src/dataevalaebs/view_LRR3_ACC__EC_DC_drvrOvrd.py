import datavis
import interface

DefParam = interface.NullParam

SignalGroups = [{"csi.DriverActions_T20.Driveractions.Driveractions.DriverOverride_b": ("ECU", "csi.DriverActions_T20.Driveractions.Driveractions.DriverOverride_b"),
                 "csi.VehicleData_T20.vehicleData.vehicleData.NoBrkForce_b": ("ECU", "csi.VehicleData_T20.vehicleData.vehicleData.NoBrkForce_b"),
                 "Dai_X.PRIFLAGS.w.NoBrakeForceBrs_B": ("ECU", "Dai_X.PRIFLAGS.w.NoBrakeForceBrs_B"),
                 "Dai_X.PRIFLAGS.w.NoBrakeForceRet1_B": ("ECU", "Dai_X.PRIFLAGS.w.NoBrakeForceRet1_B"),
                 "Dai_X.PRIFLAGS.w.NoBrakeForceRet2_B": ("ECU", "Dai_X.PRIFLAGS.w.NoBrakeForceRet2_B"),
                 "Dai_X.PRIFLAGS.w.NoBrakeForceRet3_B": ("ECU", "Dai_X.PRIFLAGS.w.NoBrakeForceRet3_B"),
                 "lcc.priFlags.w.BrkForceReqByACC_B": ("ECU", "lcc.priFlags.w.BrkForceReqByACC_B"),
                 "csi.DriverActions_T20.Driveractions.Driveractions.BPAct_b": ("ECU", "csi.DriverActions_T20.Driveractions.Driveractions.BPAct_b"),
                 "csi.DriverActions_T20.Driveractions.Driveractions.GPAct_b": ("ECU", "csi.DriverActions_T20.Driveractions.Driveractions.GPAct_b"),
                 "csi.DriverActions_T20.fak1uGPPos": ("ECU", "csi.DriverActions_T20.fak1uGPPos"),
                 "vlc.States_T20.StateFlags.w.DCEnable_b": ("ECU", "vlc.States_T20.StateFlags.w.DCEnable_b"),
                 "vlc.States_T20.StateFlags.w.ECEnable_b": ("ECU", "vlc.States_T20.StateFlags.w.ECEnable_b"),
                 "acc.XStates_T20.SpecificState": ("ECU", "acc.XStates_T20.SpecificState"),
                 "vlc.Mea_T20.StateInternal": ("ECU", "vlc.Mea_T20.StateInternal"),
                 "vlc.Mea_T20.cdResidual": ("ECU", "vlc.Mea_T20.cdResidual"),
                 "evi.General_T20.axvRef": ("ECU", "evi.General_T20.axvRef"),
                 "ssc.axvCvDC": ("ECU", "ssc.axvCvDC"),
                 "ssc.axvCvEC": ("ECU", "ssc.axvCvEC"),
                 "foc.axvCv1": ("ECU", "foc.axvCv1"),
                 "foc.axvCv2": ("ECU", "foc.axvCv2"),
                 "csc.axvCv": ("ECU", "csc.axvCv"),
                 "acf.ControllerValues_TC.axvCv": ("ECU", "acf.ControllerValues_TC.axvCv"),
                 "acf.ControllerValues_TC.axvCvAim": ("ECU", "acf.ControllerValues_TC.axvCvAim"),
                 "vlc.Phy_T20.axvCv": ("ECU", "vlc.Phy_T20.axvCv"),
                 "vlc.Phy_T20.trqIndCv": ("ECU", "vlc.Phy_T20.trqIndCv"),
                 "lcc.axvMerged": ("ECU", "lcc.axvMerged"),
                 "lcc.axvCvAxvDelta": ("ECU", "lcc.axvCvAxvDelta"),
                 "evi.General_T20.vxvRef": ("ECU", "evi.General_T20.vxvRef"),
                 "csi.DriverActions_T20.vSet": ("ECU", "csi.DriverActions_T20.vSet"),
                 "lcc.tDCinitTime": ("ECU", "lcc.tDCinitTime"),
                 "lcc.priFlags.w.BrakeRelease_B": ("ECU", "lcc.priFlags.w.BrakeRelease_B"),
                 "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE": ("ECU", "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE"),
                 "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE2": ("ECU", "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE2"),
                 "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE3": ("ECU", "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE3"),
                 "cis_x_can_signals.FoundationBrakeUseEBC5Sa0x0B_B2": ("ECU", "cis_x_can_signals.FoundationBrakeUseEBC5Sa0x0B_B2"),
                 "cis_x_can_signals.ActualEnginePercentTorqueEEC1Sa": ("ECU", "cis_x_can_signals.ActualEnginePercentTorqueEEC1Sa"),
                 "cis_x_can_signals.DriversDemandEnginePercentTrqEE": ("ECU", "cis_x_can_signals.DriversDemandEnginePercentTrqEE"),
                 "cos_x_can_signals.axvCvXBRDa0x0B": ("ECU", "cos_x_can_signals.axvCvXBRDa0x0B"),
                 "cos_x_can_signals.ControlModeXBRDa0x0B_B2": ("ECU", "cos_x_can_signals.ControlModeXBRDa0x0B_B2"),
                 "cos_x_can_signals.OvrdCtrlModeTSC1Da0x00_B2": ("ECU", "cos_x_can_signals.OvrdCtrlModeTSC1Da0x00_B2"),
                 "cos_x_can_signals.RelTrqIndCvRqstTSC1Da0x00": ("ECU", "cos_x_can_signals.RelTrqIndCvRqstTSC1Da0x00"),},]

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
      Client = datavis.cPlotNavigator(title="Flags and states", figureNr=None)
      interface.Sync.addClient(Client)
      # 1. plot
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.DriverActions_T20.Driveractions.Driveractions.DriverOverride_b")
      Client.addSignal2Axis(Axis, "csi.DriverActions_T20.Driveractions.Driveractions.DriverOverride_b", Time, Value, unit="")
      # 2. plot
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
      # 3. plot
      Axis = Client.addAxis(ylim=(-0.1, 1.1))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "lcc.priFlags.w.BrkForceReqByACC_B")
      Client.addSignal2Axis(Axis, "lcc.priFlags.w.BrkForceReqByACC_B", Time, Value, unit="", color='-', linewidth=2)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vlc.States_T20.StateFlags.w.DCEnable_b")
      Client.addSignal2Axis(Axis, "vlc.States_T20.StateFlags.w.DCEnable_b", Time, Value, unit="", color='-', linewidth=1)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vlc.States_T20.StateFlags.w.ECEnable_b")
      Client.addSignal2Axis(Axis, "vlc.States_T20.StateFlags.w.ECEnable_b", Time, Value, unit="", color='-', linewidth=1)
      # 4. plot
      Axis = Client.addAxis(ylim=(0.0, 25.0))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_T20.SpecificState")
      Client.addSignal2Axis(Axis, "acc.XStates_T20.SpecificState", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vlc.Mea_T20.StateInternal")
      Client.addSignal2Axis(Axis, "vlc.Mea_T20.StateInternal", Time, Value, unit="")
      #
      # 2. plot window
      #
      Client = datavis.cPlotNavigator(title="Requests", figureNr=None)
      interface.Sync.addClient(Client)
      # 1. plot
      Axis = Client.addAxis(ylim=(-5.0, 5.0))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vlc.Phy_T20.axvCv")
      Client.addSignal2Axis(Axis, "vlc.Phy_T20.axvCv", Time, Value, unit="m/s^2", color='-', linewidth=2)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "evi.General_T20.axvRef")
      Client.addSignal2Axis(Axis, "evi.General_T20.axvRef", Time, Value, unit="m/s^2", color='-', linewidth=2)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ssc.axvCvDC")
      Client.addSignal2Axis(Axis, "ssc.axvCvDC", Time, Value, unit="m/s^2")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ssc.axvCvEC")
      Client.addSignal2Axis(Axis, "ssc.axvCvEC", Time, Value, unit="m/s^2")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "foc.axvCv1")
      Client.addSignal2Axis(Axis, "foc.axvCv1", Time, Value, unit="m/s^2")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "foc.axvCv2")
      Client.addSignal2Axis(Axis, "foc.axvCv2", Time, Value, unit="m/s^2")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csc.axvCv")
      Client.addSignal2Axis(Axis, "csc.axvCv", Time, Value, unit="m/s^2")
      # 2. plot
      Axis = Client.addAxis(ylim=(0.0, 3000.0))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vlc.Phy_T20.trqIndCv")
      Client.addSignal2Axis(Axis, "vlc.Phy_T20.trqIndCv", Time, Value, unit="Nm")
      # 3. plot
      Axis = Client.addAxis(ylim=(0.0, 30.0))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "evi.General_T20.vxvRef")
      Client.addSignal2Axis(Axis, "evi.General_T20.vxvRef", Time, Value, unit="m/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.DriverActions_T20.vSet")
      Client.addSignal2Axis(Axis, "csi.DriverActions_T20.vSet", Time, Value, unit="m/s")
      #
      # 3. plot window
      #
      Client = datavis.cPlotNavigator(title="EC / DC", figureNr=None)
      interface.Sync.addClient(Client)
      # 1. plot
      Axis = Client.addAxis(ylim=(-2.0, 2.0))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vlc.Mea_T20.cdResidual")
      Client.addSignal2Axis(Axis, "vlc.Mea_T20.cdResidual", Time, Value, unit="m/s^2", color='-', linewidth=1)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "evi.General_T20.axvRef")
      Client.addSignal2Axis(Axis, "evi.General_T20.axvRef", Time, Value, unit="m/s^2", color='-', linewidth=1)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vlc.Phy_T20.axvCv")
      Client.addSignal2Axis(Axis, "vlc.Phy_T20.axvCv", Time, Value, unit="m/s^2", color='-', linewidth=1)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acf.ControllerValues_TC.axvCv")
      Client.addSignal2Axis(Axis, "acf.ControllerValues_TC.axvCv", Time, Value, unit="m/s^2", color='-', linewidth=1)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acf.ControllerValues_TC.axvCvAim")
      Client.addSignal2Axis(Axis, "acf.ControllerValues_TC.axvCvAim", Time, Value, unit="m/s^2", color='-', linewidth=1)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "lcc.axvMerged")
      Client.addSignal2Axis(Axis, "lcc.axvMerged", Time, Value, unit="m/s^2", color='-', linewidth=1)
      # 2. plot
      Axis = Client.addAxis(ylim=(-0.1, 1.1))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "lcc.priFlags.w.BrkForceReqByACC_B")
      Client.addSignal2Axis(Axis, "lcc.priFlags.w.BrkForceReqByACC_B", Time, Value, unit="", color='-', linewidth=1)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VehicleData_T20.vehicleData.vehicleData.NoBrkForce_b")
      Client.addSignal2Axis(Axis, "csi.VehicleData_T20.vehicleData.vehicleData.NoBrkForce_b", Time, Value, unit="", color='-', linewidth=1)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "lcc.priFlags.w.BrakeRelease_B")
      Client.addSignal2Axis(Axis, "lcc.priFlags.w.BrakeRelease_B", Time, Value, unit="")
      # 3. plot
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "lcc.tDCinitTime")
      Client.addSignal2Axis(Axis, "lcc.tDCinitTime", Time, Value, unit="s")
      # 4. plot
      Axis = Client.addAxis(ylim=(-1.0, 1.0))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "lcc.axvCvAxvDelta")
      Client.addSignal2Axis(Axis, "lcc.axvCvAxvDelta", Time, Value, unit="m/s^2", color='-', linewidth=1)
      #
      # 4. plot window
      #
      Client = datavis.cPlotNavigator(title="External signals", figureNr=None)
      interface.Sync.addClient(Client)
      # 1. plot
      Axis = Client.addAxis(ylim=(-125.0, 25.0))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE", Time, Value, unit="", factor=0.006103515625)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE2")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE2", Time, Value, unit="", factor=0.006103515625)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE3")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.ActRetPercTrqERC1Sa0xFE3", Time, Value, unit="", factor=0.006103515625)
      # 2. plot
      Axis = Client.addAxis(ylim=(-0.1, 1.1))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.FoundationBrakeUseEBC5Sa0x0B_B2")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.FoundationBrakeUseEBC5Sa0x0B_B2", Time, Value, unit="")
      # 3. plot
      Axis = Client.addAxis(ylim=(-3.0, 2.0))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cos_x_can_signals.axvCvXBRDa0x0B")
      Client.addSignal2Axis(Axis, "cos_x_can_signals.axvCvXBRDa0x0B", Time, Value, unit="m/s^2")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "evi.General_T20.axvRef")
      Client.addSignal2Axis(Axis, "evi.General_T20.axvRef", Time, Value, unit="m/s^2", color='-', linewidth=1)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vlc.Phy_T20.axvCv")
      Client.addSignal2Axis(Axis, "vlc.Phy_T20.axvCv", Time, Value, unit="m/s^2", color='-', linewidth=1)
      # 4. plot
      Axis = Client.addAxis(ylim=(-0.1, 3.1))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cos_x_can_signals.ControlModeXBRDa0x0B_B2")
      Client.addSignal2Axis(Axis, "cos_x_can_signals.ControlModeXBRDa0x0B_B2", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cos_x_can_signals.OvrdCtrlModeTSC1Da0x00_B2")
      Client.addSignal2Axis(Axis, "cos_x_can_signals.OvrdCtrlModeTSC1Da0x00_B2", Time, Value, unit="")
      # 5. plot
      Axis = Client.addAxis(ylim=(-25.0, 125.0))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cos_x_can_signals.RelTrqIndCvRqstTSC1Da0x00")
      Client.addSignal2Axis(Axis, "cos_x_can_signals.RelTrqIndCvRqstTSC1Da0x00", Time, Value, unit="", factor=0.006103515625)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.ActualEnginePercentTorqueEEC1Sa")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.ActualEnginePercentTorqueEEC1Sa", Time, Value, unit="", factor=0.006103515625)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "cis_x_can_signals.DriversDemandEnginePercentTrqEE")
      Client.addSignal2Axis(Axis, "cis_x_can_signals.DriversDemandEnginePercentTrqEE", Time, Value, unit="", factor=0.006103515625)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.DriverActions_T20.fak1uGPPos")
      Client.addSignal2Axis(Axis, "csi.DriverActions_T20.fak1uGPPos", Time, Value, unit="-", factor=100.0)
      # 6. plot
      Axis = Client.addAxis(ylim=(-0.1, 1.1))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.DriverActions_T20.Driveractions.Driveractions.BPAct_b")
      Client.addSignal2Axis(Axis, "csi.DriverActions_T20.Driveractions.Driveractions.BPAct_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.DriverActions_T20.Driveractions.Driveractions.GPAct_b")
      Client.addSignal2Axis(Axis, "csi.DriverActions_T20.Driveractions.Driveractions.GPAct_b", Time, Value, unit="")
      pass
    pass


