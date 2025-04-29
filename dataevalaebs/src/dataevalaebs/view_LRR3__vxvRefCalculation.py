import datavis
import interface

DefParam = interface.NullParam

SignalGroups = [{"evi.General_T20.vxvRef": ("ECU", "evi.General_T20.vxvRef"),
                 "vsp.vxvRefNoCali": ("ECU", "vsp.vxvRefNoCali"),
                 "vsp.vxvRefRaw": ("ECU", "vsp.vxvRefRaw"),
                 "vsp.vxvRefMean": ("ECU", "vsp.vxvRefMean"),
                 "vsp.vxvRefMeanExtrapol": ("ECU", "vsp.vxvRefMeanExtrapol"),
                 "vsp.vxwBandMax": ("ECU", "vsp.vxwBandMax"),
                 "vsp.vxwBandMin": ("ECU", "vsp.vxwBandMin"),
                 "vsp.vxwFLMax": ("ECU", "vsp.vxwFLMax"),
                 "vsp.vxwFLMin": ("ECU", "vsp.vxwFLMin"),
                 "vsp.vxwFRMax": ("ECU", "vsp.vxwFRMax"),
                 "vsp.vxwFRMin": ("ECU", "vsp.vxwFRMin"),
                 "vsp.vxwRLMax": ("ECU", "vsp.vxwRLMax"),
                 "vsp.vxwRLMin": ("ECU", "vsp.vxwRLMin"),
                 "vsp.vxwRRMax": ("ECU", "vsp.vxwRRMax"),
                 "vsp.vxwRRMin": ("ECU", "vsp.vxwRRMin"),
                 "vsp_T20.vxwFLCorr": ("ECU", "vsp_T20.vxwFLCorr"),
                 "vsp_T20.vxwFRCorr": ("ECU", "vsp_T20.vxwFRCorr"),
                 "vsp_T20.vxwRLCorr": ("ECU", "vsp_T20.vxwRLCorr"),
                 "vsp_T20.vxwRRCorr": ("ECU", "vsp_T20.vxwRRCorr"),
                 "evi.General_T20.vxwInFFL": ("ECU", "evi.General_T20.vxwInFFL"),
                 "evi.General_T20.vxwInFFR": ("ECU", "evi.General_T20.vxwInFFR"),
                 "evi.General_T20.vxwInFRL": ("ECU", "evi.General_T20.vxwInFRL"),
                 "evi.General_T20.vxwInFRR": ("ECU", "evi.General_T20.vxwInFRR"),
                 "csi.VelocityData_T20.vxwflRaw": ("ECU", "csi.VelocityData_T20.vxwflRaw"),
                 "csi.VelocityData_T20.vxwfrRaw": ("ECU", "csi.VelocityData_T20.vxwfrRaw"),
                 "csi.VelocityData_T20.vxwrlRaw": ("ECU", "csi.VelocityData_T20.vxwrlRaw"),
                 "csi.VelocityData_T20.vxwrrRaw": ("ECU", "csi.VelocityData_T20.vxwrrRaw"),
                 "vsp.NumberErrWheel": ("ECU", "vsp.NumberErrWheel"),
                 "vsp.Flags.w.CaseBrake_B": ("ECU", "vsp.Flags.w.CaseBrake_B"),
                 "vsp.Flags.w.CaseDrive_B": ("ECU", "vsp.Flags.w.CaseDrive_B"),},]

