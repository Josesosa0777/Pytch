"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""
import datavis

def viewSITActive(Sync, Source, FgNr):
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
  IntroTime, IntroValue = Source.getSignalFromECU('sit.IntroFinder_TC.Intro.i0.Id')
  Intervals             = Source.getSITIntroIntervals(IntroTime, IntroValue)     
  SIT_Intros            = Source.getSITIntroObjects(IntroTime, IntroValue, Intervals)
  
  IN = datavis.cIntervalNavigator('Intro intervals')
  IN.addIntervalList('Intro intervals', Intervals)
  Sync.addClient(IN)
  
  i = 0  
  for Lower, Upper, Intro, Objects in SIT_Intros:  
    if not i%10:
      if i != 0:
        Sync.addClient(PN)
      PN = datavis.cPlotNavigator('SIT', FgNr)
      PN.addsignal('sit.IntroFinder_TC.Intro.i0.Id',
                   (IntroTime, IntroValue),
                   yticks=Source.Yticks['SIT_Intro'])
    for FUS_ObjHandle, SIT_ObjRel in Objects:
      PN.addsignal('I: %s R: %s H: %d' %(Intro, SIT_ObjRel, FUS_ObjHandle),
                   Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.dxv' %(FUS_ObjHandle,), Imin=Lower, Imax=Upper, ScaleTime=IntroTime),
                   ylabel = '[m]')
    FgNr += 1
    i        += 1
  else:
    if SIT_Intros: 
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
    
    viewSITActive(Sync, Source, 700)    
    if os.path.isfile(AviFile):
      Sync.addClient(datavis.cVideoNavigator(AviFile, {}), Source.getSignal('Multimedia_0_0', 'Multimedia_1'))
    
    Sync.run()    
    raw_input("Press Enter to Exit\n")
    Sync.close()
      
  else:
    sys.stderr.write('The %s needs one input argument for mdf file path!\n' %__file__)
