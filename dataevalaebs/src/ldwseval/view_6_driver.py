# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

"""
It shows the steering wheel angle, the turn indicators, and the hazard light switch signals.
"""

import interface
import datavis

import numpy as np
sgs  = [
{


  "BX_LDW_Suppr": ("Bendix_Info", "BX_LDW_Suppr"),
  "VDC2_SteerWhlAngle_0B": ("VDC2_0B", "VDC2_SteerWhlAngle_0B"),
  "OEL_TurnSigSw_E6": ("OEL_E6", "OEL_TurnSigSw_E6"),
  "OEL_HazardLightSw_E6": ("OEL_E6", "OEL_HazardLightSw_E6"),
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

    ###AXIS01###
    ############
    axis01 = client00.addAxis()
    t_StrWhlAngle, StrWhlAngle = group.get_signal("VDC2_SteerWhlAngle_0B")
    StrWhlAngle = StrWhlAngle *180.0/np.pi
    client00.addSignal2Axis(axis01, "SteerWhlAngle", t_StrWhlAngle, StrWhlAngle, unit="degree")
    axis01.set_ylim((-40, 40))
    axis01.set_ylabel('[degree]')
    
    ###AXIS02###
    ############
    axis02 = client00.addAxis()
    t_turnsignal, turnsignal =  group.get_signal("OEL_TurnSigSw_E6")
    t_hazard_light_switch, hazard_light_switch = group.get_signal("OEL_HazardLightSw_E6")
    
    client00.addSignal2Axis(axis02, "turn_signal", t_turnsignal, turnsignal, unit="")
    client00.addSignal2Axis(axis02, "hazard_lightswitch", t_hazard_light_switch, hazard_light_switch, unit="",offset=3, displayscaled=False)
    axis02.set_yticklabels(['','OFF','LEFT','RIGHT','OFF','ON'])
    axis02.set_ylabel('turn_ind. haz.l.switch')
    axis02.set_ylim((0, 4))
    
    axis03 = client00.addAxis()
    t_LDW_suppr,  LDW_suppr = group.get_signal("BX_LDW_Suppr")
    client00.addSignal2Axis(axis03, "BX LDW suppression", t_LDW_suppr, LDW_suppr, unit="")
    return
