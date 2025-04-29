# -*- dataeval: init -*-

import numpy as np

from pyutils.math import degminsec2decdeg
from ad.fill import calc_vbox_gps

signal_group = [{"Longitude":   ("GPS_Maus_1", "Longitude"),
                 "Latitude":    ("GPS_Maus_1", "Latitude")},]


class MausTrajectory(calc_vbox_gps.VBoxTrajectory):
    normalize_value = 100.0

    def __init__(self, time, lon, lat):
        super(MausTrajectory, self).__init__(time, lon, lat)
        self.convertToDecDeg()
        return

    def convertToDecDeg(self):
        lat_frac, lat_int = np.modf(self.lat)
        self.lat = degminsec2decdeg(lat_int, lat_frac, 0.0)
        lon_frac, lon_int = np.modf(self.lon)
        self.lon = degminsec2decdeg(lon_int, lon_frac, 0.0)
        return


class Calc(calc_vbox_gps.Calc):
    sgs = signal_group
    traj_obj = MausTrajectory
