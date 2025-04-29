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

SignalGroups = [{"XBR_Control_Mode": ("XBR", "XBR_Control_Mode"),
                 "mastsam.__b_Mst.activePhase": ("ECU", "mastsam.__b_Mst.activePhase"),
                 "namespaceSIT._.Egve._.pBrake_uw": ("ECU", "namespaceSIT._.Egve._.pBrake_uw"),
                 "padasf_x_par_a.REPDESUGPPosDriverMax": ("ECU", "padasf_x_par_a.REPDESUGPPosDriverMax"),
                 "padasf_x_par_a.REPDESUaAvoidThresholdStartSTD": ("ECU", "padasf_x_par_a.REPDESUaAvoidThresholdStartSTD"),
                 "padasf_x_par_a.REPDESUaAvoidThresholdStopRED": ("ECU", "padasf_x_par_a.REPDESUaAvoidThresholdStopRED"),
                 "padasf_x_par_a.REPDESUaAvoidThresholdStopSTD": ("ECU", "padasf_x_par_a.REPDESUaAvoidThresholdStopSTD"),
                 "padasf_x_par_a.REPDESUaBrakeMinBaseValue": ("ECU", "padasf_x_par_a.REPDESUaBrakeMinBaseValue"),
                 "padasf_x_par_a.REPDESUaBrakeMinStartRED": ("ECU", "padasf_x_par_a.REPDESUaBrakeMinStartRED"),
                 "padasf_x_par_a.REPDESUpBrakeMaxStop": ("ECU", "padasf_x_par_a.REPDESUpBrakeMaxStop"),
                 "padasf_x_par_a.REPDESUpBrakeMinStart": ("ECU", "padasf_x_par_a.REPDESUpBrakeMinStart"),
                 "padasf_x_par_a.REPDESUtActivationTimer": ("ECU", "padasf_x_par_a.REPDESUtActivationTimer"),
                 "padasf_x_par_a.REPDESUtBlockingTimer": ("ECU", "padasf_x_par_a.REPDESUtBlockingTimer"),
                 "padasf_x_par_a.REPDESUvEgoMinStart": ("ECU", "padasf_x_par_a.REPDESUvEgoMinStart"),
                 "padasf_x_par_a.REPDESUvEgoMinStop": ("ECU", "padasf_x_par_a.REPDESUvEgoMinStop"),
                 "pressam.ShotTheDeputy_DESU": ("ECU", "pressam.ShotTheDeputy_DESU"),
                 "repdesu.EnableREPDESU_b": ("ECU", "repdesu.EnableREPDESU_b"),
                 "repdesu.ShotTheSheriff": ("ECU", "repdesu.ShotTheSheriff"),
                 "repdesu.__b_Rep.__b_RepBase.ExecutionStatus": ("ECU", "repdesu.__b_Rep.__b_RepBase.ExecutionStatus"),
                 "repdesu.__b_Rep.__b_RepBase.status": ("ECU", "repdesu.__b_Rep.__b_RepBase.status"),
                 "repdesu.aAvoid": ("ECU", "repdesu.aAvoid"),
                 "repdesu.aAvoidThresholdStart": ("ECU", "repdesu.aAvoidThresholdStart"),
                 "repdesu.aAvoidThresholdStop": ("ECU", "repdesu.aAvoidThresholdStop"),
                 "repdesu.aDriverOffset": ("ECU", "repdesu.aDriverOffset"),
                 "repdesu.tAcoActivationTimer": ("ECU", "repdesu.tAcoActivationTimer"),
                 "repdesu.tActivationTimer": ("ECU", "repdesu.tActivationTimer"),
                 "repdesu.tBlockingTimer": ("ECU", "repdesu.tBlockingTimer"),},]

