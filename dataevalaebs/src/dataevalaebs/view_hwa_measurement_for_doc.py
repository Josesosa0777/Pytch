# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis
def_param = interface.NullParam

sgs   = [
{
  "Model Root/HighwayAssist/InputInterface/motion_constraints.t_min": ("HostService", "Model Root/HighwayAssist/InputInterface/motion_constraints.t_min"),
  "Model Root/HighwayAssist/InputInterface/motion_constraints.jx_max": ("HostService", "Model Root/HighwayAssist/InputInterface/motion_constraints.jx_max"),
  "Model Root/HighwayAssist/InputInterface/motion_constraints.ax_max": ("HostService", "Model Root/HighwayAssist/InputInterface/motion_constraints.ax_max"),
  "Model Root/HighwayAssist/InputInterface/motion_constraints.ay_max": ("HostService", "Model Root/HighwayAssist/InputInterface/motion_constraints.ay_max"),
  "Model Root/HighwayAssist/MotionControler/TrajectoryController/TrajectoryController/LongitudinalDemand/EngineControl/is_active{Occurence1}": ("HostService", "Model Root/HighwayAssist/MotionControler/TrajectoryController/TrajectoryController/LongitudinalDemand/EngineControl/is_active{Occurence1}"),
  "Model Root/HighwayAssist/InputInterface/track.vx": ("HostService", "Model Root/HighwayAssist/InputInterface/track.vx"),
  "Model Root/HighwayAssist/InputInterface/motion_constraints.ay_min": ("HostService", "Model Root/HighwayAssist/InputInterface/motion_constraints.ay_min"),
  "Model Root/HighwayAssist/InputInterface/track.dx": ("HostService", "Model Root/HighwayAssist/InputInterface/track.dx"),
  "Model Root/HighwayAssist/InputInterface/vehicle_states.vx": ("HostService", "Model Root/HighwayAssist/InputInterface/vehicle_states.vx"),
  "Model Root/HighwayAssist/InputInterface/motion_constraints.ax_min": ("HostService", "Model Root/HighwayAssist/InputInterface/motion_constraints.ax_min"),
  "Model Root/HighwayAssist/InputInterface/motion_constraints.jx_min": ("HostService", "Model Root/HighwayAssist/InputInterface/motion_constraints.jx_min"),
  "Model Root/HighwayAssist/InputInterface/motion_constraints.t_max": ("HostService", "Model Root/HighwayAssist/InputInterface/motion_constraints.t_max"),
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
    time00, value00, unit00 = group.get_signal_with_unit("Model Root/HighwayAssist/MotionControler/TrajectoryController/TrajectoryController/LongitudinalDemand/EngineControl/is_active{Occurence1}")
    client00.addSignal2Axis(axis00, "EngineControl_is_active", time00, value00, unit=unit00)
    axis01 = client00.addAxis()
    time01, value01, unit01 = group.get_signal_with_unit("Model Root/HighwayAssist/InputInterface/track.dx")
    client00.addSignal2Axis(axis01, "track.dx", time01, value01, unit=unit01)
    axis02 = client00.addAxis()
    time02, value02, unit02 = group.get_signal_with_unit("Model Root/HighwayAssist/InputInterface/track.vx")
    client00.addSignal2Axis(axis02, "track.vx", time02, value02, unit=unit02)
    time03, value03, unit03 = group.get_signal_with_unit("Model Root/HighwayAssist/InputInterface/vehicle_states.vx")
    client00.addSignal2Axis(axis02, "vehicle_states.vx", time03, value03, unit=unit03)
    client01 = datavis.cPlotNavigator(title="")
    self.sync.addClient(client01)
    axis03 = client01.addAxis()
    time04, value04, unit04 = group.get_signal_with_unit("Model Root/HighwayAssist/InputInterface/motion_constraints.ax_max")
    client01.addSignal2Axis(axis03, "Model Root/HighwayAssist/InputInterface/motion_constraints.ax_max", time04, value04, unit=unit04)
    time05, value05, unit05 = group.get_signal_with_unit("Model Root/HighwayAssist/InputInterface/motion_constraints.ax_min")
    client01.addSignal2Axis(axis03, "Model Root/HighwayAssist/InputInterface/motion_constraints.ax_min", time05, value05, unit=unit05)
    time06, value06, unit06 = group.get_signal_with_unit("Model Root/HighwayAssist/InputInterface/motion_constraints.ay_max")
    client01.addSignal2Axis(axis03, "Model Root/HighwayAssist/InputInterface/motion_constraints.ay_max", time06, value06, unit=unit06)
    time07, value07, unit07 = group.get_signal_with_unit("Model Root/HighwayAssist/InputInterface/motion_constraints.ay_min")
    client01.addSignal2Axis(axis03, "Model Root/HighwayAssist/InputInterface/motion_constraints.ay_min", time07, value07, unit=unit07)
    axis04 = client01.addAxis()
    time08, value08, unit08 = group.get_signal_with_unit("Model Root/HighwayAssist/InputInterface/motion_constraints.jx_max")
    client01.addSignal2Axis(axis04, "Model Root/HighwayAssist/InputInterface/motion_constraints.jx_max", time08, value08, unit=unit08)
    time09, value09, unit09 = group.get_signal_with_unit("Model Root/HighwayAssist/InputInterface/motion_constraints.jx_min")
    client01.addSignal2Axis(axis04, "Model Root/HighwayAssist/InputInterface/motion_constraints.jx_min", time09, value09, unit=unit09)
    axis05 = client01.addAxis()
    time10, value10, unit10 = group.get_signal_with_unit("Model Root/HighwayAssist/InputInterface/motion_constraints.t_max")
    client01.addSignal2Axis(axis05, "Model Root/HighwayAssist/InputInterface/motion_constraints.t_max", time10, value10, unit=unit10)
    time11, value11, unit11 = group.get_signal_with_unit("Model Root/HighwayAssist/InputInterface/motion_constraints.t_min")
    client01.addSignal2Axis(axis05, "Model Root/HighwayAssist/InputInterface/motion_constraints.t_min", time11, value11, unit=unit11)
    return
