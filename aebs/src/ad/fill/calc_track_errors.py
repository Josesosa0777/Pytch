# -*- dataeval: init -*-

import numpy as np

from interface import iCalc
from primitives.bases import Primitive
from measproc.MapTileCalculation import Coord, get_distance_from_lat_lon

SEARCH_WINDOW_WIDTH = 10


class TrackErrors(Primitive):
    def __init__(self, rec_traj, meas_traj):
        super(TrackErrors, self).__init__(meas_traj.time)
        self.rec_traj = rec_traj
        self.meas_traj = meas_traj
        # the trajectory error is measured on these points
        self.lon = self.meas_traj.lon
        self.lat = self.meas_traj.lat
        # calc the cross error
        self.cross_error, self.orientation_error = self.cross_track_error(self.rec_traj, self.meas_traj)
        # get the color map
        self.colors = self.calc_color_map(self.cross_error)
        return

    @staticmethod
    def cross_track_error(desired_traj, actual_traj, minimum_distance=True):
        des_lon, des_lat = desired_traj.lon, desired_traj.lat
        act_lon, act_lat = actual_traj.lon, actual_traj.lat
        # get the vector which is perpendicular to the heading
        dist_orient = np.deg2rad((actual_traj.heading + 90.0) % 360)
        vx = np.float64(np.sin(dist_orient))
        vy = np.float64(np.cos(dist_orient))
        # get the line --> vy * lat - vx * lon = vy * curr_lat - vx * curr_lon
        const = vy * act_lat - vx * act_lon
        # allocate memory for track error and for the orientation error
        desired = Coord(des_lon, des_lat)
        track_error = np.zeros(act_lon.shape, dtype=np.float64)
        orientation_error = np.zeros(act_lon.shape, dtype=np.float64)
        for i in xrange(len(track_error)):
            # get the current coordinate
            curr_cord = Coord(act_lon[i], act_lat[i])
            # calculate the minimum distance from the desired trajectory
            dist = get_distance_from_lat_lon(curr_cord, desired)
            min_index = np.argmin(dist)
            # calculate the dynamic window range
            end_dist = len(track_error) - min_index
            start_dist = min_index

            if minimum_distance:
                index = min_index
            else:
                if start_dist < SEARCH_WINDOW_WIDTH / 2:
                    start = 0
                    end = min_index + SEARCH_WINDOW_WIDTH - start_dist
                elif end_dist < SEARCH_WINDOW_WIDTH / 2:
                    start = min_index - SEARCH_WINDOW_WIDTH + end_dist
                    end = len(track_error)
                else:
                    start = min_index - SEARCH_WINDOW_WIDTH / 2
                    end = min_index + SEARCH_WINDOW_WIDTH / 2
                # calculate intersection in the search window
                intersect = const[i] - vy[i] * des_lat[start:end] + vx[i] * des_lon[start:end]
                # get the original index of the intersection point
                index = np.argmin(np.abs(intersect)) + start
            # add distance to the result
            track_error[i] = dist[index]
            orientation_error[i] = desired_traj.heading[index] - actual_traj.heading[i]
            if 360.0 - abs(orientation_error[i]) < 10:
                or_error_a = desired_traj.heading[index] + 360.0 - actual_traj.heading[i]
                or_error_b = desired_traj.heading[index] - 360.0 - actual_traj.heading[i]
                orientation_error[i] = or_error_a if abs(or_error_a) < abs(or_error_b) else or_error_b
        return track_error, orientation_error

    @staticmethod
    def calc_color_map(cross_error):
        ratio = 2 * (cross_error - np.min(cross_error)) / (np.max(cross_error) - np.min(cross_error))
        temp = np.zeros(ratio.shape)
        color_map = np.zeros((ratio.size, 4))
        b = np.array((1 - ratio))
        color_map[:, 2] = np.where(b < 0, temp, b)
        r = np.array((ratio - 1))
        color_map[:, 0] = np.where(r < 0, temp, r)
        color_map[:, 1] = 1. - color_map[:, 0] - color_map[:, 2]
        color_map[:, 3] = 1.
        return color_map


class Calc(iCalc):
    dep = 'calc_rec_gps', 'calc_debug_es_gps'

    def check(self):
        rec_traj = self.modules.fill(self.dep[0])
        meas_traj = self.modules.fill(self.dep[1])
        return rec_traj, meas_traj

    def fill(self, rec_traj, meas_traj):
        track_error = TrackErrors(rec_traj, meas_traj)
        return track_error


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r'C:\KBData\Highway_Assist\measurements\boxberg\TMC_measurement426.MF4'
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    track_errors = manager_modules.calc('calc_track_errors@ad.fill', manager)

    import matplotlib.pyplot as plt
    plt.plot(track_errors.cross_error)
    plt.show()
