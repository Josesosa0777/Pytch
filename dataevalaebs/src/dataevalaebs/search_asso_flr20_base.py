# -*- dataeval: init -*-

import numpy as np

from interface import iSearch
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList
from aebs.labeling.track import labelMovState, labelMovDir

class SearchAssoFlr20(iSearch):

  dep = ('fill_flr20_raw_tracks@aebs.fill',
         'fill_flc20_raw_tracks@aebs.fill',
         'calc_asso_flr20@aebs.fill',
         'calc_flr20_egomotion@aebs.fill')

  def init(self):
    self.title = None
    self.votes = self.batch.get_labelgroups('AC100 track', 'S-Cam object',
      'asso problem', 'moving direction', 'moving state')
    self.names = self.batch.get_quanamegroups('ego vehicle','target')
    self.DIST_LIMIT = 100 # distance limit [m]
    return

  def check(self):
    radarTracks = self.modules.fill('fill_flr20_raw_tracks@aebs.fill')
    videoTracks = self.modules.fill('fill_flc20_raw_tracks@aebs.fill')
    videoTracksRescaled = videoTracks.rescale(radarTracks.time)
    a = self.modules.fill('calc_asso_flr20@aebs.fill')
    egoMotion = self.modules.fill('calc_flr20_egomotion@aebs.fill')
    return a, radarTracks, videoTracksRescaled, egoMotion

  def fill(self):
    raise NotImplementedError()

  def search(self, report):
    result = self.FAILED if report.isEmpty() else self.PASSED
    self.batch.add_entry(report, result=result, tags=['SDF', 'association'])
    return

  def create_report(self, time):
    return Report( cIntervalList(time), self.title, votes=self.votes, names=self.names )

  @classmethod
  def label_basics(cls, report, interval, i, j, obj):
    index = report.addInterval(interval)
    cls.label_object_pair(report, index, i, j)
    cls.label_mov_state_n_dir(report, index, interval, obj)
    return index

  @classmethod
  def label_object_pair(cls, report, index, i, j):
    report.vote(index, 'AC100 track',  str(i))
    report.vote(index, 'S-Cam object', str(j))
    return

  @classmethod
  def label_mov_state_n_dir(cls, report, index, interval, obj):
    labelMovState(report, index, obj, interval, wholetime=False)
    labelMovDir(report, index, obj, interval, wholetime=False)
    return

  @staticmethod
  def set_ego_quantities(report, index, interval, ego):
    slicer = slice(*interval)
    egoSpeedKph = ego.vx * 3.6
    egoSpeedOnEvent = egoSpeedKph[slicer]
    report.set( index, 'ego vehicle', 'speed', np.average(egoSpeedOnEvent) )
    return

  @staticmethod
  def set_target_quantities(report, index, interval, obj):
    slicer = slice(*interval)
    dx = obj.dx[slicer]
    report.set( index, 'target', 'dx min', np.min(dx) )
    report.set( index, 'target', 'dx max', np.max(dx) )
    report.set( index, 'target', 'dx start', dx[0] )
    report.set( index, 'target', 'dx end',   dx[-1] )
    ttc = obj.ttc[slicer]
    report.set( index, 'target', 'ttc min', np.min(ttc) )
    return
