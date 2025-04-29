import warnings
import logging

import numpy
from scipy.signal import lsim


def convTime2Cycle(Time, TimeInterval):
  """
  :Parameters:
    Time : `numpy.ndarray`
    TimeIterval : float
  :ReturnType: int
  """
  return int(TimeInterval / numpy.diff(Time).mean() + 0.5)


def isSameTime(Time, ScaleTime, RelTol=0., AbsTol=1e-8):
  """
  True if `Time` and `ScaleTime` are the same object or they
  contains the same values.

  :Parameters:
    Time : `numpy.ndarray`
    ScaleTime : `numpy.ndarray`
    RelTol : float, optional
      Relative tolerance, see `numpy.allclose` for details
    AbsTol : float, optional
      Absolute tolerance, see `numpy.allclose` for details
  :ReturnType: bool
  """
  if Time is not ScaleTime:
    if Time.shape == ScaleTime.shape:
      return numpy.allclose(Time, ScaleTime, rtol=RelTol, atol=AbsTol)
    else:
      return False
  else:
    return True


def rescale(Time, Value, ScaleTime, Order='zoh', Mask=None, InvalidValue=None,
            Left=None, Right=None):
  """
  Rescale the `Value` with the new `ScaleTime`

  :Parameters:
    Time : `ndarray`
      The original time (as 1-D array) of the `Value`.
    Value : `ndarray`
      The value (as 1-D array) to rescale.
    ScaleTime : `ndarray`
      The scale time (as 1-D array) of the rescaling.
    Order : str, optional
      Interpolation order (in case a different scale time is provided).
      * 'zoh' : zero order hold (default)
      * 'foh' : first order (linear) interpolation. Warning: Linear interpolation
                can return array with different dtype from original signal
                (e.g. numpy.float64 when numpy.int32 is given).
      * 'mix' : mixed interpolation, applies first order on valid intervals
               (see `Mask` parameter), and zero order elsewhere.
      * 'valid' : zero order hold considering invalid values (see `InvalidValue`
                  parameter). If selected, rescaled value is of class
                  `numpy.ma.MaskedArray`. See `rescaleValidToCommonTime` method's
                  docstring for details.
    Mask : `ndarray`, optional
      Boolean mask where `Value` is considered as valid (with same shape). 
      Only used for mixed interpolation.
      Note: Single-element valid intervals are interpolated with zero-order.
    InvalidValue : int or float, optional
      Invalid value for masked elements. If not specified, masked elements will
      hold uninitialized (random) values.
    Left : int or float, optional
      Value to return for `ScaleTime < Time[0]`, default is `Value[0]`.
    Right : int or float, optional
      Value to return for `ScaleTime > Time[-1]`, default is `Value[-1]`.
  :ReturnType: `ndarray`, `ndarray`
  :Return:
    The rescale time. 
    The rescaled value. If the rescale time is the same as the original time,
    the original value is given.
  :Exceptions:
    ValueError : if invalid input parameters are given
  """
  if not isSameTime(Time, ScaleTime):
    # zero order interpolation
    if Order == 'zoh':
      Index = mapTimeToScaleTime(Time, ScaleTime)
      try:
        ScaleValue = Value[Index]
      except IndexError as e:
        Index = numpy.where(Index >= len(Value), len(Value)-1, Index)
        ScaleValue = Value[Index]
      setBoundaries(Time, ScaleTime, ScaleValue, Left, Right)
    # linear interpolation
    elif Order == 'foh':
      ScaleValue = numpy.interp(ScaleTime, Time, Value, left=Left, right=Right)
    # mixed interpolation
    elif Order == 'mix':
      if Mask is None or Mask.shape != Value.shape:
        raise ValueError('Invalid mixed interpolation mask!')
      ScaleValue = interp01(Time, Value, ScaleTime, Mask)
      setBoundaries(Time, ScaleTime, ScaleValue, Left, Right)
    elif Order == 'valid':
      ScaleValue = rescaleValidToCommonTime(Time, Value, ScaleTime,
                                            InvalidValue=InvalidValue)
      setBoundaries(Time, ScaleTime, ScaleValue, Left, Right)
    else:
      raise ValueError('Invalid interpolation order: %s' %Order)
  else:
    if Order == 'valid':
      ScaleValue = numpy.ma.masked_array(Value, mask=False)
    else:
      ScaleValue = Value
  return ScaleTime, ScaleValue

