import datavis
import interface

DefParam = interface.NullParam

SignalGroups = [{"yod.psiDtInLP": ("ECU", "yod.psiDtInLP"),
                 "yod.psiDtInMean": ("ECU", "yod.psiDtInMean"),
                 "yod.psiDtInMedian": ("ECU", "yod.psiDtInMedian"),
                 "yod.psiDtInMedianLP": ("ECU", "yod.psiDtInMedianLP"),
                 "csi.VehicleData_T20.psiDt": ("ECU", "csi.VehicleData_T20.psiDt"),
                 "evi.General_T20.psiDtOpt": ("ECU", "evi.General_T20.psiDtOpt"),
                 # "Mrf._.PssObjectDebugInfo.wExistProb": ("ECU", "Mrf._.PssObjectDebugInfo.wExistProb"),
                 # "Mrf._.PssObjectDebugInfo.wObstacle": ("ECU", "Mrf._.PssObjectDebugInfo.wObstacle"),
                 "sit.IntroFinder_TC.Intro.i0.Id": ("ECU", "sit.IntroFinder_TC.Intro.i0.Id"),},]

class cView(interface.iView):
  @classmethod
  def view(cls, Param=DefParam):
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except ValueError, error:
      print __file__
      print error.message
    else:
      # First plot navigator
      Client = datavis.cPlotNavigator(title="Filtered yaw rates", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis(ylim=(-0.05, 0.05))
      # Axis2 = Client.addAxis(ylim=(-0.35, 0.35))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VehicleData_T20.psiDt")
      Client.addSignal2Axis(Axis, "csi.VehicleData_T20.psiDt", Time, Value, unit="1/s", color='-', linewidth=1)
      # gradient = (Value[1:] - Value[:-1]) / (Time[1:] - Time[:-1])
      # tGrad = Time[1:]
      # Client.addSignal2Axis(Axis2, "psiDtDt", tGrad, gradient, unit="1/ss", color='-', linewidth=1)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "yod.psiDtInLP")
      Client.addSignal2Axis(Axis, "yod.psiDtInLP", Time, Value, unit="1/s", color='-', linewidth=0)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "yod.psiDtInMean")
      Client.addSignal2Axis(Axis, "yod.psiDtInMean", Time, Value, unit="1/s", color='-', linewidth=0)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "yod.psiDtInMedian")
      Client.addSignal2Axis(Axis, "yod.psiDtInMedian", Time, Value, unit="1/s", color='-', linewidth=0)
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "yod.psiDtInMedianLP")
      Client.addSignal2Axis(Axis, "yod.psiDtInMedianLP", Time, Value, unit="1/s", color='-', linewidth=0)
      # Second plot navigator
      Client = datavis.cPlotNavigator(title="", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis(ylim=(-0.05, 0.05))
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "evi.General_T20.psiDtOpt")
      Client.addSignal2Axis(Axis, "evi.General_T20.psiDtOpt", Time, Value, unit="1/s")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "sit.IntroFinder_TC.Intro.i0.Id")
      Client.addSignal2Axis(Axis, "sit.IntroFinder_TC.Intro.i0.Id", Time, Value, unit="")
      # Axis = Client.addAxis(ylim=(0.0,1.0))
      # Time, Value = interface.Source.getSignalFromSignalGroup(Group, "Mrf._.PssObjectDebugInfo.wExistProb")
      # Client.addSignal2Axis(Axis, "Mrf._.PssObjectDebugInfo.wExistProb", Time, Value, unit="-")
      # Time, Value = interface.Source.getSignalFromSignalGroup(Group, "Mrf._.PssObjectDebugInfo.wObstacle")
      # Client.addSignal2Axis(Axis, "Mrf._.PssObjectDebugInfo.wObstacle", Time, Value, unit="-")
      pass
    pass


