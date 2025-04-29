# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import interface
import datavis

import numpy as np
sgs  = [
{
  "ME_LDW_LaneDeparture_Right": ("Bendix_Info", "ME_LDW_LaneDeparture_Right"),
  "ME_LDW_LaneDeparture_Left": ("Bendix_Info", "ME_LDW_LaneDeparture_Left"),
  "LDW_LaneDeparture_Left": ("Bendix_Info", "LDW_LaneDeparture_Left"),
  "LDW_LaneDeparture_Right": ("Bendix_Info", "LDW_LaneDeparture_Right"),
  "FLI1_AcousticalWarningLeft_E8": ("FLI1_E8", "FLI1_AcousticalWarningLeft_E8"),
  "FLI1_AcousticalWarningRight_E8": ("FLI1_E8", "FLI1_AcousticalWarningRight_E8"),
  "FLI1_OpticalWarningRight_E8": ("FLI1_E8", "FLI1_OpticalWarningRight_E8"),
  "FLI1_OpticalWarningLeft_E8": ("FLI1_E8", "FLI1_OpticalWarningLeft_E8"),
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

    ###used signals###
    t_ME_LDW_left, ME_LDW_left = group.get_signal("ME_LDW_LaneDeparture_Left")
    t_ME_LDW_right, ME_LDW_right = group.get_signal("ME_LDW_LaneDeparture_Right")
    t_LDW_left, LDW_left = group.get_signal("LDW_LaneDeparture_Left")
    t_LDW_right, LDW_right = group.get_signal("LDW_LaneDeparture_Right")
    t_Optic_Warn_left, Optic_Warn_left = group.get_signal("FLI1_OpticalWarningLeft_E8")
    t_Optic_Warn_right, Optic_Warn_right = group.get_signal("FLI1_OpticalWarningRight_E8")
    t_Acoust_Warn_left, Acoust_Warn_left = group.get_signal("FLI1_AcousticalWarningLeft_E8")
    t_Acoust_Warn_right, Acoust_Warn_right = group.get_signal("FLI1_AcousticalWarningRight_E8")
    
    ###LEFT_SIDE###
    ############
    axis01 = client00.addAxis()
    axis01.set_title('left_side')
    client00.addSignal2Axis(axis01, "LDW_left", t_LDW_left, LDW_left, unit="")
    client00.addSignal2Axis(axis01, "ME_LDW_left", t_ME_LDW_left, ME_LDW_left, unit="",offset=2, displayscaled=False)
    client00.addSignal2Axis(axis01, "Optic_Warn_left", t_Optic_Warn_left, Optic_Warn_left, unit="",offset=4, displayscaled=False)
    client00.addSignal2Axis(axis01, "Acoustical_Warn_left", t_Acoust_Warn_left, Acoust_Warn_left, unit="",offset=6, displayscaled=False)
    axis01.set_yticklabels(['','Off','On','Off','On','Off','On','Off','On'])
    axis01.set_ylim((0, 7))

    ###RIGHT_SIDE###
    ############
    axis02 = client00.addAxis()
    axis02.set_title('right_side')
    client00.addSignal2Axis(axis02, "LDW_right", t_LDW_right, LDW_right, unit="")
    client00.addSignal2Axis(axis02, "ME_LDW_right", t_ME_LDW_right, ME_LDW_right, unit="",offset=2, displayscaled=False)
    client00.addSignal2Axis(axis02, "Optic_Warn_right", t_Optic_Warn_right, Optic_Warn_right, unit="",offset=4, displayscaled=False)
    client00.addSignal2Axis(axis02, "Acoustical_Warn_right", t_Acoust_Warn_right, Acoust_Warn_right, unit="",offset=6, displayscaled=False)
    axis02.set_yticklabels(['','Off','On','Off','On','Off','On','Off','On'])
    axis02.set_ylim((0, 7))
    return
