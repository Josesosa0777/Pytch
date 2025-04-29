# -*- dataeval: init -*-

import numpy as np

from measproc.IntervalList import maskToIntervals
from search_asso_flr20_base import SearchAssoFlr20

__version__ = '0.1.0'

class SearchFlr20AebTrack(SearchAssoFlr20):
  dep = 'fill_flr20_aeb_track@aebs.fill',

  def init(self):
    SearchAssoFlr20.init(self)
    self.title = 'AEB track fusion status'
    self.votes = self.batch.get_labelgroups('AC100 track', 'asso state')
    self.names = None
    return

  def check(self):
    modules = self.get_modules()
    track = modules.fill('fill_flr20_aeb_track@aebs.fill')
    return track

  def fill(self, track):
    # create report
    report = self.create_report(track.time)
    for id in track.unique_ids:
      m = track.id == id
      fused = m & track.fused
      # fused
      for interval in maskToIntervals(fused):
        index = report.addInterval(interval)
        report.vote(index, 'asso state', 'fused')
        report.vote(index, 'AC100 track', str(id))
      # radar-only
      radar_only = m & ~track.fused
      for interval in maskToIntervals(radar_only):
        index = report.addInterval(interval)
        report.vote(index, 'asso state', 'radar only')
        report.vote(index, 'AC100 track', str(id))
    # sort intervals in report
    report.sort()
    return report
