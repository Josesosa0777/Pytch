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

SignalGroups = [{"fus.General_T20.aRefSync": ("ECU", "fus.General_T20.aRefSync"),
                 "fus.General_TC.aRefSync": ("ECU", "fus.General_TC.aRefSync"),
                 "mastsam.__b_Mst.activePhase": ("ECU", "mastsam.__b_Mst.activePhase"),
                 "pressam.ShotTheDeputy_RETG": ("ECU", "pressam.ShotTheDeputy_RETG"),
                 "repretg.DriverEnable_b": ("ECU", "repretg.DriverEnable_b"),
                 "repretg.EnableREPRETG_b": ("ECU", "repretg.EnableREPRETG_b"),
                 "repretg.ShotTheSheriff": ("ECU", "repretg.ShotTheSheriff"),
                 "repretg.__b_Rep.__b_RepBase.ExecutionStatus": ("ECU", "repretg.__b_Rep.__b_RepBase.ExecutionStatus"),
                 "repretg.__b_Rep.__b_RepBase.status": ("ECU", "repretg.__b_Rep.__b_RepBase.status"),
                 "repretg.aAvoid_DEBUG": ("ECU", "repretg.aAvoid_DEBUG"),
                 "repretg.aPartialBraking": ("ECU", "repretg.aPartialBraking"),
                 "repretg.tAcoActivationTimer": ("ECU", "repretg.tAcoActivationTimer"),
                 "repretg.tActivationTimer": ("ECU", "repretg.tActivationTimer"),
                 "repretg.tBlockingTimer": ("ECU", "repretg.tBlockingTimer"),},]

class cView(interface.iView):
  @classmethod
  def view(Sync, cls, Param=DefParam): 
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except measparser.signalgroup.SignalGroupError, error:
      print __file__
      print error.message
    else:
      #######
      #RETG #
      #######
      Client = datavis.cPlotNavigator(title="retg", figureNr=204) 
      interface.Sync.addClient(Client)
      y_limits = [-1,11]
      Client.addsignal('shot_dep_retg []', interface.Source.getSignalFromSignalGroup(Group, "pressam.ShotTheDeputy_RETG"),
                       'shot_sher_retg []', interface.Source.getSignalFromSignalGroup(Group, "repretg.ShotTheSheriff"),ylim=y_limits)
      Client.addsignal('rep_status_retg []', interface.Source.getSignalFromSignalGroup(Group, "repretg.__b_Rep.__b_RepBase.status"),
                       'rep_exec_status_deretg []', interface.Source.getSignalFromSignalGroup(Group, "repretg.__b_Rep.__b_RepBase.ExecutionStatus"),	
                       'mast_sam_act_phase[]', interface.Source.getSignalFromSignalGroup(Group, "mastsam.__b_Mst.activePhase"),
                       'repretg.DriverEnable[]', interface.Source.getSignalFromSignalGroup(Group, "repretg.DriverEnable_b"),
                       'enable_rep_retg[]', interface.Source.getSignalFromSignalGroup(Group, "repretg.EnableREPRETG_b"),ylim=y_limits)
      Client.addsignal('a_avoid_debug [m/ss]', interface.Source.getSignalFromSignalGroup(Group, "repretg.aAvoid_DEBUG"),
                       'a_Ref_sync_T20 [m/ss]', interface.Source.getSignalFromSignalGroup(Group, "fus.General_T20.aRefSync"),
                       'a_Ref_sync_TC [m/ss]', interface.Source.getSignalFromSignalGroup(Group, "fus.General_TC.aRefSync"),
                       'a_Partial_brake [m/ss]', interface.Source.getSignalFromSignalGroup(Group, "repretg.aPartialBraking"))
      Client.addsignal('t_act_retg []', interface.Source.getSignalFromSignalGroup(Group, "repretg.tActivationTimer"),
                       't_act_aco_retg []', interface.Source.getSignalFromSignalGroup(Group, "repretg.tAcoActivationTimer"),
                       't_block_retg[]', interface.Source.getSignalFromSignalGroup(Group, "repretg.tBlockingTimer"))
      return []

