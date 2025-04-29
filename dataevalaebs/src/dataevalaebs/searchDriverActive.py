# -*- dataeval: method -*-
import numpy

import interface
import measproc
from measproc.report2 import Report
from measproc import cIntervalList
import aebs

DefParam = interface.NullParam

signalgroups =   [{
  "sit.BasicInput_T20.GPPos": ("RadarFC", "sit.BasicInput_T20.GPPos"),
  "AccelPedalPosition": ("EEC2--Message--Knorr_Bremse__CVR3_Prototype_1_5__ACC_J1939", "AccelPedalPosition"),
  "BrakePedalPosition": ("EBC1--Message--Knorr_Bremse__CVR3_Prototype_1_5__ACC_J1939", "BrakePedalPosition"),
  "EBSBrakeSwitch": ("EBC1--Message--Knorr_Bremse__CVR3_Prototype_1_5__ACC_J1939", "EBSBrakeSwitch"),
  "SteeringWheelAngle": ("VDC2--Message--Knorr_Bremse__CVR3_Prototype_1_5__ACC_J1939", "SteeringWheelAngle"),
  "Blinker_Zugwagen_links": ("Aux_St_ZBR_3", "Blinker_Zugwagen_links"),
  "Blinker_Zugwagen_rechts": ("Aux_St_ZBR_3", "Blinker_Zugwagen_rechts"),
  }]

class cSearch(interface.iSearch):
  def check(self):
    source = self.get_source('main')
    group = source.selectSignalGroup(signalgroups)
    return group

  def fill(self, group):
    return group

  def search(self, param, group):
    source = self.get_source('main')
    batch = self.get_batch()

    T20, Value = source.getSignalFromSignalGroup(group, "sit.BasicInput_T20.GPPos")

    # input signals from CAN on T20
    Time, GPPos = source.getSignalFromSignalGroup(group, "AccelPedalPosition", ScaleTime=T20)
    Time, pBrake = source.getSignalFromSignalGroup(group, "BrakePedalPosition", ScaleTime=T20)
    Time, BPAct = source.getSignalFromSignalGroup(group, "EBSBrakeSwitch", ScaleTime=T20)
    Time, alpSteeringWheel = source.getSignalFromSignalGroup(group, "SteeringWheelAngle", ScaleTime=T20)
    Time, b_DirIndL = source.getSignalFromSignalGroup(group, "Blinker_Zugwagen_links", ScaleTime=T20)
    Time, b_DirIndR = source.getSignalFromSignalGroup(group, "Blinker_Zugwagen_rechts", ScaleTime=T20)

    # eliminate blinking from indicator signals
    intervals = cIntervalList.fromMask(T20, b_DirIndL)
    DirIndL = intervals.merge(DistLimit=1.0).toMask(dtype=numpy.int32)
    intervals = cIntervalList.fromMask(T20, b_DirIndR)
    DirIndR = intervals.merge(DistLimit=1.0).toMask(dtype=numpy.int32)
    
    DriverActive, DriverActiveGP, DriverActiveBrake, \
      DriverActiveSteering, DriverActiveDirInd = \
      aebs.proc.calcDriverActive(
        T20, GPPos, pBrake, BPAct, alpSteeringWheel, DirIndL, DirIndR)
    
    activitytovotes = {
      'driver active'  : DriverActive, 
      'accel pedal'    : DriverActiveGP, 
      'brake pedal'    : DriverActiveBrake, 
      'steering wheel' : DriverActiveSteering, 
      'indicator'      : DriverActiveDirInd,}
    
    title = 'Driver activity'
    votes = batch.get_labelgroups('DMT driver monitoring')
    
    report = Report(cIntervalList(T20), title, votes)
    for vote, activity in activitytovotes.iteritems():
      intervals = cIntervalList.fromMask(T20, activity) 
      for interval in intervals:
        id = report.addInterval(interval)
        report.vote(id, 'DMT driver monitoring', vote)
    batch.add_entry(report, 'passed', ('radar',))
    return