def rescaledd(Time, Value, ScaleTime, TimeAxis=0, **kwargs):
  """
  Rescale the multi-dimensional `Value` array on `Time` with the new
  `ScaleTime`.
  
  :Parameters:
    Time : `ndarray`
      The original time (as 1-D array) of the `Value`.
    Value : `ndarray`
      The value (as N-D array) to rescale.
    ScaleTime : `ndarray`
      The scale time (as 1-D array) of the rescaling.
    TimeAxis : int, optional
      The axis which represents the time. Default 0 means that increasing 
      indices of the 0th axis (i.e. row) correspond to values of later time
      instances.
  :Keywords:
    * : *
      Any valid optional parameter of the `rescale` function, except `Mask`.
      (`Mask` might be available in future versions.)
  """
  if kwargs.has_key('Mask'):
    raise NotImplementedError("unsupported 'Mask' parameter")
  if isinstance(Value, numpy.ma.MaskedArray):
    apply_along_axis = numpy.ma.apply_along_axis
  else:
    apply_along_axis = numpy.apply_along_axis
  func = lambda val: rescale(Time, val, ScaleTime, **kwargs)[1]
  ScaleValue = apply_along_axis(func, TimeAxis, Value)
  return ScaleTime, ScaleValue

def setBoundaries(Time, ScaleTime, ScaleValue, Left, Right):
  """ Set in-place `ScaleValue` data outside `Time` boundaries """
  if Left is not None:
    setLeftBoundary(ScaleTime, ScaleValue, Time[0], Left)
  if Right is not None:
    setRightBoundary(ScaleTime, ScaleValue, Time[-1], Right)
  return

def setLeftBoundary(Time, Value, Start, Left):
  if Time[0] < Start:
    Start = Time.searchsorted(Start)
    Value[:Start] = Left
  return

def setRightBoundary(Time, Value, End, Right):
  if Time[-1] > End:
    End = Time.searchsorted(End, side='right')
    Value[End:] = Right
  return

def rescaleValidToCommonTime(Time, Value, ScaleTime, InvalidValue=None):
  """
  Rescale the `Value` on `Time` to the common `ScaleTime`, using the preceding 
  timestamp ('x') of `ScaleTime`. Invalid values ('*') are set where data is
  missing for a timestamp.

  Time       ----x--------x--------------------------x--------x--------x--
  Value      ----2--------5--------------------------7--------0--------3--
  ScaleTime  --x--------x--------x--------x--------x--------x--------x----
  ScaleValue --2--------5--------*--------*--------7--------0--------3----

  :Parameters:
    Time : `ndarray`
      The original time of the `Value`.
    Value : `ndarray`
      The value to rescale.
    ScaleTime : `ndarray`
      The scale time of the rescaling.
    InvalidValue : int or float, optional
      Invalid value for masked elements. If not specified, masked elements will
      hold uninitialized (random) values.
  :ReturnType: `numpy.ma.MaskedArray`
  :Return:
    The rescaled value, masked elements indicate missing values. Mask is always
    an `ndarray` (never a single bool) with the same shape of the rescaled value.
  """
  # trim boundaries
  Start, End = None, None
  if Time[0] < ScaleTime[0]:
    # data before first rescale timestamp is of no interest
    Start = Time.searchsorted(ScaleTime[0])
  if Time.size > 1 and Time[-2] > ScaleTime[-1]:
    # more than 1 element after last rescale timestamp is redundant
    End = Time.searchsorted(ScaleTime[-1], side='right') + 1
  if Start is not None or End is not None:
    Time = Time[Start:End]
    Value = Value[Start:End]
  # find mapping
  Index = mapTimeToScaleTime(ScaleTime, Time)
  Mask = numpy.ones_like(ScaleTime, dtype=numpy.bool)
  Mask[Index] = False
  ScaleData = numpy.empty_like(ScaleTime, dtype=Value.dtype)
  if InvalidValue is not None:
    ScaleData.fill(InvalidValue)
  ScaleData[Index] = Value
  ScaleValue = numpy.ma.masked_array(ScaleData, Mask)
  return ScaleValue

