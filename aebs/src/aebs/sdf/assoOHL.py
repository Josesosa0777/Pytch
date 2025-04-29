""" Associates the OHL objects of LRR3 and CVR3 sensors for a given measurement.
The association is based on both position and relative velocity of the object:

 state = [dx]  covar = [varDx,     0,     0,     0]
         [dy]          [    0, varDy,     0,     0]
         [vx]          [    0,     0, varVx,     0]
         [vy]          [    0,     0,     0, varVy]

Statistical distances are calculated and gating is applied in both cases,
resulting an assignment cost matrix in each time step. The assignment problem
is solved using the Hungarian method.

Note: covariances are neglected from the association, since longitudinal and lateral
state estimates are calculated independently in sensors (different model for dx/vx/ax and dy/vy estimation),
moreover their normalization is ambigous.
"""
from datavis import pyglet_workaround  # necessary as early as possible (#164)
import sys

import numpy as np
import scipy.stats

import measparser
import asso
import fusutils

OHL_OBJ_NUM = 40  # for both sensors
OHL_OBJ_NUM_RANGE = xrange(OHL_OBJ_NUM)
LRR3  = 'LRR3' # avoid bugs from mistyping
CVR3  = 'CVR3'

# constants to correct wrong LLR3/CVR3 OHL object variance normalization
N_vSL_ul       = float(2**24) # velocity   [m/s] LRR3/CVR3 norm.h
N_varNormSL_ul = float(2**20) # variance   [-]   LRR3/CVR3 norm.h
physUnit2norm = {'m/s' : N_vSL_ul,
                 '-'   : N_varNormSL_ul,
                 ''    : 1.0}

def correctNorming(signal, physUnit, physUnitMeas):
  if physUnitMeas != physUnit:
    normUsedInMeas = physUnit2norm[physUnitMeas]
    normCorrect    = physUnit2norm[physUnit]
    signal = signal * (normUsedInMeas / normCorrect)
  return signal

signalTemplates = (
  ('%s_OHL_%d_dx'        , 'i%d.dx'         ),
  ('%s_OHL_%d_dy'        , 'i%d.dy'         ),
  ('%s_OHL_%d_vx'        , 'i%d.vx'         ),
  ('%s_OHL_%d_vy'        , 'i%d.vy'         ),
  ('%s_OHL_%d_varDx'     , 'i%d.varDx'      ),
  ('%s_OHL_%d_varDy'     , 'i%d.varDy'      ),
  ('%s_OHL_%d_varVx'     , 'i%d.varVx'      ),
  ('%s_OHL_%d_varVy'     , 'i%d.varVy'      ),
  ('%s_OHL_%d_covarDxVx' , 'i%d.covarDxVx'  ),
  ('%s_OHL_%d_covarDyVy' , 'i%d.covarDyVy'  ),
  ('%s_OHL_%d_wExistProb', 'i%d.wExistProb' ),
  ('%s_OHL_%d_stationary', 'i%d.c.c.Stand_b'),
)

ohlNamePrefixes = (
  'ohl.ObjData_TC.OhlObj.', # nomenclature till B2 sample
  'ohy.ObjData_TC.OhlObj.', # nomenclature from B4 sample
)

cvr3deviceNames = 'MRR1plus', 'RadarFC'

# signal group definitions
lrr3signalGroup = {}
for aliasTemplate, signalTemplate in signalTemplates:
  for i in OHL_OBJ_NUM_RANGE:
    lrr3signalGroup[aliasTemplate %(LRR3,i)] = ('ECU', 'ohl.ObjData_TC.OhlObj.' + signalTemplate %i)

signalGroups = []
for ohlPrefix in ohlNamePrefixes:
  for devName in cvr3deviceNames:
    signalGroup = lrr3signalGroup.copy() # shallow copy
    for aliasTemplate, signalTemplate in signalTemplates:
      for i in OHL_OBJ_NUM_RANGE:
        signalGroup[aliasTemplate %(CVR3,i)] = (devName, ohlPrefix + signalTemplate %i)
    signalGroups.append(signalGroup)

# state estimates (order is important)
stateTemplates = (
#  signalname      unit
  ('%s_OHL_%d_dx', 'm'  ),
  ('%s_OHL_%d_dy', 'm'  ),
  ('%s_OHL_%d_vx', 'm/s'),
  ('%s_OHL_%d_vy', 'm/s'),
)

