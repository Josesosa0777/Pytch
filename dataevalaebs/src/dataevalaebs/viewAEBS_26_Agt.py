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

SignalGroups = [{"asaxsex.__b_Agt.plaus": ("ECU", "asaxsex.__b_Agt.plaus"),
                 "asaxsex.__b_Agt.skill": ("ECU", "asaxsex.__b_Agt.skill"),
                 "asaxsex.__b_Agt.skillW": ("ECU", "asaxsex.__b_Agt.skillW"),
                 #"asaxsex.__b_Agt.status": ("ECU", "asaxsex.__b_Agt.status"),
                 "asamlam.__b_ASxxLxx.__b_Agt.plaus": ("ECU", "asamlam.__b_ASxxLxx.__b_Agt.plaus"),
                 "asamlam.__b_ASxxLxx.__b_Agt.skill": ("ECU", "asamlam.__b_ASxxLxx.__b_Agt.skill"),
                 "asamlam.__b_ASxxLxx.__b_Agt.skillW": ("ECU", "asamlam.__b_ASxxLxx.__b_Agt.skillW"),
                 #"asamlam.__b_ASxxLxx.__b_Agt.status": ("ECU", "asamlam.__b_ASxxLxx.__b_Agt.status"),
                 "asamram.__b_ASxxRxx.__b_Agt.plaus": ("ECU", "asamram.__b_ASxxRxx.__b_Agt.plaus"),
                 "asamram.__b_ASxxRxx.__b_Agt.skill": ("ECU", "asamram.__b_ASxxRxx.__b_Agt.skill"),
                 "asamram.__b_ASxxRxx.__b_Agt.skillW": ("ECU", "asamram.__b_ASxxRxx.__b_Agt.skillW"),
                 #"asamram.__b_ASxxRxx.__b_Agt.status": ("ECU", "asamram.__b_ASxxRxx.__b_Agt.status"),
                 "axamxam.__b_AXaxXax.__b_Agt.plaus": ("ECU", "axamxam.__b_AXaxXax.__b_Agt.plaus"),
                 "axamxam.__b_AXaxXax.__b_Agt.skill": ("ECU", "axamxam.__b_AXaxXax.__b_Agt.skill"),
                 #"axamxam.__b_AXaxXax.__b_Agt.status": ("ECU", "axamxam.__b_AXaxXax.__b_Agt.status"),
                 "axamxam.__b_AXaxXax.__b_Agt.skillW": ("ECU", "axamxam.__b_AXaxXax.__b_Agt.skillW"),},]

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
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "asaxsex.__b_Agt.plaus")
      PlausSAXSEX = Value
      Client.addSignal2Axis(Axis, "asaxsex.__b_Agt.plaus", Time, Value, unit="-")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "asaxsex.__b_Agt.skill")
      SkillSAXSEX = Value
      Client.addSignal2Axis(Axis, "asaxsex.__b_Agt.skill", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "asaxsex.__b_Agt.skillW")
      SkillWSAXSEX = Value
      Client.addSignal2Axis(Axis, "asaxsex.__b_Agt.skillW", Time, Value, unit="")
      #Time, Value = interface.Source.getSignalFromSignalGroup(Group, "asaxsex.__b_Agt.status")
      #Client.addSignal2Axis(Axis, "asaxsex.__b_Agt.status", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "asamlam.__b_ASxxLxx.__b_Agt.plaus")
      PlausSAMLAM = Value
      Client.addSignal2Axis(Axis, "asamlam.__b_ASxxLxx.__b_Agt.plaus", Time, Value, unit="-")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "asamlam.__b_ASxxLxx.__b_Agt.skill")
      SkillSAMLAM = Value
      Client.addSignal2Axis(Axis, "asamlam.__b_ASxxLxx.__b_Agt.skill", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "asamlam.__b_ASxxLxx.__b_Agt.skillW")
      Client.addSignal2Axis(Axis, "asamlam.__b_ASxxLxx.__b_Agt.skillW", Time, Value, unit="")
      #Time, Value = interface.Source.getSignalFromSignalGroup(Group, "asamlam.__b_ASxxLxx.__b_Agt.status")
      #Client.addSignal2Axis(Axis, "asamlam.__b_ASxxLxx.__b_Agt.status", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "asamram.__b_ASxxRxx.__b_Agt.plaus")
      PlausSAMRAM = Value
      Client.addSignal2Axis(Axis, "asamram.__b_ASxxRxx.__b_Agt.plaus", Time, Value, unit="-")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "asamram.__b_ASxxRxx.__b_Agt.skill")
      SkillSAMRAM = Value
      Client.addSignal2Axis(Axis, "asamram.__b_ASxxRxx.__b_Agt.skill", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "asamram.__b_ASxxRxx.__b_Agt.skillW")
      Client.addSignal2Axis(Axis, "asamram.__b_ASxxRxx.__b_Agt.skillW", Time, Value, unit="")
      #Time, Value = interface.Source.getSignalFromSignalGroup(Group, "asamram.__b_ASxxRxx.__b_Agt.status")
      #Client.addSignal2Axis(Axis, "asamram.__b_ASxxRxx.__b_Agt.status", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "axamxam.__b_AXaxXax.__b_Agt.plaus")
      PlausXAMXAM = Value
      Client.addSignal2Axis(Axis, "axamxam.__b_AXaxXax.__b_Agt.plaus", Time, Value, unit="-")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "axamxam.__b_AXaxXax.__b_Agt.skill")
      SkillXAMXAM = Value
      Client.addSignal2Axis(Axis, "axamxam.__b_AXaxXax.__b_Agt.skill", Time, Value, unit="")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "axamxam.__b_AXaxXax.__b_Agt.skillW")
      Client.addSignal2Axis(Axis, "axamxam.__b_AXaxXax.__b_Agt.skillW", Time, Value, unit="")
      #Time, Value = interface.Source.getSignalFromSignalGroup(Group, "axamxam.__b_AXaxXax.__b_Agt.status")
      #Client.addSignal2Axis(Axis, "axamxam.__b_AXaxXax.__b_Agt.status", Time, Value, unit="")
      
      Axis = Client.addAxis()
      result = SkillSAXSEX.copy()
      # Define Parameters (see PAD_Gen and Code)
      BrakingSkillMinLeave = 16.5
      BrakingSkillWMinLeave = 20.5
      SteeringSkillMinLeave = 38.9
      NeutralPlaus = 0.5
      MediumPlaus = 0.75

      # Calculate MastSAM_PhaseSwitchRequired_B
      for i in range(len(SkillSAXSEX)):
          if (((SkillSAXSEX[i] != 0) and (SkillSAMLAM[i] !=0) and (SkillSAMRAM[i] !=0) and ((SkillXAMXAM[i] !=0 or PlausXAMXAM[i] == NeutralPlaus))) 
          and (((SkillSAXSEX[i] >= BrakingSkillMinLeave) and (PlausSAXSEX[i] > NeutralPlaus)) 
            or ((SkillSAMLAM[i] >= SteeringSkillMinLeave) and (PlausSAMLAM[i] > MediumPlaus)) 
            or ((SkillSAMRAM[i] >= SteeringSkillMinLeave) and (PlausSAMRAM[i] > MediumPlaus)) 
            or ((SkillSAMLAM[i] >= SteeringSkillMinLeave) and (SkillSAMRAM[i] >= SteeringSkillMinLeave) and (PlausSAMLAM[i] == MediumPlaus) and (PlausSAMRAM[i] == MediumPlaus)) 
            or ((PlausSAXSEX[i] <= NeutralPlaus) and (PlausSAMLAM[i] <= NeutralPlaus) and (PlausSAMRAM[i] <= NeutralPlaus) and (SkillWSAXSEX[i] >= BrakingSkillWMinLeave)))):
              result[i] = 1
          else:
              result[i] = 0

      # Plot MastSAM_PhaseSwitchRequired_B
      Client.addSignal2Axis(Axis, "MastSAM_PhaseSwitchRequired_B", Time, result, unit="B")
      pass
    pass
