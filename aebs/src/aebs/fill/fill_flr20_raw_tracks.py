# -*- dataeval: init -*-

import numpy as np

from interface import iCalc
from primitives.bases import PrimitiveCollection
from nputils.math import hyst
from measparser.signalgroup import select_allvalid_sgs, SignalGroupError
from measparser.signalproc import correctNorming, masked_all_like_fill
from calc_flr20_egomotion import is_left_positive
from metatrack import MovingState, MovingDirection, TrackingState, LaneStatus
from flr20_raw_tracks_base import TrackFromMessage, findUniqueIds, template2signame,\
       rescaleCanMessages, createRadarTrackMasks, stoppedNstationary, CREDIBILITY_MAX,\
       TRACKING_STATE, TR_SEL_ST, ACC_STATUS, A087MB,\
       TRACK_MESSAGE_NUM, TARGET_NOT_REPORTED, TARGET_NOT_ASSOD,\
       create_flr20_track_mask
from fill_flc20_raw_tracks import INVALID_VIDEO_ID

# optional track signal templates (not all the tracks might be present)
signalTemplates_A087MB_V3_1 = (
  'tr%d_acc_track_info',
  'tr%d_acceleration_over_ground',
  'tr%d_asso_target_index',
  'tr%d_corrected_lateral_distance',
  'tr%d_credibility',
  'tr%d_CW_track',
  'tr%d_forbidden',
  'tr%d_internal_track_index',
  'tr%d_is_video_associated',
  'tr%d_power',
  'tr%d_range',
  'tr%d_relative_velocitiy',
  'tr%d_secondary',
  'tr%d_track_selection_status',
  'tr%d_tracking_status',
  'tr%d_uncorrected_angle',
)

extraSignalTemplates_A087MB_V3_2 = (
  'tr%d_asso_video_ID',
  'tr%d_env_object_ID',
  'tr%d_is_env_object',
  'tr%d_object_class',
  'tr%d_radar_confidence',
  'tr%d_video_confidence',
  'tr%d_width',
)

extraSignalTemplates_A087MB_V3_3 = (
  'tr%d_lateral_position',
# 'tr%d_reserved',
)

signalTemplates_A087MB_V3_2 = signalTemplates_A087MB_V3_1 + extraSignalTemplates_A087MB_V3_2
signalTemplates_A087MB_V3_3 = signalTemplates_A087MB_V3_2 + extraSignalTemplates_A087MB_V3_3

def createMessageGroups(signalTemplates):
  messageGroups = []
  for m in xrange(TRACK_MESSAGE_NUM):
    messageGroup = {}
    for signalTemplate in signalTemplates:
      fullName = signalTemplate %m
      shortName = template2signame(signalTemplate)
      messageGroup[shortName] = ('Tracks', fullName)
    messageGroups.append(messageGroup)
  return messageGroups

messageGroups_A087MB_V3_1 = createMessageGroups(signalTemplates_A087MB_V3_1)
messageGroups_A087MB_V3_2 = createMessageGroups(signalTemplates_A087MB_V3_2)
messageGroups_A087MB_V3_3 = createMessageGroups(signalTemplates_A087MB_V3_3)


