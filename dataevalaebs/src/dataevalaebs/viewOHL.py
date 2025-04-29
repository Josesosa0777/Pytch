"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""
import datavis

def viewOHL(Sync, Source, FgNr):
  """
  Create PlotNavigators to illustrate the OHL. 
  
  :Parameters:
    sync : `datavis.cSynchronizer`
      Synchronizer instance to connect the `datavis.cPlotNavigators`s.
    Source : `aebs.proc.cLrr3Source`
      Signal source to get mdf signals.
    FgNr : int
      Intialize the figure number of the first `datavis.cPlotNavigators`.
  :ReturnType: None
  """
  FUS_idx = Source.getFUSIndexMode(0)
  Time, Value = Source.getSignalFromECU('fus_asso_mat.LrrObjIdx.i%d' %(FUS_idx,))
  OHL_idx = Source.mode(Value, 255)
    
  Signals = []
  for i in xrange(40):
    Signals.append(''),
    Signals.append(Source.getSignalFromECU('ohl.ObjData_TC.OhlObj.i%d.dx' %(i,)))
  
  PN = datavis.cPlotNavigator('OHL objects - dx', FgNr)
  PN.addsignal(xlabel='time [s]',
               *Signals)
  Sync.addClient(PN)  
  
  PN = datavis.cPlotNavigator('obstacle classifier (FUS and OHL - different norming)')
  PN.addsignal('probClass[0]-underpassable',
               Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.probClass.i0' %(FUS_idx,)),
               'probClass[1]-overrunable',
               Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.probClass.i1' %(FUS_idx,)),
               'probClass[2]-interference',
               Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.probClass.i2' %(FUS_idx,)),
               'probClass[3]-unknown',
               Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.probClass.i3' %(FUS_idx,)),
               'probClass[4]-unknown',
               Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.probClass.i4' %(FUS_idx,)))
  PN.addsignal('probClass[0]-obstacle',
               Source.getSignalFromECU('ohl.ObjData_TC.OhlObj.i%d.probClass.i0' %(OHL_idx,)),
               'probClass[1]-underpassable',
               Source.getSignalFromECU('ohl.ObjData_TC.OhlObj.i%d.probClass.i1' %(OHL_idx,)),
               'probClass[2]-overrunable',
               Source.getSignalFromECU('ohl.ObjData_TC.OhlObj.i%d.probClass.i2' %(OHL_idx,)),
               'probClass[3]-interference',
               Source.getSignalFromECU('ohl.ObjData_TC.OhlObj.i%d.probClass.i3' %(OHL_idx,)),
               'probClass[4]-unknown',
               Source.getSignalFromECU('ohl.ObjData_TC.OhlObj.i%d.probClass.i4' %(OHL_idx,)))
  Sync.addClient(PN)  
  
  PN = datavis.cPlotNavigator('Power vs distance to obstacle')
  PN.addsignal('dx',
               Source.getSignalFromECU('ohl.ObjData_TC.OhlObj.i%d.dx' %(OHL_idx,)))
  PN.addsignal('dbPowerFilt',
               Source.getSignalFromECU('ohl.ObjData_TC.OhlObj.i%d.internal.dbPowerFilt' %(OHL_idx,)))
  PN.addsignal('probClass[0]-obstacle',
               Source.getSignalFromECU('ohl.ObjData_TC.OhlObj.i%d.probClass.i0' %(OHL_idx,)),
               'probClass[1]-underpassable',
               Source.getSignalFromECU('ohl.ObjData_TC.OhlObj.i%d.probClass.i1' %(OHL_idx,)),
               'probClass[2]-overrunable',
               Source.getSignalFromECU('ohl.ObjData_TC.OhlObj.i%d.probClass.i2' %(OHL_idx,)),
               'probClass[3]-interference',
               Source.getSignalFromECU('ohl.ObjData_TC.OhlObj.i%d.probClass.i3' %(OHL_idx,)),
               'probClass[4]-unknown',
               Source.getSignalFromECU('ohl.ObjData_TC.OhlObj.i%d.probClass.i4' %(OHL_idx,)),
               xlabel='time [s]')
  Sync.addClient(PN)  

  PN = datavis.cPlotNavigator('scatter plot')
  PN.addsignal('',
               (Source.getSignalFromECU('ohl.ObjData_TC.OhlObj.i%d.dx' %(OHL_idx,))[1],
                Source.getSignalFromECU('ohl.ObjData_TC.OhlObj.i%d.internal.dbPowerFilt' %(OHL_idx,))[1]),
                xlabel = 'dx [m]',
                ylabel = 'dbPowerFilt',
                color  = 'b.')
  Sync.addClient(PN)  

  # - show probClass type for all OHL objects versus time
  # - find the index of the OHL objects which has the best classification
  #   result for a given class type
  
  ClassType = 3
  """:type: int
  (0) - obstacle
  (1) - underpassable
  (2) - overrunable
  """
  ProbClassMax    = 0
  ProbClassMaxIdx = 0
  
  Signals = []
  for i in xrange(40):
    t, v = Source.getSignalFromECU('ohl.ObjData_TC.OhlObj.i%d.probClass.i%d' %(i, ClassType))
    ActProbClassMax = v.max()
    if ActProbClassMax > ProbClassMax:
      ProbClassMax    = ActProbClassMax
      ProbClassMaxIdx = i
    Signals.append('')
    Signals.append((t,v))
  
  PN = datavis.cPlotNavigator('All OHL objects')
  PN.addsignal(*Signals)
  PN.addsignal('best: %d' %(ProbClassMaxIdx,),
               Source.getSignalFromECU('ohl.ObjData_TC.OhlObj.i%d.probClass.i%d' %(ProbClassMaxIdx, ClassType)),
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
    
    viewOHL(Sync, Source, 100)    
    if os.path.isfile(AviFile):
      Sync.addClient(datavis.cVideoNavigator(AviFile, {}), Source.getSignal('Multimedia_0_0', 'Multimedia_1'))
    
    Sync.run()    
    raw_input("Press Enter to Exit")
    Sync.close()
      
  else:
    sys.stderr.write('The %s needs one input argument for mdf file path!\n' %__file__)