class cView(interface.iView):
  @classmethod
  def view(Sync, cls, Param=DefParam): 
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except measparser.signalgroup.SignalGroupError, error:
      print __file__
      print error.message
    else:
      ##############
      #DeSu analyze#
      ##############
      Client = datavis.cPlotNavigator(title="Deceleration_support", figureNr=205) 
      interface.Sync.addClient(Client) 
      Client.addsignal('shot_dep_desu []', interface.Source.getSignalFromSignalGroup(Group, "pressam.ShotTheDeputy_DESU"),
               'shot_sher_desu []', interface.Source.getSignalFromSignalGroup(Group, "repdesu.ShotTheSheriff"))
      Client.addsignal('rep_status_desu []', interface.Source.getSignalFromSignalGroup(Group, "repdesu.__b_Rep.__b_RepBase.status"),
               'rep_exec_status_desu []', interface.Source.getSignalFromSignalGroup(Group, "repdesu.__b_Rep.__b_RepBase.ExecutionStatus"),	
               'mast_sam_act_phase[]', interface.Source.getSignalFromSignalGroup(Group, "mastsam.__b_Mst.activePhase"),
               'enable_rep_desu[]', interface.Source.getSignalFromSignalGroup(Group, "repdesu.EnableREPDESU_b"))
      Client.addsignal('a_avoid_desu [m/ss]', interface.Source.getSignalFromSignalGroup(Group, "repdesu.aAvoid"),
               'a_avoid_stop_desu [m/ss]', interface.Source.getSignalFromSignalGroup(Group, "repdesu.aAvoidThresholdStop"),
               'a_Driver_offset[m/ss]', interface.Source.getSignalFromSignalGroup(Group, "repdesu.aDriverOffset"),
               'a_avoid_start_desu[m/ss]', interface.Source.getSignalFromSignalGroup(Group, "repdesu.aAvoidThresholdStart"))
      Client.addsignal('t_act_desu []', interface.Source.getSignalFromSignalGroup(Group, "repdesu.tActivationTimer"),
               't_act_aco_desu []', interface.Source.getSignalFromSignalGroup(Group, "repdesu.tAcoActivationTimer"),
               't_block_desu[]', interface.Source.getSignalFromSignalGroup(Group, "repdesu.tBlockingTimer"))
      Client.addsignal('pBrake[bar]', interface.Source.getSignalFromSignalGroup(Group, "namespaceSIT._.Egve._.pBrake_uw"))
      Client.addsignal('XBRControlMode[]', interface.Source.getSignalFromSignalGroup(Group, "XBR_Control_Mode"))       
      
      Client = datavis.cListNavigator(title="DeSu_parameter")
      interface.Sync.addClient(Client) 
      Client.addsignal('GPPosDriverMax [m/ss]', interface.Source.getSignalFromSignalGroup(Group, "padasf_x_par_a.REPDESUGPPosDriverMax"))
      Client.addsignal('aAvoidThresholdStartSTD [m/ss]', interface.Source.getSignalFromSignalGroup(Group, "padasf_x_par_a.REPDESUaAvoidThresholdStartSTD"))
      Client.addsignal('aAvoidThresholdStopRED [m/ss]', interface.Source.getSignalFromSignalGroup(Group, "padasf_x_par_a.REPDESUaAvoidThresholdStopRED"))
      Client.addsignal('aAvoidThresholdStopSTD [m/ss]', interface.Source.getSignalFromSignalGroup(Group, "padasf_x_par_a.REPDESUaAvoidThresholdStopSTD"))
      Client.addsignal('aBrakeMinBaseValue [m/ss]', interface.Source.getSignalFromSignalGroup(Group, "padasf_x_par_a.REPDESUaBrakeMinBaseValue"))
      Client.addsignal('aBrakeMinStartRED [m/ss]', interface.Source.getSignalFromSignalGroup(Group, "padasf_x_par_a.REPDESUaBrakeMinStartRED"))
      Client.addsignal('pBrakeMaxStop [bar]', interface.Source.getSignalFromSignalGroup(Group, "padasf_x_par_a.REPDESUpBrakeMaxStop"))
      Client.addsignal('pBrakeMinStart [bar]', interface.Source.getSignalFromSignalGroup(Group, "padasf_x_par_a.REPDESUpBrakeMinStart"))
      Client.addsignal('tActivationTimer [s]', interface.Source.getSignalFromSignalGroup(Group, "padasf_x_par_a.REPDESUtActivationTimer"))
      Client.addsignal('tBlockingTimer [s]', interface.Source.getSignalFromSignalGroup(Group, "padasf_x_par_a.REPDESUtBlockingTimer"))
      Client.addsignal('padasf_x_par_a.REPDESUvEgoMinStart[m/s]',interface.Source.getSignalFromSignalGroup(Group, "padasf_x_par_a.REPDESUvEgoMinStart"))
      Client.addsignal('padasf_x_par_a.REPDESUvEgoMinStop[m/s]',interface.Source.getSignalFromSignalGroup(Group, "padasf_x_par_a.REPDESUvEgoMinStop"))
      return []

