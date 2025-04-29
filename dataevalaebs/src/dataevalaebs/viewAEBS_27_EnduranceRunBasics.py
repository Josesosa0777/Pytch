"""
:Organization: Knorr-Bremse SfN GmbH T/CES3.2 (BU2) Budapest Schwieberdingen T/CES3.2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""
import datavis
import measparser
import interface

DefParam = interface.NullParam

SignalGroups = [{"Buzzer": ("PGNFFB2", "Buzzer"),
                 "XBR_Control_Mode": ("XBR-8C040B2A", "XBR_Control_Mode"),
                 "repprew.__b_Rep.__b_RepBase.status": ("ECU", "repprew.__b_Rep.__b_RepBase.status"),
                 "repretg.__b_Rep.__b_RepBase.status": ("ECU", "repretg.__b_Rep.__b_RepBase.status"),
                 "repdesu.__b_Rep.__b_RepBase.status": ("ECU", "repdesu.__b_Rep.__b_RepBase.status"),
                 "repretg.ExtendedRETGinProgress_b": ("ECU", "repretg.ExtendedRETGinProgress_b"),
                 "namespaceSIT._.Egve._.pBrake_uw": ("ECU", "namespaceSIT._.Egve._.pBrake_uw"),
                 "csi.DriverActions_T20.fak1uGPPos": ("ECU", "csi.DriverActions_T20.fak1uGPPos"),
                 "Mrf._.PssObjectDebugInfo.vxv": ("ECU", "Mrf._.PssObjectDebugInfo.vxv"),
                 "csi.VelocityData_T20.vDis": ("ECU", "csi.VelocityData_T20.vDis"),
                 "Mrf._.PssObjectDebugInfo.dxv": ("ECU", "Mrf._.PssObjectDebugInfo.dxv"),
                 "Mrf._.PssObjectDebugInfo.dyv": ("ECU", "Mrf._.PssObjectDebugInfo.dyv"),
                 "sit.IntroFinder_TC.Intro.i0.Id": ("ECU", "sit.IntroFinder_TC.Intro.i0.Id"),
                 "Ext_Acceleration_Demand": ("XBR-8C040B2A", "Ext_Acceleration_Demand"),
                 "csi.XCustomerData_T20.CustData.flags.MO_Kickdown_b": ("ECU", "csi.XCustomerData_T20.CustData.flags.MO_Kickdown_b"),},]

class cView(interface.iView):
  @classmethod
  def view(cls, Param=DefParam):
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except measparser.signalgroup.SignalGroupError, error:
      print __file__
      print error.message
    else:
      Client = datavis.cPlotNavigator(title="Endurance Run Basics 1/2", figureNr=None)
      interface.Sync.addClient(Client)
      
      Axis = Client.addAxis()
      
      # Display buzzer with offset
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "Buzzer")
      Client.addSignal2Axis(Axis, "AEBS_acoust_act_CAN", Time, (Value+2), unit="B+2", color='b')
      
      # Check XBR_Control_Mode if active
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "XBR_Control_Mode")
      Client.addSignal2Axis(Axis, "AEBS_braking_act_CAN", Time, (Value != 0), unit="B", color='r')
      
      Axis = Client.addAxis()
      
      # Check REP if locked and display with offset
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "repprew.__b_Rep.__b_RepBase.status")
      Client.addSignal2Axis(Axis, "AEBS_acoust_act_SW", Time, ((Value == 6)+6), unit="B+6", color='b')
      
      # Check REP if locked and display with offset
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "repretg.__b_Rep.__b_RepBase.status")
      Client.addSignal2Axis(Axis, "AEBS_braking_act_SW", Time, ((Value == 6)+4), unit="B+4", color='r')
      
      # Check REP if locked and display with offset
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "repdesu.__b_Rep.__b_RepBase.status")
      Client.addSignal2Axis(Axis, "AEBS_desu_act_SW", Time, ((Value == 6)+2), unit="B+2", color='g')
      
      # Check REPRETG if in extended mode
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "repretg.ExtendedRETGinProgress_b")
      Client.addSignal2Axis(Axis, "AEBS_targetbraking_act_SW", Time, Value, unit="B", color='k')
      
      Axis = Client.addAxis()
      
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "Ext_Acceleration_Demand")
      Client.addSignal2Axis(Axis, "Acceleration_Demand_CAN", Time, Value, unit="m/s2")
      
      Axis = Client.addAxis()
      
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "namespaceSIT._.Egve._.pBrake_uw")
      Client.addSignal2Axis(Axis, "Brakepedal_SW", Time, Value, unit="%", color='r')
      
      # Get Accelerationpedal and convert to %
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.DriverActions_T20.fak1uGPPos")
      Client.addSignal2Axis(Axis, "Accelerationpedal_SW", Time, (Value*100), unit="%", color='b')
      
      # Check for GP-Kickdown and multiply with 10 for better viewing
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.XCustomerData_T20.CustData.flags.MO_Kickdown_b")
      Client.addSignal2Axis(Axis, "GPKickdown_act_SW", Time, (Value*10), unit="B*10", color='g')
      
      
          
      
      Client = datavis.cPlotNavigator(title="Endurance Run Basics 2/2", figureNr=None)
      interface.Sync.addClient(Client)
      
      Axis = Client.addAxis()
      
      # Check for SAM-intro
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "sit.IntroFinder_TC.Intro.i0.Id")
      Client.addSignal2Axis(Axis, "Same_Approach_Moving", Time, ((Value == 1)+2), unit="B+2", color='b')
      
      # Check for SAS-intro
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "sit.IntroFinder_TC.Intro.i0.Id")
      Client.addSignal2Axis(Axis, "Same_Approach_Standing", Time, (Value == 3), unit="B", color='r')
      
      Axis = Client.addAxis()
      
      # Get object relative speed and convert to km/h
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "Mrf._.PssObjectDebugInfo.vxv")
      Client.addSignal2Axis(Axis, "Inv_Object_Relative_Speed_SW", Time, (Value*-3.6), unit="-km/h", color='r')
      
      # Get ego absolute speed and convert to km/h
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VelocityData_T20.vDis")
      Client.addSignal2Axis(Axis, "Ego_Absolute_Speed_SW", Time, (Value*3.6), unit="km/h", color='b')
      
      Axis = Client.addAxis()
      
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "Mrf._.PssObjectDebugInfo.dxv")
      Client.addSignal2Axis(Axis, "Object_Longitudinal_Distance_SW", Time, Value, unit="m")
      
      Axis = Client.addAxis()
      
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "Mrf._.PssObjectDebugInfo.dyv")
      Client.addSignal2Axis(Axis, "Object_Lateral_Distance_SW", Time, Value, unit="m")
      
      pass
    pass
