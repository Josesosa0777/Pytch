# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

"""
Plots some attributes of the selected MBL2 track
"""

from interface import iView
import datavis

init_params = dict( ('TRACK_%02d' %i, dict(id=i)) for i in xrange(1, 21) )

class View(iView):
  dep = 'calc_mbl2_raw_tracks@aebs.fill',
  TITLE_PAT = 'MBL2 track #%d'   
  
  def init(self, id):
    self.id = id
    return
  
  def check(self):
    tracks = self.modules.fill(self.dep[0])
    assert self.id in tracks, 'Track %d is not recorded' %self.id
    track = tracks[self.id]
    return track
  
  def view(self, track):
    t = track.time
    graph = datavis.cPlotNavigator(title = self.TITLE_PAT%self.id)
    
    axis_dx = graph.addAxis(ylabel="dx")
    axis_dy = graph.addAxis(ylabel="dy")
    axis_vx = graph.addAxis(ylabel="vx")
    axis_vy = graph.addAxis(ylabel="vy")
    axis_ttc= graph.addAxis(ylabel="TTC", xlabel="time [s]")
    
    graph.addSignal2Axis(axis_dx,   'dx', t, track.dx, unit='m')
    graph.addSignal2Axis(axis_dy,   'dy', t, track.dy, unit='m')
    graph.addSignal2Axis(axis_vx,   'vx', t, track.vx, unit='m/s')
    graph.addSignal2Axis(axis_vy,   'vy', t, track.vy, unit='m/s')
    graph.addSignal2Axis(axis_ttc, 'ttc', t, track.ttc, unit='s')
    
    self.sync.addClient(graph)
    
    return