class Flr20Track_A087MB_V3_1(TrackFromMessage):
  _attribs = tuple(template2signame(tmpl) for tmpl in signalTemplates_A087MB_V3_1)
  _special_methods = 'refl_asso_masks', 'video_asso_masks'

  def __init__(self, id, msgTime, msgMasks, source, optgroups, dirCorr, ego,
               scaleTime=None, **kwargs):
    TrackFromMessage.__init__(self, id, msgTime, msgMasks, source, optgroups,
                              dirCorr, scaleTime=scaleTime, **kwargs)
    self._ego = ego
    return

  def rescale(self, scaleTime, **kwargs):
    ego = self._ego.rescale(scaleTime, **kwargs)
    cls = self.__class__
    return cls(self._id, self._msgTime, self._msgMasks, self._source,
               self._groups, self._dirCorr, ego, scaleTime=scaleTime, **kwargs)

  def id(self):
    data = np.repeat( np.uint8(self._id), self.time.size )
    arr = np.ma.masked_array(data, mask=self.dx.mask)
    return arr

  def angle(self):
    return self._dirCorr * np.deg2rad(self._uncorrected_angle)

  def range(self):
    return self.dx / np.cos(self.angle)

  def dx(self):
    return self._range # track range signal is in cartesian coordinates (contrary to targets)

  def dy(self):
    return self.dx * np.tan(self.angle)

  def dy_corr(self):
    return self._dirCorr * self._corrected_lateral_distance

  def vx(self):
    return self._relative_velocitiy

  def vx_abs(self):
    return self._ego.vx + self.vx

  def ax(self):
    return self.ax_abs - self._ego.ax

  def ax_abs(self):
    return self._acceleration_over_ground

  def fused(self):
    # data from generate_apvs.xls
    cw_video_confidence_high = 0.25
    cw_video_confidence_low = 0.1
    # apply hysteresis as in sensor
    fused_data = hyst(self.video_conf.data, cw_video_confidence_low, cw_video_confidence_high)
    fused = np.ma.masked_array(fused_data, mask=self.video_conf.mask)
    return fused

  def fused_momentary(self):
    return self._is_video_associated.astype(np.bool) # np.asarray gives ndarray

  def mov_state(self):
    standing = (self._track_selection_status & TR_SEL_ST.STATIONARY).astype(np.bool)
    ongoing = self.mov_dir.ongoing
    oncoming = self.mov_dir.oncoming
    moving = ongoing | oncoming
    stationary, stopped = stoppedNstationary(standing.data, moving.data)
    stationary = np.ma.masked_array(stationary, mask=standing.mask)
    stopped = np.ma.masked_array(stopped, mask=standing.mask)
    unknown = ~(stationary | stopped | moving)
    # dummy data
    dummy = np.zeros(self.dx.shape, dtype=bool)
    arr = np.ma.masked_array(dummy, mask=self.dx.mask)
    return MovingState(stat=stationary, stopped=stopped, moving=moving, unknown=unknown, crossing=arr, crossing_left=arr, crossing_right=arr, oncoming=oncoming)

  def mov_dir(self):
    oncoming = (self._track_selection_status & TR_SEL_ST.OPPOSITE_DIRECTION).astype(np.bool)
    ongoing  = (self._track_selection_status & TR_SEL_ST.SAME_DIRECTION).astype(np.bool)
    undef = ~(ongoing | oncoming)
    dummy = np.zeros(self.dx.shape, dtype=bool)
    arr = np.ma.masked_array(dummy, mask=self.dx.mask)
    return MovingDirection(oncoming=oncoming, ongoing=ongoing, undefined=undef, crossing=arr, crossing_left=arr, crossing_right=arr)

  def tr_state(self):
    valid = self._tracking_status != TRACKING_STATE.EMPTY
    meas  = self._tracking_status == TRACKING_STATE.ESTABLISHED
    hist  = self._tracking_status != TRACKING_STATE.INIT
    return TrackingState(valid=valid, measured=meas, hist=hist)

  def lane(self):
    same  = (self._track_selection_status & TR_SEL_ST.INLANE).astype(np.bool)
    left  = (self._track_selection_status & TR_SEL_ST.LEFTLANE).astype(np.bool)
    right = (self._track_selection_status & TR_SEL_ST.RIGHTLANE).astype(np.bool)
    uncorr_left  = (self._track_selection_status & TR_SEL_ST.EXTREMELEFT).astype(np.bool)
    uncorr_right = (self._track_selection_status & TR_SEL_ST.EXTREMERIGHT).astype(np.bool)
    unknown = ~(same | left | right | uncorr_left | uncorr_right)
    lane = LaneStatus(same=same, left=left, right=right, uncorr_left=uncorr_left,
                      uncorr_right=uncorr_right, unknown=unknown)
    return lane

  def credib(self):
    return self._credibility / CREDIBILITY_MAX

  def radar_conf(self):
    return masked_all_like_fill(self.credib, value=0)

  def video_conf(self):
    return masked_all_like_fill(self.credib, value=0)

  def acc_track(self):
    return self._acc_track_info == ACC_STATUS.ACC

  def aeb_track(self):
    return self._CW_track.astype(np.bool) # np.asarray gives ndarray

  def secondary(self):
    return self._secondary.astype(np.bool) # np.asarray gives ndarray

  def power(self):
    return self._power

  def width(self):
    return masked_all_like_fill(self.time, value=0)

  def refl_id(self):
    return self._asso_target_index

  def radar_id(self):
    return self.id

  def video_id(self):
    return masked_all_like_fill(self.id, value=0)

  def refl_asso_masks(self):
    """ Collect where reflections were associated to this track
    :ReturnType: dict
    :Return: { refl_id<int> : mask<ndarray> }
    """
    return self._get_asso_masks(self.refl_id, (TARGET_NOT_REPORTED, TARGET_NOT_ASSOD))

  def video_asso_masks(self):
    """ Collect where video tracks were associated to this track
    :ReturnType: dict
    :Return: { video_id<int> : mask<ndarray> }
    """
    return self._get_asso_masks(self.video_id, (INVALID_VIDEO_ID,))


