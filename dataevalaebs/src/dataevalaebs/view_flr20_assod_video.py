# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import numpy as np

import datavis
from interface import iView
from view_flr20_assod_target_n_video import init_params, collectMaskedArray

aeb_latency_query = """
SELECT DISTINCT late_cam_subquery.la_name, late_subquery.start, late_subquery.end
--Note: DISTINCT is needed because aeb flag can occur several times during a late interval, thus the interval intersection may result duplicate rows
FROM (
  SELECT ei.id ei_id, ei.start, ei.end, ei.start_time, ei.end_time, la.name la_name, en.measurementid me_id
  FROM entryintervals ei
  JOIN interval2label il ON ei.id = il.entry_intervalid
  JOIN labels la         ON il.labelid = la.id
  JOIN labelgroups lg    ON la.groupid = lg.id
  JOIN entries en        ON ei.entryid = en.id
  JOIN modules mo        ON en.moduleid = mo.id
  JOIN measurements meas ON en.measurementid = meas.id
  WHERE     lg.name = "AC100 track"
        AND la.name = :track_id
        AND mo.class = "dataevalaebs.search_asso_late_flr20.SearchFlr20AssoLate"
        AND meas.basename = :basename
  ) late_subquery
JOIN (
  SELECT ei.id ei_id, la.name la_name
  FROM entryintervals ei
  JOIN interval2label il ON ei.id = il.entry_intervalid
  JOIN labels la         ON il.labelid = la.id
  JOIN labelgroups lg    ON la.groupid = lg.id
  WHERE     lg.name = "asso problem"
        AND la.name = "late"
  ) late_2_subquery ON late_2_subquery.ei_id = late_subquery.ei_id
JOIN (
  SELECT ei.id ei_id, la.name la_name
  FROM entryintervals ei
  JOIN interval2label il ON ei.id = il.entry_intervalid
  JOIN labels la         ON il.labelid = la.id
  JOIN labelgroups lg    ON la.groupid = lg.id
  WHERE     lg.name = "S-Cam object"
  ) late_cam_subquery ON late_cam_subquery.ei_id = late_subquery.ei_id
JOIN (
  SELECT en.measurementid me_id, la.name la_name, ei.start_time, ei.end_time
  FROM entryintervals ei
  JOIN interval2label il ON ei.id = il.entry_intervalid
  JOIN labels la         ON il.labelid = la.id
  JOIN labelgroups lg    ON la.groupid = lg.id
  JOIN entries en        ON ei.entryid = en.id
  JOIN modules mo        ON en.moduleid = mo.id
  WHERE     lg.name = "AC100 track"
        AND mo.class = "dataevalaebs.search_flr20_aeb_track.SearchFlr20aebTrack"
  ) aeb_subquery ON
                        late_subquery.me_id = aeb_subquery.me_id
                    AND late_subquery.la_name = aeb_subquery.la_name
                    AND MAX(late_subquery.start_time, aeb_subquery.start_time) <= MIN(late_subquery.end_time, aeb_subquery.end_time)
;
"""

aeb_dropout_reunion_query = """
SELECT DISTINCT late_cam_subquery.la_name, dropout_subquery.start, dropout_subquery.end
--Note: DISTINCT is needed because aeb flag can occur several times during a dropout interval, thus the interval intersection may result duplicate rows
FROM (
  SELECT ei.id ei_id, ei.start, ei.end, ei.start_time, ei.end_time, la.name la_name, en.measurementid me_id
  FROM entryintervals ei
  JOIN interval2label il ON ei.id = il.entry_intervalid
  JOIN labels la         ON il.labelid = la.id
  JOIN labelgroups lg    ON la.groupid = lg.id
  JOIN entries en        ON ei.entryid = en.id
  JOIN modules mo        ON en.moduleid = mo.id
  JOIN measurements meas ON en.measurementid = meas.id
  WHERE     lg.name = "AC100 track"
        AND la.name = :track_id
        AND mo.class = "dataevalaebs.search_asso_dropout_reunion_flr20.SearchFlr20AssoReunion"
        AND meas.basename = :basename
  ) dropout_subquery
JOIN (
  SELECT ei.id ei_id, la.name la_name
  FROM entryintervals ei
  JOIN interval2label il ON ei.id = il.entry_intervalid
  JOIN labels la         ON il.labelid = la.id
  JOIN labelgroups lg    ON la.groupid = lg.id
  WHERE     lg.name = "S-Cam object"
  ) late_cam_subquery ON late_cam_subquery.ei_id = dropout_subquery.ei_id
JOIN (
  SELECT en.measurementid me_id, la.name la_name, ei.start_time, ei.end_time
  FROM entryintervals ei
  JOIN interval2label il ON ei.id = il.entry_intervalid
  JOIN labels la         ON il.labelid = la.id
  JOIN labelgroups lg    ON la.groupid = lg.id
  JOIN entries en        ON ei.entryid = en.id
  JOIN modules mo        ON en.moduleid = mo.id
  WHERE     lg.name = "AC100 track"
        AND mo.class = "dataevalaebs.search_flr20_aeb_track.SearchFlr20aebTrack"
  ) aeb_subquery ON
                        dropout_subquery.me_id = aeb_subquery.me_id
                    AND dropout_subquery.la_name = aeb_subquery.la_name
                    AND MAX(dropout_subquery.start_time, aeb_subquery.start_time) <= MIN(dropout_subquery.end_time, aeb_subquery.end_time)
;
"""

