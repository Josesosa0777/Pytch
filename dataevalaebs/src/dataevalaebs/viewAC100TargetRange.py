import interface
import measparser
import datavis

DefParam = interface.NullParam

SignalGroups = [{"ta0_range": ("Targets", "ta0_range"),
                 "ta1_range": ("Targets", "ta1_range"),
                 "ta2_range": ("Targets", "ta2_range"),
                 "ta3_range": ("Targets", "ta3_range"),
                 "ta4_range": ("Targets", "ta4_range"),
                 "ta5_range": ("Targets", "ta5_range"),
                 "ta6_range": ("Targets", "ta6_range"),
                 "ta7_range": ("Targets", "ta7_range"),
                 "ta8_range": ("Targets", "ta8_range"),
                 "ta9_range": ("Targets", "ta9_range"),},]

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
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta0_range")
      Client.addSignal2Axis(Axis, "ta0_range", Time, Value, unit="m")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta1_range")
      Client.addSignal2Axis(Axis, "ta1_range", Time, Value, unit="m")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta2_range")
      Client.addSignal2Axis(Axis, "ta2_range", Time, Value, unit="m")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta3_range")
      Client.addSignal2Axis(Axis, "ta3_range", Time, Value, unit="m")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta4_range")
      Client.addSignal2Axis(Axis, "ta4_range", Time, Value, unit="m")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta5_range")
      Client.addSignal2Axis(Axis, "ta5_range", Time, Value, unit="m")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta6_range")
      Client.addSignal2Axis(Axis, "ta6_range", Time, Value, unit="m")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta7_range")
      Client.addSignal2Axis(Axis, "ta7_range", Time, Value, unit="m")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta8_range")
      Client.addSignal2Axis(Axis, "ta8_range", Time, Value, unit="m")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta9_range")
      Client.addSignal2Axis(Axis, "ta9_range", Time, Value, unit="m")
      pass
    pass


