#!/usr/bin/python

import sys
import copy
import collections
import logging

import numpy as np

import measparser
from measparser.signalproc import mapTimeToScaleTime, isSameTime

def argsort(seq, **kwargs):
  """
  Return the indices that would sort the sequence. See `sorted` for details.

  :Keywords:
    cmp : function
      Comparison function
    reverse : bool
      Sort in reverse order, default is False.
  """
  return sorted(xrange(len(seq)), key=seq.__getitem__, **kwargs)

def intervalsToMask(Intervals, DomainSize, dtype=np.bool):
  """
  :Parameters:
    Intervals : iterable
      Sequence of interval boundary pairs
    DomainSize : int
      Size of intervals' domain
    dtype : `numpy.dtype`, optional
      Default is `numpy.bool`
  :Exceptions:
    IndexError : `DomainSize` does not agree with `Intervals` indices
  :ReturnType: `numpy.ndarray<dtype>`
  :Return:
    Mask-like array, 1 between interval bounds, 0 elsewhere

  Note: the mapping is not bijective if there are adjacent (or overlapping)
  intervals, i.e. transforming [(k,k+m), (k+m,n)] will be seen as [(k,n)],
  an union of the intervals in the mask (True-s between "k" and "n-1" position).
  """
  Mask = np.zeros(DomainSize, dtype=dtype)
  for Start, End in Intervals:
    Mask[Start:End] = 1
  return Mask

def maskToIntervals(Mask, ExcludeSingles=False):
  """
  Create intervals from mask-like array

  Remark: if numpy masked array is given, the masked elements are considered as
  False values (so they can not show up accidentally in any interval)

  :Parameters:
    Mask : `ndarray`
      Mask-like array (contains only 0 or 1 values)
    ExcludeSingles : bool, optional
      Exclude single element intervals, default is False
  :Exceptions:
    ValueError : `Mask` contains values other than 0 or 1
  :ReturnType: list
  :Return: [ (start<int>, end<int>), .. ]
    Indices of continuous 1-value interval boundaries in input array
  """
  Intervals = []
  if isinstance(Mask, np.ma.MaskedArray):
    if np.all(Mask) is np.ma.masked:
      return Intervals
    # if values other than 0 or 1 would be accepted, '&' could cause problems
    Mask = np.logical_and(Mask.data, ~Mask.mask)
  if not np.all( (Mask == 0) | (Mask==1) ):
    raise ValueError('Input array contains values other than 0 or 1!')
  IntMask = np.asarray(Mask, np.int8)
  ExtMask = np.concatenate( ((0,), IntMask, (0,)) )
  ExtMaskD1 = np.diff(ExtMask)
  ExtMaskD2 = np.diff(ExtMaskD1)
  Starts  = (ExtMaskD1[:-1] == 1) & (ExtMaskD2 == -1)
  Ends    = (ExtMaskD1[:-1] == 0) & (ExtMaskD2 == -1)
  if ExcludeSingles:
    BoundaryIndices, = np.where(Starts | Ends)
    for Start, End in zip(BoundaryIndices[::2], BoundaryIndices[1::2]):
      Intervals.append( ( int(Start),int(End)+1) )
  else:
    Singles = ExtMaskD2 == -2
    SingleIndices,   = np.where(Singles)
    BoundaryIndices, = np.where(Singles | Starts | Ends)
    Iterator = iter(BoundaryIndices)
    try:
      while True:
        Start = int( Iterator.next() )
        if Start in SingleIndices:
          Intervals.append( (Start,Start+1) )
        else:
          End = int( Iterator.next() )
          Intervals.append( (Start,End+1) )
    except StopIteration:
      pass
  return Intervals

