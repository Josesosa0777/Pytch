# -*- dataeval: init -*-

"""
Plot basic driver activities and FCW outputs

FCW-relevant driver activities (pedal activation, steering etc.) and
FCW outputs (in AEBS1 messages) are shown.
"""

import numpy as np

import datavis
from interface import iView


class View(iView):
    def check(self):
        sgs = [
            {
                "steer_wheel_angle": ("VDC2_0B", "VDC2_SteerWhlAngle_0B"),
                "acc_pedal_pos": ("EEC2_00", "EEC2_APPos1_00"),
                "velocity" : ("VehDyn", "ARS4xx_Device_AlgoVehCycle_VehDyn_Longitudinal_MotVar_Velocity"),
            },
            {
                "steer_wheel_angle": ("VDC2_0B_s0B", "VDC2_SteerWhlAngle_0B"),
                "acc_pedal_pos": ("EEC2_00_s00", "EEC2_APPos1_00"),
                "velocity": ("VehDyn", "ARS4xx_Device_AlgoVehCycle_VehDyn_Longitudinal_MotVar_Velocity"),
            },
            {
                "steer_wheel_angle": ("VDC2_0B","VDC2_SteerWhlAngle_0B_s0B"),
                "acc_pedal_pos"    : ("EEC2_00","EEC2_APPos1_00"),
                "velocity"         : ("ARS4xx Device.AlgoVehCycle.VehDyn","ARS4xx_Device_AlgoVehCycle_VehDyn_Longitudinal_MotVar_Velocity"),
            },


        ]
        # select signals
        group = self.source.selectLazySignalGroup(sgs)
        # give warning for not available signals
        for alias in sgs[0]:
            if alias not in group:
                self.logger.warning("Signal for '%s' not available" % alias)
        return group

    def view(self, group):
        pn = datavis.cPlotNavigator(title="Vehicle Speed & Accelerator Pedal Position")

        ax = pn.addAxis(ylabel="accel. p. pos.", ylim=(-5.0, 105.0))
        # accel. pedal
        if 'acc_pedal_pos' in group:
            time00, value00, unit00 = group.get_signal_with_unit("acc_pedal_pos")
            pn.addSignal2Axis(ax, "accel. p. pos.", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="velocity_x", ylim=(0, 30.0))
        # Vehicle Speed
        if 'velocity' in group:
            time02, value02, unit02 = group.get_signal_with_unit("velocity")
            if unit02 == "m/s" or not unit02:  # assuming m/s if unit is empty
                value02 = 3.6 * value02
                unit02 = "km/h"
            pn.addSignal2Axis(ax, "velocity_x", time02, value02, unit=unit02)

        ax = pn.addAxis(ylabel="steering wheel angle", ylim=(-100.0, 100.0))
        if 'steer_wheel_angle' in group:
            time04, value04, unit04 = group.get_signal_with_unit("steer_wheel_angle")
            if unit04 == "rad" or not unit04:  # assuming rad if unit is empty
                value04 = np.rad2deg(value04)
                unit04 = "deg"
            pn.addSignal2Axis(ax, "steering wheel angle", time04, value04, unit=unit04)

        self.sync.addClient(pn)
        return

    def extend_aebs_state_axis(self, pn, ax):
        return
