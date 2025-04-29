""" Interface for 2D track-to-track associations
"""

import numpy as np

import association
from pyutils.functional import cached_attribute
from measproc.IntervalList import maskToIntervals

DEFAULT_COST = 0.
INVALID_COST_COEFF = 10.
DEFAULT_SIGNIF_LEVEL = 0.95

__version__ = '0.2.1'

def occurence2pairs(assoData, n, **kwargs):
  """
  :Parameters:
      assoData : dict
        Associated object pair (1-1) occurences in time
      n : int
        Number of time steps
  :Keywords:
        Passed to `list.sort` function, affecting the order of object pairs.
  :ReturnType: list
  :Return:
    Associated object pairs (1-1) over time (empty list where no association was done)
  """
  pairs = [ [] for k in xrange(n) ]
  for (i,j), indices in assoData.iteritems():
    for k in indices:
      pairs[k].append( (i,j) )
  for elem in pairs:
    elem.sort(**kwargs)
  return pairs

def pairs2occurence(pairs):
  """
  :Parameters:
      pairs : list
        Associated object pairs (1-1) over time (empty list where no association was done)
  :ReturnType: dict
  :Return:
    Associated object pair (1-1) occurences in time
  """
  assoData = {}
  for k in xrange( len(pairs) ):
    for pair in pairs[k]:
      indices = assoData.setdefault(pair, [])
      indices.append(k)
  return assoData

