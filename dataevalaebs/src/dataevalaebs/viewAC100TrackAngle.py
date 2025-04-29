import datavis
import measparser
import interface

DefParam = interface.NullParam

SignalGroups = [{"tr0_uncorrected_angle": ("Tracks", "tr0_uncorrected_angle"),
                 "tr1_uncorrected_angle": ("Tracks", "tr1_uncorrected_angle"),
                 "tr2_uncorrected_angle": ("Tracks", "tr2_uncorrected_angle"),
                 "tr3_uncorrected_angle": ("Tracks", "tr3_uncorrected_angle"),
                 "tr4_uncorrected_angle": ("Tracks", "tr4_uncorrected_angle"),},]

class cView(interface.iView):
  @classmethod
  def view(cls, Param=DefParam):
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except measparser.signalgroup.SignalGroupError, error:
      print __file__
      print error.message
    else:
      Client = datavis.cPlotNavigator(title="PN", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "tr0_uncorrected_angle")
      Client.addSignal2Axis(Axis, "tr0_uncorrected_angle", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "tr1_uncorrected_angle")
      Client.addSignal2Axis(Axis, "tr1_uncorrected_angle", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "tr2_uncorrected_angle")
      Client.addSignal2Axis(Axis, "tr2_uncorrected_angle", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "tr3_uncorrected_angle")
      Client.addSignal2Axis(Axis, "tr3_uncorrected_angle", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "tr4_uncorrected_angle")
      Client.addSignal2Axis(Axis, "tr4_uncorrected_angle", Time, Value, unit="")
      pass
    pass


