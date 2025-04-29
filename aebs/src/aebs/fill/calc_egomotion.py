# -*- dataeval: init -*-

"""
Calculates ego motion attributes.

Calculates ego motion attributes (speed, yaw rate, accel.) from any source
(J1939, FLR20, FLR25).
"""

import interface


class Calc(interface.iCalc):
    optdep = "calc_j1939_egomotion", "calc_flr20_egomotion", "calc_radar_egomotion-flr25"

    def check(self):
        assert self.passed_optdep, "Ego motion data not available"
        return

    def fill(self):
        return self.modules.fill(self.passed_optdep[0])
