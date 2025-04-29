from collections import OrderedDict, namedtuple

import numpy as np

from pyutils.enum import enum
from metatrack import ObjectFromMessage
from measparser.signalproc import findUniqueValues, masked_all_like_fill
from measproc.IntervalList import cIntervalList, maskToIntervals, intervalsToMask

TRACK_MESSAGE_NUM = 20

TARGET_NOT_REPORTED = 30
TARGET_NOT_ASSOD = 31

# credibility norming [0..100 saturated to 0..63 on CAN] -> [0..0.63]
CREDIBILITY_MAX = np.float32(100)

# enums (position counts)
TRACKING_STATE = enum(EMPTY=0, INIT=1, ESTABLISHED=2, SLEEPING=3)
TR_SEL_ST_BITS = (
  'LEFTLANE', 'RIGHTLANE', 'INLANE', 'SAME_DIRECTION', 'STATIONARY',
  'OPPOSITE_DIRECTION', 'MIRROR', 'OVERTAKEN', 'ACCTRACK',
  'OUTOFACCLANE', 'EXTREMELEFT', 'EXTREMERIGHT', 'SUPPRESSED'
)
TR_SEL_ST = enum( **dict((name, 2**n) for n, name in enumerate(TR_SEL_ST_BITS)) )
ACC_STATUS = enum(NORMAL=0, ACC=1, IIV=2, NIV=3)
CM_SYSTEM_STATUS = enum(NOT_ALLOWED=0, ALLOWED=1, WARNING=2, BRAKING=3, WAITING=4)

A087MB = namedtuple('A087MB', ['sgs', 'size', 'cls'])

def create_flr20_track_mask(signals, id):
  internal_track_index = signals["internal_track_index"]  # Track ID
  tracking_status = signals["tracking_status"]            # Valid data
  mask = internal_track_index.data == id                  # track occurs in message
  mask &= ~internal_track_index.mask                      # data is valid
  mask &= tracking_status.data != TRACKING_STATE.EMPTY    # tracking status ok
  mask &= ~tracking_status.mask                           # data is valid
  return mask

def findUniqueIds(ids, exclude=None, **kwargs):
  """ Find unique ids in input arrays """
  uniqueIds = set()
  for arr in ids:
    uniques = findUniqueValues(arr, exclude=exclude)
    uniqueIds.update(uniques)
  sortedUniqueIds = sorted(uniqueIds, **kwargs)
  return sortedUniqueIds

def rescaleCanMessages(scaleTime, source, groups, groupSize=None, names=None, **kwargs):
  messages = {}
  """ { messageNum<int> : {signalName<str> : signal<numpy.ma.MaskedArray>} } """
  for i, group in enumerate(groups):
    if groupSize is not None and len(group) != groupSize:
      # skip message if not all signals are present
      continue
    signals = {}
    signalNames = group.iterkeys() if names is None else names
    for signalName in signalNames:
      signals[signalName] = source.getSignalFromSignalGroup(group, signalName,
                                                            ScaleTime=scaleTime, Order='valid', **kwargs)[1]
    messages[i] = signals
  return messages

def createArrayFromMessages(signalName, messages, msgMasks):
  # collect array
  arr = None
  for k, mask in msgMasks.iteritems():
    signal = messages[k][signalName]
    if arr is None:
      arr = masked_all_like_fill(signal, value=0)
    arr.data[mask] = signal[mask]
    arr.mask &= ~mask
  return arr

def createRadarTrackMasks(messages, ids, mask_creator):
  """ Create validity masks of internal radar tracks from messages

  :Parameters:
    messages : dict
      { messageNum<int> : {signalName<str> : signal<numpy.ma.MaskedArray>} }
    ids : iterable
      Sequence of possible internal radar track ids (order followed in output)
    mask_creator: callback
      Callback of mask creation
  :ReturnType: OrderedDict
  :Return:
    { id<int> : {messageNum<int> : mask<ndarray>} }
  """
  trackMasks = OrderedDict()
  for i in ids:
    messageMasks = {}
    for k, signals in messages.iteritems():
      # create track mask from message
      mask = mask_creator(signals, i)
      # register message only when valid track data is present
      if np.any(mask):
        messageMasks[k] = mask
    # register track only when message mask is found
    if messageMasks:
      trackMasks[i] = messageMasks
  return trackMasks

