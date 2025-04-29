# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import interface
import datavis
import os
import kbtools
import kbtools_user


SignalGroups  = [
{
  "tr0_range": ("Tracks", "tr0_range"),
},
]

class cView(interface.iView):
  dep = 'search_flr20_KBAEBS_sim',
  def check(self):
    source = self.get_source()
    group = source.selectSignalGroup(SignalGroups)
    return group

  def view(self, group):
    sync = self.get_sync()
    client = datavis.cPlotNavigator(title="PN", figureNr=None)
    sync.addClient(client)

    axis = client.addAxis()
    time, value, unit = group.get_signal_with_unit("tr0_range")
    client.addSignal2Axis(axis, "ta0_range", time, value, unit=unit)

    t, masks =  self.get_modules().fill('search_flr20_KBAEBS_sim')
    axis = client.addAxis()
    offset = 0
    for title, mask in masks.iteritems(masks):
      client.addSignal2Axis(axis, title, t, warning, offset=offset,
                            displayscaled=False, unit=u"bool")
      offset += 2
    return

