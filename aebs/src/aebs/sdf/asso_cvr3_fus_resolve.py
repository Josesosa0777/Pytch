""" Associates the tracks of radar and camera for a given measurement 
based on CVR3 FUS signals using different assignment solver methods.
"""

import numpy as np

from asso_cvr3_fus_recalc import prob2cost, OHL_OBJ_NUM, VID_OBJ_NUM,\
                                 fix2float, norms, defpars, devnames
import asso


OHL_OBJ_NUM_RANGE = xrange(OHL_OBJ_NUM)
VID_OBJ_NUM_RANGE = xrange(VID_OBJ_NUM)

sgs = []
for devname in devnames:
  # required signal group
  sg = {}
  for l in VID_OBJ_NUM_RANGE:
    sg["VidObj.i%d.Handle" %l] = devname, "fus.SVidBasicInput_TC.VidObj.i%d.Handle" %l
    for k in OHL_OBJ_NUM_RANGE:
      sg["ProbAssoMat.i%d.i%d" %(k,l)] = devname, "fus_s_asso_mat.ProbAssoMat.probability.i%d.i%d" %(k,l)
  sgs.append(sg)

class AssoCvr3fusResolve(asso.interface.AssoObject):
  def __init__(self, source, Solver=asso.greedy.Greedy, useVideoHandle=False):
    """    
    :Parameters:
        source : measparser.cSignalSource
          Measurement signal source
        Solver : class, optional
          Assignment solver class
        useVideoHandle : bool, optional
          Use video handle in association results. If True, the internal object id (handle) is utilized, 
          otherwise the video object indices are used. Default is False.
    :Exceptions:
      measparser.signalgroup.SignalGroupError
        if required signals are not present
      MemoryError
        there is not enough memory to do the calculations (e.g. when measurement is too long)
    """
    asso.interface.AssoObject.__init__(self)
    
    self.source = source
    self.useVideoHandle = useVideoHandle
    # handle signal groups
    self.group = source.selectSignalGroup(sgs)
    # asso interface attributes
    self.solver = Solver()
    self.scaleTime = source.getSignalFromSignalGroup(self.group, "ProbAssoMat.i0.i0")[0]
    self.K = OHL_OBJ_NUM
    self.L = VID_OBJ_NUM
    self.N = self.scaleTime.size
    self.isAssoSuccessful = np.zeros(self.N, dtype=np.bool)
    # complementary attributes
    self.filteredAssoProb = np.zeros(shape=(self.N, OHL_OBJ_NUM, VID_OBJ_NUM), dtype=np.float32)
    self.vidHandles = {}
    # query and store signals
    for j in VID_OBJ_NUM_RANGE:
      self.vidHandles[j] = source.getSignalFromSignalGroup(self.group, "VidObj.i%d.Handle" %j)[1]
      for i in OHL_OBJ_NUM_RANGE:
        filteredAssoProb = self.source.getSignalFromSignalGroup(self.group, "ProbAssoMat.i%d.i%d" %(i,j))[1]
        if filteredAssoProb.dtype.kind != 'f':
          # normalization needed
          filteredAssoProb = fix2float( filteredAssoProb, norms['N_prob1UW_uw'] )
        self.filteredAssoProb[:,i,j] = filteredAssoProb
    return
  
  def _createCostMatrix(self):
    self.C = prob2cost( self.filteredAssoProb )
    return
  
  def _calcGate(self):
    self.gate = prob2cost( defpars.prob1AsoProbLimit )
    return
  
  def _register(self, n, Ccut, validRows, validCols, indices):
    assoObjIndices = []
    for rowNum, colNum in indices:
      # filter invalid association
      if not np.allclose(Ccut[rowNum, colNum], self.invalidAssoCost):
        i = validRows[rowNum]
        l = validCols[colNum]
        j = self.vidHandles[l][n] if self.useVideoHandle else l
        objPair = (i,j)
        assoObjIndices.append(objPair)
        timeIndices = self.assoData.setdefault(objPair, [])
        timeIndices.append(n)
    if assoObjIndices:
      self.isAssoSuccessful[n] = True
      assoObjIndices.sort(cmp=self.cmp) # in-place sort of tuple elements
    self.objectPairs.append(assoObjIndices)
    return

if __name__ == '__main__':
  import sys
  
  import measparser
  
  measPath = sys.argv[1]
  source = measparser.cSignalSource(measPath)
  try:
    # asso object init (signal queries)
    a = AssoCvr3fusResolve(source)
    a.calc()
  except (measparser.signalgroup.SignalGroupError, AssertionError), error:
    print error.message
  else:
    print a
  # close resources
  source.save()
