# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis


class View(interface.iView):
  dep = 'calc_track_errors@ad.fill',

  def check(self):
    track_errors = self.modules.fill(self.dep[0])
    return track_errors

  def fill(self, track_errors):
    return track_errors

  def view(self, track_errors):
    client = datavis.cPlotNavigator(title="")
    self.sync.addClient(client)
    axis00 = client.addAxis()
    client.addSignal2Axis(axis00, "Orientation error", track_errors.time, track_errors.orientation_error)
    axis01 = client.addAxis()
    client.addSignal2Axis(axis01, "Cross track error", track_errors.time, track_errors.cross_error)
    return
