def findKlinkner(Source, TCDiffLimit, T20TCDiffLimit):
  import numpy
  import measproc
  
  Reports = []
  T20, StatusT20 = Source.getSignal('ECU_0_0', 'acobraj_t20.__b_AcoCoFb_T20.__b_Aco_T20.status')
  TC,  StatusTC  = Source.getSignal('ECU_0_0', 'acobraj.__b_AcoCoFb.__b_Aco.status')
  
  TCDiff     = numpy.zeros_like(TC)
  TCDiff[1:] = numpy.diff(TC)
  TCDiffIs   = Source.compExtSigScal(TC, TCDiff, measproc.less, TCDiffLimit)
  
  Tall        = numpy.concatenate([T20, TC])
  SortPos     = Tall.argsort()
  MovePos     = SortPos.argsort()
  MovePosT20  = MovePos[:T20.size]  
  MovePosTC   = MovePos[T20.size:]  
  Follow      = numpy.diff(MovePosTC) == 1
  To          = numpy.concatenate([[False], Follow])
  From        = numpy.concatenate([Follow, [False]])  
  MovePosTC[To] = MovePosTC[From]
  MovePosTC    -= 1
  Tall        = Tall[SortPos]
  T20TCDiff   = TC - Tall[MovePosTC]  
  if MovePosTC[0] == -1:
    T20TCDiff[0] == 0
  T20TCDiffIs = Source.compExtSigScal(TC, T20TCDiff, measproc.less, T20TCDiffLimit)
  
  StatusEq1Is = Source.compExtSigScal(TC, StatusTC, measproc.equal, 1)
  StatusEq8Is = Source.compExtSigScal(TC, StatusTC, measproc.equal, 8)  
  StatusEq1Is = StatusEq1Is.neighbour(StatusEq8Is, CycleMargins=[0, 2])
  TCDiffIs    = TCDiffIs.intersect(T20TCDiffIs)
  TCDiffIs    = TCDiffIs.intersect(StatusEq1Is)  
  
  Report = measproc.cIntervalListReport(Source, TCDiffIs, 'Klinkner too fast TC')
  Reports.append(Report)
  
  TCNr   = numpy.diff(MovePosT20)
  TCNr  -= 1
  TCNr   = numpy.concatenate([TCNr, [0]])
  TCNrIs = Source.compExtSigScal(T20, TCNr, measproc.greater, 1)
  TCNrIs = TCNrIs.addMargin(CycleMargins=[0, 1])
  
  Report = measproc.cIntervalListReport(Source, TCNrIs, 'Klinkner too many TC')
  Reports.append(Report)  
  return Reports
  
import datavis

def viewKlinkner(Sync, Source, FgNr):  
  """
  :Parameters:
    sync : `datavis.cSynchronizer`
      Synchronizer instance to connect the `datavis.cPlotNavigators`s.
    Source : `aebs.proc.cLrr3Source`
      Signal source to get mdf signals.
    FgNr : int
      Intialize the figure number of the first `datavis.cPlotNavigators`.
  """
  T20, StatusT20 = Source.getSignal('ECU_0_0', 'acobraj_t20.__b_AcoCoFb_T20.__b_Aco_T20.status')
  TC,  StatusTC  = Source.getSignal('ECU_0_0', 'acobraj.__b_AcoCoFb.__b_Aco.status')
  
  PN = datavis.cPlotNavigator('Klinkner')
  PN.addsignal('acobraj_t20.__b_AcoCoFb_T20.__b_Aco_T20.status', (T20, StatusT20), color='.-')
  PN.addsignal('acobraj.__b_AcoCoFb.__b_Aco.status',             (TC,  StatusTC), color='.-')
  Sync.addClient(PN)
  pass
  
if __name__ == '__main__':
  import sys
  import datavis
  import measproc
  
  if len(sys.argv) == 2:
    MdfFile = sys.argv[1]
  else:
    MdfFile = r'D:\Measuremets\mdf\Klinker\AEBS_H05.2604_2010-07-19_15-07_09.MDF'
    sys.stderr.write('Default mesurement file is used: %s\n' %MdfFile)
  
  AviFile = MdfFile.lower().replace('.mdf', '.avi')
  Sync    = datavis.cSynchronizer()    
  Source  = measproc.cEventFinder(MdfFile)
  
  Reports  = findKlinkner(Source, 25e-3, 5e-3)  
  datavis.viewReports(Sync, Source, Reports, 'Klinkners', 'm')  
  viewKlinkner(Sync, Source, 100)  
  # if os.path.exists(AviFile):
    # viewFUSoverlay.viewFUSoverlay(Sync, Source, AviFile)
    
  Sync.run()    
  raw_input("Press Enter to Exit\n")
  Sync.close()
