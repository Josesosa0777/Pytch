# -*- dataeval: init -*-

import numpy as np

from interface import iSearch
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList
from aebs.labeling.track import labelMovState, labelMovDir
from search_asso_flr20_base import SearchAssoFlr20
from search_flc20_sensor_status import sgs

FULLY_OPERATIONAL = 0

class Search(iSearch):
  dep = 'fill_flc20_raw_tracks@aebs.fill', 'fill_flr20_aeb_track@aebs.fill', \
        'calc_flr20_egomotion@aebs.fill'

  def init(self):
    self.title = 'FLC20 missing AEB track'
    votes = self.batch.get_labelgroups(
              'AC100 track', 'moving state', 'moving direction', 'sensor check')
    names = self.batch.get_quanamegroups('ego vehicle', 'target', 'mobileye')
    self.kwargs = dict(votes=votes, names=names)
    return

  def check(self):
    aeb = self.modules.fill('fill_flr20_aeb_track@aebs.fill')
    videos_orig = self.modules.fill('fill_flc20_raw_track@aebs.fills')
    videos = videos_orig.rescale(aeb.time)
    ego = self.modules.fill('calc_flr20_egomotion@aebs.fill')
    assert ego.time is aeb.time or np.array_equal(ego.time, aeb.time), 'Time mismatch'
    group = self.source.selectSignalGroup(sgs)
    return aeb, videos, ego, group

  def error(self):
    report = Report( cIntervalList(np.array([])), self.title, **self.kwargs )
    self.batch.add_entry(report, result=self.FAILED)
    return

  def fill(self, aeb, videos, ego, group):
    t = aeb.time
    # camera status
    video_status = group.get_value('SensorStatus', ScaleTime=t)
    video_frames = group.get_value('Frame_ID',     ScaleTime=t)
    # create report
    report = Report( cIntervalList(t), self.title, **self.kwargs )
    for alive_interval in aeb.alive_intervals:
      st,end = alive_interval
      alive_event = slice(*alive_interval)
      fused = aeb.fused[alive_event]
      if np.all(fused):
        # skip interval if fusion was all ok (hence also camera tracking)
        continue
      elif np.any(fused):
        # check existence of associated video tracks on interval
        video_ids = np.unique( aeb.video_id[alive_event][fused.data] )
        video_exists = np.zeros_like(t, dtype=np.bool)
        for video_id in video_ids:
          video = videos[video_id]
          video_exists |= video.alive_intervals.toMask()
        video_missing = ~(video_exists[alive_event])
        if np.any(video_missing):
          defect_intervals = cIntervalList.fromMask( t[alive_event], video_missing )
          merged_defect_intervals = defect_intervals.merge(DistLimit=1.0) # merge within 1s
          for start,stop in merged_defect_intervals:
            event_st, event_end = st+start, st+stop
            event = slice(event_st, event_end)
            interval = event_st, event_end
            index = report.addInterval(interval)
            report.vote(index, 'AC100 track', str( aeb.id[st] ))
            # ego speed average
            report.set( index, 'ego vehicle', 'speed', np.average( ego.vx[event] ) )
            # dx, ttc
            SearchAssoFlr20.set_target_quantities(report, index, interval, aeb)
            # moving state & direction
            labelMovState(report, index, aeb, interval, wholetime=False)
            labelMovDir(  report, index, aeb, interval, wholetime=False)
            # sensor status
            status = 'valid' if np.all(video_status[event] == FULLY_OPERATIONAL) else 'invalid'
            report.vote(index, 'sensor check', status)
            # video frame
            report.set( index, 'mobileye', 'frame start', video_frames[event_st] )
            report.set( index, 'mobileye', 'frame end',   video_frames[event_end-1] )
      else:
        # print 'No fusion of AEB track on [%.2f, %.2f] interval' %( t[st], t[end-1] )
        pass
    return report

  def search(self, report):
    self.batch.add_entry(report, result=self.PASSED)
    return
