import datavis
import interface

DefParam = interface.NullParam

SignalGroups = [{"DFM_red_button": ("DIRK", "DFM_red_button"),
                 "DFM_green_button": ("DIRK", "DFM_green_button"),
                 "DFM_Cnt_green_button": ("DIRK", "DFM_Cnt_green_button"),
                 "DFM_Cnt_red_button": ("DIRK", "DFM_Cnt_red_button"),
                 "evi.General_T20.vxvRef": ("ECU", "evi.General_T20.vxvRef"),
                 "vlc.States_T20.StateFlags.w.DCEnable_b": ("ECU", "vlc.States_T20.StateFlags.w.DCEnable_b"),
                 "vlc.States_T20.StateFlags.w.ECEnable_b": ("ECU", "vlc.States_T20.StateFlags.w.ECEnable_b"),
                 "evi.General_T20.axvRef": ("ECU", "evi.General_T20.axvRef"),
                 "vlc.Phy_T20.axvCv": ("ECU", "vlc.Phy_T20.axvCv"),
                 "acc.XStates_TC.SpecificState": ("ECU", "acc.XStates_TC.SpecificState"),
                 "vlc.Mea_T20.StateInternal": ("ECU", "vlc.Mea_T20.StateInternal"),
                 "csi.VehicleData_T20.vehicleData.vehicleData.NoBrkForce_b": ("ECU", "csi.VehicleData_T20.vehicleData.vehicleData.NoBrkForce_b"),
                 "Dai_X.PRIFLAGS.w.NoBrakeForceBrs_B": ("ECU", "Dai_X.PRIFLAGS.w.NoBrakeForceBrs_B"),
                 "Dai_X.PRIFLAGS.w.NoBrakeForceRet1_B": ("ECU", "Dai_X.PRIFLAGS.w.NoBrakeForceRet1_B"),
                 "Dai_X.PRIFLAGS.w.NoBrakeForceRet2_B": ("ECU", "Dai_X.PRIFLAGS.w.NoBrakeForceRet2_B"),
                 "Dai_X.PRIFLAGS.w.NoBrakeForceRet3_B": ("ECU", "Dai_X.PRIFLAGS.w.NoBrakeForceRet3_B"),
                 "ats.Po_TC.PO.i0.dxvFilt": ("ECU", "ats.Po_TC.PO.i0.dxvFilt"),
                 "foc.dDesiredPO1": ("ECU", "foc.dDesiredPO1"),
                 "csi.DriverActions_T20.vSet": ("ECU", "csi.DriverActions_T20.vSet"),},]

class cView(interface.iView):
  @classmethod
  def view(cls, Param=DefParam):
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except ValueError, error:
      print __file__
      print error.message
    else:
      Client = datavis.cPlotNavigator(title="Driver's Interactive Response Knobs", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis(ylim=(-0.1,1.1))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "DFM_red_button")
      Client.addSignal2Axis(Axis, "DFM_red_button", Time, Value, unit="",color="r")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "DFM_green_button")
      Client.addSignal2Axis(Axis, "DFM_green_button", Time, Value, unit="",color="g")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "DFM_Cnt_green_button")
      Client.addSignal2Axis(Axis, "DFM_Cnt_green_button", Time, Value, unit="",color="g")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "DFM_Cnt_red_button")
      Client.addSignal2Axis(Axis, "DFM_Cnt_red_button", Time, Value, unit="",color="r")
      Axis = Client.addAxis(ylim=(0,30))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "evi.General_T20.vxvRef")
      Client.addSignal2Axis(Axis, "evi.General_T20.vxvRef", Time, Value, unit="m/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.DriverActions_T20.vSet")
      Client.addSignal2Axis(Axis, "csi.DriverActions_T20.vSet", Time, Value, unit="m/s")
      Axis = Client.addAxis(ylim=(-3.0,2.0))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "evi.General_T20.axvRef")
      Client.addSignal2Axis(Axis, "evi.General_T20.axvRef", Time, Value, unit="m/s^2")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vlc.Phy_T20.axvCv")
      Client.addSignal2Axis(Axis, "vlc.Phy_T20.axvCv", Time, Value, unit="m/s^2")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ats.Po_TC.PO.i0.dxvFilt")
      Client.addSignal2Axis(Axis, "ats.Po_TC.PO.i0.dxvFilt", Time, Value, unit="m")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "foc.dDesiredPO1")
      Client.addSignal2Axis(Axis, "foc.dDesiredPO1", Time, Value, unit="m")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "acc.XStates_TC.SpecificState")
      Client.addSignal2Axis(Axis, "acc.XStates_TC.SpecificState", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vlc.Mea_T20.StateInternal")
      Client.addSignal2Axis(Axis, "vlc.Mea_T20.StateInternal", Time, Value, unit="")
      Axis = Client.addAxis(ylim=(-0.1,1.1))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vlc.States_T20.StateFlags.w.DCEnable_b")
      Client.addSignal2Axis(Axis, "vlc.States_T20.StateFlags.w.DCEnable_b", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vlc.States_T20.StateFlags.w.ECEnable_b")
      Client.addSignal2Axis(Axis, "vlc.States_T20.StateFlags.w.ECEnable_b", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VehicleData_T20.vehicleData.vehicleData.NoBrkForce_b")
      Client.addSignal2Axis(Axis, "csi.VehicleData_T20.vehicleData.vehicleData.NoBrkForce_b", Time, Value, unit="",linewidth=2)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "Dai_X.PRIFLAGS.w.NoBrakeForceBrs_B")
      Client.addSignal2Axis(Axis, "Dai_X.PRIFLAGS.w.NoBrakeForceBrs_B", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "Dai_X.PRIFLAGS.w.NoBrakeForceRet1_B")
      Client.addSignal2Axis(Axis, "Dai_X.PRIFLAGS.w.NoBrakeForceRet1_B", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "Dai_X.PRIFLAGS.w.NoBrakeForceRet2_B")
      Client.addSignal2Axis(Axis, "Dai_X.PRIFLAGS.w.NoBrakeForceRet2_B", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "Dai_X.PRIFLAGS.w.NoBrakeForceRet3_B")
      Client.addSignal2Axis(Axis, "Dai_X.PRIFLAGS.w.NoBrakeForceRet3_B", Time, Value, unit="")
      pass
    pass