def make_intervals_per_id(q):
  d = {} # { video_id<int> : intervals<list> }
  for id,st,end in q:
    intervals = d.setdefault( int(id), [] )
    intervals.append( (st,end) )
  return d

def collect_arr_with_defects(track, objects, name, defects):
  signal = collectMaskedArray(track.time, track.video_asso_masks, objects, name)
  insert_defect_intervals(signal, objects, name, defects)
  return signal

def insert_defect_intervals(arr, objects, name, defects):
  for id, intervals in defects.iteritems():
    for st,end in intervals:
      if np.any( arr.mask[st:end] ):
        print 'Warning: risk of data overwrite, object %d has already values on [%d,%d] interval' %(id, st, end)
      arr[st:end] = objects[id][name][st:end]
  return

class cView(iView):
  dep = ('fill_flr20_raw_tracks@aebs.fill',
         'fill_flc20_raw_tracks@aebs.fill')

  def init(self, id):
    self.id = id
    return

  def check(self):
    modules = self.get_modules()
    radarTracks = modules.fill('fill_flr20_raw_tracks@aebs.fill')
    assert self.id in radarTracks, 'Track %d is not recorded' %self.id
    track = radarTracks[self.id]
    videoTracks = modules.fill('fill_flc20_raw_tracks@aebs.fill')
    objects = videoTracks.rescale(radarTracks.time)
    # get association defect events from database
    batch = self.get_batch()
    basename = self.get_source().getBaseName()
    lates_res    = batch.query(aeb_latency_query,         track_id=self.id, basename=basename)
    reunions_res = batch.query(aeb_dropout_reunion_query, track_id=self.id, basename=basename)
    all_res = lates_res + reunions_res # list elements added together
    defects = make_intervals_per_id(all_res)
    return track, objects, defects

  def view(self, track, objects, defects):
    t = track.time
    pn = datavis.cPlotNavigator(title='FLR20 internal track %d' %self.id)
    # associated video id
    ax = pn.addAxis(ylabel='asso id')
    pn.addSignal2Axis(ax, 'video id', t, track.video_id)
    missing_video_id = np.ma.masked_all_like(track.video_id)
    insert_defect_intervals(missing_video_id, objects, 'id', defects)
    pn.addSignal2Axis(ax, 'unfused video id', t, missing_video_id)
    # status flags
    yticks = dict( (k,v) for k,v in zip(xrange(6),[0,1]*3) )
    ax = pn.addAxis(ylabel='flags', yticks=yticks)
    pn.addSignal2Axis(ax, 'aeb track',  t, track.aeb_track, offset=4, displayscaled=False)
    pn.addSignal2Axis(ax, 'fused',      t, track.fused,     offset=2, displayscaled=False)
    pn.addSignal2Axis(ax, 'measured',   t, track.tr_state.measured)
    # dx
    ax = pn.addAxis(ylabel='dx')
    pn.addSignal2Axis(ax, 'radar dx', t, track.dx, unit='m')
    video_dx = collect_arr_with_defects(track, objects, 'dx', defects)
    pn.addSignal2Axis(ax, 'video dx', t, video_dx, unit='m')
    dx_diff_abs = np.abs(track.dx - video_dx)
    twinax = pn.addTwinAxis(ax, color='m', ylabel='abs diff')
    pn.addSignal2Axis(twinax, 'abs diff', t, dx_diff_abs, unit='m')
    # angle
    ax = pn.addAxis(ylabel='angle')
    angle_left  = collect_arr_with_defects(track, objects, 'angle_left',  defects)
    angle_right = collect_arr_with_defects(track, objects, 'angle_right', defects)
    angle_left_deg  = np.rad2deg(angle_left)
    angle_right_deg = np.rad2deg(angle_right)
    pn.addSignal2Axis(ax, 'video left angle', t, angle_left_deg, unit=u"°")
    pn.addSignal2Axis(ax, 'video right angle', t, angle_right_deg, unit=u"°")
    radar_angle_deg = np.rad2deg(track.angle)
    pn.addSignal2Axis(ax, 'radar angle', t, radar_angle_deg, unit=u"°")
    # vx
    ax = pn.addAxis(ylabel='vx')
    pn.addSignal2Axis(ax, 'radar vx', t, track.vx, unit='m/s')
    video_vx = collect_arr_with_defects(track, objects, 'vx', defects)
    pn.addSignal2Axis(ax, 'video vx', t, video_vx, unit='m/s')
    dx_diff_abs = np.abs(track.vx - video_vx)
    twinax = pn.addTwinAxis(ax, color='m', ylabel='abs diff')
    pn.addSignal2Axis(twinax, 'abs diff', t, dx_diff_abs, unit='m/s')
    # moving state
    ax = pn.addAxis(yticks=track.mov_state.mapping)
    pn.addSignal2Axis(ax, 'mov state', t, track.mov_state.join())
    # confidence
    ax = pn.addAxis(ylabel='conf')
    pn.addSignal2Axis(ax, 'radar conf', t, track.radar_conf)
    pn.addSignal2Axis(ax, 'video conf', t, track.video_conf)
    pn.addSignal2Axis(ax, 'credibility', t, track.credib)
    # register client
    sync = self.get_sync()
    sync.addClient(pn)
    return
