# -*- dataeval: init -*-

import numpy as np

from interface import iCalc
from metatrack import EmptyTrack
from measparser.signalproc import masked_all_like_fill
from fill_flr20_raw_tracks import Flr20Track_A087MB_V3_1, TARGET_NOT_REPORTED, TARGET_NOT_ASSOD
from fill_flc20_raw_tracks import INVALID_VIDEO_ID
from measproc.IntervalList import cIntervalList


class Flr20SelectedTrack(EmptyTrack):
  _attribs = Flr20Track_A087MB_V3_1._methods
  _attribs_prefix = ''
  _reserved_names = EmptyTrack._reserved_names + ('get_selection_timestamp',)

  def __init__(self, tracks):
    assert tracks, 'Tracks must not be empty!'
    super(Flr20SelectedTrack, self).__init__(tracks.time)
    self._tracks = tracks
    self._masks = None
    return

  def _collect_masks(self, selection_attr_name):
    masks = {}
    for i, track in self._tracks.iteritems():
      signal = track[selection_attr_name]
      mask = signal.data & ~signal.mask
      if np.any(mask):
        masks[i] = mask
    return masks

  def _create(self, name):
    out = None
    if not self._masks:
      # no track is selected as relevant to AEBS
      track = self._tracks.itervalues().next()
      res = track[name]
      out = self._create_empty_attrib(res)
    else:
      # AEBS track exists
      for i, mask in self._masks.iteritems():
        res = self._tracks[i][name]
        # create empty placeholder
        if out is None:
          out = self._create_empty_attrib(res)
        # paste data
        if isinstance(out, tuple):
          for k, arr in enumerate(res):
            out[k][mask] = arr.data[mask]
        else:
          out[mask] = res.data[mask]
    return out

  @staticmethod
  def _create_empty_attrib(res):
    if isinstance(res, tuple):
      out = res._make( [masked_all_like_fill(arr, value=0) for arr in res] )
    else:
      out = masked_all_like_fill(res, value=0)
    return out

  def rescale(self, timescale, **kwargs):
    return self.__class__( self._tracks.rescale(timescale, **kwargs) )

  def is_empty(self):
    " Check if selected track is empty the whole time "
    return not self._masks

  def unique_ids(self):
    " Unique ids of tracks that are selected over time "
    return tuple( self._masks.keys() )

  def refl_asso_masks(self):
    """ Collect where reflections was associated to this track
    :ReturnType: dict
    :Return: { refl_id<int> : mask<ndarray> }
    """
    return self._get_asso_masks(self.refl_id, (TARGET_NOT_REPORTED, TARGET_NOT_ASSOD))

  def video_asso_masks(self):
    """ Collect where video tracks was associated to this track
    :ReturnType: dict
    :Return: { video_id<int> : mask<ndarray> }
    """
    return self._get_asso_masks(self.video_id, (INVALID_VIDEO_ID,))

  def selection_intervals(self):
    """ Determine intervals where any object was selected.

    :ReturnType: cIntervalList
    """
    return cIntervalList.fromMask(self.time, ~self.id.mask)

  def alive_intervals(self):
    """ Determine intervals where object was alive. This function splits
    `selection_intervals` where the selected object's id has changed.

    :ReturnType: cIntervalList
    """
    id_ext = np.concatenate( [self.id.data[0:1], self.id.data] )
    diffid = np.diff(id_ext)
    jumps, = np.where((diffid != 0) & ~self.id.mask)
    alive_intervals = self.selection_intervals.split(jumps)
    return alive_intervals

  def get_selection_timestamp(self, timestamp):
    """ Get when the track at `timestamp` was selected (back in time)

    :Parameters:
      timestamp : int
    :ReturnType: int
    :Exceptions:
      ValueError : No AEBS track exists on `timestamp`
    """
    start,end = self.alive_intervals.findInterval(timestamp)
    return start


class Flr20AebTrack(Flr20SelectedTrack):
  def __init__(self, tracks):
    super(Flr20AebTrack, self).__init__(tracks)
    self._masks = self._collect_masks('aeb_track')
    return


class cFill(iCalc):
  dep = 'fill_flr20_raw_tracks',

  def check(self):
    modules = self.get_modules()
    tracks = modules.fill('fill_flr20_raw_tracks')
    track = Flr20AebTrack(tracks)
    return track
