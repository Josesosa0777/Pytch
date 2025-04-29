# -*- dataeval: init -*-

from interface import iCalc
from fill_flr20_aeb_track import Flr20SelectedTrack


class Flr20AccTrack(Flr20SelectedTrack):
  def __init__(self, tracks):
    super(Flr20AccTrack, self).__init__(tracks)
    self._masks = self._collect_masks('acc_track')
    return


class cFill(iCalc):
  dep = 'fill_flr20_raw_tracks',

  def check(self):
    modules = self.get_modules()
    tracks = modules.fill('fill_flr20_raw_tracks')
    track = Flr20AccTrack(tracks)
    return track
