# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import numpy as np

from interface import iCalc
from metatrack import EmptyTrack
from calc_mb79_kb_track_slots import KBTracks
from fill_flr20_aeb_track import Flr20SelectedTrack

warning_signal = [{
    "WarningTrack": ("TA", "warn_trigg_out_warning_track"),
}]


class MB79KBSelectedTrack(Flr20SelectedTrack):
    _attribs = KBTracks._methods
    _attribs_prefix = ''
    _reserved_names = EmptyTrack._reserved_names + ('get_selection_timestamp',)

    def __init__(self, tracks):
        assert tracks, 'Tracks must not be empty!'
        super(MB79KBSelectedTrack, self).__init__(tracks)
        self._tracks = tracks
        self._masks = None
        return

    def _collect_masks(self, warning_track):
        masks = {}
        for i, track in self._tracks.iteritems():
            mask = np.ma.masked_equal(warning_track, i+1).mask
            if np.any(mask):
                masks[i] = mask
        return masks

    def selection_intervals(self):
        raise NotImplementedError

    def alive_intervals(self):
        raise NotImplementedError

    def get_selection_timestamp(self, timestamp):
        raise NotImplementedError


class MB79KBWarningTrack(MB79KBSelectedTrack):
    def __init__(self, tracks, warning_track):
        super(MB79KBWarningTrack, self).__init__(tracks)
        self._masks = self._collect_masks(warning_track)
        return


class Calc(iCalc):
    dep = 'calc_mb79_kb_track_slots',

    def check(self):
        group = self.source.selectSignalGroup(warning_signal)
        warning_track = group.get_value("WarningTrack")
        modules = self.get_modules()
        tracks = modules.fill(self.dep[0])
        track = MB79KBWarningTrack(tracks, warning_track)
        return track
