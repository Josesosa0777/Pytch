'''

   CIPV - Closest In Path Vehicle
   
   for radar sensor CVR3
   
   - CVR3:    Position Matrix L1 (first object in same lane)
   
   Ulrich Guecker 
   2012-10-21

'''


import datavis
import measparser
import interface

import kbtools_user   # required for cDataCVR3 and cDataAC100

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
      Client = datavis.cPlotNavigator(title="CVR3 - first left lane (L1)", figureNr=None)
      interface.Sync.addClient(Client)

      # ---------------------------------------------------------------------------
      # load signals      
      # CVR3 
      CVR3_sig = kbtools_user.cDataCVR3.load_CVR3_from_Source(interface.Source)
      CVR3_ObjName = 'L1'
      CVR3_color_Fusion = 'b'    # blue
      CVR3_color_Radar = 'r'     # red
      CVR3_color_Video = 'g'     # green
      
      
      
      
     
      
     
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
      Client.addSignal2Axis(Axis, "L1", Time, Value, unit="", color='b')


      Time  = CVR3_sig['PosMatrix'][CVR3_ObjName]['Time']
      Value = CVR3_sig['PosMatrix'][CVR3_ObjName]['AdditionalSensorAssociated_b']+2.0
      Client.addSignal2Axis(Axis, "Associated+2", Time, Value, unit="", color='r')

      
      # -----------------------------------------------    
      # longitudinal distance to CIPV
      Axis = Client.addAxis()
     
      # CVR3 
      Time  = CVR3_sig['PosMatrix'][CVR3_ObjName]['Time']
      Value = CVR3_sig['PosMatrix'][CVR3_ObjName]['dx_VID']
      Client.addSignal2Axis(Axis, "dx Video", Time, Value, unit="m", color=CVR3_color_Video)

      Time  = CVR3_sig['PosMatrix'][CVR3_ObjName]['Time']
      Value = CVR3_sig['PosMatrix'][CVR3_ObjName]['dx_OHY']
      Client.addSignal2Axis(Axis, "dx Radar", Time, Value, unit="m", color=CVR3_color_Radar)

      Time  = CVR3_sig['PosMatrix'][CVR3_ObjName]['Time']
      Value = CVR3_sig['PosMatrix'][CVR3_ObjName]['dx']
      Client.addSignal2Axis(Axis, "dx Fusion", Time, Value, unit="m", color=CVR3_color_Fusion)

                
      # -----------------------------------------------    
      # lateral distance to CIPV
      Axis = Client.addAxis()
     
      # CVR3 
      Time  = CVR3_sig['PosMatrix'][CVR3_ObjName]['Time']
      Value = CVR3_sig['PosMatrix'][CVR3_ObjName]['dy_VID']
      Client.addSignal2Axis(Axis, "dy Video", Time, Value, unit="m", color=CVR3_color_Video)

      Time  = CVR3_sig['PosMatrix'][CVR3_ObjName]['Time']
      Value = CVR3_sig['PosMatrix'][CVR3_ObjName]['dy_OHY']
      Client.addSignal2Axis(Axis, "dy Radar", Time, Value, unit="m", color=CVR3_color_Radar)

      Time  = CVR3_sig['PosMatrix'][CVR3_ObjName]['Time']
      Value = CVR3_sig['PosMatrix'][CVR3_ObjName]['dy']
      Client.addSignal2Axis(Axis, "dy Fusion", Time, Value, unit="m", color=CVR3_color_Fusion)

      # -----------------------------------------------    
      # Width
      Axis = Client.addAxis()

      Time  = CVR3_sig['PosMatrix'][CVR3_ObjName]['Time']
      Value = CVR3_sig['PosMatrix'][CVR3_ObjName]['dWidth']
      Client.addSignal2Axis(Axis, "Width", Time, Value, unit="", color='b')

      
      # -----------------------------------------------    
      # CIPV is detected as stationary 
      Axis = Client.addAxis()
     
      # CVR3 
      Time  = CVR3_sig['PosMatrix'][CVR3_ObjName]['Time']
      Value = CVR3_sig['PosMatrix'][CVR3_ObjName]['Stand_b']
      Client.addSignal2Axis(Axis, "Stationary", Time, Value, unit="", color='b')
  
      # AESB Warning based on CIPV  

      Time  = CVR3_sig['ASF']['Time']
      Value = CVR3_sig['ASF']['FirstWarning']+2.0
      Client.addSignal2Axis(Axis, "AEBS Warning+2", Time, Value, unit="", color='r')
      
      # -----------------------------------------------    
      # Position Matrix 
      Axis = Client.addAxis()
     
      # CVR3 
      Time  = CVR3_sig['PosMatrix']['L1']['Time']
      Value = CVR3_sig['PosMatrix']['L1']['Valid']+4.0
      Client.addSignal2Axis(Axis, "L1+4", Time, Value, unit="", color='g')

      Time  = CVR3_sig['PosMatrix']['S1']['Time']
      Value = CVR3_sig['PosMatrix']['S1']['Valid']+2.0
      Client.addSignal2Axis(Axis, "S1+2", Time, Value, unit="", color='b')
     
      Time  = CVR3_sig['PosMatrix']['R1']['Time']
      Value = CVR3_sig['PosMatrix']['R1']['Valid']
      Client.addSignal2Axis(Axis, "R1", Time, Value, unit="", color='r')

      
      
      pass
    pass



