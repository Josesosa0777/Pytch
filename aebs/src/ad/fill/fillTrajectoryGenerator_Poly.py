# -*- dataeval: init -*-

import interface


class cFill(interface.iTrajectoryFill):
    dep = 'calc_trajectory_generator_poly',

    def fill(self):
        time = None
        traj_data = []
        for trajectory_data in self.modules.fill(self.dep[0]):
            if time is None:
                time = trajectory_data.time
            traj = dict()
            traj['b0'] = trajectory_data.b0
            traj['b1'] = trajectory_data.b1
            traj['b2'] = trajectory_data.b2
            traj['b3'] = trajectory_data.b3

            traj['c0'] = trajectory_data.c0
            traj['c1'] = trajectory_data.c1
            traj['c2'] = trajectory_data.c2
            traj['c3'] = trajectory_data.c3
            traj['c4'] = trajectory_data.c4

            traj['valid_dist_max'] = trajectory_data.valid_dist_max
            traj['valid_dist_min'] = trajectory_data.valid_dist_min
            traj['valid_time_max'] = trajectory_data.valid_time_max
            traj['valid_time_min'] = trajectory_data.valid_time_min

            traj['func'] = trajectory_data.func
            traj['mask_s'] = trajectory_data.mask_s

            traj['type'] = self.get_grouptype(trajectory_data.group_type)

            traj['name'] = trajectory_data.name
            traj_data += [traj]
        return time, traj_data
