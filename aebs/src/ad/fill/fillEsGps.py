# -*- dataeval: init -*-

import interface


class cFill(interface.iGPSTrajectoryFill):
    dep = 'calc_debug_es_gps',

    def fill(self):
        es_gps_data = self.modules.fill(self.dep[0])
        traj = {}
        traj['longitude'] = es_gps_data.lon
        traj['latitude'] = es_gps_data.lat
        traj['type'] = self.get_grouptype('MEAS_TRAJ')
        # convert the heading values to the mapnavigator's coordinate frame
        traj['heading'] = (360 - es_gps_data.heading + 90) % 360
        return es_gps_data.time, traj
