import datavis
import measparser
import interface

DefParam = interface.NullParam

SignalGroups = [{"ta0_angle_LSB": ("Targets", "ta0_angle_LSB"),
                 "ta0_angle_MSB": ("Targets", "ta0_angle_MSB"),
                 "ta1_angle_LSB": ("Targets", "ta1_angle_LSB"),
                 "ta1_angle_MSB": ("Targets", "ta1_angle_MSB"),
                 "ta2_angle_LSB": ("Targets", "ta2_angle_LSB"),
                 "ta2_angle_MSB": ("Targets", "ta2_angle_MSB"),
                 "ta3_angle_LSB": ("Targets", "ta3_angle_LSB"),
                 "ta3_angle_MSB": ("Targets", "ta3_angle_MSB"),
                 "ta4_angle_LSB": ("Targets", "ta4_angle_LSB"),
                 "ta4_angle_MSB": ("Targets", "ta4_angle_MSB"),
                 "ta5_angle_LSB": ("Targets", "ta5_angle_LSB"),
                 "ta5_angle_MSB": ("Targets", "ta5_angle_MSB"),
                 "ta6_angle_LSB": ("Targets", "ta6_angle_LSB"),
                 "ta6_angle_MSB": ("Targets", "ta6_angle_MSB"),
                 "ta7_angle_LSB": ("Targets", "ta7_angle_LSB"),
                 "ta7_angle_MSB": ("Targets", "ta7_angle_MSB"),
                 "ta8_angle_LSB": ("Targets", "ta8_angle_LSB"),
                 "ta8_angle_MSB": ("Targets", "ta8_angle_MSB"),
                 "ta9_angle_LSB": ("Targets", "ta9_angle_LSB"),
                 "ta9_angle_MSB": ("Targets", "ta9_angle_MSB"),},]

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
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta0_angle_LSB")
      Client.addSignal2Axis(Axis, "ta0_angle_LSB", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta0_angle_MSB")
      Client.addSignal2Axis(Axis, "ta0_angle_MSB", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta1_angle_LSB")
      Client.addSignal2Axis(Axis, "ta1_angle_LSB", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta1_angle_MSB")
      Client.addSignal2Axis(Axis, "ta1_angle_MSB", Time, Value, unit="")
      Axis = Client.addAxis()
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta2_angle_LSB")
      Client.addSignal2Axis(Axis, "ta2_angle_LSB", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta2_angle_MSB")
      Client.addSignal2Axis(Axis, "ta2_angle_MSB", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta3_angle_LSB")
      Client.addSignal2Axis(Axis, "ta3_angle_LSB", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta3_angle_MSB")
      Client.addSignal2Axis(Axis, "ta3_angle_MSB", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta4_angle_LSB")
      Client.addSignal2Axis(Axis, "ta4_angle_LSB", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta4_angle_MSB")
      Client.addSignal2Axis(Axis, "ta4_angle_MSB", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta5_angle_LSB")
      Client.addSignal2Axis(Axis, "ta5_angle_LSB", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta5_angle_MSB")
      Client.addSignal2Axis(Axis, "ta5_angle_MSB", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta6_angle_LSB")
      Client.addSignal2Axis(Axis, "ta6_angle_LSB", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta6_angle_MSB")
      Client.addSignal2Axis(Axis, "ta6_angle_MSB", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta7_angle_LSB")
      Client.addSignal2Axis(Axis, "ta7_angle_LSB", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta7_angle_MSB")
      Client.addSignal2Axis(Axis, "ta7_angle_MSB", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta8_angle_LSB")
      Client.addSignal2Axis(Axis, "ta8_angle_LSB", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta8_angle_MSB")
      Client.addSignal2Axis(Axis, "ta8_angle_MSB", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta9_angle_LSB")
      Client.addSignal2Axis(Axis, "ta9_angle_LSB", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ta9_angle_MSB")
      Client.addSignal2Axis(Axis, "ta9_angle_MSB", Time, Value, unit="")
      pass
    pass