class AssoObject(object):
  """ Abstract association object
  """
  
  def __init__(self):
    self.scaleTime = None
    """:type: ndarray
    Common scale time between sensors"""
    self.N = None
    """:type: int
    Time length (scale time size)"""
    self.K = None
    """:type: int
    1st sensor's maximal number of detected objects"""
    self.L = None
    """:type: int
    2nd sensor's maximal number of detected objects"""
    self.sensorNames = None
    """:type: tuple
    (1stSensorName<str>, 2ndSensorName<str>)"""
    self.params = None
    """:type: named tuple
    Parameters used in association"""
    self.C = None
    """:type: ndarray, shape (N, K, L)
    Assignment cost matrices, aligned in time (N times KxL matrices, where K is the 1st sensor's
    and L is the 2nd sensor's maximal object number)"""
    self.gate = None
    """:type: float
    Gate size"""
    self.invalidAssoCost = None
    """:type: float
    Invalid association cost in the assignment cost matrix"""
    self.maskInvalidAsso = None
    """:type: ndarray, shape (N, K, L)
    Masks invalid elements of the assignment cost matrix"""
    self.solver = None
    """Assignment problem solver. It is assumed that the solver object has a `compute` method 
    which performes the association using the assignment matrix"""
    self.isAssoSuccessful = None
    """:type: ndarray, shape (N,)
    Success in association over time (False if no association was done, otherwise True)
    """
    self.objectPairs = []
    """:type: list
    Associated object pairs (1-1) over time (empty list where no association was done)
    [
      [(objNum1stSensor<int>, objNum2ndSensor<int>), ], # scaleTime[0]
      [(objNum1stSensor<int>, objNum2ndSensor<int>), ], # scaleTime[1]
      ...
      ...
      [(objNum1stSensor<int>, objNum2ndSensor<int>), ]  # scaleTime[N-1]
    ]
    """
    self.objectGroups = []
    """:type: list
    Associated object groups (many-many) over time (empty list if no association was done)
    [
      [ (objGroup1stSensor<tuple>, objGroup2ndSensor<tuple>, ],
    ]
    """
    self.assoData = {}
    """:type: dict
    Associated object pair (1-1) occurences in time
    { (objNum1stSensor<int>, objNum2ndSensor<int>) : timeIndices<list, length 1...N> }"""
    self.maxNumOfAssociations = None
    """:type: int
    Maximum number of associations (over the whole time range)"""
    self.isAssoDone = False
    """:type: bool
    Indicates if association was done"""
    self.cmp = None
    """:type: method
    Comparison function to sort the list of object pairs. See `list.sort` for requirements"""
    return
  
  def calc(self):
    """ Calculates global optimal object associations in each time step.
    Results are stored in object attributes.
    """
    if not self.isAssoDone:
      self._createCostMatrix()
      self._calcGate()
      self._gating()
      self._associate()
      self.isAssoDone = True
    return
  
  def _createCostMatrix(self):
    """ Calculates cost matrices from sensor object attributes.
    """
    raise NotImplementedError()
    
  def _calcGate(self, *args, **kwargs):
    """ Calculates gate size.
    """
    raise NotImplementedError()
  
  def _gating(self):
    """ Performes gating on the cost matrices
    
    :Exceptions:
      AssertionError : if cost matrix or resulting gate size is invalid
    """
    # check cost matrix validity
    maskMeaningfulCosts = self.C > DEFAULT_COST
    assert     np.any(maskMeaningfulCosts)
    assert not np.any(self.C < DEFAULT_COST)
    assert not np.any(np.isinf(self.C))
    assert not np.any(np.isnan(self.C))
    # check gate size
    maxAssoCost = np.max(self.C)
    assert self.gate < maxAssoCost
    # gating
    self.invalidAssoCost = INVALID_COST_COEFF * self.gate # arbitrary large number
    self.maskInvalidAsso = (~maskMeaningfulCosts) | (self.C > self.gate)
    self.C[self.maskInvalidAsso] = self.invalidAssoCost
    return
  
  def _associate(self):
    """ Associate objects by finding minimal cost.
    """
    # loop over time ~N
    for n in xrange(self.N):
      C = self.C[n]
      maskInvalid = self.maskInvalidAsso[n]
      # step 1 - reduce matrix dimensions before association
      Ccut, validRows, validCols = association.shrinkCostMatrix(C, maskInvalid)
      # step 2 - solve (reduced) assignment problem
      indices = self.solver.compute(Ccut)
      # step 3 -register results
      self._register(n, Ccut, validRows, validCols, indices)
    # count the max number of associations
    self.maxNumOfAssociations = np.max( map(len, self.objectPairs) )
    return
  
  def _register(self, n, Ccut, validRows, validCols, indices):
    """ Register association results
    """
    assoObjIndices = []
    for rowNum, colNum in indices:
      # filter invalid association
      if not np.allclose(Ccut[rowNum, colNum], self.invalidAssoCost):
        rowObjNum = validRows[rowNum]
        colObjNum = validCols[colNum]
        objPair = (rowObjNum, colObjNum)
        assoObjIndices.append(objPair)
        timeIndices = self.assoData.setdefault(objPair, [])
        timeIndices.append(n)
    if assoObjIndices:
      self.isAssoSuccessful[n] = True
      assoObjIndices.sort(cmp=self.cmp) # in-place sort of tuple elements
    self.objectPairs.append(assoObjIndices)
    return

  def get_1to1_violations(self):
    """ Check if one-to-one (1-1) association assumption is violated

    :ReturnType: list
    :Return:
      List of time indices where violations happen (empty list if no violation)
    :Exceptions:
      AssertionError : if association object is inconsistent or not ready
    """
    assert self.is_consistent() and self.isAssoDone
    out = []
    if self.maxNumOfAssociations > 0:
      for k, pairs in enumerate(self.objectPairs):
        if not pairs:
          continue
        ii = [i for i,_ in pairs]
        jj = [j for _,j in pairs]
        if len(ii) != len( set(ii) ) or len(jj) != len( set(jj) ):
          out.append(k)
    return out

  def is_consistent(self):
    return self.N == self.scaleTime.size == len(self.objectPairs)

  def get_sensor_objects(self, sensorname):
    """ Get objects of the given `sensorname` that are involved in association """
    ndx = self.sensorNames.index(sensorname)
    return set( pair[ndx] for pair in self.assoData )

  def get_pair_of_obj(self, sensorname, objnum, timestamp):
    ndx = self.sensorNames.index(sensorname)
    ndx_other = int( not ndx ) # toggle between 0 and 1
    for pair in self.objectPairs[timestamp]:
      if objnum == pair[ndx]:
        return pair[ndx_other]
    raise ValueError( 'Pair of %s object %d at timestamp %d not found!'
                      %(sensorname, objnum, timestamp) )

  def get_objs_at(self, sensorname, timestamp):
    ndx = self.sensorNames.index(sensorname)
    return set( pair[ndx] for pair in self.objectPairs[timestamp] )

  def is_obj_assod_at(self, sensorname, objnum, timestamp):
    return objnum in self.get_objs_at(sensorname, timestamp)

  @cached_attribute
  def asso_intervals(self):
    """ { (i,j) : [(st,end),] } """
    assert self.is_consistent() and self.isAssoDone
    res = {}
    for (i,j), indices in self.assoData.iteritems():
      mask = np.zeros(self.N, dtype=np.bool)
      mask[indices] = True
      res[i,j] = maskToIntervals(mask)
    return res

  def is_obj_assod_during(self, sensorname, objnum, st, end, wholetime=False, index=False):
    """
    Return True if requested sensor's object is associated during the interval.

    :Parameters:
      sensorname : str
      objnum : int
      st : int
      end : int
      wholetime : bool, optional
        Check if association exists the whole time. Default is False.
      index : bool, optional
        If set to True, first time index occurrence is also given. Default is False.
        None is returned, if the object is not associated during the interval.
    :ReturnType: bool, [int]
    """
    assod = [ self.is_obj_assod_at(sensorname, objnum, k) for k in xrange(st,end) ]
    fn = all if wholetime else any
    res = fn(assod)
    if index:
      idx = st + assod.index(True) if res else None
      out = res, idx
    else:
      out = res
    return out

  def __str__(self):
    elems = [ '%d %.3f %s' %(k, self.scaleTime[k], assoList) for k, assoList in enumerate(self.objectPairs) ]
    out = '\n'.join(elems)
    return out
