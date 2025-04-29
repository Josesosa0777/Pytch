import grouptypes as gtps
from datavis.GroupParam import cGroupParam as Param
from config.parameter import GroupParams

fill_prj = '@ad.fill'

Groups = GroupParams({
    'fillVBOX_Traj%s' % fill_prj: {
        'VBOX_GPS_Traj': Param(gtps.MEAS_TRAJ, '1', False, False)
    },
    'fillMaus_Traj%s' % fill_prj: {
        'Maus_GPS_Traj': Param(gtps.MEAS_TRAJ, '1', False, False)
    },
    'fillEsGps%s' % fill_prj: {
        'ES_GPS_Traj': Param(gtps.MEAS_TRAJ, '1', False, False)
    },
    'fillRecGps%s' % fill_prj: {
        'Recorded_GPS_Traj': Param(gtps.REC_TRAJ, '2', False, False)
    },
    'fillTrackError%s' % fill_prj: {
        'Track error': Param(gtps.DIFF_TRAJ, '3', False, False)
    },
    'fillTrajectoryGenerator_Poly%s' % fill_prj: {
        'Trajectory_Generator_poly': Param(gtps.TRAJ_GEN_POLY, '4', False, False),
        'Trajectory_Generator_poly_velocity': Param(gtps.TRAJ_GEN_POLY_VEL, '5', False, False)
    },
    'fillTrajectoryGenerator_Bezier%s' % fill_prj: {
        'Trajectory_Generator_bezier': Param(gtps.TRAJ_GEN_BEZIER, '6', False, False),
        'Trajectory_Generator_bezier_velocity': Param(gtps.TRAJ_GEN_BEZIER_VEL, '7', False, False)
    },
})
"""type : GroupParams
{StatusName<str>: {GroupName<str> : GroupParam<Param>}, }"""
