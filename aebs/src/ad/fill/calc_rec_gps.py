# -*- dataeval: init -*-

import numpy as np

from interface import iCalc
from primitives.bases import Primitive
from measproc.IntervalList import maskToIntervals, intervalsToMask

coord_sgs = [{"Longitude":   ("XCP_Test", "debug_ES_TRAJ_RecLongitude"),
              "Latitude":    ("XCP_Test", "debug_ES_TRAJ_RecLatitude"),
              "Heading":     ("XCP_Test", "debug_ES_TRAJ_RecHeading"),
              "Index":       ("XCP_Test", "debug_ES_TRAJ_RecIndex"),},]


class RecordedGpsTrajectory(Primitive):
    def __init__(self, time, lon, lat, heading, indexes):
        self.mask = self.get_interval_and_mask(indexes, np.logical_and(lon != 0., lat != 0.))
        super(RecordedGpsTrajectory, self).__init__(time[self.mask])

        self.lon = lon[self.mask]
        self.lat = lat[self.mask]
        self.heading = heading[self.mask]
        return

    @staticmethod
    def get_interval_and_mask(indexes, mask):
        intervals = maskToIntervals(indexes > 0)
        length = [(interval[1] - interval[0]) for interval in intervals]
        start, end = intervals[np.argmax(np.array(length))]
        pre_index_mask = intervalsToMask([(start, end)], indexes.size)
        _, index_arr = np.unique(np.ma.masked_array(indexes, mask=~pre_index_mask), return_index=True)

        index_mask = np.zeros(indexes.shape, dtype=np.bool)
        index_mask[index_arr] = True
        return index_mask & pre_index_mask & mask


class Calc(iCalc):
    def check(self):
        coord_grp = self.source.selectSignalGroup(coord_sgs)
        return coord_grp

    def fill(self, coord_grp):
        time, longitude = coord_grp.get_signal("Longitude")
        latitude = coord_grp.get_value('Latitude', ScaleTime=time)
        heading = coord_grp.get_value('Heading', ScaleTime=time)
        indexes = coord_grp.get_value('Index', ScaleTime=time)
        obj = RecordedGpsTrajectory(time, longitude, latitude, heading, indexes)
        return obj

if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r'C:\KBData\Highway_Assist\measurements\boxberg\TMC_measurement398.MF4'
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    desired_traj = manager_modules.calc('calc_rec_gps@ad.fill', manager)
