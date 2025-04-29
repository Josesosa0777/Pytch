# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

from collections import namedtuple

import numpy as np

import datavis
from interface import iView
from view_flr20_assod_video import make_intervals_per_id

aeb_dropout_video_id_query = """
SELECT DISTINCT cam_tb.label, asso_dropout.start, asso_dropout.end
FROM (
  SELECT ei.id ei_id, en.measurementid me_id, ei.start, ei.end
  FROM entryintervals ei
  JOIN entries en        ON ei.entryid = en.id
  JOIN modules mo        ON en.moduleid = mo.id
  WHERE mo.class =
    "dataevalaebs.search_flr20_aeb_track_asso_dropout.SearchFlr20AssoDropout"
  ) asso_dropout
JOIN (
  SELECT ei.id ei_id, la.name label
  FROM entryintervals ei
  JOIN interval2label il ON ei.id = il.entry_intervalid
  JOIN labels la         ON il.labelid = la.id
  JOIN labelgroups lg    ON la.groupid = lg.id
  WHERE     lg.name = 'S-Cam object'
  ) cam_tb ON asso_dropout.ei_id = cam_tb.ei_id
JOIN (
  SELECT meas.id me_id, meas.basename
  FROM measurements meas
  WHERE meas.basename = :basename
  ) meas_tb ON asso_dropout.me_id = meas_tb.me_id
;
"""

class cView(iView):
  Dep = namedtuple('Dep', ['aeb', 'objects'])
  dep = Dep(aeb='fill_flr20_aeb_track@aebs.fill',
            objects='fill_flc20_raw_tracks@aebs.fill')

  @staticmethod
  def collect_obj_slices(aeb, objects, id2intervals):
    obj_slices = {} # { id<int> : slices<list<slice>> }
    for id, intervals in id2intervals.iteritems():
      t = aeb.time
      obj = objects[id]
      for st,end in intervals:
        aeb_st, aeb_end = aeb.alive_intervals.findInterval(st)
        # try to find a timestamp (step-by-step backwards) where object is alive
        for k in xrange(st, aeb_st-1, -1):
          try:
            obj_st, obj_end = obj.alive_intervals.findInterval(k)
          except ValueError:
            continue # keep on searching
          else:
            start = max(obj_st, aeb_st)
            stop  = min(obj_end, aeb_end)
            slices = obj_slices.setdefault(id, [])
            slices.append( slice(start,stop) )
            break
    return obj_slices

  @staticmethod
  def collect_array(signame, objects, obj_slices):
    dummy_obj = objects.itervalues().next()
    arr = np.ma.masked_all_like( dummy_obj[signame] )
    for id, slices in obj_slices.iteritems():
      signal = objects[id][signame]
      for sl in slices:
        arr[sl] = signal[sl]
    return arr

  def check(self):
    modules = self.get_modules()
    aeb     = modules.fill('fill_flr20_aeb_track@aebs.fill')
    objects = modules.fill('fill_flc20_raw_tracks@aebs.fill')
    objects = objects.rescale(aeb.time)
    # get association defect events from database
    batch = self.get_batch()
    basename = self.get_source().getBaseName()
    dropout_res = batch.query(aeb_dropout_video_id_query, basename=basename)
    id2intervals = make_intervals_per_id(dropout_res)
    obj_slices = self.collect_obj_slices(aeb, objects, id2intervals)
    return aeb, objects, obj_slices

  def view(self, aeb, objects, obj_slices):
    t = aeb.time
    pn = datavis.cPlotNavigator(title='FLR20 AEB track fusion dropout')
    # associated video id
    ax = pn.addAxis(ylabel='id')
    pn.addSignal2Axis(ax, 'radar id', t, aeb.id)
    pn.addSignal2Axis(ax, 'video id', t, aeb.video_id)
    missing_video_id = self.collect_array('id', objects, obj_slices)
    pn.addSignal2Axis(ax, 'unfused video id', t, missing_video_id)
    # status flags
    yticks = dict( (k,v) for k,v in zip(xrange(4),[0,1]*2) )
    ax = pn.addAxis(ylabel='flags', yticks=yticks)
    pn.addSignal2Axis(ax, 'fused',    t, aeb.fused, offset=2,
      displayscaled=False)
    pn.addSignal2Axis(ax, 'measured', t, aeb.tr_state.measured)
    # dx
    ax = pn.addAxis(ylabel='dx')
    pn.addSignal2Axis(ax, 'radar dx', t, aeb.dx, unit='m')
    video_dx = self.collect_array('dx', objects, obj_slices)
    pn.addSignal2Axis(ax, 'video dx', t, video_dx, unit='m')
    dx_diff_abs = np.abs(aeb.dx - video_dx)
    twinax = pn.addTwinAxis(ax, color='m', ylabel='abs diff')
    pn.addSignal2Axis(twinax, 'abs diff', t, dx_diff_abs, unit='m')
    # angle
    ax = pn.addAxis(ylabel='angle')
    angle_left  = self.collect_array('angle_left', objects, obj_slices)
    angle_right = self.collect_array('angle_right', objects, obj_slices)
    angle_left_deg  = np.rad2deg(angle_left)
    angle_right_deg = np.rad2deg(angle_right)
    pn.addSignal2Axis(ax, 'video left angle', t, angle_left_deg, unit=u"°")
    pn.addSignal2Axis(ax, 'video right angle', t, angle_right_deg, unit=u"°")
    radar_angle_deg = np.rad2deg(aeb.angle)
    pn.addSignal2Axis(ax, 'radar angle', t, radar_angle_deg, unit=u"°")
    # vx
    ax = pn.addAxis(ylabel='vx')
    pn.addSignal2Axis(ax, 'radar vx', t, aeb.vx, unit='m/s')
    video_vx = self.collect_array('vx', objects, obj_slices)
    pn.addSignal2Axis(ax, 'video vx', t, video_vx, unit='m/s')
    dx_diff_abs = np.abs(aeb.vx - video_vx)
    twinax = pn.addTwinAxis(ax, color='m', ylabel='abs diff')
    pn.addSignal2Axis(twinax, 'abs diff', t, dx_diff_abs, unit='m/s')
    # moving state
    ax = pn.addAxis(yticks=aeb.mov_state.mapping)
    pn.addSignal2Axis(ax, 'mov state', t, aeb.mov_state.join())
    # confidence
    ax = pn.addAxis(ylabel='conf')
    pn.addSignal2Axis(ax, 'credibility', t, aeb.credib)
    pn.addSignal2Axis(ax, 'radar conf', t, aeb.radar_conf)
    pn.addSignal2Axis(ax, 'video conf', t, aeb.video_conf, lw=2)
    # register client
    sync = self.get_sync()
    sync.addClient(pn)
    return
