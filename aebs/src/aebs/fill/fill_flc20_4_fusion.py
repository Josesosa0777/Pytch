# -*- dataeval: init -*-

from collections import OrderedDict

import numpy as np

import interface
from measparser import signalproc
from fill_flr20_4_fusion import rescaleCanMessages, createRawTracks, dtypeFloat64to32

N_SCAM_MESSAGES = 10
N_SCAM_INT_TRACKS = 64
# tracking status
OLDER_VALID = 2

sg = {'number_of_obstacles': ('Obstacle_Status', 'Num_Obstacles')}
sgs = [sg,]

# optional track signal templates (not all the tracks might be present)
signalTemplates = {
  'Obstacle_%02d_Data_A' : ('ID', 'Pos_X', 'Vel_X', 'Valid'),
  'Obstacle_%02d_Data_B' : ('Obstacle_Right_Angle', 'Obstacle_Left_Angle'),
}

messageGroups = []
for m in xrange(1, N_SCAM_MESSAGES+1):
  messageGroup = {}
  for devNameTemplate, signalNames in signalTemplates.iteritems():
    devName = devNameTemplate %m
    for signalName in signalNames:
      messageGroup[signalName] = (devName, signalName)
  messageGroups.append(messageGroup)

def createCameraTrackMasks(messages, ids):
  """ Create validity masks of internal camera tracks from messages

  :Parameters:
    messages : dict
      { messageNum<int> : {signalName<str> : signal<numpy.ma.MaskedArray>} }
    ids : iterable
      Sequence of possible internal camera track ids (order followed in output)
  :ReturnType: OrderedDict
  :Return:
    { id<int> : {messageNum<int> : mask<ndarray>} }
  """
  trackMasks = OrderedDict()
  """ { trackNum<int> : {messageNum<int> : mask<ndarray>} } """
  for i in ids:
    messageMasks = {}
    for k, signals in messages.iteritems():
      # create track mask from message
      internal_track_index = signals['ID']
      mask = internal_track_index.data == i # track occurs in message
      mask &= ~internal_track_index.mask    # data is valid
      # skip message if track data is not present
      if np.any(mask):
        messageMasks[k] = mask
    trackMasks[i] = messageMasks
  return trackMasks

def rescaleToExternalTime(time, tracks, scaleTime):
  """ Simplified approach to rescale track data """
  newtracks = []
  for track in tracks:
    newtrack = {}
    for name, value in track.iteritems():
      if name in ('valid_b', 'measured_b', 'historical_b'):
        _, newvalue = signalproc.rescale(time, value, scaleTime)
      else:
        _, newvalue = signalproc.rescale(time, value, scaleTime,
                                         Order='mix', Mask=track['valid_b'])
      newtrack[name] = newvalue
    newtracks.append(newtrack)
  return newtracks

class cFill(interface.iCalc):
  def check(self):
    group = interface.Source.selectSignalGroup(sgs)
    optgroups = interface.Source.filterSignalGroups(messageGroups)
    return group, optgroups

  def fill(self, group, optgroups):
    scaleTime = interface.Source.getSignalFromSignalGroup(group, 'number_of_obstacles')[0]
    # rescale to common message time
    messages = rescaleCanMessages(scaleTime, interface.Source, optgroups,
                  len(optgroups[0]), InvalidValue=0)
    # create track masks
    trackMasks = createCameraTrackMasks(messages, xrange(N_SCAM_INT_TRACKS))
    # create raw tracks from track messages
    rawTracks = createRawTracks(messages, trackMasks,
                                dtypeFunc=dtypeFloat64to32, ma=False)
    # # create final tracks
    tracks = []
    for rawTrack in rawTracks.itervalues():
      track = {}
      tracks.append(track)
      if not rawTrack:
        continue
      track['alpRightEdge'] = np.deg2rad( rawTrack['Obstacle_Right_Angle'] )
      track['alpLeftEdge']  = np.deg2rad( rawTrack['Obstacle_Left_Angle'] )
      track['dx'] = rawTrack['Pos_X']
      with np.errstate(invalid='ignore', divide='ignore'):
        track['invttc'] = np.where( track['dx'] > 0,
                                    - rawTrack['Vel_X'] / rawTrack['Pos_X'],
                                    0)
      track['valid_b'] = rawTrack['Valid'] > 0
      track['measured_b'] = np.copy( track['valid_b'] )
      track['historical_b'] = rawTrack['Valid'] == OLDER_VALID
    return scaleTime, tracks
