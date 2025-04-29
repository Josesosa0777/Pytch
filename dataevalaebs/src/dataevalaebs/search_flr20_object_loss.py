# -*- dataeval: init -*-

import numpy as np

from search_asso_flr20_base import SearchAssoFlr20

MAX_NUM_LAST_AEB_CYCLES = 5

class SearchFlr20ObjectLoss(SearchAssoFlr20):

  def init(self):
    SearchAssoFlr20.init(self)
    self.title = 'Radar/camera object loss'
    self.votes = self.batch.get_labelgroups('AC100 track', 'S-Cam object', 'track selection',
      'asso afterlife', 'asso breakup reason', 'moving direction', 'moving state')
    return

  def fill(self, a, radarTracks, videoTracksRescaled, egoMotion):
    t = a.scaleTime
    # create report
    report = self.create_report(t)
    # start investigating track losses using asso breakups
    for (i,j), intervals in a.asso_intervals.iteritems():
      radar = radarTracks[i]
      if j not in videoTracksRescaled:
        print 'Warning: video track %d missing but referenced at intervals %s' %(j,intervals)
        continue
      video = videoTracksRescaled[j]
      assost_prev = None
      # loop back on association intervals
      for assost,assoend in intervals[::-1]:
        # skip asso interval if it's not the last during objects' lifetime (reunion)
        sl = slice(assoend,assost_prev)
        if assost_prev is not None:
          both_alive = (    np.all( ~radar.tr_state.valid.mask[sl] & radar.tr_state.valid.data[sl] )
                        and np.all( ~video.tr_state.valid.mask[sl] & video.tr_state.valid.data[sl] )  )
          if both_alive:
            assost_prev = assost
          else:
            assost_prev = None
          continue
        else:
          assost_prev = assost
        # skip interval if radar object was above dx limit
        if radar.dx[assoend-1] > self.DIST_LIMIT:
          continue
        # find the end timestamp of both tracks
        radarst, radarend = radar.alive_intervals.findInterval(assoend-1)
        try:
          _, videoend = video.alive_intervals.findInterval(assoend-1)
        except ValueError:
          # video tracking ended but object kept for a few cycles in radar
          videoend = assoend
        # compare end timestamps
        if videoend > radarend:
          # radar track loss
          survival_sensor = 'video'
          survival = video
          interval = radarend,videoend
        elif radarend > videoend:
          # video track loss
          survival_sensor = 'radar'
          survival = radar
          interval = videoend,radarend
        else:
          # both lost at the same time (uninteresting)
          continue
        # check afterlife
        reassod, reasso_idx = a.is_obj_assod_during(survival_sensor, survival._id, *interval, wholetime=False, index=True)
        if reassod:
          st,end = interval
          if reasso_idx == st:
            # lost sensor track was immediately replaced by another (uninteresting)
            continue
          new_objnum = a.get_pair_of_obj(survival_sensor, survival._id, reasso_idx)
          new_obj = radarTracks[new_objnum] if survival_sensor == 'video' else videoTracksRescaled[new_objnum]
          try:
            new_obj_st, _ = new_obj.alive_intervals.findInterval(reasso_idx)
          except ValueError:
            print 'Timestamp %d not in %s (num %d) alive intervals!' %(reasso_idx, new_obj, new_obj._id)
          else:
            if st < new_obj_st < end:
              # new object is born after previous ended -> sensor tracking missing on target vehicle
              interval = st, new_obj_st
            else:
              # new object is born before previous ended -> sensor tracking exists on target vehicle (uninteresting)
              continue
        # skip single interval at measurement end
        if interval[1] == t.size and interval[1]-interval[0] == 1:
          continue
        # labeling
        index = report.addInterval(interval)
        self.label_afterfile(report, index, interval, a, survival._id, survival_sensor, reassod)
        self.label_object_pair(report, index, i, j)
        self.label_mov_state_n_dir(report, index, interval, survival)
        self.set_target_quantities(report, index, interval, survival)
        self.set_ego_quantities(   report, index, interval, egoMotion)
        aeb_st = max(radarst, radarend-MAX_NUM_LAST_AEB_CYCLES)
        if np.any( radar.aeb_track[aeb_st:radarend] ):
          report.vote(index, 'track selection', 'AEB')
    # sort intervals in report
    report.sort()
    return report

  @staticmethod
  def label_afterfile(report, index, interval, a, survival_objnum, survival_sensor, reassod):
    breakup_reason = 'radar loss' if survival_sensor == 'video' else 'video loss'
    report.vote(index, 'asso breakup reason', breakup_reason)
    if reassod:
      report.vote(index, 'asso afterlife', 'new pair')
    else:
      report.vote(index, 'asso afterlife', 'lonely')
    return index
