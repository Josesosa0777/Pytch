import datavis
import interface

DefParam = interface.NullParam

SignalGroups = [{"CVR2.ats.Po_TC.PO.i0.dxvFilt": ("ECU", "ats.Po_TC.PO.i0.dxvFilt"),
                 "CVR3.ats.Po_TC.PO.i0.dxvFilt": ("MRR1plus", "ats.Po_TC.PO.i0.dxvFilt"),
                 "CVR2.ats.Po_TC.dxMaxFollowPO": ("ECU", "ats.Po_TC.dxMaxFollowPO"),
                 "CVR3.ats.Po_TC.dxMaxFollowPO": ("MRR1plus", "ats.Po_TC.dxMaxFollowPO"),
                 "CVR2.ats.Po_TC.PO.i0.vxvFilt": ("ECU", "ats.Po_TC.PO.i0.vxvFilt"),
                 "CVR3.ats.Po_TC.PO.i0.vxvFilt": ("MRR1plus", "ats.Po_TC.PO.i0.vxvFilt"),
                 "CVR2.ats.Po_TC.PO.i0.axvAbsFilt": ("ECU", "ats.Po_TC.PO.i0.axvAbsFilt"),
                 "CVR3.ats.Po_TC.PO.i0.axvAbsFilt": ("MRR1plus", "ats.Po_TC.PO.i0.axvAbsFilt"),},]

class cView(interface.iView):
  def check(self):
    Group = interface.Source.selectSignalGroup(SignalGroups)
    return Group
    
  def fill(self, Group):
    return Group

  def view(cls, Param, Group):
    Client = datavis.cPlotNavigator(title="ATS PO0 (LRR3 vs. MRR)", figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis(ylim=(-0.0, 150.0))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "CVR2.ats.Po_TC.PO.i0.dxvFilt")
    Client.addSignal2Axis(Axis, "CVR2.ats.Po_TC.PO.i0.dxvFilt", Time, Value, unit="m", color="b-")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "CVR3.ats.Po_TC.PO.i0.dxvFilt")
    Client.addSignal2Axis(Axis, "CVR3.ats.Po_TC.PO.i0.dxvFilt", Time, Value, unit="m", color="g-")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "CVR2.ats.Po_TC.dxMaxFollowPO")
    Client.addSignal2Axis(Axis, "CVR2.ats.Po_TC.dxMaxFollowPO", Time, Value, unit="m", color="b:")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "CVR3.ats.Po_TC.dxMaxFollowPO")
    Client.addSignal2Axis(Axis, "CVR3.ats.Po_TC.dxMaxFollowPO", Time, Value, unit="m", color="g:")
    Axis = Client.addAxis(ylim=(-10.0, 10.0))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "CVR2.ats.Po_TC.PO.i0.vxvFilt")
    Client.addSignal2Axis(Axis, "CVR2.ats.Po_TC.PO.i0.vxvFilt", Time, Value, unit="m/s", color="b-")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "CVR3.ats.Po_TC.PO.i0.vxvFilt")
    Client.addSignal2Axis(Axis, "CVR3.ats.Po_TC.PO.i0.vxvFilt", Time, Value, unit="m/s", color="g-")
    Axis = Client.addAxis(ylim=(-3.0, 3.0))
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "CVR2.ats.Po_TC.PO.i0.axvAbsFilt")
    Client.addSignal2Axis(Axis, "CVR2.ats.Po_TC.PO.i0.axvAbsFilt", Time, Value, unit="m/s^2", color="b-")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "CVR3.ats.Po_TC.PO.i0.axvAbsFilt")
    Client.addSignal2Axis(Axis, "CVR3.ats.Po_TC.PO.i0.axvAbsFilt", Time, Value, unit="m/s^2", color="g-")
    return

