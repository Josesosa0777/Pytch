# -*- dataeval: init -*-

from collections import OrderedDict

import numpy as np

import interface
from fillAC100 import N_AC100_TR
from calc_flr20_egomotion import is_left_positive
from flr20_raw_tracks_base import rescaleCanMessages, CREDIBILITY_MAX,\
       createRadarTrackMasks, stoppedNstationary, create_flr20_track_mask

AC100_OBJ_NUM = 20
# tracking status
TRACK_IS_EMPTY       = 0
TRACK_IS_INIT        = 1
TRACK_IS_ESTABLISHED = 2
TRACK_IS_SLEEPING    = 3
# track selection status
SAME_DIRECTION     = 2**3
STATIONARY         = 2**4
OPPOSITE_DIRECTION = 2**5

sg = {"number_of_tracks": ("General_radar_status", "number_of_tracks")}
sgs = [sg,]

# optional track signal templates (not all the tracks might be present)
ac100signalTemplates = (
  'tr%d_internal_track_index',
  'tr%d_range',
  'tr%d_uncorrected_angle',
  'tr%d_relative_velocitiy',
  'tr%d_credibility',
  'tr%d_tracking_status',
  'tr%d_track_selection_status',
)

def dtypeFloat64to32(dtype):
  return np.float32 if dtype == np.float64 else dtype

messageGroups = []
for m in xrange(N_AC100_TR):
  messageGroup = {}
  for signalTemplate in ac100signalTemplates:
    fullName = signalTemplate %m
    shortName = signalTemplate.partition('_')[2]
    messageGroup[shortName] = ('Tracks', fullName)
  messageGroups.append(messageGroup)

def createRawTracks(messages, trackMasks, dtypeFunc=None, ma=True):
  """ Create raw internal sensor tracks

  :Parameters:
    messages : dict
      { messageNum<int> : {signalName<str> : signal<numpy.ma.MaskedArray>} }
    trackMasks : OrderedDict
      { id<int> : {messageNum<int> : mask<ndarray>} }
    dtypeFunc : function, optional
      Function for casting array dtypes. Disabled by default.
    ma : bool, optional
      Use masked array in output signals. If set to False, signals are regular
      numpy ndarrays (missing elements filled with zeros). True by default.
  :ReturnType: OrderedDict
  :Return:
    { id<int> : {signalName<str> : signal<numpy.ma.MaskedArray>} }
  """
  rawTracks = OrderedDict()
  for i, messageMasks in trackMasks.iteritems():
    track = {}
    for k, mask in messageMasks.iteritems():
      signals = messages[k]
      # collect track data using mask
      for name, signal in signals.iteritems():
        if name not in track:
          # transform dtype if required
          dtype = signal.dtype if dtypeFunc is None else dtypeFunc(signal.dtype)
          data = np.zeros_like(signal.data, dtype=dtype)
          # handle masked array request
          array = np.ma.masked_array(data, np.ones_like(mask)) if ma else data
          track[name] = array
        else:
          array = track[name]
          data = array.data if ma else array
        data[mask] = signal[mask]
        if ma:
          array.mask &= ~mask
    rawTracks[i] = track
  return rawTracks


class cFill(interface.iCalc):
  def check(self):
    group = interface.Source.selectSignalGroup(sgs)
    optgroups = interface.Source.filterSignalGroups(messageGroups)
    return group, optgroups

  def fill(self, group, optgroups):
    scaleTime = interface.Source.getSignalFromSignalGroup(group, 'number_of_tracks')[0]
    # rescale to common message time
    messages = rescaleCanMessages(scaleTime, interface.Source, optgroups,
                  len(ac100signalTemplates), InvalidValue=0)
    # create track masks
    trackMasks = createRadarTrackMasks(messages, xrange(AC100_OBJ_NUM), create_flr20_track_mask)
    # create raw tracks from track messages
    rawTracks = createRawTracks(messages, trackMasks,
                                dtypeFunc=dtypeFloat64to32, ma=False)
    # create final tracks
    tracks = []
    leftPositive = is_left_positive(interface.Source)
    for rawTrack in rawTracks.itervalues():
      track = {}
      tracks.append(track)
      if not rawTrack:
        continue
      track['angle'] = np.deg2rad( rawTrack['uncorrected_angle'] )
      if not leftPositive:
        track['angle'] *= -1.
      track['dx'] = rawTrack['range'] * np.cos( track['angle'] )
      track['dy'] = rawTrack['range'] * np.sin( track['angle'] )
      track['vx'] = rawTrack['relative_velocitiy']
      with np.errstate(invalid='ignore', divide='ignore'):
        track['invttc'] = np.where(track['dx'] > 0, -track['vx']/track['dx'], 0)
      track['valid_b'] = rawTrack['tracking_status'] != TRACK_IS_EMPTY
      track['measured_b'] = rawTrack['tracking_status'] == TRACK_IS_ESTABLISHED
      track['historical_b'] = rawTrack['tracking_status'] != TRACK_IS_INIT
      track['existProb'] = rawTrack['credibility'] / CREDIBILITY_MAX
      track['obstacleProb'] = track['existProb']
      ongoing  = np.asarray(rawTrack['track_selection_status'] & SAME_DIRECTION    , dtype=np.bool)
      standing = np.asarray(rawTrack['track_selection_status'] & STATIONARY        , dtype=np.bool)
      oncoming = np.asarray(rawTrack['track_selection_status'] & OPPOSITE_DIRECTION, dtype=np.bool)
      stationary, stopped = stoppedNstationary(standing, oncoming | ongoing)
      track['stationary_b'] = stationary
      track['stopped_b'] = stopped
      track['notClassified_b'] = ~(ongoing | standing | oncoming)
    return scaleTime, tracks
