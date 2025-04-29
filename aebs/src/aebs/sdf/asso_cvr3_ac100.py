""" Associates the OHL objects of CVR3 and the Tracks of AC100 for a given measurement.
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

import measparser
import asso
from assoOHL import correctNorming, cvr3deviceNames, CVR3, OHL_OBJ_NUM

AC100_MESSAGE_NUM = 10
AC100_OBJ_NUM = 20
NORM_CREDIB = 1. / float(2**6 - 1) # credibility norming [0..63] -> [0..1]
TRACK_IS_EMPTY = 0
AC100_VAR_ESTIM = (1.0, # varDx estimate [m^2]
                   1.0, # varDy estimate [m^2]
                   1.1) # varVx estimate [(m/s)^2]
AC100 = 'AC100'
# CVR3 signal group definitions
ohlNamePrefixes = (
  'ohl.ObjData_TC.OhlObj.', # nomenclature till B2 sample
  'ohy.ObjData_TC.OhlObj.', # nomenclature from B4 sample
)

cvr3stateTemplates = {
#  signal name    pos   phys unit
  'i%d.dx'    :  (0,     'm'  ),
  'i%d.dy'    :  (1,     'm'  ),
  'i%d.vx'    :  (2,     'm/s'),
}
cvr3varTemplates = {
#  signal name    pos   phys unit
  'i%d.varDx' : ((0,0), '-'), # [m^2]
  'i%d.varDy' : ((1,1), '-'), # [m^2]
  'i%d.varVx' : ((2,2), '-'), # [(m/s)^2]
}
cvr3signalGroups = []
for ohlPrefix in ohlNamePrefixes:
  for cvr3deviceName in cvr3deviceNames:
    cvr3signalGroup   = {}
    for i in xrange(OHL_OBJ_NUM):
      cvr3signalGroup['i%d.wExistProb' %i] = (cvr3deviceName, ohlPrefix + 'i%d.wExistProb'  %i)
      cvr3signalGroup['i%d.stationary' %i] = (cvr3deviceName, ohlPrefix + 'i%d.c.c.Stand_b' %i)
      cvr3signalGroup['i%d.guardrail'  %i] = (cvr3deviceName, ohlPrefix + 'i%d.wConstElem'  %i)
      cvr3signalGroup['i%d.age'        %i] = (cvr3deviceName, ohlPrefix + 'i%d.internal.CntAlive' %i)
      for stateTemplate, varTemplate in zip(cvr3stateTemplates, cvr3varTemplates):
        cvr3signalGroup[stateTemplate %i] = (cvr3deviceName, ohlPrefix + stateTemplate %i)
        cvr3signalGroup[varTemplate   %i] = (cvr3deviceName, ohlPrefix + varTemplate   %i)
    cvr3signalGroups.append(cvr3signalGroup)

# AC100 signal group definitions
ac100signalTemplates = (
  'tr%d_range'                 ,
  'tr%d_uncorrected_angle'     ,
  'tr%d_relative_velocitiy'    ,
  'tr%d_credibility'           ,
  'tr%d_internal_track_index'  ,
  'tr%d_track_selection_status',
  'tr%d_tracking_status'       ,
)
ac100signalGroup = {}
ac100deviceName = 'Tracks'
for k in xrange(AC100_MESSAGE_NUM):
  for signalTemplate in ac100signalTemplates:
    signalName = signalTemplate %k
    ac100signalGroup[signalName] = (ac100deviceName, signalName)
ac100signalGroups = [ac100signalGroup, ]

# composite signal group, contains all the CVR3 and the minimum AC100 signals (must be present for association)
signalGroups = []
for cvr3signalGroup in cvr3signalGroups:
  signalGroup = cvr3signalGroup.copy() # shallow copy, does not harm (string and tuple are immutable)
  signalGroup['protocol_version'] = 'General_radar_status', 'A087MB_version'
  for signalTemplate in ac100signalTemplates:
    signalName = signalTemplate %0 # at least track message #0 must be transmitted
    signalGroup[signalName] = (ac100deviceName, signalName)
  signalGroups.append(signalGroup)

class AssoCvr3Ac100(asso.interface.AssoObject):
  def __init__(self, source, scaleTime=None, reliabilityLimit=0.4, mapAc100credib=lambda x:x):
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
        mapAc100credib : function
          Mapping between AC100 track (normed) credibility and reliability: [0,1] -> [0,1]
          Default mapping is linear.
    :Exceptions:
      measparser.signalgroup.SignalGroupError : if required signals are not present
    """
    asso.interface.AssoObject.__init__(self)

    self.reliabilityLimit = reliabilityLimit
    """:type: float
    Track reliability threshold, in 0...1 range"""
    self.sensorNames = (CVR3, AC100)
    self.source = source
    """:type: measparser.cSignalSource
    Measurement signal source"""
    self.group = self.source.selectSignalGroup(signalGroups)
    """:type: dict
    Composite signal group (all CVR3 and the minimum AC100 signals)"""
    self.ac100Group, = self.source.filterSignalGroups(ac100signalGroups)
    """:type: dict
    AC100 signal group (not all the signals might be present)"""
    self.ac100scaleTime = self.source.getSignalFromSignalGroup(self.group, 'tr0_range')[0]
    """:type: numpy.ndarray
    Common scale time for AC100 tracks (merged from several CAN messages on different transmission times)
    Note: message #0 is always sent in each transmission cycle"""
    self.scaleTime = scaleTime if scaleTime is not None else self._selectScaleTime()
    self.ac100signals = {}
    """:type: dict
    AC100 signals on common message time { signalName<str> : signal<ndarray> } """
    self.kwargs0 = dict(ScaleTime=self.scaleTime, Order='zoh')
    """:type: dict
    Keyword arguments for signal queries (scale time and interpolation order)"""
    self.N = self.scaleTime.size
    self.M = len(cvr3stateTemplates)
    """:type: int
    State dimension"""
    self.tracks = {}
    """:type: dict
    Sensor tracks { sensorName<str> : {objNum<int> : (state<ndarray>, covarmtx<ndarray>),} }
    Note: some AC100 internal tracks might not be present in measurement"""
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

    for sensorName in (CVR3, AC100):
      self.tracks[sensorName] = {}
      # interface tracks
      self.posTracks[sensorName] = {}
      self.velTracks[sensorName] = None # AC100 does not provide enough information
      # other attributes
      self.reliability[sensorName] = {}
      self.masks[sensorName] = {}
      self.movingState[sensorName] = {}
    self._createCvr3Data()
    self._createAc100Data(mapAc100credib)
    self.K = OHL_OBJ_NUM
    self.L = len(self.tracks[AC100]) # not all AC100 internal tracks might be transmitted
    self.C = np.zeros(shape=(self.N, OHL_OBJ_NUM, AC100_OBJ_NUM))
    self.solver = asso.hungarian._Hungarian()
    self.isAssoSuccessful = np.zeros(self.N, dtype=np.bool)
    return

  def _selectScaleTime(self):
    # dummy time queries
    scaleTimeCvr3  = self.source.getSignalFromSignalGroup(self.group, 'i0.dx')[0]
    scaleTimes = [scaleTimeCvr3, self.ac100scaleTime]
    scaleTime = measparser.signalproc.selectTimeScale(scaleTimes, True)
    return scaleTime

  def _createCvr3Data(self):
    for i in xrange(OHL_OBJ_NUM):
      # fill tracks
      x = self._getCvr3States(i)
      P = self._getCvr3CovarMatrices(i)
      self.tracks[CVR3][i] = (x,P)
      self.posTracks[CVR3][i] = (x[:,:2],P[:,:2,:2])
      # set reliability
      existProb = self.source.getSignalFromSignalGroup(self.group, 'i%d.wExistProb' %i, **self.kwargs0)[1]
      reliability = existProb
      self.reliability[CVR3][i] = reliability
      self.masks[CVR3][i] = reliability > self.reliabilityLimit
      # set moving state
      stationary = self.source.getSignalFromSignalGroup(self.group, 'i%d.stationary' %i, **self.kwargs0)[1]
      self.movingState[CVR3][i] = stationary.astype(np.bool)

  def _getCvr3States(self, objNum):
    x = np.zeros(shape=(self.N, self.M))
    for stateTemplate, (i, physUnit) in cvr3stateTemplates.iteritems():
      t, state = self.source.getSignalFromSignalGroup(self.group, stateTemplate %objNum)
      mask = state != 0
      state = self.source.rescale(t, state, self.scaleTime, Order='mix', Mask=mask)[1]
      physUnitMeas = self.source.getPhysicalUnitFromSignalGroup(self.group, stateTemplate %objNum)
      state = correctNorming(state, physUnit, physUnitMeas)
      x[:,i] = state
    return x

  def _getCvr3CovarMatrices(self, objNum):
    P = np.zeros(shape=(self.N, self.M, self.M))
    for covarTemplate, ((i,j), physUnit) in cvr3varTemplates.iteritems():
      t, covar = self.source.getSignalFromSignalGroup(self.group, covarTemplate %objNum)
      covar = self.source.rescale(t, covar, self.scaleTime, Order='zoh')[1]
      physUnitMeas = self.source.getPhysicalUnitFromSignalGroup(self.group, covarTemplate %objNum)
      covar = correctNorming(covar, physUnit, physUnitMeas)
      P[:,i,j] = covar
    return P

  def _createAc100Data(self, mapAc100credib):
    # find transformation of different message times to common message time
    signalName2indices = {} # { signalName<str> : (mapping<ndarray>, start<int>, end<int>) }
    messageNums = [] # message numbers which are present
    # mapping between individual message times and common message time
    for k in xrange(AC100_MESSAGE_NUM):
      # skip track message if required signals are not present (usually #5-#9 is not sent)
      for signalTemplate in ac100signalTemplates:
        if (signalTemplate %k) not in self.ac100Group:
          break
      else:
        # all the necessary signals are transmitted in current message
        messageNums.append(k)
        # signals within the same message can be transmitted on different time
        mapping, start, end = None, None, None
        for signalTemplate in ac100signalTemplates:
          signalName = signalTemplate %k
          timeOrig = self.source.getSignalFromSignalGroup(self.ac100Group, signalName)[0] # original time
          if timeOrig is not self.ac100scaleTime:
            # handle critical periods (when measurement started/ended during message transmissions)
            if timeOrig[0] < self.ac100scaleTime[0]:
              start = 1
            if timeOrig[-1] > self.ac100scaleTime[-1]:
              end = -1
            if start is not None or end is not None:
              timeOrig = timeOrig[start:end] # indexing with None does not affect basic slicing
            mapping = measparser.signalproc.mapTimeToScaleTime(self.ac100scaleTime, timeOrig)
          # register signal mapping properties
          signalName2indices[signalName] = mapping, start, end
    # transform AC100 signals to common message time
    for signalName, (mapping, start, end) in signalName2indices.iteritems():
      signal = self.source.getSignalFromSignalGroup(self.ac100Group, signalName)[1]
      if mapping is not None:
        # current message time is different from common message time
        newsignal = np.zeros_like(self.ac100scaleTime, dtype=signal.dtype)
        if start is not None or end is not None:
          # remove outliers
          newsignal[mapping] = signal[start:end]
        else:
          newsignal[mapping] = signal
      else:
        newsignal = signal.copy()
        newsignal[-1] = 0 # clear (set to default) the last element of each signal on common message time
      self.ac100signals[signalName] = newsignal
    # for each object: put the state together from track messages
    for i in xrange(AC100_OBJ_NUM):
      messageNum2mask = {}
      # loop through all track messages
      for k in messageNums:
        mask = (self.ac100signals['tr%d_internal_track_index' %k] == i) & \
               (self.ac100signals['tr%d_tracking_status' %k] != TRACK_IS_EMPTY)
        if np.any(mask):
          messageNum2mask[k] = mask
      # skip current AC100 internal track if it was not available in messages
      if not messageNum2mask:
        continue
      # fill tracks
      x = self._getAc100States(messageNum2mask)
      P = self._estimAc100CovarMatrices()
      self.tracks[AC100][i] = (x,P)
      self.posTracks[AC100][i] = (x[:,:2],P[:,:2,:2])
      # set reliability
      credibility = self._getAc100objectSignal('tr%d_credibility', messageNum2mask)
      credibilityNorm = credibility * NORM_CREDIB # norm credibility
      reliability = mapAc100credib(credibilityNorm) # map credibility to reliability
      self.reliability[AC100][i] = reliability
      self.masks[AC100][i] = reliability > self.reliabilityLimit
      # set moving state
      stationary = self._getAc100objectSignal('tr%d_track_selection_status', messageNum2mask)
      stationary &= 2**4 # according to AC100 signal description database
      self.movingState[AC100][i] = stationary.astype(np.bool)
    return

  def _getAc100States(self, messageNum2mask):
    objRange = self._getAc100objectSignal('tr%d_range'             , messageNum2mask, Order='mix')
    angleDeg = self._getAc100objectSignal('tr%d_uncorrected_angle' , messageNum2mask, Order='mix')
    vx       = self._getAc100objectSignal('tr%d_relative_velocitiy', messageNum2mask, Order='mix')
    angleRad = np.radians(angleDeg)
    # handle angle direction change in protocol
    version  = self.source.getSignalFromSignalGroup(self.group, 'protocol_version')[1]
    assert np.all(np.diff(version) == 0), "Inconsistent protocol version information"
    angleDir = 1.0 if version[0] > 6 else -1.0  # angle direction changed in version 7
    # position data
    dx = objRange * np.cos(angleRad) * angleDir
    dy = objRange * np.sin(angleRad) * angleDir
    x = np.vstack( (dx,dy,vx) )
    x = x.transpose() # creates view whenever possible
    return x

  def _estimAc100CovarMatrices(self):
    P = np.diag(AC100_VAR_ESTIM)
    P = np.resize(P, (self.N, self.M, self.M))
    return P

  def _getAc100objectSignal(self, signalTemplate, messageNum2mask, Order='zoh'):
    """ Collects the required AC100 internal track's signal from track messages.

    :Parameters:
        signalTemplate : str
          AC100 track message signal template (without message number)
        messageNum2mask : dict
          Occurrence (in common message time) of the required internal track in the messages
          { messageNum<int> : mask<ndarray> }
    :ReturnType: ndarray or None
    :Exceptions:
      ValueError : if `messageNum2mask` is empty
    """
    if not messageNum2mask:
      raise ValueError('No internal track occurrence!')
    # get track's signal (on common message time)
    signal = None
    for k, mask in messageNum2mask.iteritems():
      signalName = signalTemplate %k
      newsignal = self.ac100signals[signalName]
      if signal is None:
        signal = np.zeros_like(newsignal)
      signal[mask] = newsignal[mask]
    # rescale signal
    if self.scaleTime is not self.ac100scaleTime:
      if Order=='mix':
        mask = signal != 0
      else:
        mask = None
      _, rescaledSignal = self.source.rescale(self.ac100scaleTime, signal, self.scaleTime, Order=Order, Mask=mask)
    else:
      rescaledSignal = signal
    return rescaledSignal

  def _createCostMatrix(self):
    # step 1 - calculate cost matrices (object loop ~40x10)
    for i in xrange(OHL_OBJ_NUM):
      xi,Pi = self.tracks[CVR3][i]
      reliability_i = self.masks[CVR3][i]
      for j in xrange(AC100_OBJ_NUM):
        if j not in self.tracks[AC100]: # skip track if it was not transmitted
          continue
        xj,Pj = self.tracks[AC100][j]
        reliability_j = self.masks[AC100][j]
        mask = reliability_i & reliability_j # when both tracks are reliable
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
  import sys

  import fusutils

  measPath = sys.argv[1]
  source = measparser.cSignalSource(measPath)
  try:
    # asso object init (track inits using signal queries)
    assoObj = AssoCvr3Ac100(source, mapAc100credib=lambda x:x**(1./3.)) # nonlinear AC100 credibility mapping
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
