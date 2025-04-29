""" Track-to-track fusion of CVR3 and S-Cam tracks
"""

import numpy as np

from fus import fusion

class FusObject(object):
  
  def __init__(self, assoObj):
    """
    :Parameters:
        assoObj : asso.interface.assoObject
          Association object
    """
    self.assoObj = assoObj
    """:type: asso.interface.assoObject
    Association object"""
    self.tracks = {}
    """:type: dict
    Fused tracks { (objNum<int>, objNum<int>) : (state<ndarray>, covarMatrix<ndarray>) }"""
    self.indices = {}
    """:type: dict
    Connects associated object pair time index to fused data array index
    { (objNum<int>, objNum<int>) : {timeIndex<int> : arrayIndex<int>} }"""
    self.movingState = {}
    """:type: dict
    Fused track moving state, in binary range (0: moving/stopped, 1: stationary)
    { (objNum<int>, objNum<int>) : movingState<ndarray>}"""
    self.isFusionDone = False
    """:type: bool
    Indicates if fusion was done"""
    return
    
  def calc(self, fusMethod=fusion.weightedAverage, isDiag=False):
    if not self.isFusionDone:
      cvr3, sCam = self.assoObj.sensorNames
      for (i,j), timeIndices in self.assoObj.assoData.iteritems():
        # get original tracks
        xi, Pi = self.assoObj.tracks[cvr3][i]
        xj, Pj = self.assoObj.tracks[sCam][j]
        # fuse only lateral distance of associated track pair
        xfus_y, Pfus_y = fusMethod(xi[timeIndices,1][...,np.newaxis],
                                   xj[timeIndices,1][...,np.newaxis],
                                   Pi[timeIndices,1,1][...,np.newaxis,np.newaxis],
                                   Pj[timeIndices,1,1][...,np.newaxis,np.newaxis],
                                   isDiag=isDiag)
        xfus = xi[timeIndices] # advanced indexing results copy w/o losing array dim
        Pfus = Pi[timeIndices]
        xfus[...,1] = xfus_y.squeeze()
        Pfus[...,1,1] = Pfus_y.squeeze()
        # save fused tracks
        self.tracks[i,j] = xfus, Pfus
        arrange = np.arange(len(timeIndices))
        indices = np.vstack( (timeIndices, arrange) )
        self.indices[i,j] = dict(indices.T)
        # set moving state of fused object to the radar's (which is much more reliable)
        self.movingState[i,j] = self.assoObj.movingState[cvr3][i][timeIndices]
      self.isFusionDone = True
    return