def selectTimeScale(ScaleTimes, StrictlyGrowingCheck):
  """ Selects the "most dense" time domain. The function omits the times from 
  selection which are shorter than 2 or not strictly growing.  

  Remark: the actually most dense time can be too short to be selected for 
  practical timescale, therefore the time domain duration is also considered.
  
  :Parameters:
    ScaleTimes : iterable
      Time bases represented by `numpy.ndarray`s
    StrictlyGrowingCheck : bool
  :Exceptions:
    IndexError : if empty input sequence is given
  :ReturnType: `numpy.ndarray`
  """
  Message = ['no valid time in ScaleTimes']
  MaxSize = -1
  MaxSizeTime = numpy.array([])
  MaxUniformSize = -1
  ScaleTime = None
  for Time in ScaleTimes:
    MaxSize = max(Time.size, MaxSize)
    if MaxSize == Time.size == 1:
      MaxSizeTime = max(Time, MaxSizeTime)
      continue
    if Time.size < 2:
      Message.append('wrong time size')
      continue
    dTime = numpy.diff(Time)
    if (dTime <= 0.0).any():
      msg = 'not strictly growing time'
      logging.getLogger().debug(msg)
      if StrictlyGrowingCheck:
        Message.append(msg)
        continue
    Mean = dTime.mean()
    Duration = Time[-1] - Time[0]
    UniformSize = Duration / Mean
    if UniformSize >= MaxUniformSize:
      ScaleTime = Time
      MaxUniformSize = UniformSize
    Message.append('')
  if MaxSize == 1:
    ScaleTime = MaxSizeTime
  if ScaleTime is None:
    raise IndexError('\n'.join(Message))
  if (numpy.diff(ScaleTime) <= 0.0).any():  # validate result
    logging.getLogger().warning('not strictly growing time')
  return ScaleTime

def calcOrderedBurstTimeScale(msg_times):
  """
  Calculate the time scale for Order='valid' rescaling.
  Incomplete packets will be dropped (at the beginning and/or at the end).
  
  Example:
  
    t1:  -----x------x------x------x------x-
    t2:  ------x------x------x------x------x
    t3:  x------x------x------x------x------
  
    out:      x------x------x------x
  
  :Parameters:
    msg_times : list or tuple
      Time vectors that have to be aligned. Order important: first element
      shall correspond to the earliest timestamps in every processing cycle,
      while the last one shall correspond to the last packet of each cycle.
      Intermediate time vectors have no effect.
  :ReturnType: `numpy.ndarray`
    The calculated time scale.
  """
  if any([msg_time.size < 1 for msg_time in msg_times]):
    return numpy.array(())
  time_scale = numpy.copy(msg_times[0])
  # trim time if extra elements present
  if msg_times[-1][-1] < msg_times[0][-1]:
    time_scale = time_scale[:-1]
  return time_scale

