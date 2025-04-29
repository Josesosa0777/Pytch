""" Associates the tracks of radar and camera for a given measurement
using the same algorithm as in CVR3 FUS component.
This allows easy benchmark of different parameter sets and assignment solver methods.
"""

import numpy as np

from asso_cvr3_asofus import defpars, normParams, checkInputParams,\
                             calcCurrentAssoProb, calcFilterAssoProb, Cvr3fusTransf
import asso

def prob2cost(p):
  return 1 - p

class AssoFlr20Core(asso.interface.AssoObject):
  def __init__(self, scaleTime, radarTracks, videoTracks, Solver=asso.greedy.Greedy):
    asso.interface.AssoObject.__init__(self)

    # asso interface attributes
    self.solver = Solver()
    self.scaleTime = scaleTime
    self.K = len(radarTracks)
    self.L = len(videoTracks)
    self.N = self.scaleTime.size
    self.radarTracks = radarTracks
    self.videoTracks = videoTracks
    # coordinate transf between sensors (!not measured yet!)
    self.transf = Cvr3fusTransf(dLongOffsetObjToVidCoordSys=0,
                                dMountOffsetVid=0)
    # track co-existence masks
    self.masks = np.zeros(shape=(self.N, self.K, self.L), dtype=np.bool)
    for i, radarTrack in radarTracks.iteritems():
      if not radarTrack:
        continue
      for j, videoTrack in videoTracks.iteritems():
        if not videoTrack:
          continue
        self.masks[:,i,j] = radarTrack['valid_b'] & videoTrack['valid_b']
    self.masks.flags.writeable = False # safety
    # initial condition for filter
    self.filteredAssoProbInit = np.zeros(shape=(self.K, self.L), dtype=np.float32)
    # set association parameters to default
    self.params = defpars
    return

  def update(self, usedefault=True, **params):
    """ Update parameters

    :Parameters:
        usedefault : bool, optional
          If set to True (default), the parameters are updated based on the
          default parameter set, otherwise based on the last set (iterative update).
    :Keywords:
      parameter name=value pairs
    :Exceptions:
      AssertionError
        invalid association algorithm parameter name or value (outside range)
    """
    checkInputParams(params)
    self._updateParams(params, usedefault=usedefault)
    if self.isAssoDone:
      self._resetAssoResults()
    return

  def _updateParams(self, params, usedefault=True):
    # update params
    normedparams = normParams(params)
    if self.params and not usedefault:
      # update current params with the new ones
      self.params = self.params._replace(**normedparams)
    else:
      # update default params with the new ones
      self.params = defpars._replace(**normedparams)
    return

  def _resetAssoResults(self):
    self.objectPairs = []
    self.isAssoDone = False
    return

  def _createCostMatrix(self):
    currentAssoProb_uint32 = self._calcCurrentAssoProb()
    filteredAssoProb = calcFilterAssoProb(currentAssoProb_uint32,
                                          self.filteredAssoProbInit,
                                          self.radarTracks,
                                          self.videoTracks,
                                          self.masks,
                                          self.params)
    self.C = prob2cost( filteredAssoProb )
    return

  def _calcCurrentAssoProb(self):
    currentAssoProb_uint32, _ = calcCurrentAssoProb(self.radarTracks,
                                                    self.videoTracks,
                                                    self.masks,
                                                    self.params,
                                                    self.transf)
    return currentAssoProb_uint32

  def _calcGate(self):
    self.gate = prob2cost( self.params.prob1AsoProbLimit )
    return

  def _register(self, n, Ccut, validRows, validCols, indices):
    assoObjIndices = []
    for rowNum, colNum in indices:
      # filter invalid association
      if not np.allclose(Ccut[rowNum, colNum], self.invalidAssoCost):
        i = validRows[rowNum]
        j = validCols[colNum]
        assoObjIndices.append( (i,j) )
    if assoObjIndices:
      assoObjIndices.sort(cmp=self.cmp) # in-place sort of tuple elements
    self.objectPairs.append(assoObjIndices)
    return
