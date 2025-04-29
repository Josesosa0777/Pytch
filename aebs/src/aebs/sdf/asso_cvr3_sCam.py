""" Associates the tracks of CVR3 and S-Cam sensors for a given measurement.
The association is based on the object position and longitudinal relative velocity:

         [dx]          [varDx,     0,     0]
 state = [dy]  covar = [0    , varDy,     0]
         [vx]          [0    ,     0, varVx]
         
Statistical distances are calculated and gating is applied, resulting an assignment 
cost matrix in each time step. The assignment problem is solved using a selected 
optimization method.
"""

from datavis import pyglet_workaround  # necessary as early as possible (#164)

import numpy as np
import scipy.stats

from assoOHL                import OHL_OBJ_NUM
from asso_cvr3_sCam_cipv    import CVR3, SCAM, \
                                   sCamSignalGroups, sCamGroupLen, \
                                   sCamSignalTemplates, sCamStateTemplates, sCamStdTemplates
from asso_cvr3_ac100        import cvr3signalGroups, cvr3stateTemplates, cvr3varTemplates, \
                                   correctNorming
import asso
import measparser
import measproc.IntervalList

__version__ = '0.1.4'

SCAM_TRACK_NUM = 64 # number of S-Cam internal tracks
SCAM_STATUS_STANDING = 1
SCAM_STATUS_PARKED   = 5

# object filtering params
GUARDRAIL_LIMIT = 0.3
AGE_LIMIT = 10

# gating params
SIGNIFICANCE_LEVEL = 0.99
LAMBDA = 4.

# required signal group: contains all the CVR3 and the minimum S-Cam signals
signalGroups = []
for cvr3signalGroup in cvr3signalGroups:
  signalGroup = cvr3signalGroup.copy() # shallow copy, does not harm (string and tuple are immutable)
  signalGroup['sCamNumObstacles'] = 'Obstacle_Status', 'Num_Obstacles'
  for signalName, deviceNameTemplate in sCamSignalTemplates.iteritems():
    signalGroup[signalName] = (deviceNameTemplate %1, signalName) # first S-Cam message must be present
  signalGroups.append(signalGroup)