def calcUnorderedBurstTimeScale(msg_times, dt_burst=None):
  """
  Calculate the time scale for Order='valid' rescaling, with message
  order change handling. Values are considered as belonging to the same
  processing cycle if they arrived within `dt_burst` time.
  Incomplete packets will be dropped (at the beginning and/or at the end).
  Works only for arrays having at least 2 elements.
  
  Example:
  
    t1:  -----x------x------x------x------x-
    t2:  ------x----x--------x------x------x
    t3:  x------x------x------x------x------
  
    out:      x-----x-------x------x
  
  :Parameters:
    msg_times : list or tuple
      Time vectors that have to be aligned.
    dt_burst : float
      Maximum duration in which the values are considered as belonging to the
      same processing cycle.
      Assumption for dt_burst=None (auto determination):
        dt_burst < min(min(diff(msg_times[i])) for all i) / 2.0
  :ReturnType: `numpy.ndarray`
    The calculated time scale.
  """
  assert all([msg_time.size > 1 for msg_time in msg_times]), \
    "all time vectors must have at least 2 elements"
  if dt_burst is None:
    dt_cycle = min([numpy.min(numpy.diff(msg_time)) for msg_time in msg_times])
    dt_burst = dt_cycle / 2.0
  t_start = max([msg_time[0] for msg_time in msg_times])
  t_end = min([msg_time[-1] for msg_time in msg_times])
  new_msg_times = [msg_time for msg_time in msg_times]  # shallow copy
  # trim arrays if extra elements present
  for i in xrange(len(msg_times)):
    if msg_times[i][0] < t_start - dt_burst:
      new_msg_times[i] = msg_times[i][1:]
    if msg_times[i][-1] > t_end + dt_burst:
      new_msg_times[i] = msg_times[i][:-1]
  # calc time scale
  times = numpy.vstack(new_msg_times)
  time_scale = numpy.min(times, axis=0)
  return time_scale

def mapTimeToScaleTime(Time, ScaleTime):
  """ Index mapping between `Time` and `ScaleTime`
  
  :Parameters:
    Time : `ndarray`
      The original time of a signal. Assumed to be sorted.
    ScaleTime : `ndarray`
      The scale time of the rescaling. Assumed to be sorted in the same order as `Time`.
  :ReturnType: `ndarray`
  :Return:
    Index value array, where size corresponds to `ScaleTime` size and 
    the stored index range refers to indices of `Time`.
  """
  Index  = Time.searchsorted(ScaleTime, side='right')
  Index -= 1
  Index  = numpy.where(Index < 0, 0, Index)
  return Index


def interp01(Time, Value, ScaleTime, Mask):
  """ Mixed interpolation, linear where applicable, zero order elsewhere. See `rescale` 
  method's docstring for details.
  Remark: Linear interpolation result is silently casted to the original dtype of `Value`.
  
  :ReturnType: `ndarray`
  :Return:
    Interpolated value of the requested signal.
  """
  # search intervals where linear interpolation is reasonable
  IntMask = numpy.asarray(Mask, numpy.int32)
  ExtMask = numpy.concatenate( ((0,), IntMask, (0,)) ) # checking boundaries
  ExtMaskD1 = numpy.diff(ExtMask)
  ExtMaskD2 = numpy.diff(ExtMaskD1)
  NonSingles = ExtMaskD2 != -2
  NonStarts  = (ExtMaskD2 != -1) | (ExtMaskD1[:-1] != 1)
  MyMask = numpy.copy(Mask)
  MyMask &= NonSingles # exclude single-element intervals
  MyMask &= NonStarts # exclude beginning of intervals
  # mapping between Time and ScaleTime
  MapIndices = numpy.searchsorted(Time, ScaleTime)
  MapIndices = numpy.where(MapIndices == Time.size, Time.size-1, MapIndices)
  ScaleMask1 = MyMask[MapIndices]
  # linear interpolation
  ScaleValue1 = numpy.interp(ScaleTime[ScaleMask1], Time, Value)
  # zero order interpolation
  ScaleMask0  = ~ScaleMask1
  ScaleTime0  = ScaleTime[ScaleMask0]
  Indices     = mapTimeToScaleTime(Time, ScaleTime0)
  ScaleValue0 = Value[Indices]
  # mixed interpolation
  ScaleValue = numpy.zeros(shape=ScaleTime.shape, dtype=Value.dtype)
  ScaleValue[ScaleMask0] = ScaleValue0
  ScaleValue[ScaleMask1] = ScaleValue1.astype(Value.dtype)
  return ScaleValue