def findSingles(Mask):
  """
  Find single True values of mask-like array. Returns bool mask with True
  element where such isolated value is found.

  Remark: if numpy masked array is given, the masked elements are considered as
  False values (so they can not show up accidentally)

  :Parameters:
    Mask : `ndarray`
      Mask-like array (contains only 0 or 1 values)
  :Exceptions:
    ValueError : `Mask` contains values other than 0 or 1
  :ReturnType: `ndarray<bool>`
  :Return:
    Bool mask with True element where single True value is found.

  >>> m = np.array([1,0,1,1,0,1,0,1], dtype=np.bool)
  >>> m
  array([ True, False,  True,  True, False,  True, False,  True], dtype=bool)
  >>> findSingles(m)
  array([ True, False, False, False, False,  True, False,  True], dtype=bool)
  """
  if isinstance(Mask, np.ma.MaskedArray):
    Mask = np.logical_and(Mask.data, ~Mask.mask)
  SinglesExcluded = maskToIntervals(Mask, ExcludeSingles=True)
  Singles = np.array(Mask, dtype=np.bool, copy=True)
  for Start, End in SinglesExcluded:
    Singles[Start:End] = False
  return Singles

def _calcGroupBounds(Groups):
  """
  >>> Groups = [[(0, 6), (4, 10)], [(16, 17)]]
  >>> _calcGroupBounds(Groups)
  [(0, 10), (16, 17)]
  """
  Bounds = []
  for Group in Groups:
    Lower = min([_Lower for _Lower, _Upper in Group])
    Upper = max([_Upper for _Lower, _Upper in Group])
    Bounds.append((Lower, Upper))
  return Bounds

def splitInterval(Interval, Separators):
  """ Split `Interval` by `Separators`

  :Parameters:
    Separators : iterable<int>
  :Exceptions:
      ValueError
        If any element in `Separators` is out of `Interval` bounds.
  :ReturnType: list<int>

  >>> splitInterval( (2,15), [2,6,11] )
  [(2, 6), (6, 11), (11, 15)]
  >>> splitInterval( (3,6), xrange(3,7) )
  [(3, 4), (4, 5), (5, 6)]
  >>> splitInterval( (3,6), xrange(2,5) )
  Traceback (most recent call last):
  ...
  ValueError: [2, 3, 4] out of interval (3,6)
  """
  st,end = Interval
  Separators = list(Separators) # Separators might be a generator object
  if not all( st <= sep <= end for sep in Separators ):
    raise ValueError( '%s out of interval (%d,%d)' %(Separators,st,end) )
  s = set(Interval)
  s.update(Separators)
  l = sorted(s)
  Split = [ (st,end) for st,end in zip(l,l[1:]) ]
  return Split

def findBounds(Time, StartTime, EndTime):
  """ Find boundary indices in `Time` that correspond to input boundary values

  :Parameters:
    Time : ndarray
      Time domain
    StartTime : float
      Start time of interval
    EndTime : float
      End time of interval
  :Exceptions:
    AssertionError : invalid interval is given (`StartTime` is after `EndTime`)
                     or interval has no intersection with `Time`
  :ReturnType: tuple
  :Return: Start<int>, End<int>

  >>> import numpy as np
  >>> t = np.arange(10.)
  >>> findBounds(t, 0., 1.) # exact match
  (0, 2)
  >>> findBounds(t, 2.1, 4.2) # regular
  (3, 5)
  >>> findBounds(t, 2.1, 2.2) # short
  (3, 4)
  >>> findBounds(t, -1., 0.5) # starts before first timestamp
  (0, 1)
  >>> findBounds(t, 3.4, 10.5) # ends after last timestamp
  (4, 10)
  >>> findBounds(t, -1., 10.5) # starts before first ends after last
  (0, 10)
  >>> findBounds(t, -1., -0.5) # out of bounds (before)
  Traceback (most recent call last):
  ...
  AssertionError: Event ends (-0.5) before first measurement timestamp (0.0)
  >>> findBounds(t, 10.1, 11.2) # out of bounds (after)
  Traceback (most recent call last):
  ...
  AssertionError: Event starts (10.1) after last measurement timestamp (9.0)
  >>> findBounds(t, 1.2, 0.3) # invalid interval
  Traceback (most recent call last):
  ...
  AssertionError: Invalid interval (1.2,0.3)
  """
  assert StartTime <= EndTime, 'Invalid interval (%s,%s)'%(StartTime,EndTime)
  assert StartTime <= Time[-1], 'Event starts (%s) after last measurement '\
                                'timestamp (%s)' %(StartTime, Time[-1])
  assert EndTime >= Time[0], 'Event ends (%s) before first measurement '\
                             'timestamp (%s)' %(EndTime, Time[0])
  Start = Time.searchsorted(StartTime)
  End = Time.searchsorted(EndTime, side='right')
  if End == Start:
    End += 1 # interval is too short (falls between 2 neighbour timestamps)
  return Start, End