def createIdenticalRadarTrackMasks(messages):
  """ Create validity masks of radar tracks from messages

  :Parameters:
    messages : dict
      { messageNum<int> : {signalName<str> : signal<numpy.ma.MaskedArray>} }
  :ReturnType: OrderedDict
  :Return:
    { id<int> : {messageNum<int> : mask<ndarray>} }
  """
  signals = messages.itervalues().next()
  t_size = signals['internal_track_index'].size
  # TODO: proper masking in trackMasks
  trackMasks = OrderedDict( (i, {i: np.ones(t_size, dtype=np.bool)})
                            for i in xrange(TRACK_MESSAGE_NUM) )
  return trackMasks

def stoppedNstationary(standing, moving):
  """ Distinguish between stationary and stopped moving state """
  N = standing.size
  stationaryIntervals = []
  stoppedIntervals = []
  for st,end in maskToIntervals(standing):
    if st > 0 and (moving[st-1]):
      stationary = False # has been seen moving before
    else:
      stationary = True # any other case
    # append interval
    if stationary:
      stationaryIntervals.append( (st,end) )
    else:
      stoppedIntervals.append( (st,end) )
  stationary = intervalsToMask(stationaryIntervals, N)
  stopped    = intervalsToMask(stoppedIntervals,    N)
  return stationary, stopped

def template2signame(sigTemplate):
  return sigTemplate.partition('_')[2]


class TrackFromMessage(ObjectFromMessage):
  """Load/rescale signals to common time and collect them using message masks"""

  _special_methods = 'alive_intervals',

  def __init__(self, id, msgTime, msgMasks, source, optgroups, dirCorr,
               scaleTime=None, **kwargs):
    assert msgMasks, 'Message masks must not be empty!'
    super(TrackFromMessage, self).__init__(id, msgTime, source, dirCorr,
                                      scaleTime=scaleTime, **kwargs)
    self._msgMasks = msgMasks
    self._groups = optgroups
    return

  def _create(self, signalName):
    messages = rescaleCanMessages(self._msgTime, self._source, self._groups,
                  names=(signalName,), InvalidValue=0)
    arr = createArrayFromMessages(signalName, messages, self._msgMasks)
    out = self._rescale(arr)
    return out

  def alive_intervals(self):
    """ Determine intervals where object was alive. This function splits valid
    intervals at timestamps where object became new (i.e. was replaced but id
    remained the same).

    :ReturnType: cIntervalList
    """
    new = self.tr_state.valid & ~self.tr_state.hist
    validIntervals = cIntervalList.fromMask(self.time, self.tr_state.valid)
    newIntervals   = cIntervalList.fromMask(self.time, new)
    alive_intervals = validIntervals.split(st for st,_ in newIntervals)
    return alive_intervals

  def sleeping_counter(self):
    """ Count how long the track has been sleeping (only predicted) in each cycle

    :ReturnType: np.ma.MaskedArray<np.uint32>
    """
    data = np.zeros_like(self.time, dtype=np.uint32)
    sleeping = ~self.tr_state.measured
    sleeping_counter = np.ma.masked_array(data, mask=sleeping.mask)
    for st,end in self.alive_intervals:
      for start,stop in maskToIntervals( sleeping[st:end] ):
        sleeping_counter[st+start:st+stop] = np.arange(1, stop-start+1)
    return sleeping_counter

  def ttc(self):
    with np.errstate(divide='ignore'):
      ttc = np.where(self.vx < -1e-3, # avoid too large (meaningless) values
                     -self.dx/self.vx,
                     np.inf)
    return ttc

  def invttc(self):
    return 1./self.ttc