def smooth(y, t, w_cutoff):
  """
  Low-pass filtering of the given signal `y(t)`, using the given
  cut-off frequency `w_cutoff`.
  The filtering is realized with a first-order filter.
  
  TODO: implement an 'order' parameter for the filter order.
  TODO: auto-determination of w_cutoff
  
  :Parameters:
    y : numpy.ndarray
      1-D array of the signal values
    t : numpy.ndarray
      1-D array of the corresponding time values
    w_cutoff : float
      Cut-off (angular) frequency in rad/sec.
      For a 5 Hz cut-off, define w_cutoff = 5 * 2*pi.
  :ReturnType: numpy.ndarray
  :Return:
    The smoothed signal as a 1-D array.
  """
  if y.size < 1:
    return numpy.copy(y)
  x0 = y[0,...] / float(w_cutoff)  # init state to match initial signal value
  smoother = ((w_cutoff,), (1, w_cutoff))
  # call lsim() with suppressing its warning:
  # .../lib/site-packages/scipy/signal/ltisys.py:
  # ComplexWarning: Casting complex values to real discards the imaginary part
  original_filters = warnings.filters[:]
  warnings.simplefilter("ignore")
  try:
    t_out, y_out, x_out = lsim(smoother, y, t, X0=x0)
  finally:
    warnings.filters = original_filters
  return y_out


def trim(Time, ScaleTime, RescaleBefore, RescaleAfter):
  """
  Trim `ScaleTime` if it exceeds boundaries of `Time`.

  :Parameters:
    Time : `ndarray`
      The original time of the `Value`.
    ScaleTime : `ndarray`
      The scale time of the rescaling.
    RescaleBefore : bool
      Rescale the `Value` before the first `Time` timestamp. Default is True. If set
      to False, the returned rescale time and value will not contain data before the
      original time.
    RescaleAfter : bool
      Rescale the `Value` after the last `Time` timestamp. Default is True. If set
      to False, the returned rescale time and value will not contain data after the
      original time.
  """
  Start, End = 0, ScaleTime.size
  if not RescaleBefore and ScaleTime[0] < Time[0]:
    Start = ScaleTime.searchsorted(Time[0])
  if not RescaleAfter and ScaleTime[-1] > Time[-1]:
    End = ScaleTime.searchsorted(Time[-1])
  # preserve scaletime reference if clipping is not needed
  if (Start, End) != (0, ScaleTime.size):
    ScaleTime = ScaleTime[Start:End]
  return ScaleTime


