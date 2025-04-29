# -*- dataeval: init -*-

import numpy as np

from interface import iSearch
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList, maskToIntervals

sgs  = [
{
  "is_object_fusion": ("General_radar_status", "is_object_fusion"),
  "is_correct_video_protocol": ("General_radar_status", "is_correct_video_protocol"),
  "is_not_video_timeout": ("General_radar_status", "is_not_video_timeout"),
  "is_camera_working": ("General_radar_status", "is_camera_working"),
  "is_correct_video_sw": ("General_radar_status", "is_correct_video_sw"),
  "is_fusion_sw": ("General_radar_status", "is_fusion_sw"),
},
]

video_sgs  = [ {"SensorStatus": ("Video_Data_General_B", "SensorStatus"),}, ]

class Search(iSearch):
  dep = 'calc_asso_flr20@aebs.fill', 'calc_flr20_egomotion@aebs.fill'

  def init(self):
    self.title = 'Radar/camera object fusion availability'
    votes = self.batch.get_labelgroups('sensor check', 'availability')
    names = self.batch.get_quanamegroups('ego vehicle')
    self.kwargs = dict(votes=votes, names=names)
    return

  def check(self):
    a = self.modules.fill('calc_asso_flr20@aebs.fill')
    ego_motion = self.modules.fill('calc_flr20_egomotion@aebs.fill')
    assert a.scaleTime is ego_motion.time, 'Radar asso and ego motion time does not agree'
    group = self.source.selectSignalGroup(sgs)
    return a, ego_motion, group

  def error(self):
    report = Report( cIntervalList(np.array([])), self.title, **self.kwargs )
    self.batch.add_entry(report, result=self.FAILED)
    return

  def fill(self, a, ego_motion, group):
    t = a.scaleTime
    # create report
    report = Report( cIntervalList(t), self.title, **self.kwargs )
    mask = np.zeros_like(t, dtype=np.bool)
    # check fusion status indicator signals and collect invalid intervals
    for alias in group:
      signal = group.get_value(alias, ScaleTime=t)
      mask |= signal != 1
    # loop on invalid intervals
    for interval in maskToIntervals(mask):
      index = report.addInterval(interval)
      report.vote(index, 'sensor check', 'invalid')
      # check if fusion worked
      slicer = slice(*interval)
      if np.any(a.isAssoSuccessful[slicer]):
        availability = 'available'
      else:
        availability = 'n/a'
      report.vote(index, 'availability', availability)
      # register average ego speed on interval
      report.set( index, 'ego vehicle', 'speed', np.average(ego_motion.vx[slicer]) )
    return report

  def search(self, report):
    self.batch.add_entry(report, result=self.PASSED)
    return
