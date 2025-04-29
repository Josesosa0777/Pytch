""" Fuses the associated OHL objects of LRR3 and CVR3 sensors
"""
from datavis import pyglet_workaround  # necessary as early as possible (#164)
import numpy as np

import fus.fusion
import fus.interface

class FuseOHL(fus.interface.FusObject):
  def __init__(self, assoObj):
    fus.interface.FusObject.__init__(self, assoObj)
    return

  def calc(self, fusMethod=fus.fusion.weightedAverage, isDiag=False):
    assoObj = self.assoObj
    for (LRR3ohlObjNum, CVR3ohlObjNum), timeIndices in assoObj.assoData.iteritems():
      # get original position tracks
      xi, Pi = assoObj.posTracks['LRR3'][LRR3ohlObjNum]
      xj, Pj = assoObj.posTracks['CVR3'][CVR3ohlObjNum]
      # fuse tracks
      xfus, Pfus = fusMethod(xi[timeIndices],
                             xj[timeIndices],
                             Pi[timeIndices],
                             Pj[timeIndices],
                             isDiag=isDiag)
      # save fused tracks
      self.tracks[LRR3ohlObjNum, CVR3ohlObjNum] = xfus, Pfus
      arrayIndexRange = np.arange(len(timeIndices))
      timeAndArrayIndex = np.vstack((timeIndices, arrayIndexRange))
      self.indices[LRR3ohlObjNum, CVR3ohlObjNum] = dict(timeAndArrayIndex.T)
    return

if __name__ == '__main__':
  import sys
  import measparser
  from assoOHL import AssoOHL

  measPath = sys.argv[1]
  source = measparser.cSignalSource(measPath)
  try:
    # asso object init (track inits using signal queries)
    assoObj = AssoOHL(source)
  except measparser.signalgroup.SignalGroupError, error:
    # in case signals are not present
    print error.message
  else:
    # track-to-track association
    assoObj.calc()
    # track-to-track fusion
    fuseObj = FuseOHL(assoObj)
    fuseObj.calc()
  # close resources
  source.save()
