import datavis
import interface

DefParam = interface.NullParam

SignalGroups = [{"ats.Po_TC.PO.i0.dxvFilt": ("ECU", "ats.Po_TC.PO.i0.dxvFilt"),
                 "ats.Po_TC.PO.i1.dxvFilt": ("ECU", "ats.Po_TC.PO.i1.dxvFilt"),
                 "ats.Po_TC.PO.i0.dycAct": ("ECU", "ats.Po_TC.PO.i0.dycAct"),
                 "ats.Po_TC.PO.i1.dycAct": ("ECU", "ats.Po_TC.PO.i1.dycAct"),
                 "ats.Po_TC.PO.i0.vxvFilt": ("ECU", "ats.Po_TC.PO.i0.vxvFilt"),
                 "ats.Po_TC.PO.i1.vxvFilt": ("ECU", "ats.Po_TC.PO.i1.vxvFilt"),
                 "ats.Po_TC.PO.i0.dyv": ("ECU", "ats.Po_TC.PO.i0.dyv"),
                 "ats.Po_TC.PO.i1.dyv": ("ECU", "ats.Po_TC.PO.i1.dyv"),
                 "foc.axvCv1": ("ECU", "foc.axvCv1"),
                 "foc.axvCv2": ("ECU", "foc.axvCv2"),
                 "foc.axvFollowPO1": ("ECU", "foc.axvFollowPO1"),
                 "foc.axvFollowPO2": ("ECU", "foc.axvFollowPO2"),
                 "foc.axvApproachPO1": ("ECU", "foc.axvApproachPO1"),
                 "foc.axvApproachPO2": ("ECU", "foc.axvApproachPO2"),
                 "foc.dDesiredPO1": ("ECU", "foc.dDesiredPO1"),
                 "foc.dDesiredPO2": ("ECU", "foc.dDesiredPO2"),
                 "foc.dSlowDownPO1": ("ECU", "foc.dSlowDownPO1"),
                 "foc.dSlowDownPO2": ("ECU", "foc.dSlowDownPO2"),
                 "vlc.Phy_T20.axvTracMin": ("ECU", "vlc.Phy_T20.axvTracMin"),
                 "ats.Po_TC.PO.i0.dxvFilt": ("ECU", "ats.Po_TC.PO.i0.dxvFilt"),
                 "ats.Po_TC.PO.i1.dxvFilt": ("ECU", "ats.Po_TC.PO.i1.dxvFilt"),
                 "evi.General_TC.vxvRef": ("ECU", "evi.General_TC.vxvRef"),
                 "csi.DriverActions_TC.tauGapSet": ("ECU", "csi.DriverActions_TC.tauGapSet"),},]

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
      Client = datavis.cPlotNavigator(title="ATS target object data", figureNr=None)
      interface.Sync.addClient(Client)
      # 1. plot
      Axis = Client.addAxis(ylim=(0.0, 150.0))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ats.Po_TC.PO.i0.dxvFilt")
      Client.addSignal2Axis(Axis, "ats.Po_TC.PO.i0.dxvFilt", Time, Value, unit="m", color='-', linewidth=1)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ats.Po_TC.PO.i1.dxvFilt")
      Client.addSignal2Axis(Axis, "ats.Po_TC.PO.i1.dxvFilt", Time, Value, unit="m", color=':', linewidth=1)
      # 2. plot
      Axis = Client.addAxis(ylim=(-5.0, 5.0))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ats.Po_TC.PO.i0.dyv")
      Client.addSignal2Axis(Axis, "ats.Po_TC.PO.i0.dyv", Time, Value, unit="m", color='-', linewidth=1)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ats.Po_TC.PO.i1.dyv")
      Client.addSignal2Axis(Axis, "ats.Po_TC.PO.i1.dyv", Time, Value, unit="m", color=':', linewidth=1)
      # 3. plot
      Axis = Client.addAxis(ylim=(-5.0, 5.0))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ats.Po_TC.PO.i0.dycAct")
      Client.addSignal2Axis(Axis, "ats.Po_TC.PO.i0.dycAct", Time, Value, unit="m", color='-', linewidth=1)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ats.Po_TC.PO.i1.dycAct")
      Client.addSignal2Axis(Axis, "ats.Po_TC.PO.i1.dycAct", Time, Value, unit="m", color=':', linewidth=1)
      # 4. plot
      Axis = Client.addAxis(ylim=(-15.0, 15.0))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ats.Po_TC.PO.i0.vxvFilt")
      Client.addSignal2Axis(Axis, "ats.Po_TC.PO.i0.vxvFilt", Time, Value, unit="m/s", color='-', linewidth=1)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ats.Po_TC.PO.i1.vxvFilt")
      Client.addSignal2Axis(Axis, "ats.Po_TC.PO.i1.vxvFilt", Time, Value, unit="m/s", color=':', linewidth=1)
      #
      # 2. plot window
      #
      Client = datavis.cPlotNavigator(title="Controller values", figureNr=None)
      interface.Sync.addClient(Client)
      # 1. plot
      Axis = Client.addAxis(ylim=(0.0, 150.0))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "foc.dDesiredPO1")
      Client.addSignal2Axis(Axis, "foc.dDesiredPO1", Time, Value, unit="m", color='g-', linewidth=1)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "foc.dDesiredPO2")
      Client.addSignal2Axis(Axis, "foc.dDesiredPO2", Time, Value, unit="m", color='g:', linewidth=1)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ats.Po_TC.PO.i0.dxvFilt")
      Client.addSignal2Axis(Axis, "ats.Po_TC.PO.i0.dxvFilt", Time, Value, unit="m", color='r-', linewidth=1)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ats.Po_TC.PO.i1.dxvFilt")
      Client.addSignal2Axis(Axis, "ats.Po_TC.PO.i1.dxvFilt", Time, Value, unit="m", color='r:', linewidth=1)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "foc.dSlowDownPO1")
      Client.addSignal2Axis(Axis, "foc.dSlowDownPO1", Time, Value, unit="m", color='y-', linewidth=0)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "foc.dSlowDownPO2")
      Client.addSignal2Axis(Axis, "foc.dSlowDownPO2", Time, Value, unit="m", color='y:', linewidth=0)
      # 2. plot
      Axis = Client.addAxis(ylim=(-2.0, 8.0))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.DriverActions_TC.tauGapSet")
      Client.addSignal2Axis(Axis, "csi.DriverActions_TC.tauGapSet", Time, Value, unit="s", color='b-', linewidth=1)
      Time, dxvFiltPO1 = interface.Source.getSignalFromSignalGroup(Group, "ats.Po_TC.PO.i0.dxvFilt")
      Time, dxvFiltPO2 = interface.Source.getSignalFromSignalGroup(Group, "ats.Po_TC.PO.i1.dxvFilt")
      Time, vxvRef = interface.Source.getSignalFromSignalGroup(Group, "evi.General_TC.vxvRef")
      tauPO1 = dxvFiltPO1 / vxvRef
      tauPO2 = dxvFiltPO2 / vxvRef
      Client.addSignal2Axis(Axis, "PO.i0.tau", Time, tauPO1, unit="s", color='r-', linewidth=1)
      Client.addSignal2Axis(Axis, "PO.i1.tau", Time, tauPO2, unit="s", color='r:', linewidth=1)
      # 3. plot
      Axis = Client.addAxis(ylim=(-3.0, 2.0))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "foc.axvCv1")
      Client.addSignal2Axis(Axis, "foc.axvCv1", Time, Value, unit="m/s^2", color='k-', linewidth=2)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "foc.axvCv2")
      Client.addSignal2Axis(Axis, "foc.axvCv2", Time, Value, unit="m/s^2", color='k:', linewidth=2)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "foc.axvFollowPO1")
      Client.addSignal2Axis(Axis, "foc.axvFollowPO1", Time, Value, unit="m/s^2", color='b-', linewidth=1)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "foc.axvFollowPO2")
      Client.addSignal2Axis(Axis, "foc.axvFollowPO2", Time, Value, unit="m/s^2", color='b:', linewidth=1)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "foc.axvApproachPO1")
      Client.addSignal2Axis(Axis, "foc.axvApproachPO1", Time, Value, unit="m/s^2", color='r-', linewidth=1)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "foc.axvApproachPO2")
      Client.addSignal2Axis(Axis, "foc.axvApproachPO2", Time, Value, unit="m/s^2", color='r:', linewidth=1)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vlc.Phy_T20.axvTracMin")
      Client.addSignal2Axis(Axis, "vlc.Phy_T20.axvTracMin", Time, Value, unit="m/s^2", color='y-', linewidth=1)
      pass
    pass


