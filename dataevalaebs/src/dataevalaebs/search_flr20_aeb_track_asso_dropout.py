# -*- dataeval: init -*-

""" Search for intervals where FLR20 AEB track fusion has dropout. Investigation
    is based on the video confidence and fusion status signals.

    Example situation:

     ^ video_conf
     |
    1| xxxx                      xx
     |     xx                   x
     |       xxx              xx
     |          xxxxx       xx
    0|               xxxxxxx
      --------------------------> t
     fused | dropout | tail | fused
"""

from collections import namedtuple

import numpy as np

from interface import iSearch
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList, maskToIntervals
from search_asso_flr20_base import SearchAssoFlr20

class SearchFlr20AssoDropout(iSearch):

  Dep = namedtuple('Dep', ['aeb', 'ego', 'tracks'])
  dep = Dep(aeb='fill_flr20_aeb_track@aebs.fill',
            ego='calc_flr20_egomotion@aebs.fill',
            tracks='fill_flr20_raw_tracks@aebs.fill')
  sgs = [ {"SensorStatus": ("Video_Data_General_B", "SensorStatus"),}, ]

  def init(self):
    self.title = 'FLR20 AEB track fusion dropout'
    self.votes = self.batch.get_labelgroups('AC100 track', 'S-Cam object',
                   'asso problem', 'moving direction', 'moving state',
                   'camera status')
    self.names = self.batch.get_quanamegroups('ego vehicle','target', 'conf fusion')
    return

  def check(self):
    aeb = self.modules.fill(self.dep.aeb)
    ego = self.modules.fill(self.dep.ego)
    tracks = self.modules.fill(self.dep.tracks)
    assert aeb.time is ego.time is tracks.time
    group = self.source.selectSignalGroup(self.sgs)
    return aeb, ego, tracks, group

  def fill(self, aeb, ego, tracks, group):
    t = aeb.time
    # create report
    report = Report( cIntervalList(t), self.title, votes=self.votes, names=self.names )
    sensor_status = group.get_value("SensorStatus", ScaleTime=t)
    sensor_status_lut = group.get_conversion_rule("SensorStatus")
    # start investigating
    for st,end in aeb.alive_intervals:
      sl = slice(st,end)
      # criterion: track is not fused but was before (hence video_conf is nonzero)
      unfused = ~aeb.fused[sl]
      video_conf_sl = aeb.video_conf[sl]
      video_conf_nonzero = video_conf_sl >  0.
      dropout = video_conf_nonzero & unfused
      if not np.any(dropout):
        # if nothing interesting found
        continue
      dropout_intervals = maskToIntervals(dropout)

      # merge "tails" of dropout (where video conf has fallen to zero)
      dropout_tail = (~video_conf_nonzero) & unfused
      if np.any(dropout_tail):
        for k, (st1,end1) in enumerate( list(dropout_intervals) ):
          for st2,end2 in maskToIntervals(dropout_tail):
            if end1 == st2:
              # mutate list in loop
              dropout_intervals[k] = st1,end2

      # merge close events
      intervals = cIntervalList.fromList(t, dropout_intervals)
      intervals = intervals.merge(0.5)

      # register interval in report
      i = aeb.id[st]
      for start, stop in intervals:
        interval = st_final, end_final = st+start, st+stop
        index = report.addInterval(interval)
        report.vote(index, 'AC100 track',  str(i))
        # check if previously associated video object id is available
        if st_final > st:
          j = aeb.video_id[st_final-1]
          report.vote(index, 'S-Cam object', str(j))
        else:
          # try to find video id in track history
          track = tracks[i]
          tr_st,tr_end = track.alive_intervals.findInterval(st_final)
          tr_fused_idx, = np.where( track.fused[tr_st:end_final] )
          if tr_fused_idx.size > 0:
            tr_last_fused = tr_st + tr_fused_idx[-1]
            j = track.video_id[tr_last_fused]
            report.vote(index, 'S-Cam object', str(j))
          else:
            # no video id found (track history is not completely measured)
            self.logger.info('no video id found for track %d in [%d,%d]' %(i,tr_st,tr_end))
        # check camera sensor status during dropout
        self.label_camera_status(report, index, interval, sensor_status, sensor_status_lut)
        # register radar track and ego vehicle attributes
        SearchAssoFlr20.set_ego_quantities(report, index, interval, ego)
        SearchAssoFlr20.label_mov_state_n_dir(report, index, interval, aeb)
        SearchAssoFlr20.set_target_quantities(report, index, interval, aeb)
        self.label_video_conf(report, index, interval, aeb)
    return report

  @staticmethod
  def label_camera_status(report, index, interval, sensor_status, lut):
    sl = slice(*interval)
    for status in np.unique( sensor_status[sl] ):
      label = lut[status]
      report.vote(index, 'camera status', label)
    return

  @staticmethod
  def label_video_conf(report, index, interval, obj):
    sl = slice(*interval)
    video_conf_event = obj.video_conf[sl]
    report.set(index, 'conf fusion', 'video conf min', video_conf_event.min())
    report.set(index, 'conf fusion', 'video conf max', video_conf_event.max())
    report.set(index, 'conf fusion', 'video conf start', video_conf_event[0])
    report.set(index, 'conf fusion', 'video conf end', video_conf_event[-1])
    return

  def search(self, report):
    result = self.FAILED if report.isEmpty() else self.PASSED
    self.batch.add_entry(report, result=result, tags=['SDF', 'association'])
    return