class Flr20Track_A087MB_V3_2(Flr20Track_A087MB_V3_1):
  _attribs = tuple(template2signame(tmpl) for tmpl in signalTemplates_A087MB_V3_2)

  CONF_UINT8_MAX = 255.
  BAD_CONF_OFFSET = 6.
  BAD_CONF_FACTOR = 0.1
  BAD_CONF_MIN = BAD_CONF_OFFSET
  BAD_CONF_MAX = BAD_CONF_OFFSET + BAD_CONF_FACTOR * CONF_UINT8_MAX
  CONF_OFFSET = 0.
  CONF_FACTOR = 1./CONF_UINT8_MAX

  def radar_conf(self):
    return self._correct_conf_norm( self._radar_confidence )

  def video_conf(self):
    return self._correct_conf_norm( self._video_confidence )

  def video_id(self):
    return self._asso_video_ID

  def width(self):
    return self._width

  def _correct_conf_norm(self, arr):
    if np.min(arr) >= self.BAD_CONF_MIN and np.max(arr) <= self.BAD_CONF_MAX:
      res = correctNorming(arr, self.BAD_CONF_OFFSET, self.BAD_CONF_FACTOR,
                           self.CONF_OFFSET, self.CONF_FACTOR)
    else:
      res = arr
    return res


class Flr20Track_A087MB_V3_3(Flr20Track_A087MB_V3_2):
  _attribs = tuple(template2signame(tmpl) for tmpl in signalTemplates_A087MB_V3_3)

  def dy(self):
    return self._dirCorr * self._lateral_position


versions = [
  A087MB(sgs=messageGroups_A087MB_V3_1, size=len(signalTemplates_A087MB_V3_1), cls=Flr20Track_A087MB_V3_1),
  A087MB(sgs=messageGroups_A087MB_V3_2, size=len(signalTemplates_A087MB_V3_2), cls=Flr20Track_A087MB_V3_2),
  A087MB(sgs=messageGroups_A087MB_V3_3, size=len(signalTemplates_A087MB_V3_3), cls=Flr20Track_A087MB_V3_3),
]

class cFill(iCalc):
  dep = 'calc_flr20_egomotion',

  def check(self):
    modules = self.get_modules()
    ego = modules.fill('calc_flr20_egomotion')
    source = self.get_source()
    for version in versions[::-1]:
      filtgroups = source.filterSignalGroups(version.sgs)
      try:
        optgroups = select_allvalid_sgs(filtgroups, version.size)
      except SignalGroupError:
        continue
      else:
        cls = version.cls
        break
    else:
      raise SignalGroupError('Missing radar track signals')
    return ego, optgroups, cls

  def fill(self, ego, optgroups, cls):
    msgTime = ego.time
    # rescale signals (needed for track masks) to common message time
    source = self.get_source()
    names = ('internal_track_index', 'tracking_status')
    messages = rescaleCanMessages(msgTime, source, optgroups,
                  names=names, InvalidValue=0)
    # find unique track ids
    ids = [message['internal_track_index'].compressed() for message in messages.itervalues()]
    uniqueIds = findUniqueIds(ids)
    # create track masks
    trackMasks = self._createRadarTrackMasks(messages, uniqueIds, create_flr20_track_mask)
    # check for y coord axis direction correction
    dirCorr = 1 if is_left_positive(source) else -1
    # create empty tracks
    rawTracks = PrimitiveCollection(msgTime)
    for id, msgMasks in trackMasks.iteritems():
      rawTracks[id] = cls(id, msgTime, msgMasks, source, optgroups, dirCorr, ego)
    return rawTracks

  @staticmethod
  def _createRadarTrackMasks(messages, ids, callback):
    return createRadarTrackMasks(messages, ids, callback)
