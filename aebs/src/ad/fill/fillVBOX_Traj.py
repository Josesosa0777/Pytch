# -*- dataeval: init -*-

import interface


class cFill(interface.iGPSTrajectoryFill):
    dep = 'calc_vbox_gps',

    def fill(self):
        vbox_gps_data = self.modules.fill(self.dep[0])
        traj = {}
        traj['longitude'] = vbox_gps_data.lon
        traj['latitude'] = vbox_gps_data.lat
        traj['type'] = self.get_grouptype('MEAS_TRAJ')
        return vbox_gps_data.time, traj
