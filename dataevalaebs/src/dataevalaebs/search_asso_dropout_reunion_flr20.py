# -*- dataeval: init -*-

import numpy as np

from measproc.IntervalList import maskToIntervals, intervalsToMask
from search_asso_flr20_base import SearchAssoFlr20
from search_asso_late import exclude_interval_object_far_away

__version__ = '0.1.0'

class SearchFlr20AssoReunion(SearchAssoFlr20):

  def init(self):
    SearchAssoFlr20.init(self)
    self.title = 'Association dropout - reunion'
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
      bothValid = radar.tr_state.valid & video.tr_state.valid
      reunion = self.findReunion(
                  a, i, j, bothValid, radar.tr_state.hist, video.tr_state.hist)
      # drop (or shorten) intervals where radar object was above dx limit
      exclude_interval_object_far_away(reunion, radar.dx, limit=self.DIST_LIMIT)
      # register intervals (if any)
      for interval in reunion:
        index = self.label_basics(report, interval, i, j, radar)
        report.vote(index, 'asso problem', 'reunion')
        self.set_ego_quantities(report, index, interval, egoMotion)
        self.set_target_quantities(report, index, interval, radar)
    # sort intervals in report
    report.sort()
    return report

  @staticmethod
  def findReunion(a, i, j, bothValid, radarHist, videoHist):
    indices = a.assoData[i,j]
    # search for asso gaps
    assoMask = np.zeros(a.N, dtype=np.bool)
    assoMask[indices] = True
    notAssoMask = ~assoMask
    notAssoIntervals = maskToIntervals(notAssoMask)
    assoGapIntervals = [ (st,end) for (st,end) in notAssoIntervals
                                    if st != 0 and end != a.N ]
    assoGaps = intervalsToMask(assoGapIntervals, a.N)
    # check if objects were the same during asso gaps
    sameObjects = radarHist & videoHist
    sameObjects &= bothValid
    reunionCandidates = assoGaps & sameObjects
    reunion = [interval for interval in maskToIntervals(reunionCandidates)
                            if interval in assoGapIntervals]
    return reunion
