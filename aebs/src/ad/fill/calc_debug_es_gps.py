# -*- dataeval: init -*-

import numpy as np

from interface import iCalc
from primitives.bases import Primitive

signal_group = [{"Longitude":   ("XCP_Test", "debug_ES_GPS_Longitude"),
                 "Latitude":    ("XCP_Test", "debug_ES_GPS_Latitude"),
                 "Heading":     ("XCP_Test", "debug_ES_GPS_Heading"),},]


class DebugEsGpsTrajectory(Primitive):
    def __init__(self, time, lon, lat, heading):
        mask = np.logical_and(lon != 0., lat != 0.)
        super(DebugEsGpsTrajectory, self).__init__(time[mask])
        self.lon = lon[mask]
        self.lat = lat[mask]
        self.heading = heading[mask]
        return


class Calc(iCalc):
    def check(self):
        coord_grp = self.source.selectSignalGroup(signal_group)
        return coord_grp

    def fill(self, coord_grp):
        time, longitude = coord_grp.get_signal("Longitude")
        latitude = coord_grp.get_value('Latitude', ScaleTime=time)
        heading = coord_grp.get_value('Heading', ScaleTime=time)
        obj = DebugEsGpsTrajectory(time, longitude, latitude, heading)
        return obj