# variances (order is important)
varTemplates = (
#  signalname         unit
  ('%s_OHL_%d_varDx', '-'), # [m^2]
  ('%s_OHL_%d_varDy', '-'), # [m^2]
  ('%s_OHL_%d_varVx', '-'), # [(m/s)^2]
  ('%s_OHL_%d_varVy', '-'), # [(m/s)^2]
)

class AssoOHL(asso.interface.AssoObject):
  def __init__(self, source, scaleTime=None, reliabilityLimit=0.4):
    """
    :Parameters:
        source : measparser.cSignalSource
          Measurement signal source
    :KeyWords:
        scaleTime : numpy.ndarray
          Common scale time for data association. If not specified, the most dense (in average)
          sensor time is selected.
        reliabilityLimit : float
          Determines the required lower limit of track reliability, in 0...1 range.
          Default value is 0.4.
    :Exceptions:
      measparser.signalgroup.SignalGroupError : if required signals are not present
    """
    asso.interface.AssoObject.__init__(self)

    self.reliabilityLimit = reliabilityLimit
    """:type: float
    Track reliability threshold, in 0...1 range"""
    self.sensorNames = (LRR3, CVR3)
    self.source = source
    """:type: measparser.cSignalSource
    Measurement signal source"""
    self.group = self.source.selectSignalGroup(signalGroups)
    """:type: dict
    Selected signal group"""
    self.scaleTime = scaleTime if scaleTime is not None else self._selectScaleTime()
    self.kwargs0 = dict(ScaleTime=self.scaleTime, Order='zoh')
    """:type: dict
    Keyword arguments for signal queries (scale time and interpolation order)"""
    self.M = len(stateTemplates)
    """:type: int
    State dimension"""
    self.N = self.scaleTime.size
    self.K = OHL_OBJ_NUM
    self.L = OHL_OBJ_NUM
    self.tracks = {}
    """:type: dict
    Sensor tracks (with all kinematic states)
    { sensorName<str> : {objNum<int> : (state<ndarray, shape (N,M)>, covarmtx<ndarray, shape (N,M,M)>),} }"""
    self.posTracks = {}
    """:type: dict
    Position tracks (longitudinal and lateral position in cartesian coordinates)
    { sensorName<str> : {objNum<int> : (state<ndarray, shape (N,2)>, covarmtx<ndarray, shape (N,2,2)>),} }"""
    self.velTracks = {}
    """:type: dict
    Velocity tracks (longitudinal and lateral velocity in cartesian coordinates)
    { sensorName<str> : {objNum<int> : (state<ndarray, shape (N,2)>, covarmtx<ndarray, shape (N,2,2)>),} }"""
    self.reliability = {}
    """:type: dict
    Track reliability measure, in 0...1 range
    { sensorName<str> : {objNum<int> : reliability<ndarray>,} }"""
    self.masks = {}
    """:type: dict
    Stores the masked intervals where the sensor objects are 'reliable',
    therefore can be considered in data association
    { sensorName<str> : {objNum<int> : mask<ndarray, shape (N,)>} }"""
    self.movingState = {}
    """:type: dict
    Track moving state, in binary range (0: moving/stopped, 1: stationary)
    { sensorName<str> : {objNum<int> : movingState<ndarray>,} } """

    for sensorName in self.sensorNames:
      # interface tracks
      self.tracks[sensorName] = {}
      self.posTracks[sensorName] = {}
      self.velTracks[sensorName] = {}
      # other attributes
      self.reliability[sensorName] = {}
      self.masks[sensorName] = {}
      self.movingState[sensorName] = {}
      for i in OHL_OBJ_NUM_RANGE:
        # fill states and covariance matrices
        x = self._getStates(sensorName, i, stateTemplates)
        P = self._getCovarMatrices(sensorName, i, varTemplates)
        # store interface tracks
        self.tracks[sensorName][i] = x,P
        self.posTracks[sensorName][i] = ( x[:,:2], P[:,:2,:2] )
        self.velTracks[sensorName][i] = ( x[:,2:], P[:,2:,2:] )
        # set reliability
        existProb = self.source.getSignalFromSignalGroup(self.group, '%s_OHL_%d_wExistProb' %(sensorName, i), **self.kwargs0)[1]
        self.reliability[sensorName][i] = existProb
        maskReliability = existProb > self.reliabilityLimit
        # correct track validity (in case of corrupt variance values)
        maskValidity = np.ones_like(maskReliability)
        variances = P.diagonal(axis1=1, axis2=2) # shape (N,M)
        for k in xrange( variances.shape[1] ):
          maskCorrectVariance = variances[:,k] > fusutils.matrixop.EPS # filter invalid variances
          if not np.array_equal(maskReliability, maskCorrectVariance & maskReliability):
            maskValidity &= maskCorrectVariance
            # give warning to user
            aliasTemplate, _ = varTemplates[k]
            deviceName, signalName = self.group[ aliasTemplate %(sensorName,i) ]
            sys.stderr.write( 'Warning: %s %s signal might be corrupted!\n' %(deviceName,signalName) )
        self.masks[sensorName][i] = maskReliability & maskValidity
        # set moving state
        stationary = self.source.getSignalFromSignalGroup(self.group, '%s_OHL_%d_stationary' %(sensorName, i), **self.kwargs0)[1]
        self.movingState[sensorName][i] = stationary.astype(np.bool)

    self.C = np.zeros(shape=(self.N, self.K, self.L))
    self.solver = asso.hungarian._Hungarian()
    self.isAssoSuccessful = np.zeros(self.N, dtype=np.bool)
    return

  def _selectScaleTime(self):
    scaleTimes  = []
    for sensorName in self.sensorNames:
      scaleTime = self.source.getSignalFromSignalGroup(self.group, '%s_OHL_11_dx' %sensorName)[0] # dummy query
      scaleTimes.append(scaleTime)
    scaleTime = measparser.signalproc.selectTimeScale(scaleTimes, True)
    return scaleTime

  def _getStates(self, sensorName, objNum, stateTemplates):
    x = np.zeros(shape=(self.N, self.M))
    for i, (stateTemplate, physUnit) in enumerate(stateTemplates):
      t, state = self.source.getSignalFromSignalGroup(self.group, stateTemplate %(sensorName, objNum))
      mask = state != 0
      _, state = self.source.rescale(t, state, self.scaleTime, Order='mix', Mask=mask)
      physUnitMeas = self.source.getPhysicalUnitFromSignalGroup(self.group, stateTemplate %(sensorName, objNum))
      state = correctNorming(state, physUnit, physUnitMeas)
      x[:,i] = state
    return x

  def _getCovarMatrices(self, sensorName, objNum, varTemplates):
    P = np.zeros(shape=(self.N, self.M, self.M))
    for i, (varTemplate, physUnit) in enumerate(varTemplates):
      t, variance = self.source.getSignalFromSignalGroup(self.group, varTemplate %(sensorName, objNum))
      _, variance = self.source.rescale(t, variance, self.scaleTime, Order='zoh')
      physUnitMeas = self.source.getPhysicalUnitFromSignalGroup(self.group, varTemplate %(sensorName, objNum))
      variance = correctNorming(variance, physUnit, physUnitMeas)
      P[:,i,i] = variance
    return P

  def _createCostMatrix(self):
    # step 1 - calculate cost matrices (object loop ~40x40)
    for i in OHL_OBJ_NUM_RANGE:
      xi,Pi = self.tracks[LRR3][i]
      maski = self.masks[LRR3][i]
      for j in OHL_OBJ_NUM_RANGE:
        xj,Pj = self.tracks[CVR3][j]
        maskj = self.masks[CVR3][j]
        mask = maski & maskj # when both tracks are valid and reliable
        if np.any(mask): # in case of overlapping intervals
          self.C[mask,i,j] = asso.association.calcCostMatrixElements(xi[mask],
                                                                     xj[mask],
                                                                     Pi[mask],
                                                                     Pj[mask],
                                                                     isDiag=True) # diagonal covariance matrices
    return

  def _calcGate(self):
    df = self.M # chi2 degree of freedom
    self.gate = asso.association.calcGate(asso.interface.DEFAULT_SIGNIF_LEVEL, scipy.stats.chi2, df)
    return

if __name__ == '__main__':
  measPath = sys.argv[1]
  source = measparser.cSignalSource(measPath)
  try:
    # asso object init (track inits using signal queries)
    assoObj = AssoOHL(source)
  except measparser.signalgroup.SignalGroupError, error:
    # in case signals are not present
    print error.message
  else:
    # cost matrix calculation and track-to-track association
    assoObj.calc()
    if '-v' in sys.argv:
      # print out association result
      for k, assoList in enumerate(assoObj.objectPairs):
        print k, assoObj.scaleTime[k], assoList
      # check if all base class attributes are set
      missings = fusutils.debug.checkAttributes(assoObj)
      if missings:
        print 'Attribute(s) might be unset: %s' %missings
  # close resources
  source.save()
