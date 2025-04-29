from datavis import pyglet_workaround  # necessary as early as possible (#164)

import math
import os

import numpy
import scipy.signal

import kbtools
import measparser
import datavis
import interface

DefParam = interface.NullParam

SignalGroups = [{"FrontAxleSpeed": ("EBC2_X_EBS", "FrontAxleSpeed"),
                 "FoundationBrakeUse": ("EBC5_X_EBS", "FoundationBrakeUse"),
                 "Pitch_Rate": ("IMU_Pitch_and_RollRate", "Pitch_Rate"),},]

def CalcTilt(tEBC2, vFrontAxleSpeed, tEBC5, vFoundationBrakeUse, tIMU, vPitch_Rate, name=""):
  #Filter Pitch_rate
  [b, a] = scipy.signal.butter(3, 0.1)
  vPitch_Filtered = kbtools.filtfilt(b, a, vPitch_Rate)
  #Offset compensation  
  offset = numpy.mean(vPitch_Filtered)
  vPitch_Filtered = vPitch_Filtered - offset
  #Find event 
  deltamax = 5.0 #Max length of integration
  minspeed = 5.0 #Minimal speed(km/h)  
  pitch = numpy.zeros_like(tIMU)      
  dtall = numpy.zeros_like(tIMU)
  dtall[1:] = numpy.diff(tIMU)
  pitchall = numpy.cumsum(vPitch_Filtered * dtall)
  regions = numpy.zeros_like(tIMU)      
  brakestarts = tEBC5[numpy.diff(vFoundationBrakeUse) == 1]
  lastbrakestart = -deltamax
  for start in brakestarts:
    if lastbrakestart + deltamax < start:
      lastbrakestart = start
      mask = numpy.logical_and(tEBC2 >= start, tEBC2 < start + deltamax)
      end = tEBC2[mask][min((-1 * vFrontAxleSpeed[mask]).searchsorted(-minspeed), len(tEBC2[mask]) - 1)]
      mask = numpy.logical_and(tIMU >= start, tIMU <= end)
      #integration trapz
      # r = numpy.trapz(vPitch_Filtered[mask], x=tIMU[mask])
      #running integration and maximum selection
      dt = numpy.zeros_like(tIMU[mask])
      dt[1:] = numpy.diff(tIMU[mask])
      pitch[mask] = numpy.cumsum(vPitch_Filtered[mask] * dt)
      maxdeg = numpy.min(pitch[mask])
      # maxdeg = 0
      # print "%s (%f) %f - %f: %f" % (name, offset, start, end, maxdeg)
      print '"%s",%f,%f,%f,%f' % (name, offset, start, end, maxdeg)
      regions[mask] = 1
  return vPitch_Filtered, regions, pitch, pitchall 
                 
class cView(interface.iView):
  @classmethod
  def view(cls, Param=DefParam):
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except measparser.signalgroup.SignalGroupError, error:
      print __file__
      print error.message
    else:
      
      tEBC2, vFrontAxleSpeed = interface.Source.getSignalFromSignalGroup(Group, "FrontAxleSpeed")
      tEBC5, vFoundationBrakeUse = interface.Source.getSignalFromSignalGroup(Group, "FoundationBrakeUse")
      tIMU, vPitch_Rate = interface.Source.getSignalFromSignalGroup(Group, "Pitch_Rate")
      #Reshape signals (needed fbecause of mat source????)
      tEBC2 = tEBC2[:,0]
      vFrontAxleSpeed = vFrontAxleSpeed[:,0]
      tEBC5 = tEBC5[:,0]
      vFoundationBrakeUse = vFoundationBrakeUse[:,0]
      tIMU = tIMU[:,0]
      vPitch_Rate = vPitch_Rate[:,0]
      #Call calculation
      vPitch_Filtered, regions, pitch, pitchall = CalcTilt(tEBC2, vFrontAxleSpeed, tEBC5, vFoundationBrakeUse, tIMU, vPitch_Rate)
      #Plot
      Client = datavis.cPlotNavigator(title=os.path.split(interface.Source.FileName)[1], figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Client.addSignal2Axis(Axis, "FrontAxleSpeed", tEBC2, vFrontAxleSpeed, unit="")
      Axis = Client.addAxis()
      Client.addSignal2Axis(Axis, "FoundationBrakeUse", tEBC5, vFoundationBrakeUse, unit="")
      Axis = Client.addAxis()
      Client.addSignal2Axis(Axis, "Pitch_Rate", tIMU, vPitch_Rate, unit="")
      Client.addSignal2Axis(Axis, "Pitch_Rate_Filtered", tIMU, vPitch_Filtered, unit="")
      Axis = Client.addAxis()
      Client.addSignal2Axis(Axis, "Pitch_for_Braking(integrated)", tIMU, pitch, unit="deg")
      Client.addSignal2Axis(Axis, "Pitch_for_whole_measurement(integrated)", tIMU, pitchall, unit="deg")
      Axis = Client.addAxis()
      Client.addSignal2Axis(Axis, "Regions", tIMU, regions, unit="")
      pass
    pass

if __name__=='__main__':
  import os, stat
  import sys
  import glob
  import measparser

  if len(sys.argv) != 2:
    print "Usage: %s meas_dir" % (sys.argv[0])
    exit()
  else:  
    path = sys.argv[1]
    for matFile in glob.glob( os.path.join(path, '*.mat') ):
      try:
        source = measparser.cSignalSource(matFile)
        tEBC2, vFrontAxleSpeed = source.getSignal("EBC2_X_EBS", "FrontAxleSpeed")
        tEBC5, vFoundationBrakeUse = source.getSignal("EBC5_X_EBS", "FoundationBrakeUse")
        tIMU, vPitch_Rate = source.getSignal("IMU_Pitch_and_RollRate", "Pitch_Rate")
        tEBC2 = tEBC2[:,0]
        vFrontAxleSpeed = vFrontAxleSpeed[:,0]
        tEBC5 = tEBC5[:,0]
        vFoundationBrakeUse = vFoundationBrakeUse[:,0]
        tIMU = tIMU[:,0]
        vPitch_Rate = vPitch_Rate[:,0]
        CalcTilt(tEBC2, vFrontAxleSpeed, tEBC5, vFoundationBrakeUse, tIMU, vPitch_Rate, os.path.split(matFile)[1])
      except:
        # print "Error in %s" % (matFile)
        pass
