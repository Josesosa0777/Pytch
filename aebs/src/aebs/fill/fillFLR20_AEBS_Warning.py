# -*- dataeval: init -*-
from collections import namedtuple

import numpy as np

from interface.Interfaces import iObjectFill
from measproc.IntervalList import intervalsToMask
from fillFLR20 import INVALID_TRACK_ID

init_params = {
  'kb': dict(phases='calc_aebs_phases', name='KB'),
  'trw': dict(phases='calc_trw_aebs_phases', name='TRW'),
  'flr20': dict(phases='calc_flr20_aebs_phases-radar', name='FLR20'),
  'autobox': dict(phases='calc_flr20_aebs_phases-autobox', name='AUTOBOX'),
  'sil': dict(phases='calc_aebs_wrapper_phases@silkbaebs', name='SIL'),
}

class Fill(iObjectFill):
  def init(self, phases, name):
    self.dep = namedtuple('Dep', ['phases', 'aeb_track'])(
      phases, 'fill_flr20_aeb_track')
    self.grouptype_name = 'FLR20_AEBS_WARNING_' + name
    return

  def fill(self):
    modules = self.get_modules()
    phases = modules.fill(self.dep.phases)
    track = modules.fill(self.dep.aeb_track).rescale(phases.time)

    intervention = phases.warning | phases.partial_braking | phases.emergency_braking
    obj = dict(
      id=np.where(track.id.mask, INVALID_TRACK_ID, track.id.data),
      valid=track.tr_state.valid.data & ~track.tr_state.valid.mask,
      label='',
      dx=track.dx.data,
      dy=track.dy.data,
      type=np.where(intervention,
                    self.get_grouptype(self.grouptype_name),
                    self.get_grouptype('NONE_TYPE')),
    )
    init_intervals = [(st, st + 1) for st, end in track.alive_intervals]
    obj["init"] = intervalsToMask(init_intervals, track.dx.size)
    return track.time, [obj]

