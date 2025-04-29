# -*- dataeval: init -*-

from fill_flr20_raw_tracks import cFill as Flr20RawTracksFill
from aebs.fill.flr20_raw_tracks_base import createIdenticalRadarTrackMasks

class cFill(Flr20RawTracksFill):
  @staticmethod
  def _createRadarTrackMasks(messages, ids, callback):
    return createIdenticalRadarTrackMasks(messages)
