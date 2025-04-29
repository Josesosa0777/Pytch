"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""
__docformat__ = "restructuredtext en"

import datavis
import viewFUSoverlay

def viewTracks(Sync, Source, FgNr):  
  """
  :Parameters:
    Sync : `datavis.cSynchronizer`
    Source : `aebs.proc.cLrr3Source`
    FgNr : int
  :ReturnType: list
  :Return: [datavis.cTrackNavigator,]
  """  
  Clients = []
  
  TN = datavis.cTrackNavigator('Tracks', FgNr)
  TN.setViewAngle(-15.0, 15.0, facecolor='r', alpha=0.3)
  TN.setLegend({2:dict(label='Stationary', marker='*', ms=10, mew=0),
                0:dict(label='Moving',     marker='o', ms=10, mew=0),
                1:dict(label='Intro',      marker='s', ms=10, mew=0)})             
  
  Time, kapCurvTraj                     = Source.getSignal('ECU_0_0', 'evi.MovementData_TC.kapCurvTraj')
  Time, ROADRSOEgoLaneLeftPolyA0        = Source.getSignal('ECU_0_0', 'padsit_par_a.ROADRSOEgoLaneLeftPolyA0',        ScaleTime=Time)
  Time, ROADRSOEgoLaneRightPolyA0       = Source.getSignal('ECU_0_0', 'padsit_par_a.ROADRSOEgoLaneRightPolyA0',       ScaleTime=Time)
  Time, ROADRSORightLaneLeftPolyA0      = Source.getSignal('ECU_0_0', 'padsit_par_a.ROADRSORightLaneLeftPolyA0',      ScaleTime=Time)
  Time, ROADRSOLeftLaneRightPolyA0      = Source.getSignal('ECU_0_0', 'padsit_par_a.ROADRSOLeftLaneRightPolyA0',      ScaleTime=Time)
  Time, ROADRSOUncorrRightLaneLeftPolyA = Source.getSignal('ECU_0_0', 'padsit_par_a.ROADRSOUncorrRightLaneLeftPolyA', ScaleTime=Time)
  Time, ROADRSOUncorrLeftLaneRightPolyA = Source.getSignal('ECU_0_0', 'padsit_par_a.ROADRSOUncorrLeftLaneRightPolyA', ScaleTime=Time)
  
  R = 1.0 / kapCurvTraj
  
  TN.addTrack(TN.circle, Time, R, ROADRSOEgoLaneLeftPolyA0,        color='b')
  TN.addTrack(TN.circle, Time, R, ROADRSOEgoLaneRightPolyA0,       color='b')
  TN.addTrack(TN.circle, Time, R, ROADRSORightLaneLeftPolyA0,      color='r')
  TN.addTrack(TN.circle, Time, R, ROADRSOLeftLaneRightPolyA0,      color='r')
  TN.addTrack(TN.circle, Time, R, ROADRSOUncorrRightLaneLeftPolyA, color='g')
  TN.addTrack(TN.circle, Time, R, ROADRSOUncorrLeftLaneRightPolyA, color='g') 
  
  Time, Objects = viewFUSoverlay.fillObjects(Source)
  for Object in Objects:
    TN.addObject(Time, Object)
  Time, Intro = viewFUSoverlay.indicateIntro(Source)
  TN.addObject(Time, Intro)
  
  Clients.append(TN)
  
  for Client in Clients:
    Sync.addClient(Client)
  return Clients
  
if __name__ == '__main__':
  import datavis
  import aebs.proc
  import sys
  import os
  import viewFUSoverlay
  import viewWarnings

  if len(sys.argv) == 2:
    MdfFile = sys.argv[1]
  else:
    MdfFile = r'D:\Measurements\mdf\AEBS_H05.2604_2010-04-22_15-57_61.MDF'
    sys.stderr.write('Default mesurement file is used: %s\n' %MdfFile)
  
  Groups  = [['stationary', [2], '0', False]]
  AviFile = MdfFile.lower().replace('.mdf', '.avi') if os.path.isfile(MdfFile) else MdfFile+'.avi'
  Sync    = datavis.cSynchronizer()    
  Source  = aebs.proc.cLrr3Source(MdfFile, ECU='ECU_0_0')
  
  TN, = viewTracks(Sync, Source, 100)  
  TN.addGroups(Groups)
  TN.setViewAngle(-25.0, 25.0, facecolor='b', alpha=0.3, GroupName='stationary')
  
  Reports = Source.findEvents(viewWarnings.Warnings, 10.0)               
  datavis.viewEvents(Sync, Source, viewWarnings.Warnings, 'Warnings', 200)
  datavis.viewReports(Sync, Source, Reports, 'Warnings', 'm')
  ReportsToSplit = Reports
  
  Reports = Source.findEvents(viewWarnings.Intros, 10.0)                  
  datavis.viewEvents(Sync, Source, viewWarnings.Intros,   'Intros', 300)  
  datavis.viewReports(Sync, Source, Reports, 'Intros', 'b')  
  ReportsToSplit += Reports
  
  if os.path.exists(AviFile):
    VN, = viewFUSoverlay.viewFUSoverlay(Sync, Source, AviFile)
    VN.addGroups(Groups)
    Sync.connect('selectGroup', VN, TN)
  else:
    AviFile = ''
    
  for Report in ReportsToSplit: 
    Source.split(Report, VideoFile=AviFile)

  Sync.run()      
  raw_input("Press Enter to Exit\n")                                  
  Sync.close()
