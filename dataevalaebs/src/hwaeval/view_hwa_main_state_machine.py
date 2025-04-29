# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis
def_param = interface.NullParam

sgs  = [
    {
        "enable_switch": ("HighwayAssist", "control.enable_switch"),
        "lat_ctrl_en_switch": ("HighwayAssist", "control.lat_ctrl_en_switch"),
        "set_switch": ("HighwayAssist", "control.set_switch"),
        "pause_switch": ("HighwayAssist", "control.pause_switch"),
        "resume_switch": ("HighwayAssist", "control.resume_switch"),
        "b_pedal_switch": ("HighwayAssist", "control.b_pedal_switch"),
        "turn_signal": ("HighwayAssist", "control.turn_signal"),
        "left_line.quality": ("HighwayAssist", "lanes.left_line.quality"),
        "right_line.quality": ("HighwayAssist", "lanes.right_line.quality"),
        "left_line.view_range": ("HighwayAssist", "lanes.left_line.view_range"),
        "right_line.view_range": ("HighwayAssist", "lanes.right_line.view_range"),
        "main_lon_ctrl_state": ("TrajectoryGenerator_TrajectoryGenerator_TrajectoryCoordinator", "MainStateMachine_lon_ctrl_state"),
        "main_lat_ctrl_state": ("TrajectoryGenerator_TrajectoryGenerator_TrajectoryCoordinator", "MainStateMachine_lat_ctrl_state"),
    },
]

class View(interface.iView):
    def check(self):
        group = self.source.selectSignalGroupOrEmpty(sgs)
        return group

    def fill(self, group):
        return group

    def view(self, param, group):
        client = datavis.cPlotNavigator(title="HWA Main State Machine")
        self.sync.addClient(client)

        boolean_signals = ["enable_switch", "lat_ctrl_en_switch", "set_switch",
                           "pause_switch", "resume_switch", "b_pedal_switch"]

        ax_boolean_ticks = dict((k, v) for k, v in zip(xrange(2 * len(boolean_signals)), [0, 1] * len(boolean_signals)))
        boolean_offset_vals = [k for (k, v) in ax_boolean_ticks.iteritems() if v == 0]
        boolean_offset_vals.sort(reverse=True)

        switches_ax = client.addAxis(yticks=ax_boolean_ticks)
        for idx, signal in enumerate(boolean_signals):
            time, value, unit = group.get_signal_with_unit(signal)
            client.addSignal2Axis(switches_ax, signal, time, value, unit=unit, displayscaled=False, offset=boolean_offset_vals[idx])

        ctrls_ax = client.addAxis()
        time, value, unit = group.get_signal_with_unit("turn_signal")
        client.addSignal2Axis(ctrls_ax, "turn_signal", time, value, unit=unit)

        lane_qua_ax = client.addAxis()
        time, value, unit = group.get_signal_with_unit("left_line.quality")
        client.addSignal2Axis(lane_qua_ax, "left_line.quality", time, value, unit=unit)
        time, value, unit = group.get_signal_with_unit("right_line.quality")
        client.addSignal2Axis(lane_qua_ax, "right_line.quality", time, value, unit=unit)

        lane_vr_ax = client.addAxis()
        time, value, unit = group.get_signal_with_unit("left_line.view_range")
        client.addSignal2Axis(lane_vr_ax, "left_line.view_range", time, value, unit=unit)
        time, value, unit = group.get_signal_with_unit("right_line.view_range")
        client.addSignal2Axis(lane_vr_ax, "right_line.view_range", time, value, unit=unit)

        main_stmch_ax = client.addAxis()
        time, value, unit = group.get_signal_with_unit("main_lon_ctrl_state")
        client.addSignal2Axis(main_stmch_ax, "main_lon_ctrl_state", time, value, unit=unit)
        time, value, unit = group.get_signal_with_unit("main_lat_ctrl_state")
        client.addSignal2Axis(main_stmch_ax, "main_lat_ctrl_state", time, value, unit=unit)
        return
