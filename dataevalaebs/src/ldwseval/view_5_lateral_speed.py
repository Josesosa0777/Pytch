# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

"""
It shows the left and right lateral velocities
"""

import interface
import datavis


sgs  = [
{
  "Lateral_Velocity_Right_B": ("Bendix_Info2", "Lateral_Velocity_Right_B"),
  "Lateral_Velocity_Left_B": ("Bendix_Info2", "Lateral_Velocity_Left_B"),
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

    t_LatVel_left, LatVel_left = group.get_signal("Lateral_Velocity_Left_B")
    t_LatVel_right, LatVel_right = group.get_signal("Lateral_Velocity_Right_B")

    ###left_side###
    ###########
    axis00 = client00.addAxis()
    axis00.set_title('left_side')
    client00.addSignal2Axis(axis00, "lateral_speed_left", t_LatVel_left, LatVel_left, unit="m/s")

    ###right_side###
    ###########
    axis01 = client00.addAxis()
    axis01.set_title('right_side')
    client00.addSignal2Axis(axis01, "lateral_speed_right", t_LatVel_right, LatVel_right, unit="m/s")

    return