class AssoCvr3SCam(asso.interface.AssoObject):
  def __init__(self, source, scaleTime=None, reliabilityLimit=0.1, Solver=asso.munkres.Munkres):
    """
    :Parameters:
        source : measparser.cSignalSource
          Measurement signal source
    :KeyWords:
        scaleTime : numpy.ndarray
          Common scale time for data association. If not specified, the most dense (in average) 
          sensor time is selected.
        reliabilityLimit : float
          Required object reliability level in [0,1] range
        Solver : classobj
          Assignment solver class. The instance of the class should have a `compute` method that
          works on a cost matrix.
    :Exceptions:
      measparser.signalgroup.SignalGroupError : if required signals are not present
    """
    asso.interface.AssoObject.__init__(self)
    
    self.reliabilityLimit = reliabilityLimit
    """:type: float
    Track reliability threshold, in 0...1 range"""
    self.sensorNames = (CVR3, SCAM)
    self.source = source
    """:type: measparser.cSignalSource
    Measurement signal source"""
    self.group = self.source.selectSignalGroup(signalGroups)
    """:type: dict
    Composite signal group (all CVR3 and the minimum S-Cam signals)"""
    sCamGroups = self.source.filterSignalGroups(sCamSignalGroups)
    """:type: list
    S-Cam signal group (not all the signals might be present)"""
    self.cvr3scaleTime = self.source.getSignalFromSignalGroup(self.group, 'i0.wExistProb')[0]
    """:type: numpy.ndarray
    Common scale time for CVR3 tracks"""
    self.sCamScaleTime, self.sCamNumObstacles = self.source.getSignalFromSignalGroup(self.group, 'sCamNumObstacles')
    """:type: numpy.ndarray
    Common scale time for S-Cam tracks"""
    self.scaleTime = scaleTime if scaleTime is not None else self._selectScaleTime()
    self.sCamSignals = {}
    """:type: dict
    S-Cam signals on common message time { messageNum<int> : {signalName<str> : signal<ndarray>} } """
    self.kwargs0  = dict(ScaleTime=self.scaleTime, Order='zoh')
    self.kwargs01 = dict(ScaleTime=self.scaleTime, Order='mix')
    """:type: dict
    Keyword arguments for signal queries (scale time and interpolation order)"""
    self.K = OHL_OBJ_NUM
    self.L = SCAM_TRACK_NUM
    self.N = self.scaleTime.size
    self.M = len(cvr3stateTemplates)
    """:type: int
    State dimension"""
    self.ages = {}
    """:type: dict
    Track ages { sensorName<str> : {objNum<int> : age<ndarray>,} }"""
    self.guardrailProbs = {}
    """:type: dict
    CVR3 object guardrail element probability {objNum<int> : guardrailProb<ndarray>,}"""
    self.tracks = {}
    """:type: dict
    Sensor tracks (with all kinematic states)
    { sensorName<str> : {objNum<int> : (state<ndarray, shape (N,M)>, covarmtx<ndarray, shape (N,M,M)>),} }"""
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
      # init interface attributes
      self.tracks[sensorName] = {}
      self.reliability[sensorName] = {}
      self.masks[sensorName] = {}
      self.movingState[sensorName] = {}
      self.ages[sensorName] = {}
    self._createCvr3Data()
    self._createSCamData(sCamGroups)
    self.C = np.zeros(shape=(self.N, self.K, self.L), dtype=np.float32)
    self.solver = Solver()
    self.isAssoSuccessful = np.zeros(self.N, dtype=np.bool)
    return
  
  def _selectScaleTime(self):
    scaleTimes = [self.cvr3scaleTime, self.sCamScaleTime]
    scaleTime = measparser.signalproc.selectTimeScale(scaleTimes, True)
    return scaleTime
  
  def _createCvr3Data(self):
    for i in xrange(OHL_OBJ_NUM):
      # fill tracks
      x = self._getCvr3States(i)
      P = self._getCvr3CovarMatrices(i)
      self.tracks[CVR3][i] = (x,P)
      # set track mask (filtering unreliable objects)
      reliability = self.source.getSignalFromSignalGroup(self.group, 'i%d.wExistProb' %i, **self.kwargs0)[1]
      age = self.source.getSignalFromSignalGroup(self.group, 'i%d.age' %i, **self.kwargs0)[1]
      self.ages[CVR3][i] = age
      self.reliability[CVR3][i] = reliability
      mask = reliability > self.reliabilityLimit
      mask |= age > AGE_LIMIT
      # object that has passed the filter once in its lifetime is kept until disappearance
      valid = reliability > 0
      holes = ~mask # where reliability is not sufficient
      intervals = measproc.IntervalList.maskToIntervals(holes)
      for start, end in intervals:
        if start != 0 and np.all(valid[start:end]):
          # restore hole if object was alive (hole at the beginning of time can never be restored)
          mask[start:end] = True
      self.masks[CVR3][i] = mask
      # set moving state
      stationary = self.source.getSignalFromSignalGroup(self.group, 'i%d.stationary' %i, **self.kwargs0)[1]
      self.movingState[CVR3][i] = stationary.astype(np.bool)
      # set guardrail probability
      self.guardrailProbs[i] = self.source.getSignalFromSignalGroup(self.group, 'i%d.guardrail' %i, **self.kwargs0)[1]
      
  def _getCvr3States(self, objNum):
    x = np.zeros(shape=(self.N, self.M), dtype=np.float32)
    for stateTemplate, (i, physUnit) in cvr3stateTemplates.iteritems():
      t, state = self.source.getSignalFromSignalGroup(self.group, stateTemplate %objNum)
      mask = state != 0
      state = self.source.rescale(t, state, self.scaleTime, Order='mix', Mask=mask)[1]
      physUnitMeas = self.source.getPhysicalUnitFromSignalGroup(self.group, stateTemplate %objNum)
      state = correctNorming(state, physUnit, physUnitMeas)
      x[:,i] = state
    return x
    
  def _getCvr3CovarMatrices(self, objNum):
    P = np.zeros(shape=(self.N, self.M, self.M), dtype=np.float32)
    for covarTemplate, ((i,j), physUnit) in cvr3varTemplates.iteritems():
      t, covar = self.source.getSignalFromSignalGroup(self.group, covarTemplate %objNum)
      covar = self.source.rescale(t, covar, self.scaleTime, Order='zoh')[1]
      physUnitMeas = self.source.getPhysicalUnitFromSignalGroup(self.group, covarTemplate %objNum)
      covar = correctNorming(covar, physUnit, physUnitMeas)
      P[:,i,j] = covar
    return P
      
  def _createSCamData(self, groups):
    # query and transform signals on different message times to common message time
    ids, messageMasks = self._alignSCamMessageData(groups)
    # put the tracks together from aligned CAN messages
    self._collectSCamTrackData(ids, messageMasks)
    return
    
  def _alignSCamMessageData(self, groups):
    """ Queries and transforms all S-Cam obstacle signals on different message times to common message time.
    The following graph shows an example of the common message ('x'), original message ('*') and rescaled 
    message time stamps ('|').
    
    common time ---x-------x-------x-------x-------x-------x-------x-------x-----
    1st message ---|*------|*------|*------|*------|-------|*------|*------|*----
    2nd message ---|-*-----|-*-----|-*-----|-------|-------|-*-----|-*-----|-*---
    3rd message ---|--*----|--*----|-------|-------|-------|-------|--*----|-----
    
    Assumptions: 
      - the common message time *always* indicates the start of a transmission (sent before each obstacle message, 
        even if no obstacle message is transmitted)
      - each time domain is positive (necessary for rescale trick) and strictly increasing (general requirement)
      - the obstacle messages are sent in strict order, i.e. if message K is sent then K-1 had been sent before
      - the value of the obstacle number signal corresponds to the messages that were transmitted: 
          0: no obstacle
          1: obstacle data in message 01
          2: obstacle data in message 01, 02
          3: obstacle data in message 01, 02, 03
          ...
    
    :Parameters:
        groups : list
          [message01group<dict>, message02group<dict>, ...]
    """
    ids = set() # transmitted track IDs
    groupsLen = len(groups)
    sCamScaleTimeFlip = -self.sCamScaleTime[::-1] # for later rescale trick
    oldmask = np.zeros_like(self.sCamScaleTime, dtype=np.bool)
    messageMasks = {} # { messageNum<int> : mask<ndarray> }
    # reverse loop on message groups
    for k in xrange(groupsLen,0,-1):
      # get masks where individual messages were transmitted
      mask = self.sCamNumObstacles == k
      mask |= oldmask
      oldmask = mask
      messageMasks[k] = mask
    # normal loop on message groups
    for k in xrange(1,groupsLen+1):
      group = groups[k-1]
      # skip message if its signals are not present
      if len(group) != sCamGroupLen:
        continue
      mask = messageMasks[k]
      # convert signals to common message time
      signals = {} # { signalName<str> : signalOnCommonMessageTime<ndarrray> }
      for signalName in group.iterkeys():
        timeOrig, signalOrig = self.source.getSignalFromSignalGroup(group, signalName)
        if signalName == 'ID':
          ids.update( np.unique(signalOrig) )
        if timeOrig is not self.sCamScaleTime:
          timeOrigFlip = -timeOrig[::-1]
          signalOrigFlip = signalOrig[::-1]
          _, signalNewFlip = measparser.signalproc.rescale(timeOrigFlip, signalOrigFlip, sCamScaleTimeFlip, Order='zoh')
          signalNew = signalNewFlip[::-1]
        else:
          signalNew = signalOrig
        signalNew[~mask] = 0 # set invalid values to default (zero)
        signals[signalName] = signalNew
      self.sCamSignals[k] = signals
    return ids, messageMasks
  
  def _collectSCamTrackData(self, ids, messageMasks):
    for id in ids:
      x = np.zeros(shape=(self.N, self.M)        , dtype=np.float32)
      P = np.zeros(shape=(self.N, self.M, self.M), dtype=np.float32)
      # get track occurrence in CAN messages
      trackInAllMessagesMask = np.zeros_like(self.sCamScaleTime, dtype=np.bool)
      message2trackMask = {}
      for k, signals in self.sCamSignals.iteritems():
        basemask = messageMasks[k] # get where message was sent on common message time
        trackInMessageMask = id == signals['ID']
        trackInMessageMask &= basemask # avoid collecting invalid values (e.g. 0==ID mask might cover default zero values)
        if np.any(trackInMessageMask):
          message2trackMask[k] = trackInMessageMask
          trackInAllMessagesMask |= trackInMessageMask
      # rescale track occurrence mask from S-Cam common message time to association time
      mask = measparser.signalproc.rescale(self.sCamScaleTime, trackInAllMessagesMask, self.scaleTime, Order='zoh')[1]
      # query, join and rescale signals
      for i, (stateName, stdName) in enumerate( zip(sCamStateTemplates, sCamStdTemplates) ):
        state = self._getSCamTrackSignal(stateName, message2trackMask, order='mix', mask=trackInAllMessagesMask)
        std   = self._getSCamTrackSignal(stdName  , message2trackMask, order='zoh')
        x[mask,i]   = state[mask]
        P[mask,i,i] = np.square( std[mask] )
      self.tracks[SCAM][id] = x,P
      self.masks[SCAM][id] = mask # S-Cam objects are always considered to be 'reliable' (when received in a message)
      # set moving state
      status = self._getSCamTrackSignal('Status', message2trackMask, order='zoh')
      stationary = (status == SCAM_STATUS_STANDING) | (status == SCAM_STATUS_PARKED)
      self.movingState[SCAM][id] = stationary
      self.ages[SCAM][id] = self._getSCamTrackSignal('Age', message2trackMask, order='zoh')
    return
    
  def _getSCamTrackSignal(self, signalName, message2trackMask, order='zoh', mask=None):
    """ Collects the required S-Cam internal track's signal from CAN messages and 
    rescales them to the association time.
    
    :Parameters:
        signalName : str
          S-Cam signal name
        message2trackMask : dict
          Occurrence (on common message time) of the required internal track in the messages
          { messageNum<int> : mask<ndarray> }
        order : str
          Interpolation order
        mask : ndarray
          Track (ID) occurrence on common message time
    :ReturnType: ndarray
    :Exceptions:
      AssertionError : if `message2trackMask` is empty
    """
    assert message2trackMask
    # get track's signal (on common message time)
    signal = None
    for k, trackInMessageMask in message2trackMask.iteritems():
      newsignal = self.sCamSignals[k][signalName]
      if signal is None:
        signal = np.zeros_like(newsignal)
      signal[trackInMessageMask] = newsignal[trackInMessageMask]
    # rescale signal to association time
    _, rescaledSignal = measparser.signalproc.rescale(self.sCamScaleTime, signal, self.scaleTime, Order=order, Mask=mask)
    return rescaledSignal
  
  def _createCostMatrix(self):
    # step 1 - calculate cost matrices (object loop ~40x20)
    for i in xrange(OHL_OBJ_NUM):
      xi,Pi = self.tracks[CVR3][i]
      mask_i = self.masks[CVR3][i]
      guardrail_i = self.guardrailProbs[i] > GUARDRAIL_LIMIT
      for j in xrange(SCAM_TRACK_NUM):
        if j not in self.tracks[SCAM]: # skip track if it was not transmitted
          continue
        xj,Pj = self.tracks[SCAM][j]
        mask_j = self.masks[SCAM][j]
        mask = mask_i & mask_j # when both tracks are reliable
        # avoid association of CVR3 guardrails with S-Cam moving objects
        moving_j = ~self.movingState[SCAM][j]
        cvr3_guardrail_scam_moving = guardrail_i & moving_j
        mask &= ~cvr3_guardrail_scam_moving
        # calculate cost in case of overlapping intervals
        if np.any(mask):
          self.C[mask,i,j] = asso.association.calcCostMatrixElements(xi[mask], 
                                                                     xj[mask], 
                                                                     Pi[mask], 
                                                                     Pj[mask],
                                                                     isDiag=True) # diagonal covariance matrices
    return
  
  def _calcGate(self):
    kwargs = dict(scale = 1./LAMBDA)
    self.gate = asso.association.calcGate(SIGNIFICANCE_LEVEL, scipy.stats.expon, **kwargs)
    return
      
  def _associate(self):
    for n in xrange(self.N):
      # step 0 - gating
      C = self.C[n]
      maskAboveGate = C >= self.gate
      if n > 0:
        # consider association history in gating
        for i,j in self.objectPairs[n-1]:
          if C[i,j] < self.invalidAssoCost:
            # skip gating if objects were associated in last cycle
            maskAboveGate[i,j] = False
      maskInvalid = self.maskInvalidAsso[n] # view on array
      maskInvalid |= maskAboveGate
      C[maskInvalid] = self.invalidAssoCost
      # step 1 - reduce matrix dimensions before association
      Ccut, validRows, validCols = asso.association.shrinkCostMatrix(C, maskInvalid)
      # step 2 - solve (reduced) assignment problem
      indices = self.solver.compute(Ccut)
      # step 3 - register results
      self._register(n, Ccut, validRows, validCols, indices)
    # count the max number of associations
    self.maxNumOfAssociations = np.max( map(len, self.objectPairs) )
    return


if __name__ == '__main__':
  import sys
  
  import fusutils
  
  measPath = sys.argv[1]
  source = measparser.cSignalSource(measPath)
  try:
    # asso object init (track inits using signal queries)
    assoObj = AssoCvr3SCam(source)
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
