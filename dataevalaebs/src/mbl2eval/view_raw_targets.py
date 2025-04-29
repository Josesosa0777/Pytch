# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

"""
Plots some attributes of the selected MBL2 target
"""

from interface import iView
import datavis

init_params = dict( ('TARGET_%02d' %i, dict(id=i)) for i in xrange(1, 21) )

class View(iView):
  dep = 'calc_mbl2_raw_targets@aebs.fill',
  TITLE_PAT = 'MBL2 target #%d'
  
  def init(self, id):
    self.id = id
    return
  
  def check(self):
    targets = self.modules.fill(self.dep[0])
    assert self.id in targets, 'Target %d is not recorded' %self.id
    target = targets[self.id]
    return target
  
  def view(self, target):
    t = target.time
    graph = datavis.cPlotNavigator(title=self.TITLE_PAT%self.id)
    
    axis_range = graph.addAxis(ylabel="range")
    axis_range_rate = graph.addAxis(ylabel="velocity")
    axis_angle = graph.addAxis(ylabel="angle")
    axis_power = graph.addAxis(ylabel="power", xlabel = "time [s]")
    
    graph.addSignal2Axis(axis_range,      'range',      t, target.range, unit='m')
    graph.addSignal2Axis(axis_range_rate, 'range_rate', t, target.range_rate, unit='m/s')
    graph.addSignal2Axis(axis_angle,      'angle',      t, target.angle, unit=u'°')
    graph.addSignal2Axis(axis_power,      'power',      t, target.power, unit='')
    
    self.sync.addClient(graph)
    
    return
