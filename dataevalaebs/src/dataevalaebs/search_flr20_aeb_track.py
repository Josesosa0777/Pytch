# -*- dataeval: init -*-

import numpy as np

from measproc.report2 import Report
from measproc.IntervalList import cIntervalList, maskToIntervals
from search_asso_flr20_base import SearchAssoFlr20

__version__ = '0.1.0'

class SearchFlr20aebTrack(SearchAssoFlr20):

  dep = 'fill_flr20_aeb_track@aebs.fill',

  def init(self):
    SearchAssoFlr20.init(self)
    self.title = 'AEBS track'
    self.votes = self.batch.get_labelgroups('AC100 track')
    self.names = None
    return

  def check(self):
    modules = self.get_modules()
    track = modules.fill('fill_flr20_aeb_track@aebs.fill')
    return track

  def fill(self, track):
    report = self.create_report(track.time)
    for id in track.unique_ids:
      intervals = maskToIntervals(track.id == id)
      for interval in intervals:
        index = report.addInterval(interval)
        report.vote(index, 'AC100 track', str(id))
    # sort intervals in report
    report.sort()
    return report
