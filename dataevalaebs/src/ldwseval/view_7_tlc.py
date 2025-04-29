# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

"""

It shows the TLC flags: TLC left/right, BX TLC left/right

"""
import interface
import datavis

import numpy as np
sgs  = [
{


  "TLC_Next_Left_B": ("Video_Lane_Next_Left_B", "TLC_Next_Left_B"),
  
  "TLC_Next_Right_B": ("Video_Lane_Next_Right_B", "TLC_Next_Right_B"),
  "BX_TLC_Left": ("Bendix_Info4", "BX_TLC_Left"),
  "BX_TLC_Right": ("Bendix_Info4", "BX_TLC_Right"),
},
]

class View(interface.iView):
  def check(self):
    group = self.source.selectSignalGroup(sgs)
    return group

  def fill(self, group):
    return group

  def view(self, group):
    client00 = datavis.cPlotNavigator(title="LDWS", figureNr=None)
    self.sync.addClient(client00)


    t_BX_TLC_Right, BX_TLC_Right = group.get_signal("BX_TLC_Right")
    t_BX_TLC_Left, BX_TLC_Left = group.get_signal("BX_TLC_Left")
    t_TLC_Next_Right_B, TLC_Next_Right_B = group.get_signal("TLC_Next_Right_B")
    t_TLC_Next_Left_B, TLC_Next_Left_B = group.get_signal("TLC_Next_Left_B")

    ###AXIS01###
    ############

    axis01 = client00.addAxis()
    client00.addSignal2Axis(axis01, "TLC_left", t_TLC_Next_Left_B, TLC_Next_Left_B, unit="")
    client00.addSignal2Axis(axis01, "TLC_right", t_TLC_Next_Right_B, TLC_Next_Right_B, unit="",offset=3, displayscaled=False)
    
    axis02 = client00.addAxis()
    client00.addSignal2Axis(axis02, "BX_TLC_Left", t_BX_TLC_Left, BX_TLC_Left, unit="")
    client00.addSignal2Axis(axis02, "BX_TLC_Right", t_BX_TLC_Right, BX_TLC_Right, unit="",offset=3000, displayscaled=False)

    return
