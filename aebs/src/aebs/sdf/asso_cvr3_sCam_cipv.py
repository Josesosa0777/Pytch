""" Associates the closest-in-path-vehicle (CIPV) object of CVR3 and S-Cam for a given measurement.
The association is based on the object position and longitudinal relative velocity:

         [dx]          [varDx,     0,     0]
 state = [dy]  covar = [0    , varDy,     0]
         [vx]          [0    ,     0, varVx]

Statistical distances are calculated and gating is applied, resulting an assignment
cost matrix in each time step. The assignment problem is solved using the Hungarian method.
"""

from datavis import pyglet_workaround  # necessary as early as possible (#164)
import numpy as np
import scipy.stats

import asso
import measparser
from assoOHL import cvr3deviceNames, CVR3

# sensor names
SCAM = 'S-Cam'

SCAM_MESSAGE_NUM = 10
FUS_OBJ_NUM = 32
INVALID_FUS_HANDLE = 0
INVALID_ID = -1 # indicates invalid track id for both sensors

# S-Cam signal group definitions
sCamSignalTemplates = {
  'ID'        : 'Obstacle_%02d_Data_A',
  'Pos_X'     : 'Obstacle_%02d_Data_A',
  'Pos_Y'     : 'Obstacle_%02d_Data_A',
  'Vel_X'     : 'Obstacle_%02d_Data_A',
  'Status'    : 'Obstacle_%02d_Data_A',
  'Age'       : 'Obstacle_%02d_Data_B',
  'CIPV_Flag' : 'Obstacle_%02d_Data_B',
  'POS_X_STD' : 'Obstacle_%02d_Data_C',
  'POS_Y_STD' : 'Obstacle_%02d_Data_C',
  'VEL_X_STD' : 'Obstacle_%02d_Data_C',
}
sCamGroupLen = len(sCamSignalTemplates)
sCamSignalGroups = []
for k in xrange(1, SCAM_MESSAGE_NUM+1):
  sCamSignalGroup = {}
  for signalName, deviceNameTemplate in sCamSignalTemplates.iteritems():
    sCamSignalGroup[signalName] = (deviceNameTemplate %k, signalName)
  sCamSignalGroups.append(sCamSignalGroup)

sCamStateTemplates = (
  'Pos_X',
  'Pos_Y',
  'Vel_X',
)
sCamStdTemplates = (
  'POS_X_STD',
  'POS_Y_STD',
  'VEL_X_STD',
)

# CVR3 signal definitions
cvr3stateTemplates = (
  'fus.ObjData_TC.FusObj.i%d.dxv',
  'fus.ObjData_TC.FusObj.i%d.dyv',
  'fus.ObjData_TC.FusObj.i%d.vxv',
)
cvr3varTemplates = (
  'fus.ObjData_TC.FusObj.i%d.dVarXv',
  'fus.ObjData_TC.FusObj.i%d.dVarYv',
  'fus.ObjData_TC.FusObj.i%d.vVarXv',
)

# required signal group: contains all the CVR3 and the minimum S-Cam signals
signalGroups = []
for cvr3deviceName in cvr3deviceNames:
  signalGroup = {'SCamBaseTime'  : ('Obstacle_Status', 'Num_Obstacles'),
                 'sit.S1.handle' : (cvr3deviceName, 'sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i1'),
                }
  for i in xrange(FUS_OBJ_NUM):
    signalGroup['fusObj.i%d.handle'     %i] = (cvr3deviceName, 'fus.ObjData_TC.FusObj.i%d.Handle'      %i)
    signalGroup['fusObj.i%d.wExistProb' %i] = (cvr3deviceName, 'fus.ObjData_TC.FusObj.i%d.wExistProb'  %i)
    signalGroup['fusObj.i%d.stationary' %i] = (cvr3deviceName, 'fus.ObjData_TC.FusObj.i%d.b.b.Stand_b' %i)
    for stateTemplate, varTemplate in zip(cvr3stateTemplates, cvr3varTemplates):
      signalGroup[stateTemplate %i] = (cvr3deviceName, stateTemplate %i)
      signalGroup[varTemplate   %i] = (cvr3deviceName, varTemplate   %i)
  signalGroup.update(sCamSignalGroups[0]) # append first S-Cam message to required signals
  signalGroups.append(signalGroup)

