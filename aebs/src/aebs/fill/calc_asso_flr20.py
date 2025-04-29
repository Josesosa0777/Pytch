# -*- dataeval: init -*-

import interface
from aebs.sdf.asso_flr20_fus_result import Flr20AssoResult

class Calc(interface.iCalc):
  dep = 'fill_flr20_raw_tracks',

  def check(self):
    modules = self.get_modules()
    radarTracks = modules.fill('fill_flr20_raw_tracks')
    return radarTracks

  def fill(self, radarTracks):
    a = Flr20AssoResult(radarTracks)
    a.calc()
    return a
