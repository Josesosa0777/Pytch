"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""
import datavis

def viewSIT(Sync, Source, FgNr):
  """
  Create PlotNavigators to illustrate the SIT. 
  
  :Parameters:
    sync : `datavis.cSynchronizer`
      Synchronizer instance to connect the `datavis.cPlotNavigators`s.
    Source : `aebs.proc.cLrr3Source`
      Signal source to get mdf signals.
    FgNr : int
      Intialize the figure number of the first `datavis.cPlotNavigators`.
  :ReturnType: None
  """
  PN = datavis.cPlotNavigator('Filtered Objects', FgNr)
  PN.addsignal('Filtered Objects - ECU.sit.IntroFinder\_TC.FilteredObjects',
               Source.getSignalFromECU('sit.IntroFinder_TC.Intro.i0.Id'),
               ylabel = '[Handle]')
  PN.addsignal('left lane level 1',
               Source.getSignalFromECU('sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i0'),
               ylabel = '[Handle]')
  PN.addsignal('same lane level 1',
               Source.getSignalFromECU('sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i1'),
               ylabel = '[Handle]')
  PN.addsignal('right lane level 1',
               Source.getSignalFromECU('sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i2'),
               ylabel = '[Handle]')
  PN.addsignal('left lane level 2',
               Source.getSignalFromECU('sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i3'),
               ylabel = '[Handle]')
  PN.addsignal('same lane level 2',
               Source.getSignalFromECU('sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i4'),
               ylabel = '[Handle]')
  PN.addsignal('right lane level 2',
               Source.getSignalFromECU('sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i5'),
               ylabel = '[Handle]',
               xlabel = 'time [s]')
  Sync.addClient(PN)

  PN = datavis.cPlotNavigator('Filtered Objects - all in one plot')
  PN.addsignal('ID',
               Source.getSignalFromECU('sit.IntroFinder_TC.Intro.i0.Id'),
               'left  lane level 1',
               Source.getSignalFromECU('sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i0'),
               'same  lane level 1',
               Source.getSignalFromECU('sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i1'),
               'right lane level 1',
               Source.getSignalFromECU('sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i2'),
               'left  lane level 2',
               Source.getSignalFromECU('sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i3'),
               'same  lane level 2',
               Source.getSignalFromECU('sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i4'),
               'right lane level 2',
               Source.getSignalFromECU('sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i5'),
               ylabel='[Handle]',
               xlabel='time [s]')
  Sync.addClient(PN)             
               

  PN = datavis.cPlotNavigator('IntroFinder')
  PN.addsignal('Filtered Objects - ECU.sit.IntroFinder\_TC.FilteredObjects',
               Source.getSignalFromECU('sit.IntroFinder_TC.Intro.i0.Id'),
               ylabel='[ID]')
  PN.addsignal('Intro - ObjectList(0]',
               Source.getSignalFromECU('sit.IntroFinder_TC.Intro.i0.ObjectList.i0'),
               ylabel='[Handle]')
  PN.addsignal('Intro - ObjectRelation(0]',
               Source.getSignalFromECU('sit.IntroFinder_TC.Intro.i0.ObjectRelation.i0'))
  PN.addsignal('Intro - ObjectList(0]',
               Source.getSignalFromECU('sit.IntroFinder_TC.Intro.i0.ObjectList.i0'),
               ylabel='[FUS Obj Idx]',
               xlabel='time [s]')
  Sync.addClient(PN)             

  FUS_idx = Source.getFUSIndexMode(0)

  # PSS obstacle filter parameter
  P_dOutOfSight          = 100;
  P_dVarYLimitStationary = 1.0;
  P_dVarYLimitMovable    = 1.5;
  P_wExistProb           = 0.8;
  P_wObstacleProb        = 0.352 #0.6;
  P_wGroundReflex        = 0.1;

  if Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.b.b.Stand_b' %(FUS_idx,))[1].any():
    P_dVarYLimit = P_dVarYLimitStationary
  else:
    P_dVarYLimit = P_dVarYLimitMovable

  PN = datavis.cPlotNavigator('FUS Object Index : %d' %(FUS_idx,))
  PN.addsignal('FUS',
               Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.Handle' %(FUS_idx,)),
               'IntroFinder',             
               Source.getSignalFromECU('sit.IntroFinder_TC.Intro.i0.ObjectList.i0'),
               ylabel='[Handle]')
  PN.addsignal('dxv',
               Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.Handle' %(FUS_idx,)),
               threshold=P_dOutOfSight)
  PN.addsignal('wExistObstacle',
               Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.wExistProbBase' %(FUS_idx,)),
               threshold=P_wExistProb)
  PN.addsignal('wObstacle',
               Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.wObstacle' %(FUS_idx,)),
               threshold=P_wObstacleProb)
  PN.addsignal('dVarYvObstacle',
               Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.dVarYvBase' %(FUS_idx,)),
               threshold=P_dVarYLimit)
  PN.addsignal('wGroundReflex',
               Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.wGroundReflex' %(FUS_idx,)),
               threshold=P_wGroundReflex)
  PN.addsignal('NotClassified',
               Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.b.b.NotClassified_b' %(FUS_idx,)))
  PN.addsignal('Stand',
               Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.b.b.Stand_b' %(FUS_idx,)))
  PN.addsignal('StoppedInvDir',
               Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.b.b.StoppedInvDir_b' %(FUS_idx,)))
  PN.addsignal('Stopped',
               Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.b.b.Stopped_b' %(FUS_idx,)))
  PN.addsignal('TruckCabIndicator',
               Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.b.b.TruckCabIndicator_b' %(FUS_idx,)),
               xlabel='time [s]')
  Sync.addClient(PN)             

  PN = datavis.cPlotNavigator('FUS Object Index : %d' %(FUS_idx,))
  PN.addsignal('FUS-Handle',
               Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.Handle' %(FUS_idx,)),
               ylabel='[Handle]')
  PN.addsignal('dxv',
               Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.dxv' %(FUS_idx,)),
               'dyv',
               Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.dyv' %(FUS_idx,)))
  PN.addsignal('vxv',
               Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.vxv' %(FUS_idx,)),
               'vyv',
               Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.vyv' %(FUS_idx,)))
  PN.addsignal('probClass[0]-obstacle',
               Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.probClass.i0' %(FUS_idx,)),
               'probClass[1]-obstacle',
               Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.probClass.i1' %(FUS_idx,)),
               'probClass[2]-obstacle',
               Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.probClass.i2' %(FUS_idx,)),
               'probClass[3]-obstacle',
               Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.probClass.i3' %(FUS_idx,)),
               'probClass[4]-obstacle',
               Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.probClass.i4' %(FUS_idx,)),
               xlabel='time [s]')
  PN.addsignal('wGroundReflex',
               Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.wGroundReflex' %(FUS_idx,)),
               'wObstacle',
               Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.wObstacle' %(FUS_idx,)),
               xlabel='time [s]')
  Sync.addClient(PN)             
  pass

if __name__ == '__main__':
  import aebs.proc
  import sys
  import os
  
  if len(sys.argv) == 2:
    AviFile = sys.argv[1].lower().replace('.mdf', '.avi')
    Source  = aebs.proc.cLrr3Source(sys.argv[1], ECU='ECU_0_0')
    Sync    = datavis.cSynchronizer()    

    viewSIT(Sync, Source, 200)
    if os.path.isfile(AviFile):
      Sync.addClient(datavis.cVideoNavigator(AviFile, {}), Source.getSignal('Multimedia_0_0', 'Multimedia_1'))
    
    Sync.run()    
    raw_input("Press Enter to Exit")
    Sync.close()
      
  else:
    sys.stderr.write('The %s needs one input argument for mdf file path!\n' %__file__)
