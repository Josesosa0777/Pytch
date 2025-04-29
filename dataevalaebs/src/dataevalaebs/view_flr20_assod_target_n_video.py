# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import numpy as np

import datavis
from interface import iView

MAX_NUM_INT_RAD_TR = 21

init_params = dict( [('track %02d' %i, dict(id=i)) for i in xrange(MAX_NUM_INT_RAD_TR)] )

def collectMaskedArray(t, assoMasks, objs, signalName):
  if assoMasks:
    arr = None
    for id, mask in assoMasks.iteritems():
      if id not in objs:
        print 'Warning: "%s" of associated objects may not be fully collected'\
              '(id %d is not in recorded object ids %s)' %(signalName, id, objs.keys())
        continue
      obj = objs[id]
      signal = obj[signalName]
      if arr is None:
        arr = np.ma.masked_all_like(signal)
      arr.data[mask] = signal.data[mask]
      arr.mask &= ~mask
  else:
    arr = np.ma.masked_all_like(t)
  return arr


class cView(iView):
  dep = ('fill_flr20_raw_targets@aebs.fill',
         'fill_flr20_raw_tracks@aebs.fill',
         'fill_flc20_raw_tracks@aebs.fill')

  def init(self, id):
    self.id = id
    return

  def check(self):
    modules = self.get_modules()
    targets     = modules.fill('fill_flr20_raw_targets@aebs.fill')
    radarTracks = modules.fill('fill_flr20_raw_tracks@aebs.fill')
    videoTracks = modules.fill('fill_flc20_raw_track@aebs.fills')
    assert self.id in radarTracks, 'Track %d is not recorded' %self.id
    track = radarTracks[self.id]
    objects = videoTracks.rescale(radarTracks.time)
    return targets, track, objects

  def view(self, targets, track, objects):
    t = track.time
    pn = datavis.cPlotNavigator(title='FLR20 internal track %d' %self.id)
    # status flags
    yticks = dict( (k,v) for k,v in zip(xrange(8),[0,1,0,1,0,1,0,1]) )
    ax = pn.addAxis(ylabel='flags', yticks=yticks)
    pn.addSignal2Axis(ax, 'aeb track',  t, track.aeb_track, offset=6, displayscaled=False)
    pn.addSignal2Axis(ax, 'acc track',  t, track.acc_track, offset=4, displayscaled=False)
    pn.addSignal2Axis(ax, 'fused',      t, track.fused,     offset=2, displayscaled=False)
    pn.addSignal2Axis(ax, 'secondary',  t, track.secondary)
    # associated target and video index
    ax = pn.addAxis(ylabel='mov state')
    pn.addSignal2Axis(ax, 'stationary',  t, track.mov_state.stat)
    # associated target and video index
    ax = pn.addAxis(ylabel='asso idx')
    pn.addSignal2Axis(ax, 'asso_target_index', t, track.refl_id, alpha=.5)
    pn.addSignal2Axis(ax, 'asso_video_ID',     t, track.video_id)
    # confidence
    ax = pn.addAxis(ylabel='conf')
    pn.addSignal2Axis(ax, 'radar_conf', t, track.radar_conf)
    pn.addSignal2Axis(ax, 'video_conf', t, track.video_conf)
    # range
    ax = pn.addAxis(ylabel='dx')
    pn.addSignal2Axis(ax, 'radar dx', t, track.dx, unit='m')

    target_range = collectMaskedArray(t, track.refl_asso_masks, targets, 'dx')
    pn.addSignal2Axis(ax, 'target dx', t, target_range, unit='m', alpha=.5)

    dx = collectMaskedArray(t, track.video_asso_masks, objects, 'dx')
    pn.addSignal2Axis(ax, 'video dx', t, dx, unit='m')
    # angle
    ax = pn.addAxis(ylabel='angle')
    radar_angle_deg = np.rad2deg(track.angle)
    pn.addSignal2Axis(ax, 'radar angle', t, radar_angle_deg, unit=u"°")

    target_angle = collectMaskedArray(t, track.refl_asso_masks, targets, 'angle')
    target_angle_deg = np.rad2deg(target_angle)
    pn.addSignal2Axis(ax, 'target angle', t, target_angle_deg, unit=u"°", alpha=.5)

    angle_left  = collectMaskedArray(t, track.video_asso_masks, objects, 'angle_left')
    angle_right = collectMaskedArray(t, track.video_asso_masks, objects, 'angle_right')
    angle_left_deg  = np.rad2deg(angle_left)
    angle_right_deg = np.rad2deg(angle_right)
    pn.addSignal2Axis(ax, 'video left angle', t, angle_left_deg, unit=u"°")
    pn.addSignal2Axis(ax, 'video right angle', t, angle_right_deg, unit=u"°")
    # width
    ax = pn.addAxis(ylabel='width')
    pn.addSignal2Axis(ax, 'radar width', t, track.width, unit="m")

    width = collectMaskedArray(t, track.video_asso_masks, objects, 'width')
    pn.addSignal2Axis(ax, 'video width', t, width, unit="m")
    # register client
    sync = self.get_sync()
    sync.addClient(pn)
    return
