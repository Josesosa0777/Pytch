'''

   CIPV - Closest In Path Vehicle
   
   for radar sensor CVR3 and AC100
   
   - CVR3:    Position Matrix S1 (first object in same lane)
   - AC100:   CW (Collision Warning) Track 
   
   Ulrich Guecker 
   2011-12-16

'''


import datavis
import measparser
import interface
import numpy as np

import kbtools_user   # required for cDataCVR3 and cDataAC100

DefParam = interface.NullParam

'''
SignalGroups = [{"evi.General_T20.vxvRef": ("MRR1plus", "evi.General_T20.vxvRef"),
                },]
'''
device = "RadarFC"
SignalGroups = [{"evi.General_T20.vxvRef": (device, "evi.General_T20.vxvRef"),
                 "repPreStatus"          : (device, "repprew.__b_Rep.__b_RepBase.status")
                },]

#-------------------------------------------------------------------------
def signal_plotable(Time, Value):
  if  (Value is not None) and (Time is not None):
     if len(Value) == len(Time):
        return True
  
  return False  

# ====================================================================================
class cView(interface.iView):
  @classmethod
  def view(cls, Param=DefParam):
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except measparser.signalgroup.SignalGroupError, error:
      print __file__
      print error.message
    else:
      Client = datavis.cPlotNavigator(title="CIPV - Closest In Path Vehicle", figureNr=None)
      interface.Sync.addClient(Client)

      # ---------------------------------------------------------------------------
      # load signals      
      # CVR3 
      CVR3_sig = kbtools_user.cDataCVR3.load_CVR3_from_Source(interface.Source)
      CVR3_ObjName = 'S1'
      CVR3_color = 'b'     # blue
      
      # AC100      
      AC100_sig =kbtools_user.cDataAC100.load_AC100_from_Source(interface.Source)
      AC100_ObjName = 'CW'
      AC100_color = 'r'     # red
      
      
      # -----------------------------------------------     
      # vehicle speed 
      #Axis = Client.addAxis()
      #Time, Value = interface.Source.getSignalFromSignalGroup(Group, "evi.General_T20.vxvRef")
      #Client.addSignal2Axis(Axis, "evi.General_T20.vxvRef", Time, Value*3.6, unit="kph")
     
      # -----------------------------------------------     
      # vehicle speed 
      Axis = Client.addAxis()
      Time  = CVR3_sig['EgoVeh']["Time"]
      Value = CVR3_sig['EgoVeh']["vxvRef"]
      Client.addSignal2Axis(Axis, "veh speed", Time, Value*3.6, unit="kph")
     
     
      # -----------------------------------------------    
      # CIPV availability
      Axis = Client.addAxis()
     
      # CVR3 
      Time  = CVR3_sig['PosMatrix'][CVR3_ObjName]['Time']
      Value = CVR3_sig['PosMatrix'][CVR3_ObjName]['Valid']
      Client.addSignal2Axis(Axis, "CVR3 S1 object", Time, Value, unit="", color=CVR3_color)

      # AC100      
      Time  = AC100_sig['PosMatrix'][AC100_ObjName]['Time']
      Value = AC100_sig['PosMatrix'][AC100_ObjName]['Valid']
      #print "AC100", Time, Value
      if signal_plotable(Time, Value):
        Client.addSignal2Axis(Axis, "AC100 CW track (+2)", Time, Value+2, unit="", color=AC100_color)
      else:
        print "Value or Time None", Value, Time
      # -----------------------------------------------    
      # longitudinal distance to CIPV
      Axis = Client.addAxis()
     
      # CVR3 
      Time  = CVR3_sig['PosMatrix'][CVR3_ObjName]['Time']
      Value = CVR3_sig['PosMatrix'][CVR3_ObjName]['dx']
      Client.addSignal2Axis(Axis, "CVR3 dx", Time, Value, unit="m", color=CVR3_color)

      # AC100      
      Time  = AC100_sig['PosMatrix'][AC100_ObjName]['Time']
      Value = AC100_sig['PosMatrix'][AC100_ObjName]['dx']
      if signal_plotable(Time, Value):
        Client.addSignal2Axis(Axis, "AC100 dx", Time, Value, unit="m", color=AC100_color)

      # -----------------------------------------------    
      # lateral distance to CIPV
      Axis = Client.addAxis()
     
      # CVR3 
      Time  = CVR3_sig['PosMatrix'][CVR3_ObjName]['Time']
      Value = CVR3_sig['PosMatrix'][CVR3_ObjName]['dy']
      Client.addSignal2Axis(Axis, "CVR3 dy", Time, Value, unit="m", color=CVR3_color)

      # AC100      
      Time  = AC100_sig['PosMatrix'][AC100_ObjName]['Time']
      Value = AC100_sig['PosMatrix'][AC100_ObjName]['dy']
      if  signal_plotable(Time, Value):
        Client.addSignal2Axis(Axis, "AC100 dy", Time, Value, unit="m", color=AC100_color)

      # -----------------------------------------------    
      # relative velocity to CIPV
      Axis = Client.addAxis()
     
      # CVR3 
      Time  = CVR3_sig['PosMatrix'][CVR3_ObjName]['Time']
      Value = CVR3_sig['PosMatrix'][CVR3_ObjName]['vx']
      Client.addSignal2Axis(Axis, "CVR3 vRel", Time, Value, unit="m/s", color=CVR3_color)

      # AC100      
      Time  = AC100_sig['PosMatrix'][AC100_ObjName]['Time']
      Value = AC100_sig['PosMatrix'][AC100_ObjName]['vx']
      if  signal_plotable(Time, Value):
        Client.addSignal2Axis(Axis, "AC100 vRel", Time, Value, unit="m/s", color=AC100_color)

      # -----------------------------------------------    
      # CIPV is detected as stationary 
      Axis = Client.addAxis()
     
      # CVR3 
      Time  = CVR3_sig['PosMatrix'][CVR3_ObjName]['Time']
      Value = CVR3_sig['PosMatrix'][CVR3_ObjName]['Stand_b']
      Client.addSignal2Axis(Axis, "CVR3 Stationary", Time, Value, unit="", color=CVR3_color)

      # AC100      
      Time  = AC100_sig['PosMatrix'][AC100_ObjName]['Time']
      Value = AC100_sig['PosMatrix'][AC100_ObjName]['Stand_b']
      if signal_plotable(Time, Value):
        Client.addSignal2Axis(Axis, "AC100 Stationary (+2)", Time, Value+2, unit="", color=AC100_color)
      
      # -----------------------------------------------    
      # AESB Warning based on CIPV  
      Axis = Client.addAxis()
      
      # ego vehicle
      ego ={}
      ego['vx']   = CVR3_sig['EgoVeh']["vxvRef"]
      ego['ax']   = CVR3_sig['EgoVeh']["axvRef"] 

      # obstacle
      obs = {}
      obs['dx']   =  CVR3_sig['PosMatrix'][CVR3_ObjName]['dx']
      obs['vRel'] =  CVR3_sig['PosMatrix'][CVR3_ObjName]['vx']
      obs['aRel'] =  CVR3_sig['PosMatrix'][CVR3_ObjName]['ax']

      
      myCalcAEBS = kbtools_user.cCalcAEBS()
  
      '''
      # ------------------------------------------------------
      # cpr_CalcaAvoidance
      #  this is the pure avoidance acceleration without any delay or partial braking
      dxSecure = 2.5  # final safety distance to obstacle
      aAvoidance,Situation,UndefinedaAvoidDueToWrongdxSecure = myCalcAEBS.cpr_CalcaAvoidance(ego, obs, dxSecure)
      '''
      
      '''
      # ------------------------------------------------------
      # aAvoidancePredictedModelbased
      #  this algorithm 
      #    - uses a gradient to describe acceleration changes
      #    - is not used in the ECU because actual behaviour is more like a pure delay
      
      # parameters
      par = {}
      par['tWarn']                =   0.6
      par['tPrediction']          =   0.8
      par['P_aStdPartialBraking'] =  -3.0
      par['P_aEmergencyBrake']    =  -5.0
      par['P_aGradientBrake']     = -10.0
      aAvoidancePredicted,Situation,CollisionOccuredTillTPredict = myCalcAEBS.cpr_CalcaAvoidancePredictedModelbased(ego, obs, dxSecure, par)
      '''
      
      # ------------------------------------------------------
      # cpr_CalcaAvoidancePredictedCascade
      #  this algorithm 
      #    - uses delays to describe acceleration changes
      #    - is used in the ECU
      dxSecure                    = 2.5   # final safety distance to obstacle
      par = {}
      par['tWarn']                = 0.6   # time between prewarning and first brake intervention
      par['tPartBraking']         = 0.8   # time of partial praking
      par['tBrakeDelay1']         = 0.35  # Delay of the brake system to realize the requested deceleration at first request
      par['tBrakeDelay2']         = 0.21  # Delay of the brake system to realize the requested deceleration at request changes
      par['axvPartialBraking']    = -3.0  # Deceleration by reaction time gain standard
      par['axvFullBraking']       = -5.0  # Deceleration by reaction time gain extenden

      aAvoidancePredicted,Situation,CollisionOccuredTillTPredict = myCalcAEBS.cpr_CalcaAvoidancePredictedCascade(ego, obs, dxSecure, par)
      
      
      Time  = CVR3_sig['PosMatrix'][CVR3_ObjName]['Time']
      Client.addSignal2Axis(Axis, "CVR3 AEBS", Time, aAvoidancePredicted, unit="m/s^2", color=CVR3_color)
      
      # -----------------------------------------------     
      # online warning (generated inside the sensor )
      Axis = Client.addAxis()
      #Time, Value = interface.Source.getSignalFromSignalGroup(Group, "repPreStatus")
      #Value = Value == 6
      #Client.addSignal2Axis(Axis, "CVR3 Warning", Time, Value, unit="", color=CVR3_color)
     
      Time  = CVR3_sig['ASF']['Time']
      Value = CVR3_sig['ASF']['FirstWarning']
      Client.addSignal2Axis(Axis, "CVR3 Warning", Time, Value, unit="", color=CVR3_color)

      
      
      
      pass
    pass



