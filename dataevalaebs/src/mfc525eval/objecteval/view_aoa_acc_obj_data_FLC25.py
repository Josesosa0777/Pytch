# -*- dataeval: init -*-

import numpy as np

from interface import iParameter, iView
import datavis


class cMyView(iView):
  dep = 'fill_flc25_aoa_acc_tracks@aebs.fill',

  def check(self):
    modules = self.get_modules()
    acc_track = modules.fill("fill_flc25_aoa_acc_tracks@aebs.fill")
    return acc_track[0]

  def view(self, track):
    t = track.time
    pn = datavis.cPlotNavigator(title='FLC25 aoa acc obj track')
    # id
    ax = pn.addAxis(ylabel='obj id')
    pn.addSignal2Axis(ax, 'id', t, track.object_id, unit='')
    # dx
    ax = pn.addAxis(ylabel='dx', ylim = (-5.0, 100.0))
    pn.addSignal2Axis(ax, 'dx', t, track.dx, unit='m')
    pn.addSignal2Axis(ax, 'dy', t, track.dy, unit='m')
    # vx
    ax = pn.addAxis(ylabel='vx')
    pn.addSignal2Axis(ax, 'vx', t, track.vx, unit='m/s')
    # Lane
    #mapping = track.lane.mapping
    #ax = pn.addAxis(ylabel='LaneAssoc', yticks=mapping, ylim=(min(mapping)-0.5, max(mapping)+0.5))
    #pn.addSignal2Axis(ax, 'LaneAssoc', t, track.lane.join(), unit = '')
    # Lane
    #mapping = track.obj_type.mapping
    #ax = pn.addAxis(ylabel='Obj Type', yticks=mapping, ylim=(min(mapping)-0.5, max(mapping)+0.5))
    #pn.addSignal2Axis(ax, 'Obj Type', t, track.obj_type.join(), unit = '')
  
    # register client
    sync = self.get_sync()
    sync.addClient(pn)
    return