class cView(interface.iView):
  @classmethod
  def view(cls, Param=DefParam):
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except ValueError, error:
      print __file__
      print error.message
    else:
      Client = datavis.cPlotNavigator(title="PN", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "evi.General_T20.vxvRef")
      Client.addSignal2Axis(Axis, "evi.General_T20.vxvRef", Time, Value, unit="m/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vsp.vxvRefNoCali")
      Client.addSignal2Axis(Axis, "vsp.vxvRefNoCali", Time, Value, unit="m/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vsp.vxvRefRaw")
      Client.addSignal2Axis(Axis, "vsp.vxvRefRaw", Time, Value, unit="m/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vsp.vxvRefMean")
      Client.addSignal2Axis(Axis, "vsp.vxvRefMean", Time, Value, unit="m/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vsp.vxvRefMeanExtrapol")
      Client.addSignal2Axis(Axis, "vsp.vxvRefMeanExtrapol", Time, Value, unit="m/s")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vsp.vxwBandMax")
      Client.addSignal2Axis(Axis, "vsp.vxwBandMax", Time, Value, unit="m/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vsp.vxwBandMin")
      Client.addSignal2Axis(Axis, "vsp.vxwBandMin", Time, Value, unit="m/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vsp.vxwFLMax")
      Client.addSignal2Axis(Axis, "vsp.vxwFLMax", Time, Value, unit="m/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vsp.vxwFLMin")
      Client.addSignal2Axis(Axis, "vsp.vxwFLMin", Time, Value, unit="m/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vsp.vxwFRMax")
      Client.addSignal2Axis(Axis, "vsp.vxwFRMax", Time, Value, unit="m/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vsp.vxwFRMin")
      Client.addSignal2Axis(Axis, "vsp.vxwFRMin", Time, Value, unit="m/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vsp.vxwRLMax")
      Client.addSignal2Axis(Axis, "vsp.vxwRLMax", Time, Value, unit="m/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vsp.vxwRLMin")
      Client.addSignal2Axis(Axis, "vsp.vxwRLMin", Time, Value, unit="m/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vsp.vxwRRMax")
      Client.addSignal2Axis(Axis, "vsp.vxwRRMax", Time, Value, unit="m/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vsp.vxwRRMin")
      Client.addSignal2Axis(Axis, "vsp.vxwRRMin", Time, Value, unit="m/s")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vsp_T20.vxwFLCorr")
      Client.addSignal2Axis(Axis, "vsp_T20.vxwFLCorr", Time, Value, unit="m/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vsp_T20.vxwFRCorr")
      Client.addSignal2Axis(Axis, "vsp_T20.vxwFRCorr", Time, Value, unit="m/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vsp_T20.vxwRLCorr")
      Client.addSignal2Axis(Axis, "vsp_T20.vxwRLCorr", Time, Value, unit="m/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vsp_T20.vxwRRCorr")
      Client.addSignal2Axis(Axis, "vsp_T20.vxwRRCorr", Time, Value, unit="m/s")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "evi.General_T20.vxwInFFL")
      Client.addSignal2Axis(Axis, "evi.General_T20.vxwInFFL", Time, Value, unit="m/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "evi.General_T20.vxwInFFR")
      Client.addSignal2Axis(Axis, "evi.General_T20.vxwInFFR", Time, Value, unit="m/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "evi.General_T20.vxwInFRL")
      Client.addSignal2Axis(Axis, "evi.General_T20.vxwInFRL", Time, Value, unit="m/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "evi.General_T20.vxwInFRR")
      Client.addSignal2Axis(Axis, "evi.General_T20.vxwInFRR", Time, Value, unit="m/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VelocityData_T20.vxwflRaw")
      Client.addSignal2Axis(Axis, "csi.VelocityData_T20.vxwflRaw", Time, Value, unit="m/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VelocityData_T20.vxwfrRaw")
      Client.addSignal2Axis(Axis, "csi.VelocityData_T20.vxwfrRaw", Time, Value, unit="m/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VelocityData_T20.vxwrlRaw")
      Client.addSignal2Axis(Axis, "csi.VelocityData_T20.vxwrlRaw", Time, Value, unit="m/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VelocityData_T20.vxwrrRaw")
      Client.addSignal2Axis(Axis, "csi.VelocityData_T20.vxwrrRaw", Time, Value, unit="m/s")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vsp.NumberErrWheel")
      Client.addSignal2Axis(Axis, "vsp.NumberErrWheel", Time, Value, unit="-")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vsp.Flags.w.CaseBrake_B")
      Client.addSignal2Axis(Axis, "vsp.Flags.w.CaseBrake_B", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "vsp.Flags.w.CaseDrive_B")
      Client.addSignal2Axis(Axis, "vsp.Flags.w.CaseDrive_B", Time, Value, unit="")
      pass
    pass


