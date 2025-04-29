"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""
import datavis

def viewASF(Sync, Source, FgNr):
  """
  Create PlotNavigators to illustrate the ASF. 
  
  :Parameters:
    sync : `datavis.cSynchronizer`
      Synchronizer instance to connect the `datavis.cPlotNavigators`s.
    Source : `aebs.proc.cLrr3Source`
      Signal source to get mdf signals.
    FgNr : int
      Intialize the figure number of the first `datavis.cPlotNavigators`.
  :ReturnType: None
  """
  FUS_idx  = Source.getFUSIndexMode(0)  
  Intro    = Source.getSignalFromECU('sit.IntroFinder_TC.Intro.i0.ObjectList.i0')[1]
  RelGraph = Source.getSignalFromECU('sit.RelationGraph_TC.ObjectList.i%d' %(FUS_idx,))[1]
  SIT_idx  = Intro[Intro == RelGraph][0]

  "-------------------------------------------------------"
  "Active Safety Functions - Overview"  
  PN = datavis.cPlotNavigator('Active Safety Functions - Overview General', FgNr)
  PN.addsignal('vxvRef',
               Source.getSignalFromECU('evi.General_TC.vxvRef'),
               ylabel = '[m/s]')
  PN.addsignal('dxv',
               Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.dxv' %(FUS_idx,)),
               ylabel = '[m]')
  PN.addsignal('Intro - Id',
               Source.getSignalFromECU('sit.IntroFinder_TC.Intro.i0.Id'))
  PN.addsignal('mastsam - activePhase',
               Source.getSignalFromECU('mastsam.__b_Mst.activePhase'),
               'mastsas - activePhase',
               Source.getSignalFromECU('mastsas.__b_Mst.activePhase'),
               ylabel = 'Id')
  PN.addsignal('acoopti (+12)',
               Source.getSignalFromECU('acoopti.__b_AcoNoFb.__b_Aco.request_B'),
               'acoacoi (+10)',
               Source.getSignalFromECU('acoacoi.__b_AcoNoFb.__b_Aco.request_B'),
               'acobraj (+8)',
               Source.getSignalFromECU('acobraj.__b_AcoCoFb.__b_Aco.request_B'),
               'acoxbad (+6)',
               Source.getSignalFromECU('acoxbad.__b_AcoDece.__b_AcoCoFb.__b_Aco.request_B'),
               'acopebp (+4)',
               Source.getSignalFromECU('acopebp.__b_AcoDece.__b_AcoCoFb.__b_Aco.request_B'),
               'acopebe (+2)',
               Source.getSignalFromECU('acopebe.__b_AcoDece.__b_AcoCoFb.__b_Aco.request_B'),
               'acopebm',
               Source.getSignalFromECU('acopebm.__b_AcoDece.__b_AcoCoFb.__b_Aco.request_B'),
               offset = [12.0, 10.0, 8.0, 6.0, 4.0, 2.0, 0.0],
               ylabel = 'request',
               xlabel = 'time [s]')
  Sync.addClient(PN)

  "-------------------------------------------------------"
  "Active Safety Functions - Overview Agents"  
  PN = datavis.cPlotNavigator('Active Safety Functions - Overview Agents')

  PN.addsignal('mastsam - activePhase',
               Source.getSignalFromECU('mastsam.__b_Mst.activePhase'),
               'mastsas - activePhase',
               Source.getSignalFromECU('mastsas.__b_Mst.activePhase'),
               ylabel = 'Id')

  PN.addsignal('mastsam - status',
               Source.getSignalFromECU('mastsam.__b_Mst.status'),
               'mastsas - status',
               Source.getSignalFromECU('mastsas.__b_Mst.status'),
               ylabel = 'Id')

  PN.addsignal('asaxsex - plaus (+6)',
               Source.getSignalFromECU('asaxsex.__b_Agt.plaus'),
               'asasras - plaus (+4)',
               Source.getSignalFromECU('asasras.__b_ASxxRxx.__b_Agt.plaus'),
               'asaslas - plaus (+2)',
               Source.getSignalFromECU('asaslas.__b_ASxxLxx.__b_Agt.plaus'),
               'axasxas - plaus',
               Source.getSignalFromECU('axasxas.__b_AXaxXax.__b_Agt.plaus'),
               offset = [6.0, 4.0, 2.0, 0.0],
               ylabel = '[0..1]')

  PN.addsignal('asaxsex - skill',
               Source.getSignalFromECU('asaxsex.__b_Agt.skill'),
               'asaxsex - skillW',
               Source.getSignalFromECU('asaxsex.__b_Agt.skillW'),
               threshold = 0.35,
               factor    = [1.0/256.0, 1.0/256.0],
               ylabel = '[0..1]')

  PN.addsignal('asasras - skill',
               Source.getSignalFromECU('asasras.__b_ASxxRxx.__b_Agt.skill'),
               'asasras - skillW',
               Source.getSignalFromECU('asasras.__b_ASxxRxx.__b_Agt.skillW'),
               'asaslas - skill',
               Source.getSignalFromECU('asaslas.__b_ASxxLxx.__b_Agt.skill'),
               'asaslas - skillW',
               Source.getSignalFromECU('asaslas.__b_ASxxLxx.__b_Agt.skillW'),
               factor    = [1.0/256.0, 1.0/256.0, 1.0/256.0, 1.0/256.0],
               ylabel = '[0..1]')

  PN.addsignal('axasxas - skill',
               Source.getSignalFromECU('axasxas.__b_AXaxXax.__b_Agt.skill'),
               'axasxas - skillW',
               Source.getSignalFromECU('axasxas.__b_AXaxXax.__b_Agt.skillW'),
               factor    = [1.0/256.0, 1.0/256.0],
               ylabel = '[0..1]')
  
  PN.addsignal('acoopti+6',
               Source.getSignalFromECU('acoopti.__b_AcoNoFb.__b_Aco.request_B'),
               'acoacoi+4',
               Source.getSignalFromECU('acoacoi.__b_AcoNoFb.__b_Aco.request_B'),
               'acobraj+2',
               Source.getSignalFromECU('acobraj.__b_AcoCoFb.__b_Aco.request_B'),
               'acoxbad',
               Source.getSignalFromECU('acoxbad.__b_AcoDece.__b_AcoCoFb.__b_Aco.request_B'),
               offset = [6.0, 4.0, 2.0, 0.0],
               ylabel = 'request',
               xlabel = 'time')

  Sync.addClient(PN)

  "-------------------------------------------------------"
  "Drivers Demand"  
  PN = datavis.cPlotNavigator('Drivers Demand')

  PN.addsignal('evi - vxvRef',
               Source.getSignalFromECU('evi.General_TC.vxvRef'),
               'namespaceSIT - vx',
               Source.getSignalFromECU('namespaceSIT._.Egve._.vx_sw'),
               ylabel = '[m/s]')

  PN.addsignal('evi - axvRef',
               Source.getSignalFromECU('evi.General_TC.axvRef'),
               'namespaceSIT - ax',
               Source.getSignalFromECU('namespaceSIT._.Egve._.ax_sw'),
               ylabel = '[m/s^2]')

  PN.addsignal('GPPos * 100',
               Source.getSignalFromECU('namespaceSIT._.Egve._.GPPos_uw'),
               'pBrake',
               Source.getSignalFromECU('namespaceSIT._.Egve._.pBrake_uw'),
               factor    = [100.0, 1.0],
               ylabel = '[0..100]')

  PN.addsignal('BPAct',
               Source.getSignalFromECU('namespaceSIT._.Egve._.BPAct_b'),
               ylabel = '[bool]')

  PN.addsignal('alpWheelAngle',
               Source.getSignalFromECU('csi.VehicleData_TC.alpWheelAngle'),
               ylabel = '[degree]')

  PN.addsignal('alpDtSteeringWheel',
               Source.getSignalFromECU('namespaceSIT._.Egve._.alpDtSteeringWheel_sw'),
               ylabel = '[degree/s]')

  PN.addsignal('alpSteeringWheel Invalid',
               Source.getSignalFromECU('csi.VehicleData_TC.vehicleData.vehicleData.alpSteeringWheelInvalid_b'),
               ylabel = '[bool]',
               xlabel = 'time')

  Sync.addClient(PN)

  "-------------------------------------------------------"
  "Action coordinator - overview"  
  PN = datavis.cPlotNavigator('Action coordinator - overview')

  PN.addsignal('acoopti - status TC',
               Source.getSignalFromECU('acoopti.__b_AcoNoFb.__b_Aco.status'),
               'acoopti - status T20',
               Source.getSignalFromECU('asf.AcoStates_TC.acooptiState'),
               ylabel = '[id]')

  PN.addsignal('acoacoi - status TC',
               Source.getSignalFromECU('acoacoi.__b_AcoNoFb.__b_Aco.status'),
               'acoacoi - status T20',
               Source.getSignalFromECU('asf.AcoStates_TC.acoacoiState'),
               ylabel = '[id]')

  PN.addsignal('acobraj - status TC',
               Source.getSignalFromECU('acobraj.__b_AcoCoFb.__b_Aco.status'),
               'acobraj - status T20',
               Source.getSignalFromECU('asf.AcoStates_TC.acobrajState'),
               ylabel = '[id]')

  PN.addsignal('acoxbad - status TC',
               Source.getSignalFromECU('acoxbad.__b_AcoDece.__b_AcoCoFb.__b_Aco.status'),
               'acoxbad - status T20',
               Source.getSignalFromECU('asf.AcoStates_TC.acoxbadState'),
               ylabel = '[id]')

  PN.addsignal('acopebp - status TC',
               Source.getSignalFromECU('acopebp.__b_AcoDece.__b_AcoCoFb.__b_Aco.status'),
               'acopebp - status T20',
               Source.getSignalFromECU('asf.AcoStates_TC.acopebpState'),
               ylabel = '[id]')
  
  PN.addsignal('acopebe - status TC',
               Source.getSignalFromECU('acopebe.__b_AcoDece.__b_AcoCoFb.__b_Aco.status'),
               'acopebe - status T20',
               Source.getSignalFromECU('asf.AcoStates_TC.acopebeState'),
               ylabel = '[id]')

  PN.addsignal('acopebm - status TC',
               Source.getSignalFromECU('acopebm.__b_AcoDece.__b_AcoCoFb.__b_Aco.status'),
               'acopebm - status T20',
               Source.getSignalFromECU('asf.AcoStates_TC.acopebmState'),
               ylabel = '[id]',
               xlabel = 'time')
  Sync.addClient(PN)
  
  "-------------------------------------------------------"
  "Action coordinator - overview activation status"  
  PN = datavis.cPlotNavigator('Action coordinator - activation status')

  PN.addsignal('acoopti - activationStatus',
               Source.getSignalFromECU('acoopti.__b_AcoNoFb.__b_Aco.activationStatus_B'),
               ylabel = '[bool]')

  PN.addsignal('acoacoi - activationStatus',
               Source.getSignalFromECU('acoacoi.__b_AcoNoFb.__b_Aco.activationStatus_B'),
               ylabel = '[bool]')

  PN.addsignal('acobraj - activationStatus',
               Source.getSignalFromECU('acobraj.__b_AcoCoFb.__b_Aco.activationStatus_B'),
               ylabel = '[bool]')

  PN.addsignal('acoxbad - activationStatus',
               Source.getSignalFromECU('acoxbad.__b_AcoDece.__b_AcoCoFb.__b_Aco.activationStatus_B'),
               ylabel = '[bool]')

  PN.addsignal('acopebp - activationStatus',
               Source.getSignalFromECU('acopebp.__b_AcoDece.__b_AcoCoFb.__b_Aco.activationStatus_B'),
               ylabel = '[bool]')

  PN.addsignal('acopebe - activationStatus',
               Source.getSignalFromECU('acopebe.__b_AcoDece.__b_AcoCoFb.__b_Aco.activationStatus_B'),
               ylabel = '[bool]')

  PN.addsignal('acopebm - activationStatus',
               Source.getSignalFromECU('acopebm.__b_AcoDece.__b_AcoCoFb.__b_Aco.activationStatus_B'),
               ylabel = '[bool]',
               xlabel = 'time')
  Sync.addClient(PN)


  """
  tbd.
  %--------------------------------------------------------------------------   
  % action coordinator - optical warning

  %--------------------------------------------------------------------------   
  % action coordinator - acoustic warning

  %--------------------------------------------------------------------------   
  % action coordinator - brake jerk

  %--------------------------------------------------------------------------   
  % action coordinator - acoxbad

  """

  "-------------------------------------------------------"
  "Reaction pattern - overview"  
  PN = datavis.cPlotNavigator('Reaction pattern - overview')

  PN.addsignal('repprew - status',
               Source.getSignalFromECU('repprew.__b_Rep.__b_RepBase.status'),
               'repprew - ExecutionStatus',
               Source.getSignalFromECU('repprew.__b_Rep.__b_RepBase.ExecutionStatus'),
               ylabel = '[id]')

  PN.addsignal('repacuw - status',
               Source.getSignalFromECU('repacuw.__b_Rep.__b_RepBase.status'),
               'repacuw - ExecutionStatus',
               Source.getSignalFromECU('repacuw.__b_Rep.__b_RepBase.ExecutionStatus'),
               ylabel = '[id]')

  PN.addsignal('repinfo - status',
               Source.getSignalFromECU('repinfo.__b_Rep.__b_RepBase.status'),
               'repinfo - ExecutionStatus',
               Source.getSignalFromECU('repinfo.__b_Rep.__b_RepBase.ExecutionStatus'),
               ylabel = '[id]')

  PN.addsignal('repdesu - status',
               Source.getSignalFromECU('repdesu.__b_Rep.__b_RepBase.status'),
               'repdesu - ExecutionStatus',
               Source.getSignalFromECU('repdesu.__b_Rep.__b_RepBase.ExecutionStatus'),
               ylabel = '[id]')

  PN.addsignal('repretg - status',
               Source.getSignalFromECU('repretg.__b_Rep.__b_RepBase.status'),
               'repretg - ExecutionStatus',
               Source.getSignalFromECU('repretg.__b_Rep.__b_RepBase.ExecutionStatus'),
               ylabel = '[id]')

  PN.addsignal('repladi - status',
               Source.getSignalFromECU('repladi.__b_Rep.__b_RepBase.status'),
               'repladi - ExecutionStatus',
               Source.getSignalFromECU('repladi.__b_Rep.__b_RepBase.ExecutionStatus'),
               ylabel = '[id]',
               xlabel = 'time')
  Sync.addClient(PN)

  """
  tbd.
  reaction patterns - OperationPrevents
  %--------------------------------------------------------------------------   
  % reaction pattern - prewarning

  %--------------------------------------------------------------------------   
  % reaction pattern - acute warning
  """

  "-------------------------------------------------------"
  "Reaction pattern - deceleration support"  
  PN = datavis.cPlotNavigator('Reaction pattern - deceleration support')

  PN.addsignal('repdesu - status',
               Source.getSignalFromECU('repdesu.__b_Rep.__b_RepBase.status'),
               'repdesu - ExecutionStatus',
               Source.getSignalFromECU('repdesu.__b_Rep.__b_RepBase.ExecutionStatus'),
               ylabel = '[id]')

  PN.addsignal('repdesu - EnableREPDESU',
               Source.getSignalFromECU('repdesu.EnableREPDESU_b'),
               ylabel = '[id]')

  PN.addsignal('repdesu - aAvoid',
               Source.getSignalFromECU('repdesu.aAvoid'),
               'repdesu - aAvoidThresholdStart',
               Source.getSignalFromECU('repdesu.aAvoidThresholdStart'),
               'repdesu - aAvoidThresholdStop',
               Source.getSignalFromECU('repdesu.aAvoidThresholdStop'),
               ylabel = '[id]')

  PN.addsignal('repdesu - tActivationTimer',
               Source.getSignalFromECU('repdesu.tActivationTimer'),
               'repdesu - tBlockingTimer',
               Source.getSignalFromECU('repdesu.tBlockingTimer'),
               ylabel = '[id]',
               xlabel = 'time')

  Sync.addClient(PN)

  "-------------------------------------------------------"
  "Reaction pattern - deceleration support CheckDriverEnable"  
  PN = datavis.cPlotNavigator('Reaction pattern - deceleration support CheckDriverEnable')

  PN.addsignal('repdesu - status',
               Source.getSignalFromECU('repdesu.__b_Rep.__b_RepBase.status'),
               'repdesu - ExecutionStatus',
               Source.getSignalFromECU('repdesu.__b_Rep.__b_RepBase.ExecutionStatus'),
               ylabel = '[id]')
  
  PN.addsignal('repdesu - EnableREPDESU',
               Source.getSignalFromECU('repdesu.EnableREPDESU_b'),
               ylabel = '[id]')

  PN.addsignal('namespaceSIT - vx',
               Source.getSignalFromECU('namespaceSIT._.Egve._.vx_sw'),
               ylabel = '[m/s]')

  PN.addsignal('namespaceSIT - ax',
               Source.getSignalFromECU('namespaceSIT._.Egve._.ax_sw'),
               ylabel = '[m/s^2]')

  PN.addsignal('GPPos * 100',
               Source.getSignalFromECU('namespaceSIT._.Egve._.GPPos_uw'),
               'pBrake',
               Source.getSignalFromECU('namespaceSIT._.Egve._.pBrake_uw'),
               factor    = [100.0, 1.0],
               ylabel = '[0..100]')

  PN.addsignal('BPAct',
               Source.getSignalFromECU('namespaceSIT._.Egve._.BPAct_b'),
               ylabel = '[bool]')

  Sync.addClient(PN)

  pass

if __name__ == '__main__':
  import aebs.proc
  import datavis
  import sys
  import os
  
  if len(sys.argv) == 2:
    AviFile = sys.argv[1].lower().replace('.mdf', '.avi')
    Source  = aebs.proc.cLrr3Source(sys.argv[1], ECU='ECU_0_0')
    Sync    = datavis.cSynchronizer()    
    
    viewASF(Sync, Source, 300)    
    if os.path.isfile(AviFile):
      Sync.addClient(datavis.cVideoNavigator(AviFile, {}), Source.getSignal('Multimedia_0_0', 'Multimedia_1'))
    
    Sync.run()    
    raw_input("Press Enter to Exit")
    Sync.close()
      
  else:
    sys.stderr.write('The %s needs one input argument for mdf file path!\n' %__file__)
