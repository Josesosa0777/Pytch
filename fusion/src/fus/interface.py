""" 2D track-to-track fusion interface
"""

import numpy as np

import fusion

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
      iName, jName = self.assoObj.sensorNames
      for (i,j), timeIndices in self.assoObj.assoData.iteritems():
        # get original tracks
        xi, Pi = self.assoObj.tracks[iName][i]
        xj, Pj = self.assoObj.tracks[jName][j]
        # fuse associated track pair
        xfus, Pfus = fusMethod(xi[timeIndices],
                               xj[timeIndices],
                               Pi[timeIndices],
                               Pj[timeIndices],
                               isDiag=isDiag)
        # save fused tracks
        self.tracks[i,j] = xfus, Pfus
        arrange = np.arange(len(timeIndices))
        indices = np.vstack( (timeIndices, arrange) )
        self.indices[i,j] = dict(indices.T)
        # fuse moving state (dummy algorithm: stationary where both sensors agree, moving elsewhere)
        iMovState = self.assoObj.movingState[iName][i]
        jMovState = self.assoObj.movingState[jName][j]
        self.movingState[i,j] = iMovState[timeIndices] & jMovState[timeIndices]
      self.isFusionDone = True
    return