def isInInterval(Index, Interval):
  Lower, Upper = Interval
  return Lower <= Index < Upper

class cIntervalList:
  """List class for intervals with monotonically increasing interval bounds"""
  def __init__(self, Time=None, Intervals=None):
    """
    :Parameters:
      Time : `ndarray`
        Time domain of the interval.
      Intervals : list, optional
        List of interval boundary pairs.
    """
    self.Intervals = Intervals if Intervals is not None else []
    """:type: list
    Container of intervals"""
    self.Time = Time if Time is not None else np.empty(0)
    """:type: `ndarray`
    Time domain of the interval."""
    self.__iter__     = self.Intervals.__iter__
    self.__str__      = self.Intervals.__str__
    self.__repr__     = self.Intervals.__repr__
    self.__len__      = self.Intervals.__len__
    self.__contains__ = self.Intervals.__contains__
    self.__getitem__  = self.Intervals.__getitem__
    self.sort         = self.Intervals.sort
    self.pop          = self.Intervals.pop
    return

  @classmethod
  def fromMask(cls, Time, Mask):
    """
    :Parameters:
      Time : `ndarray`
        Time domain of the interval.
      Mask : `ndarray`
        Mask-like array (contains only 0 or 1 values)
    :Exceptions:
      ValueError : if `Mask` and `Time` array shapes do not agree
                   or `Mask` contains values other than 0 or 1
    :ReturnType: `cIntervalList`
    """
    if Time.shape != Mask.shape:
      raise ValueError("Time shape %s does not agree with Mask shape %s"
                       %(Time.shape, Mask.shape))
    Intervals = maskToIntervals(Mask)
    return cls(Time, Intervals=Intervals)

  @classmethod
  def fromList(cls, Time, Intervals):
    """
    Create interval list from iterable object
    without affecting the original sequence.

    :Parameters:
      Time : `ndarray`
        Time domain of the interval.
      Intervals : iterable, optional
        Sequence of interval boundary pairs.
    :ReturnType: `cIntervalList`
    """
    NewIntervals = list(Intervals)
    return cls(Time, Intervals=NewIntervals)

  def copy(self):
    """
    Copy current state of interval list.

    :ReturnType: `cIntervalList`
    """
    return cIntervalList.fromList(self.Time, self.Intervals)

  def __eq__(self, Other):
    """
    >>> i1 = cIntervalList(np.arange(10), Intervals=[(1,4), (2,7), (8,10)])
    >>> i2 = cIntervalList(np.arange(15), Intervals=[(1,4), (2,7), (8,10)])
    >>> i1 == i1.copy()
    True
    >>> i1 == [(1,4), (2,7), (8,10)]
    True
    >>> i1 == [(2,4), (2,7), (8,10)]
    False
    >>> i1 == i2
    False
    """
    if isinstance(Other, list):
      return Other == self.Intervals
    # "isinstance(Other, cIntervalList)" does not always work
    elif hasattr(Other, 'Time') and hasattr(Other, 'Intervals'):
      if not isSameTime(self.Time, Other.Time):
        return False
      else:
        return self.Intervals == Other.Intervals
    else:
      return False

  def __ne__(self, Other):
    """
    >>> i1 = cIntervalList(np.arange(10), Intervals=[(1,4), (2,7), (8,10)])
    >>> i2 = cIntervalList(np.arange(15), Intervals=[(1,4), (2,7), (8,10)])
    >>> i1 != i1.copy()
    False
    >>> i1 != [(1,4), (2,7), (8,10)]
    False
    >>> i1 != [(2,4), (2,7), (8,10)]
    True
    >>> i1 != i2
    True
    """
    return not self.__eq__(Other)

  def isEmpty(self):
    return len(self.Intervals) == 0

  def argsort(self, **kwargs):
    """
    Return the indices that would sort the intervals, see
    `IntervalList.argsort` for details.
    """
    return argsort(self.Intervals, **kwargs)

  def reorder(self, indices):
    """ Ordering interval list elements in-place, specified by `indices` """
    self.Intervals[:] = [self.Intervals[i] for i in indices]
    return

  def iterTime(self):
    for Lower, Upper in self.Intervals:
      yield self.Time[Lower], self.Time[Upper-1]
    return

  def sumTime(self):
    Sum = 0.0
    for Lower, Upper in self.iterTime():
      Sum += Upper - Lower
    return Sum

  def getTimeInterval(self, Lower, Upper):
    return self.Time[Lower], self.Time[Upper-1]

  def getTimeIndex(self, TimeStamp):
    return max(0, int(self.Time.searchsorted(TimeStamp, side='right'))-1)

  def getTimeIndexWithMargin(self, Index, Offset, Up):
    Index = min(self.Time.size-1, Index)
    TimeStamp = self.Time[Index]
    if Up:
      TimeStamp += Offset
    else:
      TimeStamp -= Offset
    Side = 'right' if Up else 'left'
    Found = self.Time.searchsorted(TimeStamp, side=Side)
    if Up:
      if Index == self.Time.size-1 and Offset == 0.0 or Found < self.Time.size:
        Found -= 1
        Found = max(Found, 0)
    else:
      Found = min(Found, self.Time.size-1)
    return Found

  def getTimeIndexWithShift(self, Index, Offset, Up):
    if Up:
      Index += Offset
      Index  = min(Index, self.Time.size)
    else:
      Index -= Offset
      Index  = max(Index, 0)
    return Index

  def getDuration(self):
    Duration = 0 if self.Time.size == 0 else self.Time[-1] - self.Time[0]
    return Duration

  def getIntervalIndices(self, Lower, Upper):
    Interval = Lower, Upper
    Indices = []
    Start = 0
    while True:
      try:
        Start = self.Intervals.index(Interval, Start)
      except ValueError:
        break
      else:
        Indices.append(Start)
        Start += 1
    return Indices

  def negate(self):
    """
    Calculate the negation of the intervals.

    :ReturnType: `cIntervalList`
    """
    NewIntervals = cIntervalList(self.Time)
    Start = 0
    Final = self.Time.size
    for Lower, Upper in self.Intervals:
      if Lower != 0:
        NewIntervals.add(Start, Lower)
      if Upper != Final:
        Start = Upper
      else:
        Start = Final
    if Start != Final:
      NewIntervals.add(Start, Final)
    return NewIntervals

  def intersect(self, Intervals):
    """
    Intersect intervals with the intervals of `Intervals`.

    :Parameters:
      Intervals : `cIntervalList`
    :ReturnType: `cIntervalList`
    """
    Intervals    = self.convertIndices(Intervals)
    NewIntervals = cIntervalList(self.Time)
    for __Lower, __Upper in self.Intervals:
      for Lower, Upper in Intervals:
        if (      Upper > __Lower
            and __Upper >   Lower):
          NewIntervals.add(max(__Lower, Lower),
                           min(__Upper, Upper))
    return NewIntervals

  def union(self, Intervals):
    """
    Create union with the input `Intervals`.

    :Parameters:
      Intervals : `cIntervalList`
    :ReturnType: `cIntervalList`
    """
    Intervals    = self.convertIndices(Intervals)
    # De Morgan's law
    __Negate = self.negate()
    Negate = Intervals.negate()
    Intersections = __Negate.intersect(Negate)
    Unions = Intersections.negate()
    return Unions

  def isDisjoint(self):
    """ Check if intervals are non-overlapping """
    return self.join() == self.Intervals

  def neighbour(self, Intervals, **kwargs):
    """
    Create an `cIntervalList` from the neighbouring intervalbounds.

    :Parameters:
      Intervals : `cIntervalList`
    :Keywords:
      TimeMargins : list
        Margins to extend the intervalbound intervals. The margins are in [s].
        [LowerMargin<float>, UpperMargin<float>]
      CycleMargins : list
        Margins to extend the intervalbound intervals. The margins are in cycle.
        [LowerMargin<int>, UpperMargin<int>]
    :ReturnType: `cIntervalList`
    """
    Intervals  = self.convertIndices(Intervals)
    Neighbours = cIntervalList(self.Time)
    for __Lower, __Upper in self.Intervals:
      for Lower, Upper in Intervals:
        if __Upper == Lower:
          Neighbours.add(Lower-1, Lower)
    return Neighbours.addMargin(**kwargs)

  def split(self, Separators):
    """
    Split the intervals by `Separators`.

    :Parameters:
      Separators : iterable<int>
    :Exceptions:
      ValueError
        If any element in `Separators` is out of intervals' bounds.
    :ReturnType: `cIntervalList`

    >>> time = range(10)
    >>> intervals = cIntervalList(time, Intervals=[(1,4), (2,7), (8,10)])
    >>> intervals
    [(1, 4), (2, 7), (8, 10)]
    >>> intervals.split( [5] )
    [(1, 4), (2, 5), (5, 7), (8, 10)]
    >>> intervals.split( xrange(3,4) )
    [(1, 3), (3, 4), (2, 3), (3, 7), (8, 10)]
    >>> intervals.split( [5, 3, 9] )
    [(1, 3), (3, 4), (2, 3), (3, 5), (5, 7), (8, 9), (9, 10)]
    >>> intervals.split( [9, 11] )
    Traceback (most recent call last):
    ...
    ValueError: Out of bounds separator: 11
    """
    Idx2Seps = {} # { Idx<int> : [Sep<int>,] }
    # search container interval(s) of each separator
    for Sep in Separators:
      Indices = self.findIntervalIds(Sep)
      if not Indices:
        raise ValueError("Out of bounds separator: %d" %Sep)
      for Idx in Indices:
        Seps = Idx2Seps.setdefault(Idx, [])
        Seps.append(Sep)
    # split container intervals
    Idx2Splits = {} # { Idx<int> : [Split<list>,] }
    for Idx, Seps in Idx2Seps.iteritems():
      Idx2Splits[Idx] = splitInterval( self.Intervals[Idx], Seps )
    # replace each container interval by the split intervals
    Splits = []
    for OriginalIdx in xrange( len(self.Intervals) ):
      if OriginalIdx in Idx2Splits:
        Splits.extend( Idx2Splits[OriginalIdx] )
      else:
        Splits.append( self.Intervals[OriginalIdx] )
    return cIntervalList.fromList(self.Time, Splits)

  def _group(self, Intervals):
    """
    Group the contiguous interval groups, where the interval bound is extended
    with `Margin` which is read in the time domain of `Time`.

    :Parameters:
      Margin : float
    """
    Merged = self._merge(Intervals)
    Groups = collections.OrderedDict()
    for _Lower, _Upper in self.Intervals:
      for Interval in Merged:
        Lower, Upper = Interval
        if _Lower < Upper and _Upper > Lower:
          Intervals = Groups.setdefault(Interval, [])
          Intervals.append((_Lower, _Upper))
          break
    return Groups.values()

  def group(self, Margin=0.0):
    """
    Group the contiguous interval groups, where the interval bound is extended
    with `Margin` which is read in the time domain of `Time`.

    :Parameters:
      Margin : float
    """
    Intervals = self._addMargin(Margin, Margin)
    return self._group(Intervals)

  def addMargin(self, **kwargs):
    """
    Add margin to the interval bounds.

    :Keywords:
      TimeMargins : list
        Margins to extend the intervalbound intervals. The margins are in [s].
        [LowerMargin<float>, UpperMargin<float>]
      CycleMargins : list
        Margins to extend the intervalbound intervals. The margins are in cycle.
        [LowerMargin<int>, UpperMargin<int>]
    :ReturnType: `cIntervalList`
    """
    if 'TimeMargins' in kwargs:
      LowerMargin, UpperMargin = kwargs['TimeMargins']
      LowerMargin = abs(LowerMargin)
      Intervals = self._addMargin(LowerMargin, UpperMargin)
    elif 'CycleMargins' in kwargs:
      LowerShift, UpperShift = kwargs['CycleMargins']
      LowerShift = abs(LowerShift)
      Intervals = self._addShift(LowerShift, UpperShift)
    else:
      Intervals = copy.copy(self.Intervals)
    return cIntervalList.fromList(self.Time, Intervals)

  def _addMargin(self, LowerMargin, UpperMargin):
    return [(self.getTimeIndexWithMargin(Lower, LowerMargin, False),
             self.getTimeIndexWithMargin(Upper, UpperMargin, True))
             for Lower, Upper in self.Intervals]

  def _addShift(self, LowerShift, UpperShift):
    return [(self.getTimeIndexWithShift(Lower, LowerShift, False),
             self.getTimeIndexWithShift(Upper, UpperShift, True))
             for Lower, Upper in self.Intervals]

  def _merge(self, Intervals):
    Free   = 0
    Start  = 1
    Inside = 2
    End    = 4
    StartEnd = Start | End

    Mask = np.zeros_like(self.Time, dtype=np.int32)
    for StartIndex, EndIndex in Intervals:
      StartMask = Mask[StartIndex]
      EndIndex -= 1
      EndMask = Mask[EndIndex]
      Single = StartIndex == EndIndex

      if StartMask == StartEnd and not Single:
        Mask[StartIndex] = Start
      elif StartMask == Free:
        Mask[StartIndex] |= Start
      elif StartMask & End:
        Mask[StartIndex] = Inside

      if EndMask == StartEnd and not Single:
        Mask[EndIndex] = End
      elif EndMask == Free or Single:
        Mask[EndIndex] |= End
      elif EndMask & Start:
        Mask[EndIndex] = Inside

      Mask[StartIndex+1:EndIndex] = Inside
    Starts, = np.where(Mask & Start)
    Ends,   = np.where(Mask & End)
    Ends += 1
    return [Interval for Interval in zip(Starts, Ends)]

  def _smash(self, Intervals):
    Groups = self._group(Intervals)
    Intervals = _calcGroupBounds(Groups)
    return cIntervalList.fromList(self.Time, Intervals)

  def merge(self, DistLimit=0.0):
    """
    Merge the intervals if that are closer than `DistLimit` time.

    :Parameters:
      DistLimit : float
        Interval distance limit to merge.
    :ReturnType: `cIntervalList`
    """
    Intervals = self._addMargin(0.0, DistLimit)
    return self._smash(Intervals)

  def join(self, IndexLimit=0):
    """
    Join the intervals that are closer then `IndexLimit` index.

    :Parameter:
      IndexLimit : int
    :ReturnType: `cIntervalList`
    """
    Intervals = self._addShift(0, IndexLimit)
    return self._smash(Intervals)

  def drop(self, LengthLimit):
    """
    Drop the intervals from the `Intervals` which are shorter than
    `LengthLimit`.

    :Parameters:
      LengthLimit : int or float
        Length limit for the intervals.
    :ReturnType: `cIntervalList`
    """
    Intervals   = cIntervalList(self.Time)
    LengthLimit = measparser.cSignalSource.convTime2Cycle(self.Time,LengthLimit)
    for Lower, Upper in self.Intervals:
      if (Upper - Lower) >= LengthLimit:
        Intervals.add(Lower, Upper)
    return Intervals

  def add(self, Lower, Upper):
    """
    Add new interval.

    :Parameters:
      Lower : int
        Lower bound of the new interval.
      Upper : int
        Upper bound of the new interval.
    :ReturnType: int
    :Return: The index of the added interval
    :Exceptions:
      AssertationError
        `Lower` is not smaller then `Upper`
        `Lower` does not fit into [0, size-of-time[
        `Upper` does not fit into ]0, size-of-time]
    """
    assert Lower < Upper,\
           'Lower (%d) is not smaller than upper (%d) bound' %(Lower, Upper)
    assert 0 <= Lower <  self.Time.size,\
           'Lower (%d) does not fit into [0, %d[' %(Lower, self.Time.size)
    assert 0 <  Upper <= self.Time.size,\
           'Lower (%d) does not fit into ]0, %d]' %(Upper, self.Time.size)
    Index = len(self.Intervals)
    self.Intervals.append((Lower, Upper))
    return Index

  def remove(self, Lower, Upper):
    """
    Remove the selected interval.

    :Parameters:
      Lower : int
        Lower bound of the interval to remove.
      Upper : int
        Upper bound of the interval to remove.
    """
    logger = logging.getLogger()
    try:
      self.Intervals.remove((Lower, Upper))
    except ValueError:
      logger.error('IntervalList does not contain the [%s, %s] interval!\n'
                       %(Lower, Upper))
    return

  def findInterval(self, Value):
    """
    Find the first interval which contains the `Value`.

    :Parameters:
      Value : int
    :Exceptions:
      ValueError
        If the instance does not contain `Value`.
    :ReturnType: int, int
    :Return:     Lower bound of the interval which contains `Value`.
    :Return:     Upper bound of the interval which contains `Value`.
    """
    for Interval in self.Intervals:
      if isInInterval(Value, Interval):
        return Interval
    raise ValueError('cIntervalList.findInterval: '
                     'the cIntervalList does not contain %s!' %Value)

  def findIntervals(self, Value):
    """
    Find the intervals which contain the `Value`.

    :Parameters:
      Value : int
    :ReturnType: list
    :Return: [(Lower<int>, Upper<int>)]
    """
    return [ self.Intervals[Index] for Index in self.findIntervalIds(Value) ]

  def findIntervalBounds(self, StartTime, EndTime):
    """ Find boundary indices in the time domain that correspond to the input
    time boundary values. See `findBounds` docstring for details. """
    return findBounds(self.Time, StartTime, EndTime)

  def findIntervalIds(self, Value):
    """
    Find the indices of the intervals containing `Value`.

    :Parameters:
      Value : int
    :ReturnType: list
    :Return: [Index<int>]
    """
    Indices = [ Index for Index, Interval in enumerate(self.Intervals)
                        if isInInterval(Value, Interval) ]
    return Indices

  def findLongestIntervals(self):
    """
    Find the longest intervals.

    :ReturnType: list
    :Return: [(Lower<int>, Upper<int>)]
    """
    if not self.Intervals:
      return []
    MaxLength = max([Upper-Lower for Lower, Upper in self.Intervals])
    return [(Lower, Upper)
            for Lower, Upper in self.Intervals
            if Upper-Lower == MaxLength]

  def findLongestIntervalsIds(self):
    """
    Find the ids of the longest intervals.

    :ReturnType: list
    :Return: [Index<int>]
    """
    if not self.Intervals:
      return []
    MaxLength = max([Upper-Lower for Lower, Upper in self.Intervals])
    return [Index
            for Index, (Lower, Upper) in enumerate(self.Intervals)
            if Upper-Lower == MaxLength]

  def findIntervalIdsWithin(self, Lower, Upper):
    Ids = [Index for Index, (_Lower, _Upper) in enumerate(self.Intervals)
           if _Lower < Upper and Lower < _Upper]
    return Ids

  def convertIndices(self, Intervals):
    """
    Change the indices of the intervals of the `Intervals` to be valid on `Time`
    and return with the new instance.

    :Parameters:
      Intervals : `cIntervalList`
    :ReturnType: `cIntervalList`
    """
    ConvIntervals = Intervals.rescale(self.Time)
    return ConvIntervals

  def rescale(self, Time):
    """
    >>> import numpy
    >>> t = numpy.arange(0, 1, 1e-1)
    >>> i = cIntervalList.fromList(numpy.arange(0, 1, 1e-1),
    ...                            [(0, 1), (3, 9), (6, 10), (4, 8)])

    downscale
    [ ]   [           ]               [       ]         [       ]
    0-1-2-3-4-5-6-7-8-9-+ 0-1-2-3-4-5-6-7-8-9-+ 0-1-2-3-4-5-6-7-8-9-+
    0---1---2---3---4---+ 0---1---2---3---4---+ 0---1---2---3---4---+
    [   ]   [           ]             [       ]         [       ]
    >>> i.rescale(numpy.arange(0, 1, 2e-1))
    [(0, 1), (2, 5), (3, 5), (2, 4)]

    upscale
    [     ]           [                                   ]
    0-----1-----2-----3-----4-----5-----6-----7-----8-----9-----+
    0--1--2--3--4--5--6--7--8--9-10-11-12-13-14-15-16-17-18-19--+
    [     ]           [                                   ]

                                        [                       ]
    0-----1-----2-----3-----4-----5-----6-----7-----8-----9-----+
    0--1--2--3--4--5--6--7--8--9-10-11-12-13-14-15-16-17-18-19--+
                                        [                       ]

                            [                       ]
    0-----1-----2-----3-----4-----5-----6-----7-----8-----9-----+
    0--1--2--3--4--5--6--7--8--9-10-11-12-13-14-15-16-17-18-19--+
                            [                       ]
    >>> i.rescale(numpy.arange(0, 1, 5e-2))
    [(0, 2), (6, 18), (12, 20), (8, 16)]
    """
    if isSameTime(Time, self.Time):
      Intervals = self.copy()
    else:
      Intervals = cIntervalList(Time)
      InvInd = mapTimeToScaleTime(self.Time, Time)
      for Lower, Upper in self.Intervals:
        ConvLower = min(InvInd.searchsorted(Lower), Time.size-1)
        ConvUpper = max(InvInd.searchsorted(Upper), ConvLower+1)
        Intervals.add(ConvLower, ConvUpper)
    return Intervals

  def toMask(self, dtype=np.bool):
    """ Convert intervals to mask-like array. See `intervalsToMask` function's
    docstring for important note and details.

    :Parameters:
      dtype : `numpy.dtype`, optional
        Default is `numpy.bool`
    :ReturnType: `numpy.ndarray<dtype>`
    """
    return intervalsToMask(self.Intervals, self.Time.size, dtype=dtype)

