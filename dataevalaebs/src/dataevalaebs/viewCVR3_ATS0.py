'''

   CVR3 ATS0 Object
   
   ACC Target Selection - ACC Target = CIPV for ACC
   
   
   Ulrich Guecker 
   2012-10-29

'''


import datavis
import measparser
import interface

import kbtools_user   # required for cDataCVR3

DefParam = interface.NullParam

                
device = "RadarFC"
SignalGroups = [{"evi.General_T20.vxvRef": (device, "evi.General_T20.vxvRef"),
                 "repPreStatus"          : (device, "repprew.__b_Rep.__b_RepBase.status")
                },]

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
      Client = datavis.cPlotNavigator(title="CVR3 - ACC Target Selection CIPV (ATS0)", figureNr=None)
      interface.Sync.addClient(Client)

      # ---------------------------------------------------------------------------
      # load signals      
      # CVR3 
      CVR3_sig = kbtools_user.cDataCVR3.load_CVR3_from_Source(interface.Source)
      CVR3_ObjName = 0           # ATS0
         
     
      
     
      # -----------------------------------------------     
      # vehicle speed 
      Axis = Client.addAxis()
      Time  = CVR3_sig['EgoVeh']["Time"]
      Value = CVR3_sig['EgoVeh']["vxvRef"]
      Client.addSignal2Axis(Axis, "veh speed", Time, Value*3.6, unit="kph")
     
     
      # -----------------------------------------------    
      # ATS0 availability
      Axis = Client.addAxis()
     
      # CVR3 
      Time  = CVR3_sig['ATS'][CVR3_ObjName]['Time']
      Value = CVR3_sig['ATS'][CVR3_ObjName]['Valid']
      Client.addSignal2Axis(Axis, "ATS0 valid", Time, Value, unit="", color='b')

      
      # -----------------------------------------------    
      # longitudinal distance to ATS0
      Axis = Client.addAxis()
     
      Time  = CVR3_sig['ATS'][CVR3_ObjName]['Time']
      Value = CVR3_sig['ATS'][CVR3_ObjName]['dx']
      Client.addSignal2Axis(Axis, "dx", Time, Value, unit="m", color='b')

                
      # -----------------------------------------------    
      # lateral distance to CIPV
      Axis = Client.addAxis()
     
      # CVR3 - dy
      Time  = CVR3_sig['ATS'][CVR3_ObjName]['Time']
      Value = CVR3_sig['ATS'][CVR3_ObjName]['dy']
      Client.addSignal2Axis(Axis, "dy", Time, Value, unit="m", color='b')

      # CVR3 - dycAct
      Time  = CVR3_sig['ATS'][CVR3_ObjName]['Time']
      Value = CVR3_sig['ATS'][CVR3_ObjName]['dycAct']
      Client.addSignal2Axis(Axis, "dycAct", Time, Value, unit="m", color='r')

      # CVR3 - dycHist
      Time  = CVR3_sig['ATS'][CVR3_ObjName]['Time']
      Value = CVR3_sig['ATS'][CVR3_ObjName]['dycHist']
      Client.addSignal2Axis(Axis, "dycHist", Time, Value, unit="m", color='g')

   
      
      # -----------------------------------------------    
      # vx 
      Axis = Client.addAxis()

      Time  = CVR3_sig['ATS'][CVR3_ObjName]['Time']
      Value = CVR3_sig['ATS'][CVR3_ObjName]['vx']
      Client.addSignal2Axis(Axis, "vx", Time, Value, unit="", color='b')

      
      # -----------------------------------------------    
      # flags 
      Axis = Client.addAxis()
     
      # CVR3 
      Time  = CVR3_sig['ATS'][CVR3_ObjName]['Time']
      Value = CVR3_sig['ATS'][CVR3_ObjName]['LeftLane_b']+4.0
      Client.addSignal2Axis(Axis, "LeftLane_b + 4", Time, Value, unit="", color='g')
  
      Time  = CVR3_sig['ATS'][CVR3_ObjName]['Time']
      Value = CVR3_sig['ATS'][CVR3_ObjName]['OwnLane_b']+2.0
      Client.addSignal2Axis(Axis, "OwnLane_b + 2", Time, Value, unit="", color='b')
  
      Time  = CVR3_sig['ATS'][CVR3_ObjName]['Time']
      Value = CVR3_sig['ATS'][CVR3_ObjName]['RightLane_b']
      Client.addSignal2Axis(Axis, "RightLane_b + 2", Time, Value, unit="", color='r')
     
      
      # -----------------------------------------------    
      # Lane Probability  
      Axis = Client.addAxis()
     
      Time  = CVR3_sig['ATS'][CVR3_ObjName]['Time']
      Value = CVR3_sig['ATS'][CVR3_ObjName]['lpb']
      Client.addSignal2Axis(Axis, "lpb", Time, Value, unit="", color='b')
      
      # -----------------------------------------------    
      # Lane Plausibility  
      Axis = Client.addAxis()
     
      Time  = CVR3_sig['ATS'][CVR3_ObjName]['Time']
      Value = CVR3_sig['ATS'][CVR3_ObjName]['plaus']
      Client.addSignal2Axis(Axis, "plaus", Time, Value, unit="", color='b')
      
      Time  = CVR3_sig['ATS'][CVR3_ObjName]['Time']
      Value = CVR3_sig['ATS'][CVR3_ObjName]['wCutIn']
      Client.addSignal2Axis(Axis, "plaus", Time, Value, unit="", color='g')

      pass
    pass



