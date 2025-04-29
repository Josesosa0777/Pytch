# -*- dataeval: init -*-

"""
:Name:
	view_ground_truth_delta_track.py
:Type:
	View Script
:Visualization Type:
	Plot Visualization
:Full Path:
	dataevalaebs/src/dataevalaebs/view_ground_truth_delta_track.py
:Sensors:
	ADMA(DELTA)
:Short Description:
    To visualize plot for dx,dy,vx,VY
:Output Data Image/s:
		.. image:: ../images/view_ground_truth_delta_track_1.JPG
.. note::
	For source code click on [source] tag beside functions
"""
import numpy as np

from interface import iParameter, iView
import datavis

# instantiation of module parameters
init_params = dict( ('TRACK_%03d' %i, dict(id=i)) for i in xrange(0,1) )
class cMyView(iView):
  dep = 'fill_ground_truth_delta_tracks@aebs.fill',

  def init(self, id):
    self.id = id
    return

  def check(self):
    modules = self.get_modules()
    tracks = modules.fill("fill_ground_truth_delta_tracks@aebs.fill")
    track = tracks
    return track

  def view(self, track):
    t = track["time"]
    pn = datavis.cPlotNavigator(title='Ground Truth Delta internal track #%d' %self.id)
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

    sync = self.get_sync()
    sync.addClient(pn)
    return

