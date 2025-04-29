# -*- dataeval: init -*-

import interface


class cFill(interface.iTrajectoryFill):
    dep = 'calc_trajectory_generator_bezier',

    def fill(self):
        time = None
        traj_data = []
        for trajectory_data in self.modules.fill(self.dep[0]):
            if time is None:
                time = trajectory_data.time
            traj = dict()
            traj['x_pts'] = trajectory_data.x_pts
            traj['y_pts'] = trajectory_data.y_pts
            traj['yx_start'] = trajectory_data.yx_start
            traj['yx_num'] = trajectory_data.yx_num

            traj['st_coeffs'] = trajectory_data.st_coeffs
            traj['st_bounds'] = trajectory_data.st_bounds
            traj['st_num'] = trajectory_data.st_num

            traj['func'] = trajectory_data.func
            traj['lateral'] = trajectory_data.lateral

            traj['type'] = self.get_grouptype(trajectory_data.group_type)

            traj['name'] = trajectory_data.name
            traj_data += [traj]
        return time, traj_data
