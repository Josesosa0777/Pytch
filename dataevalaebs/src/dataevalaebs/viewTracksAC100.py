"""
 Plot LRR3 and AC100 objects in one plot

:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""
__docformat__ = "restructuredtext en"

import datavis
import viewFUSoverlayAC100

def viewTracksAC100(Sync, Source, FgNr):  
  """
  :Parameters:
    Sync : `datavis.cSynchronizer`
    Source : `aebs.proc.cLrr3Source`
    FgNr : int
  """
  TN = datavis.cTrackNavigator('Tracks AC100', FgNr)
  TN.setViewAngle(-15.0, 15.0)
  TN.setLegend({6:dict(label='AC100 - Stationary', marker='+', ms=10, mew=2),
                5:dict(label='AC100 - Moving',     marker='^', ms=10, mew=2),
                2:dict(label='LRR3  - Stationary', marker='x', ms=10, mew=2),
                0:dict(label='LRR3  - Moving',     marker='o', ms=10, mew=0),
                1:dict(label='LRR3  - Intro',      marker='s', ms=10, mew=0)})             

  # selection of trajectory curvature 
  if 0:
   # LRR3  
   Time, kapCurvTraj                     = Source.getSignal('ECU_0_0', 'evi.MovementData_TC.kapCurvTraj')
  else:
   # ACC 100
   Time, kapCurvTraj                     = Source.getSignal('General_radar_status(661)_2_', 'estimated_road_curvature')
   kapCurvTraj = - kapCurvTraj
   
  
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
  
  Time, Objects = viewFUSoverlayAC100.fillObjects(Source)
  Time, Intro = viewFUSoverlayAC100.indicateIntro(Source,Time)
  Objects.append(Intro)
  
  for Object in Objects:
    TN.addObject(Time, Object)

  
  Sync.addClient(TN)
  pass
  
if __name__ == '__main__':
  import datavis
  import aebs.proc
  import sys
  import os
  import viewFUSoverlayAC100
  
  if len(sys.argv) == 2:
    MdfFile = sys.argv[1]
  else:
    MdfFile = r'D:\Measuremets\mdf\sensor_benchmark_H05.2604_2010-07-15_11-26_05.MDF'
    sys.stderr.write('Default mesurement file is used: %s\n' %MdfFile)
  
  AviFile = MdfFile.lower().replace('.mdf', '.avi')
  Sync    = datavis.cSynchronizer()    
  Source  = aebs.proc.cLrr3Source(MdfFile, ECU='ECU_0_0')
  
  viewTracksAC100(Sync, Source, 100)  
  if os.path.exists(AviFile):
    viewFUSoverlayAC100.viewFUSoverlay(Sync, Source, AviFile)
    
  Sync.run()    
  raw_input("Press Enter to Exit\n")
  Sync.close()
