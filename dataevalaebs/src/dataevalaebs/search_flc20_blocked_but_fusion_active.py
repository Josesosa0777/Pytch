# -*- dataeval: init -*-

""" Search for intervals where FLC20 sensor status is not fully operational but
    object fusion works in the FLR20 (the AEB track is fused).
"""

from collections import namedtuple

import numpy as np

from interface import iSearch
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList, maskToIntervals
from measparser.signalproc import findUniqueValues

FULLY_OPERATIONAL = 0

class Search(iSearch):

  Dep = namedtuple('Dep', ['aeb', 'ego'])
  dep = Dep(aeb='fill_flr20_aeb_track@aebs.fill',
            ego='calc_flr20_egomotion@aebs.fill')
  sgs = [
          {"SensorStatus": ("Video_Data_General_B", "SensorStatus"),
           "Frame_ID"    : ("Video_Data_General_B", "Frame_ID"),
          },
        ]

  def init(self):
    self.title = "Fusion works when FLC20 is NOT fully operational"
    self.votes = self.batch.get_labelgroups('camera status', 'relevance')
    self.names = self.batch.get_quanamegroups('mobileye', 'ego vehicle')
    return

  def check(self):
    aeb = self.modules.fill(self.dep.aeb)
    ego = self.modules.fill(self.dep.ego)
    assert aeb.time is ego.time
    group = self.source.selectSignalGroup(self.sgs)
    return aeb, ego, group

  def fill(self, aeb, ego, group):
    t = aeb.time
    # create report
    report = Report( cIntervalList(t), self.title, votes=self.votes, names=self.names )
    sensor_status = group.get_value("SensorStatus", ScaleTime=t)
    rule = group.get_conversion_rule("SensorStatus")
    frames = group.get_value("Frame_ID", ScaleTime=t)
    # start investigating
    uniques = findUniqueValues(sensor_status, exclude=FULLY_OPERATIONAL)
    for value in uniques:
      mask = sensor_status == value
      for st,end in maskToIntervals(mask):
        # no fusion at all during camera status problem -> skip event
        if not np.any( aeb.fused[st:end] ):
          continue
        # check for too short duration -> skip event
        if (st == end-1) or (t[end-1]-t[st] < 2.):
          continue
        # consider fusion timeout after camera status problem start (~0.5s)
        st_timeout = np.searchsorted( t, t[st]+1. )
        if st_timeout < st or st_timeout >= end:
          self.logger.debug("Error: time array is not properly ordered")
          relevance = 'false event' # here "false" indicates that error occurred
        else:
          relevance = 'relevant' if np.any( aeb.fused[st_timeout:end] ) else 'irrelevant'
        # start labeling
        index = report.addInterval( (st,end) )
        report.vote( index, 'camera status', rule[value] )
        report.vote( index, 'relevance', relevance )
        report.set( index, 'mobileye', 'frame start', frames[st] )
        report.set( index, 'mobileye', 'frame end',   frames[end-1] )
        report.set( index, 'ego vehicle', 'speed min', np.min(ego.vx[st:end]) )
    return report

  def search(self, report):
    result = self.FAILED if report.isEmpty() else self.PASSED
    self.batch.add_entry(report, result=result)
    return