def histogram2d(x, y, continuous=True, cond_givenaxis=None,
                toplotframe=False, **kwargs):
  """
  Wrapper to numpy.histogram2d with extended functionality.
  
  :Parameters:
    x : `ndarray`
      A sequence of values to be histogrammed along the first dimension.
    y : `ndarray`
      A sequence of values to be histogrammed along the second dimension.
    continuous : bool
      It affects the result only if normalization or conditional
      probability is requested. If True, the result represents continuous
      distribution (this is the default for numpy.histogram2d, too).
      If False, the result represents discrete distribution (i.e., input
      'x' and 'y' represent discrete random variables).
    cond_givenaxis : str or None
      If not None, conditional probability density and conditional probability
      mass function is calculated for the continuous and discrete cases,
      respectively. If cond_givenaxis='x', then the conditional probability
      of y, given x=xx is returned. If cond_givenaxis='y', then the conditional
      probability of x, given y=yy is returned.
    toplotframe : bool
      If False, the result is compatible with numpy.histogram2d, i.e. it's
      frame is in the conventional matrix form:
                                          y
                                   +------>
                                   |
                                   |
                                 x v
      
      If True, the result can directly be used for plotting as shown in the
      example below, i.e. it's frame is the conventional plotting frame:
      
                                 y ^
                                   |
                                   |
                                   +------>
                                          x
      >>> H, xedges, yedges = histogram2d(x, y, toplotframe=True)
      >>> extent = (xedges[0], xedges[-1], yedges[0], yedges[-1])
      >>> pylab.imshow(H, extent=extent)
  
  :Keywords:
    Any further numpy.histogram2d parameters.
  
  :ReturnType: tuple
  :Return:
    H : `ndarray`
        The bi-dimensional histogram of samples `x` and `y`. Values in `x`
        are histogrammed along the first dimension and values in `y` are
        histogrammed along the second dimension.
    xedges : `ndarray`
        The bin edges along the first dimension.
    yedges : `ndarray`
        The bin edges along the second dimension.
  """
  # process input
  assert cond_givenaxis in (None, 'x', 'y'), \
    "invalid parameter value: cond_givenaxis=%s" % str(cond_givenaxis)
  normed = kwargs.pop('normed') if 'normed' in kwargs else False
  if cond_givenaxis is not None:
    normed = True
  # calculate normal histogram
  H, xedges, yedges = numpy.histogram2d(x, y, normed=False, **kwargs)
  # normalize on demands
  if normed and numpy.any(H):
    # normalization
    if continuous:
      xlens = numpy.tile(numpy.diff(xedges)[numpy.newaxis].T, (1, H.shape[1]))
      ylens = numpy.tile(numpy.diff(yedges), (H.shape[0], 1))
      wholevolume = numpy.sum(H * xlens * ylens)
      H /= wholevolume
      if cond_givenaxis == 'x':
        condnorm = numpy.tile(numpy.sum(H * ylens, axis=1)[numpy.newaxis].T,
                          (1, H.shape[1]))
      elif cond_givenaxis == 'y':
        condnorm = numpy.tile(numpy.sum(H * xlens, axis=0), (H.shape[0], 1))
    else:
      H /= numpy.sum(H)
      if cond_givenaxis == 'x':
        condnorm = numpy.tile(numpy.sum(H, axis=1)[numpy.newaxis].T,
                              (1, H.shape[1]))
      elif cond_givenaxis == 'y':
        condnorm = numpy.tile(numpy.sum(H, axis=0), (H.shape[0], 1))
    # conditioning (cont. and disc.)
    if cond_givenaxis:
      with numpy.errstate(divide='ignore', invalid='ignore'):
        H = numpy.where(condnorm, H/condnorm, 0.0)
  if toplotframe:
    # transform to conventional plotting frame (y ^|_> x)
    H = H.T[::-1,:]
  return H, xedges, yedges

def mode(Vector, NaN=None):
  """
  Get the mode of the `Vector`, except the `NaN` values.
  
  :Parameters:
    Vector : `ndarray`
      The input vector.
    NaN : float or int
      The disabled value in the mode calculation. If the default value is left, 
      then no value will be disabled.
  :ReturnType: float or int
  """
  if NaN:
    Vector = Vector[Vector != NaN]
  MaxElemNr = -1
  MaxElem   = 0 
  for Elem in numpy.unique(Vector):
    ActElemNr = (Vector == Elem).sum()
    if ActElemNr > MaxElemNr:
      MaxElemNr = ActElemNr
      MaxElem   = Elem
  return MaxElem

def findUniqueValues(array, exclude=None):
  """
    Finds unique values in an array, optionally excluding a given value.

    :Parameters:
      array : ndarray
      exclude : object
        The value which should be ignored in the array.
    :ReturnType: set
    :Return:
      Set of unique values.
  """
  uniqueValues = set( numpy.unique(array) )
  if exclude is not None and exclude in uniqueValues:
    uniqueValues.remove(exclude)
  return uniqueValues

def isSorted(array, order, strict=False):
  """
    Test if the input array is sorted.

    :Parameters:
      array : ndarray
      order : str
        Sorting order property of the array. Supported values are 'increasing' and 'decreasing'.
      strict: bool, optional
        Strict or partial order property. True tests for strict ordering, False (default) for partial ordering.
    :ReturnType: bool
    :Return:
      True if the array is sorted according to the specified conditions, otherwise False.
  """
  assert order in ('increasing', 'decreasing')
  diffarr = numpy.diff(array)
  if order == 'increasing':
    if strict:
      rel = lambda a,b: a > b
    else:
      rel = lambda a,b: a >= b
  elif order == 'decreasing':
    if strict:
      rel = lambda a,b: a < b
    else:
      rel = lambda a,b: a <= b
  return numpy.all(rel(diffarr,0))

