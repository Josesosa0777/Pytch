# -*- dataeval: init -*-

import interface


class cFill(interface.iGPSTrajectoryFill):
    dep = 'calc_rec_gps',

    def fill(self):
        test_gps_data = self.modules.fill(self.dep[0])
        traj = {}
        traj['longitude'] = test_gps_data.lon
        traj['latitude'] = test_gps_data.lat
        traj['type'] = self.get_grouptype('REC_TRAJ')
        return test_gps_data.time, traj
