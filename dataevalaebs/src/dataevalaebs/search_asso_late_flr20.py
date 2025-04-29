# -*- dataeval: init -*-

import numpy as np

from measproc.IntervalList import cIntervalList, maskToIntervals
from search_asso_flr20_base import SearchAssoFlr20
from search_asso_late import exclude_interval_object_far_away

__version__ = '0.2.0'

class SearchFlr20AssoLate(SearchAssoFlr20):

  def init(self):
    SearchAssoFlr20.init(self)
    self.title = 'Late associations'
    return

  def fill(self, a, radarTracks, videoTracksRescaled, egoMotion):
    t = a.scaleTime
    # create report
    report = self.create_report(t)
    # start investigating late associations
    for (i,j), indices in a.assoData.iteritems():
      radar = radarTracks[i]
      if j not in videoTracksRescaled:
        print 'Warning: video track %d missing but referenced at time indices %s' %(j,indices)
        continue
      video = videoTracksRescaled[j]
      lates, quicks = self.findLates(a, i, j, radar, video)
      # register late asso intervals (if any)
      for interval in lates:
        index = self.label_basics(report, interval, i, j, radar)
        report.vote(index, 'asso problem', 'late')
        self.set_ego_quantities(report, index, interval, egoMotion)
        self.set_target_quantities(report, index, interval, radar)
      for interval in quicks:
        index = self.label_basics(report, interval, i, j, radar)
        report.vote(index, 'asso problem', 'quick')
        self.set_ego_quantities(report, index, interval, egoMotion)
        self.set_target_quantities(report, index, interval, radar)
    # sort intervals in report
    report.sort()
    return report

  def findLates(self, a, i, j, radar, video):
    indices = a.assoData[i,j]
    assoMask = np.zeros(a.N, dtype=np.bool)
    assoMask[indices] = True
    assos = maskToIntervals(assoMask)
    bothValid = radar.tr_state.valid & video.tr_state.valid
    defectMask = bothValid & (~assoMask)
    bvalid = cIntervalList.fromMask(a.scaleTime, bothValid)
    if np.any(defectMask):
      defects = maskToIntervals(defectMask)
      # late interval candidates: both is valid but not associated until some time
      lates = [ (st,end) for st,end in defects for start,_ in assos if end == start ]
      # drop intervals where one of the objects was involved in another pair earlier
      for st,end in list(lates):
        radarst, _ = radar.alive_intervals.findInterval(st)
        videost, _ = video.alive_intervals.findInterval(st)
        start = max(radarst, videost)
        if (    a.is_obj_assod_during('radar', i, start, end, wholetime=False)
             or a.is_obj_assod_during('video', j, start, end, wholetime=False) ):
          lates.remove( (st,end) )
      # drop (or shorten) intervals where radar object was above dx limit
      exclude_interval_object_far_away(lates, radar.dx, limit=self.DIST_LIMIT)
    else:
      lates = []
    # quick interval candidates: immediate association when both valid (except measurement start time)
    quicks = [ (st,st+1) for st,end in bvalid for start,_ in assos
                           if st == start and st != 0 and radar.dx[st] <= self.DIST_LIMIT]
    return lates, quicks
