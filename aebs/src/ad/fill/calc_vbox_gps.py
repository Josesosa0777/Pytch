# -*- dataeval: init -*-

import numpy as np

from interface import iCalc
from primitives.bases import Primitive

signal_group = [{"Longitude":   ("VBOX_2", "Longitude"),
                 "Latitude":    ("VBOX_1", "Latitude")},]


class VBoxTrajectory(Primitive):
    normalize_value = 60.0

    def __init__(self, time, lon, lat):
        mask = np.logical_and(lon != 0., lat != 0.)
        super(VBoxTrajectory, self).__init__(time[mask])
        raw_lon = np.abs(-lon) / self.normalize_value
        raw_lat = np.abs(lat) / self.normalize_value
        self.lon = raw_lon[mask]
        self.lat = raw_lat[mask]
        return


class Calc(iCalc):
    sgs = signal_group
    traj_obj = VBoxTrajectory

    def check(self):
        group = self.source.selectSignalGroup(self.sgs)
        return group

    def fill(self, group):
        time, longitude = group.get_signal("Longitude")
        latitude = group.get_value('Latitude', ScaleTime=time)
        obj = self.traj_obj(time, longitude, latitude)
        return obj
