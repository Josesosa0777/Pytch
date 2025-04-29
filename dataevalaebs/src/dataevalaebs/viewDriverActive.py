import numpy

import datavis
import interface
from measproc import cIntervalList
import aebs

DefParam = interface.NullParam

SignalGroups = [{"sit.BasicInput_T20.GPPos": ("RadarFC", "sit.BasicInput_T20.GPPos"),
                 "AccelPedalPosition": ("EEC2--Message--Knorr_Bremse__CVR3_Prototype_1_5__ACC_J1939", "AccelPedalPosition"),
                 "BrakePedalPosition": ("EBC1--Message--Knorr_Bremse__CVR3_Prototype_1_5__ACC_J1939", "BrakePedalPosition"),
                 "EBSBrakeSwitch": ("EBC1--Message--Knorr_Bremse__CVR3_Prototype_1_5__ACC_J1939", "EBSBrakeSwitch"),
                 "SteeringWheelAngle": ("VDC2--Message--Knorr_Bremse__CVR3_Prototype_1_5__ACC_J1939", "SteeringWheelAngle"),
                 "Blinker_Zugwagen_links": ("Aux_St_ZBR_3", "Blinker_Zugwagen_links"),
                 "Blinker_Zugwagen_rechts": ("Aux_St_ZBR_3", "Blinker_Zugwagen_rechts"),},]

class cView(interface.iView):
  def check(self):
    Group = interface.Source.selectSignalGroup(SignalGroups)
    return Group
    
  def fill(self, Group):
    return Group

  def view(cls, Param, Group):
    Client = datavis.cPlotNavigator(title="PN", figureNr=None)
    interface.Sync.addClient(Client)
    T20, Value = interface.Source.getSignalFromSignalGroup(Group, "sit.BasicInput_T20.GPPos")

    # input signals from CAN on T20
    Time, GPPos = interface.Source.getSignalFromSignalGroup(Group, "AccelPedalPosition", ScaleTime=T20)
    Time, pBrake = interface.Source.getSignalFromSignalGroup(Group, "BrakePedalPosition", ScaleTime=T20)
    Time, BPAct = interface.Source.getSignalFromSignalGroup(Group, "EBSBrakeSwitch", ScaleTime=T20)
    Time, alpSteeringWheel = interface.Source.getSignalFromSignalGroup(Group, "SteeringWheelAngle", ScaleTime=T20)
    Time, b_DirIndL = interface.Source.getSignalFromSignalGroup(Group, "Blinker_Zugwagen_links", ScaleTime=T20)
    Time, b_DirIndR = interface.Source.getSignalFromSignalGroup(Group, "Blinker_Zugwagen_rechts", ScaleTime=T20)

    # eliminate blinking from indicator signals
    intervals = cIntervalList.fromMask(T20, b_DirIndL)
    DirIndL = intervals.merge(DistLimit=1.0).toMask(dtype=numpy.int32)
    intervals = cIntervalList.fromMask(T20, b_DirIndR)
    DirIndR = intervals.merge(DistLimit=1.0).toMask(dtype=numpy.int32)
    
    DriverActive, DriverActiveGP, DriverActiveBrake, \
      DriverActiveSteering, DriverActiveDirInd = \
      aebs.proc.calcDriverActive(
        T20, GPPos, pBrake, BPAct, alpSteeringWheel, DirIndL, DirIndR)
        
    # Plots
    Axis = Client.addAxis()
    Client.addSignal2Axis(Axis, "AccelPedalPosition", T20, GPPos, unit="%")

    Axis = Client.addAxis()
    Client.addSignal2Axis(Axis, "BrakePedalPosition", T20, pBrake, unit="%")

    Axis = Client.addAxis()
    Client.addSignal2Axis(Axis, "EBSBrakeSwitch", T20, BPAct, unit="")

    Axis = Client.addAxis()
    Client.addSignal2Axis(Axis, "SteeringWheelAngle", T20, alpSteeringWheel, unit="rad")

    Axis = Client.addAxis()
    Client.addSignal2Axis(Axis, "Blinker_Zugwagen_links", T20, b_DirIndL, unit="")
    Client.addSignal2Axis(Axis, "Blinker_Zugwagen_rechts", T20, b_DirIndR, unit="")
    Client.addSignal2Axis(Axis, "DirIndL", T20, DirIndL, unit="")
    Client.addSignal2Axis(Axis, "DirIndR", T20, DirIndR, unit="")
        
    Axis = Client.addAxis()
    Client.addSignal2Axis(Axis, "DriverActiveGP", T20, DriverActiveGP, unit="")
    Client.addSignal2Axis(Axis, "DriverActiveBrake", T20, DriverActiveBrake, unit="")
    Client.addSignal2Axis(Axis, "DriverActiveSteering", T20, DriverActiveSteering, unit="")
    Client.addSignal2Axis(Axis, "DriverActiveDirInd", T20, DriverActiveDirInd, unit="")
    
    Axis = Client.addAxis()
    Client.addSignal2Axis(Axis, "DriverActive", T20, DriverActive, unit="")
    
    return

