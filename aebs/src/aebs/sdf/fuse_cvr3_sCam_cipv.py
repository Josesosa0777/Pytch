""" Track-to-track fusion of CVR3 and S-Cam closest-in-path vehicle (cipv) tracks
"""

from fus import fusion

class FuseCvr3SCamCipv(object):

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
    return

  def calc(self, fusMethod=fusion.weightedAverage, isDiag=False):
    iName, jName = self.assoObj.sensorNames
    for (i,j), timeIndices in self.assoObj.assoData.iteritems():
      # get original tracks
      xi, Pi = self.assoObj.tracks[iName]
      xj, Pj = self.assoObj.tracks[jName]
      # fuse associated track pair
      xfus, Pfus = fusMethod(xi[timeIndices],
                             xj[timeIndices],
                             Pi[timeIndices],
                             Pj[timeIndices],
                             isDiag=isDiag)
      # save fused tracks
      self.tracks[i,j] = xfus, Pfus
    return
