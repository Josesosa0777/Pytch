# -*- dataeval: init -*-

import interface


class cFill(interface.iGPSTrajectoryFill):
    dep = 'calc_track_errors',

    def fill(self):
        track_error = self.modules.fill(self.dep[0])
        traj = {}
        traj['longitude'] = track_error.lon
        traj['latitude'] = track_error.lat
        traj['type'] = self.get_grouptype('DIFF_TRAJ')
        traj['color'] = track_error.colors
        return track_error.time, traj