if __name__ == '__main__':
  myTime = np.linspace(0., 100., 1000)
  myIntervalList1 = cIntervalList(myTime)
  for Interval in [[1.0, 2.0], [3.0, 5.5], [5.8, 9.0], [12.0, 42.0]]:
    myIntervalList1.add(Interval[0], Interval[1])
  print 'IntervalList1: ', myIntervalList1

  myIntervalList2 = cIntervalList(myTime)
  for Interval in [[1.8, 3.2], [5.6, 5.7], [41.0, 42.0]]:
    myIntervalList2.add(Interval[0], Interval[1])
  print 'IntervalList2: ', myIntervalList2

  myIntervalList3 = cIntervalList(myTime)
  for Interval in [[1.0, 5.0], [41.5, 50.5]]:
    myIntervalList3.add(Interval[0], Interval[1])
  print 'IntervalList3: ', myIntervalList3

  myIntervalList1.merge(0.5)
  print '\nMerge the intervals in myIntervalList1 ' \
        'if that are closer than 0.5:\n', myIntervalList1

  myIntervalList1.intersect(myIntervalList2)
  print '\nIntersect myIntervalList1 with myIntervalList2:\n', myIntervalList1

  print '\nLoop over myIntervalList1:'
  for Interval in myIntervalList1:
    print Interval

  myTime = np.linspace(0.0, 100.0, 1000)
  Interval = cIntervalList(myTime)
  Interval.add(8, 10)
  Interval.add(950, 1000)
  myTime = np.linspace(0.0, 120.0, 1000)
  Onterval = cIntervalList(myTime)
  Onterval.convertIndices(Interval)
