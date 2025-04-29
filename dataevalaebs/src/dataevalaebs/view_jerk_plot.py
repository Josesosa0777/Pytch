# -*- dataeval: init -*-

"""
Plot basic driver activities and AEBS outputs

AEBS-relevant driver activities (pedal activation, steering etc.) and
AEBS outputs (in AEBS1 and XBR messages) are shown.
"""

import numpy as np

import datavis
from interface import iView


class View(iView):
    def check(self):
        sgs = [
            {
                "lateral_acceleration": ("VDC2_0B","VDC2_LatAccel_0B_s0B"),
            }
        ]
        # select signals
        group = self.source.selectLazySignalGroup(sgs)
        # give warning for not available signals
        for alias in sgs[0]:
            if alias not in group:
                self.logger.warning("Signal for '%s' not available" % alias)
        return group

    def view(self, group):
        pn = datavis.cPlotNavigator(title="Derivative of lateral acceleration")

        ax = pn.addAxis(ylabel="")

        # Subplot 1
        if 'lateral_acceleration' in group:
            lateral_accel_time, lateral_accel_value, lateral_accel_unit = group.get_signal_with_unit("lateral_acceleration")

            # Calculate derivative of lateral acceleration
            jerk = np.diff(lateral_accel_value) / np.diff(lateral_accel_time)
            for i in range(abs(lateral_accel_time.shape[0] - jerk.shape[0])):
                    jerk = np.append(jerk, 0.0)

            jerk = np.array(jerk)
            pn.addSignal2Axis(ax, "Jerk.", lateral_accel_time, jerk, unit='m/s2')

        self.sync.addClient(pn)
        return
