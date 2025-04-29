import datavis
import measparser
import interface

DefParam = interface.NullParam

SignalGroups = [{"ta0_target_flags_LSB": ("Targets", "ta0_target_flags_LSB"),
                 "ta0_target_flags_MSB": ("Targets", "ta0_target_flags_MSB"),
                 "ta1_target_flags_LSB": ("Targets", "ta1_target_flags_LSB"),
                 "ta1_target_flags_MSB": ("Targets", "ta1_target_flags_MSB"),
                 "ta2_target_flags_LSB": ("Targets", "ta2_target_flags_LSB"),
                 "ta2_target_flags_MSB": ("Targets", "ta2_target_flags_MSB"),
                 "ta3_target_flags_LSB": ("Targets", "ta3_target_flags_LSB"),
                 "ta3_target_flags_MSB": ("Targets", "ta3_target_flags_MSB"),
                 "ta4_target_flags_LSB": ("Targets", "ta4_target_flags_LSB"),
                 "ta4_target_flags_MSB": ("Targets", "ta4_target_flags_MSB"),
                 "ta5_target_flags_LSB": ("Targets", "ta5_target_flags_LSB"),
                 "ta5_target_flags_MSB": ("Targets", "ta5_target_flags_MSB"),
                 "ta6_target_flags_LSB": ("Targets", "ta6_target_flags_LSB"),
                 "ta6_target_flags_MSB": ("Targets", "ta6_target_flags_MSB"),
                 "ta7_target_flags_LSB": ("Targets", "ta7_target_flags_LSB"),
                 "ta7_target_flags_MSB": ("Targets", "ta7_target_flags_MSB"),
                 "ta8_target_flags_LSB": ("Targets", "ta8_target_flags_LSB"),
                 "ta8_target_flags_MSB": ("Targets", "ta8_target_flags_MSB"),
                 "ta9_target_flags_LSB": ("Targets", "ta9_target_flags_LSB"),
                 "ta9_target_flags_MSB": ("Targets", "ta9_target_flags_MSB"),},]

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
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta0_target_flags_LSB")
      Client.addSignal2Axis(Axis, "ta0_target_flags_LSB", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta0_target_flags_MSB")
      Client.addSignal2Axis(Axis, "ta0_target_flags_MSB", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta1_target_flags_LSB")
      Client.addSignal2Axis(Axis, "ta1_target_flags_LSB", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta1_target_flags_MSB")
      Client.addSignal2Axis(Axis, "ta1_target_flags_MSB", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta2_target_flags_LSB")
      Client.addSignal2Axis(Axis, "ta2_target_flags_LSB", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta2_target_flags_MSB")
      Client.addSignal2Axis(Axis, "ta2_target_flags_MSB", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta3_target_flags_LSB")
      Client.addSignal2Axis(Axis, "ta3_target_flags_LSB", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta3_target_flags_MSB")
      Client.addSignal2Axis(Axis, "ta3_target_flags_MSB", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta4_target_flags_LSB")
      Client.addSignal2Axis(Axis, "ta4_target_flags_LSB", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta4_target_flags_MSB")
      Client.addSignal2Axis(Axis, "ta4_target_flags_MSB", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta5_target_flags_LSB")
      Client.addSignal2Axis(Axis, "ta5_target_flags_LSB", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta5_target_flags_MSB")
      Client.addSignal2Axis(Axis, "ta5_target_flags_MSB", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta6_target_flags_LSB")
      Client.addSignal2Axis(Axis, "ta6_target_flags_LSB", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta6_target_flags_MSB")
      Client.addSignal2Axis(Axis, "ta6_target_flags_MSB", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta7_target_flags_LSB")
      Client.addSignal2Axis(Axis, "ta7_target_flags_LSB", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta7_target_flags_MSB")
      Client.addSignal2Axis(Axis, "ta7_target_flags_MSB", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta8_target_flags_LSB")
      Client.addSignal2Axis(Axis, "ta8_target_flags_LSB", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta8_target_flags_MSB")
      Client.addSignal2Axis(Axis, "ta8_target_flags_MSB", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta9_target_flags_LSB")
      Client.addSignal2Axis(Axis, "ta9_target_flags_LSB", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta9_target_flags_MSB")
      Client.addSignal2Axis(Axis, "ta9_target_flags_MSB", Time, Value, unit="")
      pass
    pass