class AssoCvr3SCamCipv(asso.interface.AssoObject):
  def __init__(self, source, scaleTime=None):
    """
    :Parameters:
        source : measparser.cSignalSource
          Measurement signal source
    :KeyWords:
        scaleTime : numpy.ndarray
          Common scale time for data association. If not specified, the most dense (in average)
          sensor time is selected.
    :Exceptions:
      measparser.signalgroup.SignalGroupError : if required signals are not present
    """
    asso.interface.AssoObject.__init__(self)

    self.sensorNames = (CVR3, SCAM)
    self.source = source
    """:type: measparser.cSignalSource
    Measurement signal source"""
    group = self.source.selectSignalGroup(signalGroups)
    """:type: dict
    Composite signal group (all CVR3 and the minimum S-Cam signals)"""
    sCamGroups = self.source.filterSignalGroups(sCamSignalGroups)
    """:type: list
    S-Cam signal group (not all the signals might be present)"""
    self.cvr3scaleTime = self.source.getSignalFromSignalGroup(group, 'sit.S1.handle')[0]
    """:type: numpy.ndarray
    Common scale time for CVR3 tracks"""
    self.sCamScaleTime = self.source.getSignalFromSignalGroup(group, 'SCamBaseTime')[0]
    """:type: numpy.ndarray
    Common scale time for S-Cam tracks"""
    self.scaleTime = scaleTime if scaleTime is not None else self._selectScaleTime()
    self.kwargs0  = dict(ScaleTime=self.scaleTime, Order='zoh')
    self.kwargs01 = dict(ScaleTime=self.scaleTime, Order='mix')
    """:type: dict
    Keyword arguments for signal queries (scale time and interpolation order)"""
    self.N = self.scaleTime.size
    self.M = len(cvr3stateTemplates)
    """:type: int
    State dimension"""
    self.tracks = {}
    """:type: dict
    Sensor CIPV tracks { sensorName<str> : (state<ndarray>, covarMatrix<ndarray>) }"""
    self.trackIds = {}
    """:type: dict
    Sensor CIPV track IDs (CVR3 FUS handle, S-Cam ID) { sensorName<str> : trackID<int> }"""
    self.masks = {}
    """:type: dict
    Stores the masked intervals where the sensor objects are 'reliable',
    therefore can be considered in data association
    { sensorName<str> : {objNum<int> : mask<ndarray, shape (N,)>} }"""
    self._createCvr3Data(group)
    self._createSCamData(sCamGroups)
    self.K = self.L = 1
    self.C = np.zeros(self.N)
    self.isAssoSuccessful = np.zeros(self.N, dtype=np.bool)
    return

  def _selectScaleTime(self):
    scaleTimes = [self.cvr3scaleTime, self.sCamScaleTime]
    scaleTime = measparser.signalproc.selectTimeScale(scaleTimes, True)
    return scaleTime

  def _createEmptyTrackData(self):
    id = np.ones(self.N, dtype=np.int32)
    id *= INVALID_ID
    x = np.zeros(shape=(self.N, self.M))
    P = np.zeros(shape=(self.N, self.M, self.M))
    return id, x, P

  def _createCvr3Data(self, group):
    id, x, P = self._createEmptyTrackData()
    s1handle = self.source.getSignalFromSignalGroup(group, 'sit.S1.handle', **self.kwargs0)[1]
    maskValidS1 = s1handle != INVALID_FUS_HANDLE
    for k in xrange(FUS_OBJ_NUM):
      handle = self.source.getSignalFromSignalGroup(group, 'fusObj.i%d.handle' %k, **self.kwargs0)[1]
      mask = (handle==s1handle) & maskValidS1
      if not np.any(mask):
        continue
      # fill tracks
      for i, (stateTemplate, covarTemplate) in enumerate( zip(cvr3stateTemplates, cvr3varTemplates) ):
        # query and rescale signals
        state = self.source.getSignalFromSignalGroup(group, stateTemplate %k, Mask=mask, **self.kwargs01)[1]
        covar = self.source.getSignalFromSignalGroup(group, covarTemplate %k,            **self.kwargs0 )[1]
        x[mask,i]   = state[mask]
        P[mask,i,i] = covar[mask]
        id[mask]    = handle[mask]
    self.masks[CVR3] = maskValidS1
    self.tracks[CVR3] = x,P
    self.trackIds[CVR3] = id
    return

  def _createSCamData(self, groups):
    id, x, P = self._createEmptyTrackData()
    maskCipv = np.zeros_like(self.scaleTime, dtype=np.bool)
    # transform different message times to common message time
    for group in groups:
      # skip message if its signals are not present
      if len(group) != sCamGroupLen:
        continue
      # skip message if no cipv obstacle was transmitted
      cipvFlagOrig = self.source.getSignalFromSignalGroup(group, 'CIPV_Flag')[1]
      if not np.any(cipvFlagOrig):
        continue
      # convert signals to common message time
      signals = {} # { signalName<str> : signalOnCommonMessageTime<ndarrray> }
      for signalName in group.iterkeys():
        timeOrig, signalOrig = self.source.getSignalFromSignalGroup(group, signalName)
        if timeOrig is not self.sCamScaleTime:
          indices = measparser.signalproc.mapTimeToScaleTime(self.sCamScaleTime, timeOrig)
          signalNew  = np.zeros_like(self.sCamScaleTime, dtype=signalOrig.dtype)
          signalNew[indices] = signalOrig
        else:
          signalNew = signalOrig
        signals[signalName] = signalNew
      # put tracks together from messages
      idRescaled   = measparser.signalproc.rescale(self.sCamScaleTime, signals['ID'],        self.scaleTime)[1]
      maskOnSCamScaleTime = signals['CIPV_Flag'] == 1 # cipv flag signal is on int32, might be boolean later
      mask = measparser.signalproc.rescale(self.sCamScaleTime, maskOnSCamScaleTime, self.scaleTime, Order='zoh')[1]
      maskCipv |= mask
      id[mask] = idRescaled[mask]
      for i, (stateName, stdName) in enumerate( zip(sCamStateTemplates, sCamStdTemplates) ):
        state = measparser.signalproc.rescale(self.sCamScaleTime, signals[stateName], self.scaleTime, Order='mix', Mask=maskOnSCamScaleTime)[1]
        std   = measparser.signalproc.rescale(self.sCamScaleTime, signals[stdName],   self.scaleTime, Order='zoh')[1]
        x[mask,i]   = state[mask]
        P[mask,i,i] = np.square(std[mask])
    self.masks[SCAM] = maskCipv
    self.tracks[SCAM] = x,P
    self.trackIds[SCAM] = id
    return

  def _createCostMatrix(self):
    # step 1 - calculate cost matrices
    xi,Pi = self.tracks[CVR3]
    xj,Pj = self.tracks[SCAM]
    mask = self.masks[CVR3] & self.masks[SCAM] # when both tracks are valid
    if np.any(mask): # in case of overlapping intervals
      self.C[mask] = asso.association.calcCostMatrixElements(xi[mask],
                                                             xj[mask],
                                                             Pi[mask],
                                                             Pj[mask],
                                                             isDiag=True) # diagonal covariance matrices
    return

  def _calcGate(self):
    df = self.M # chi2 degree of freedom
    self.gate = asso.association.calcGate(asso.interface.DEFAULT_SIGNIF_LEVEL, scipy.stats.chi2, df)
    return

  def _associate(self):
    cvr3ids = self.trackIds[CVR3]
    sCamids = self.trackIds[SCAM]
    # loop over time ~N
    for n in xrange(self.N):
      if not np.allclose(self.C[n], self.invalidAssoCost):
        self.isAssoSuccessful[n] = True
        objPair = cvr3ids[n], sCamids[n]
        timeIndices = self.assoData.setdefault(objPair, [])
        timeIndices.append(n)
        self.objectPairs.append( [objPair] )
      else:
        self.objectPairs.append([])
    return

if __name__ == '__main__':
  import sys

  import fusutils

  measPath = sys.argv[1]
  source = measparser.cSignalSource(measPath)
  try:
    # asso object init (track inits using signal queries)
    assoObj = AssoCvr3SCamCipv(source)
  except measparser.signalgroup.SignalGroupError, error:
    # in case signals are not present
    print error.message
  else:
    # cost matrix calculation and track-to-track association
    assoObj.calc()
    if '-v' in sys.argv:
      # print out association result
      for k, assoList in enumerate(assoObj.objectPairs):
        print k, '%.2f' %assoObj.scaleTime[k], assoList
      # check if all base class attributes are set
      missings = fusutils.debug.checkAttributes(assoObj)
      if missings:
        print 'Attribute(s) might be unset: %s' %missings
  # close resources
  source.save()