def calcDutyCycle(time, activity):
  """
  Calculate the ratio of the duration of activity and the total time.
  
  :Parameters:
    time : numpy.ndarray
      1-D array of timestamps
    activity : numpy.ndarray
      1-D bool-like array (with 0 and 1 elements), indicating the activity.
  :ReturnType: float
  :Return:
    Ratio of the duration of activity and the total time.
  """
  assert numpy.all((activity==0) | (activity==1)), "activity shall be bool-like"
  if time.size < 1:
    raise ValueError("empty arrays not accepted")
  if time.size == 1:
    return 1.0 if activity[0] else 0.0
  total_time = time[-1] - time[0]
  if total_time <= 0.0:
    raise ValueError("invalid interval length: %f" % total_time)
  activity = activity.astype(float)
  active_time = numpy.trapz(activity, time)
  duty_cycle = active_time / total_time
  return duty_cycle

def backwarddiff(signal, initial=0, initialmode='use_initial'):
  """
    Calculate the first order discrete backward difference.
 
    The difference is given by out[n] = a[n] - a[n-1]. The first element is 
    determined by the parameters; if initialmode = 'use_initial' than the given
    initial value is used or if initialmode = 'copy_back' than it is set to the
    same as the second element. Default is 'use_initial' and 0.
    
    :Parameters:
      signal  : ndarray
        Input signal
      initial : same as signal.dtype
        Value of the first element of the result.
      initialmode : string
        Mode of initial calculation.
    :ReturnType: ndarray
    :Return:
      The difference signal, same shape and dtype as input signal.
  """
  assert initialmode=='use_initial' or initialmode=='copy_back', \
         "%s: unknown value of initialmode parameter" % (initialmode)
  if len(signal) < 1:
    return numpy.zeros_like(signal)
  if len(signal) == 1:
    ret = numpy.zeros_like(signal)
    if initialmode=='use_initial':
      ret[0] = initial
    return ret 
  ret = numpy.empty_like(signal)
  ret[1:] = numpy.diff(signal)
  ret[0] = ret[1] if initialmode=='copy_back' else initial
  return ret

def backwardderiv(x, y, initial=0, initialmode='use_initial'):
  """
    Calculate derivative of x with respect to y using backward differences.

    The first element is determined by the initial parameter or is set to the
    same as the second element if initial is None. Default for initial is 0.
    
    :Parameters:
      x  : ndarray
        x signal
      y : ndarray same shape as x
        y signal
      initial : same as signal.dtype
        Value of the first element of the result.
      initialmode : string
        Mode of initial calculation.
    :ReturnType: ndarray
    :Return:
      The differentiated signal, same shape and dtype as input signals.
  """
  assert x.shape == y.shape, "Shape of arguments are different."
  assert initialmode=='use_initial' or initialmode=='copy_back', \
         "%s: unknown value of initialmode parameter" % (initialmode)
  if len(x) < 1:
    return numpy.zeros_like(x)
  if len(x) == 1:
    ret = numpy.zeros_like(x)
    if initialmode=='use_initial':
      ret[0] = initial
    return ret 
  ret = numpy.empty_like(x)
  ret[1:] = numpy.diff(x) / numpy.diff(y)
  ret[0] = ret[1] if initialmode=='copy_back' else initial
  return ret

def correctNorming(arr, old_offs, old_fact, new_offs, new_fact):
  original = (arr - old_offs) / old_fact
  res = new_offs + original * new_fact
  return res

def masked_all_like_fill(array, value=0):
  """ Create new all masked array object based on input `array` (shape and dtype),
      values filled with optional `value` argument (0 by default).
  """
  out = numpy.ma.masked_all_like(array)
  out.data.fill(value) # note: "out.fill(value)" would unmask all entries
  return out

def set_ma_read_only(array):
  " Set input masked array read-only (both data and mask) "
  array.flags.writeable = False
  array.harden_mask() # hack
  array.mask.flags.writeable = False
  return
