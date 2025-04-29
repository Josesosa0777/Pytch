# -*- dataeval: init -*-

import interface


class cFill(interface.iGPSTrajectoryFill):
    dep = 'calc_maus_gps',

    def fill(self):
        maus_gps_data = self.modules.fill(self.dep[0])
        traj = {}
        traj['longitude'] = maus_gps_data.lon
        traj['latitude'] = maus_gps_data.lat
        traj['type'] = self.get_grouptype('MEAS_TRAJ')
        return maus_gps_data.time, traj
