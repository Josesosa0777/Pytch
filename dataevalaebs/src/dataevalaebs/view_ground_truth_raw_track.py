# -*- dataeval: init -*-
"""
:Name:
	view_ground_truth_raw_track.py
:Type:
	View Script
:Visualization Type:
	Plot Visualization
:Full Path:
	dataevalaebs/src/dataevalaebs/view_ground_truth_raw_track.py
:Sensors:
	ADMA(FREEBOARD)
:Short Description:
    To visualize plot for dx,dy,vx,VY
:Output Data Image/s:
		.. image:: ../images/view_ground_truth_raw_track_1.JPG
.. note::
	For source code click on [source] tag beside functions
"""
import numpy as np

from interface import iParameter, iView
import datavis

# instantiation of module parameters
init_params = dict( ('TRACK_%03d' %i, dict(id=i)) for i in xrange(0,1) )
class cMyView(iView):
  dep = 'fill_ground_truth_raw_tracks@aebs.fill',

  def init(self, id):
    self.id = id
    return

  def check(self):
    modules = self.get_modules()
    tracks = modules.fill("fill_ground_truth_raw_tracks@aebs.fill")
    #assert self.id in tracks, 'Track %d is not recorded' %self.id
    track = tracks
    return track

  def view(self, track):
    t = track["time"]
    pn = datavis.cPlotNavigator(title='Ground Truth internal track #%d' %self.id)
    # tracking state
    ax = pn.addAxis(ylabel='tracking')
    pn.addSignal2Axis(ax, 'valid',       t, track["tr_state"].valid)
    pn.addSignal2Axis(ax, 'measured',    t, track["tr_state"].measured)
    pn.addSignal2Axis(ax, 'historical',  t, track["tr_state"].hist)
    # dx
    ax = pn.addAxis(ylabel='dx')
    pn.addSignal2Axis(ax, 'dx', t, track["dx"], unit='m')
    # dy
    ax = pn.addAxis(ylabel='dy')
    pn.addSignal2Axis(ax, 'dy', t, track["dy"], unit='m')
    # vx
    ax = pn.addAxis(ylabel='vx')
    pn.addSignal2Axis(ax, 'vx', t, track["vx"], unit='m/s')
    # vy
    ax = pn.addAxis(ylabel='vy')
    pn.addSignal2Axis(ax, 'vy', t, track["vy"], unit='m/s')
    # vx abs
    ax = pn.addAxis(ylabel='vx_abs')
    pn.addSignal2Axis(ax, 'vx_abs', t, track["vx_abs"], unit='m/s')
    # vy abs
    ax = pn.addAxis(ylabel='vy_abs')
    pn.addSignal2Axis(ax, 'vy_abs', t, track["vy_abs"], unit='m/s')
    # ax
    ax = pn.addAxis(ylabel='ax')
    pn.addSignal2Axis(ax, 'ax', t, track["ax"], unit='m/s^2')
    # ay
    ax = pn.addAxis(ylabel='ay')
    pn.addSignal2Axis(ax, 'ay', t, track["ay"], unit='m/s^2')
    # register client
    sync = self.get_sync()
    sync.addClient(pn)
    return

