# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis
def_param = interface.NullParam

sgs  = [
{
  "Model Root/HighwayAssist/TrajectoryGenerator/TrajectoryGenerator/TrajectoryPlanner/ControlPointDeterminer/LongitudinalControl/SetSpeedControlMode": ("HostService", "Model Root/HighwayAssist/TrajectoryGenerator/TrajectoryGenerator/TrajectoryPlanner/ControlPointDeterminer/LongitudinalControl/SetSpeedControlMode"),
  "Model Root/HighwayAssist/TrajectoryGenerator/TrajectoryGenerator/TrajectoryPlanner/ControlPointDeterminer/LongitudinalControl/feasible": ("HostService", "Model Root/HighwayAssist/TrajectoryGenerator/TrajectoryGenerator/TrajectoryPlanner/ControlPointDeterminer/LongitudinalControl/feasible"),
  "Model Root/HighwayAssist/InputInterface/track.valid": ("HostService", "Model Root/HighwayAssist/InputInterface/track.valid"),
  "Model Root/HighwayAssist/TrajectoryGenerator/TrajectoryGenerator/TrajectoryPlanner/ControlPointDeterminer/LongitudinalControl/transient": ("HostService", "Model Root/HighwayAssist/TrajectoryGenerator/TrajectoryGenerator/TrajectoryPlanner/ControlPointDeterminer/LongitudinalControl/transient"),
  "Model Root/HighwayAssist/TrajectoryGenerator/TrajectoryGenerator/TrajectoryPlanner/ControlPointDeterminer/LongitudinalControl/LongitudinalControlMode": ("HostService", "Model Root/HighwayAssist/TrajectoryGenerator/TrajectoryGenerator/TrajectoryPlanner/ControlPointDeterminer/LongitudinalControl/LongitudinalControlMode"),
  "Model Root/HighwayAssist/TrajectoryGenerator/TrajectoryGenerator/TrajectoryPlanner/ControlPointDeterminer/LongitudinalControl/FollowControlMode": ("HostService", "Model Root/HighwayAssist/TrajectoryGenerator/TrajectoryGenerator/TrajectoryPlanner/ControlPointDeterminer/LongitudinalControl/FollowControlMode"),
  "Model Root/HighwayAssist/TrajectoryGenerator/TrajectoryGenerator/TrajectoryPlanner/ControlPointDeterminer/<set_speed>": ("HostService", "Model Root/HighwayAssist/TrajectoryGenerator/TrajectoryGenerator/TrajectoryPlanner/ControlPointDeterminer/<set_speed>"),
  "Model Root/HighwayAssist/TrajectoryGenerator/TrajectoryGenerator/TrajectoryPlanner/ControlPointDeterminer/LongitudinalControl/takeover_request": ("HostService", "Model Root/HighwayAssist/TrajectoryGenerator/TrajectoryGenerator/TrajectoryPlanner/ControlPointDeterminer/LongitudinalControl/takeover_request"),
},
]

class View(interface.iView):
  def check(self):
    group = self.source.selectSignalGroupOrEmpty(sgs)
    return group

  def fill(self, group):
    return group

  def view(self, param, group):
    client00 = datavis.cPlotNavigator(title="")
    self.sync.addClient(client00)
    axis00 = client00.addAxis()
    time00, value00, unit00 = group.get_signal_with_unit("Model Root/HighwayAssist/TrajectoryGenerator/TrajectoryGenerator/TrajectoryPlanner/ControlPointDeterminer/LongitudinalControl/FollowControlMode")
    client00.addSignal2Axis(axis00, "Model Root/HighwayAssist/TrajectoryGenerator/TrajectoryGenerator/TrajectoryPlanner/ControlPointDeterminer/LongitudinalControl/FollowControlMode", time00, value00, unit=unit00)
    time01, value01, unit01 = group.get_signal_with_unit("Model Root/HighwayAssist/TrajectoryGenerator/TrajectoryGenerator/TrajectoryPlanner/ControlPointDeterminer/LongitudinalControl/LongitudinalControlMode")
    client00.addSignal2Axis(axis00, "Model Root/HighwayAssist/TrajectoryGenerator/TrajectoryGenerator/TrajectoryPlanner/ControlPointDeterminer/LongitudinalControl/LongitudinalControlMode", time01, value01, unit=unit01)
    time02, value02, unit02 = group.get_signal_with_unit("Model Root/HighwayAssist/TrajectoryGenerator/TrajectoryGenerator/TrajectoryPlanner/ControlPointDeterminer/LongitudinalControl/SetSpeedControlMode")
    client00.addSignal2Axis(axis00, "Model Root/HighwayAssist/TrajectoryGenerator/TrajectoryGenerator/TrajectoryPlanner/ControlPointDeterminer/LongitudinalControl/SetSpeedControlMode", time02, value02, unit=unit02)
    axis01 = client00.addAxis()
    time03, value03, unit03 = group.get_signal_with_unit("Model Root/HighwayAssist/TrajectoryGenerator/TrajectoryGenerator/TrajectoryPlanner/ControlPointDeterminer/LongitudinalControl/takeover_request")
    client00.addSignal2Axis(axis01, "Model Root/HighwayAssist/TrajectoryGenerator/TrajectoryGenerator/TrajectoryPlanner/ControlPointDeterminer/LongitudinalControl/takeover_request", time03, value03, unit=unit03)
    axis02 = client00.addAxis()
    time04, value04, unit04 = group.get_signal_with_unit("Model Root/HighwayAssist/TrajectoryGenerator/TrajectoryGenerator/TrajectoryPlanner/ControlPointDeterminer/LongitudinalControl/transient")
    client00.addSignal2Axis(axis02, "Model Root/HighwayAssist/TrajectoryGenerator/TrajectoryGenerator/TrajectoryPlanner/ControlPointDeterminer/LongitudinalControl/transient", time04, value04, unit=unit04)
    axis03 = client00.addAxis()
    time05, value05, unit05 = group.get_signal_with_unit("Model Root/HighwayAssist/TrajectoryGenerator/TrajectoryGenerator/TrajectoryPlanner/ControlPointDeterminer/LongitudinalControl/feasible")
    client00.addSignal2Axis(axis03, "Model Root/HighwayAssist/TrajectoryGenerator/TrajectoryGenerator/TrajectoryPlanner/ControlPointDeterminer/LongitudinalControl/feasible", time05, value05, unit=unit05)
    axis04 = client00.addAxis()
    time06, value06, unit06 = group.get_signal_with_unit("Model Root/HighwayAssist/InputInterface/track.valid")
    client00.addSignal2Axis(axis04, "Model Root/HighwayAssist/InputInterface/track.valid", time06, value06, unit=unit06)
    axis05 = client00.addAxis()
    time07, value07, unit07 = group.get_signal_with_unit("Model Root/HighwayAssist/TrajectoryGenerator/TrajectoryGenerator/TrajectoryPlanner/ControlPointDeterminer/<set_speed>")
    client00.addSignal2Axis(axis05, "Model Root/HighwayAssist/TrajectoryGenerator/TrajectoryGenerator/TrajectoryPlanner/ControlPointDeterminer/<set_speed>", time07, value07, unit=unit07)
    return
