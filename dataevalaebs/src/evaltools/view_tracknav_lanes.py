# -*- dataeval: init -*-

"""
Interactive bird-eye view visualizer (TrackNavigator) with object and lane
visualization capabilities.
The selected parameter determines the lane(s) to be shown. Select "NO_LANES"
to disable this functionality. Object visualization can be turned on/off
on-line, using key presses or GroupNavigator.
"""

import numpy

import datavis
import measparser
import interface
import pathpred.pathpredictor

Lines = [{
						 'CurveLane': ('RadarFC', 'evi.General_TC.kapCurvTraj'),
						 'CurveEgo' : ('RadarFC', 'dcp.kapCourse')
				 }]

ROADRMOLanePolyA0 = 1.5
ROADRSOLanePolyA0 = 0.9
AC100LanePolyA0 = ROADRMOLanePolyA0

RMS_MAX = 10.0

init_params = {
		"NO_LANES"                                      : dict(lanes = dict()),
		"NO_LANES_ACC_PED_VEW"                          : dict(lanes = dict(ACC_PED_VIEW = True)),
		"VBOX"                                          : dict(lanes = dict(vbox = True, )),
		"SCAM_CVR3_VBOX"                                : dict(lanes = dict(cvr3 = True, flc20 = True, vbox = True)),
		"FLC20"                                         : dict(lanes = dict(flc20 = True)),
		"FLC25_CAN"                                     : dict(lanes = dict(flc25_can = True)),
		"FLC25_ABD_LANE"                                : dict(lanes = dict(flc25_abd_lane = True)),
    "FLC25_LD_LANE"                                : dict(lanes = dict(flc25_ld_lane = True)),
		"FLC25_POINT_CLOUD"                             : dict(lanes = dict(flc25_point_cloud = True)),
		"FLC20_FLR20LF_VBOX"                            : dict(lanes = dict(flc20 = True, flr20lf = True, vbox = True)),
		"FLC20_FLR20LF_FLR20RO_VBOX"                    :
				dict(lanes = dict(flc20 = True, flr20lf = True, flr20ro = True, vbox = True)),
		"FLC20_FLR20LF"                                 : dict(lanes = dict(flc20 = True, flr20lf = True)),
		"FLC20_FLR20LF_FLR20RO"                         :
				dict(lanes = dict(flc20 = True, flr20lf = True, flr20ro = True)),
		"FLC25_CAN(R)_ABDLANE(G)"                : dict(lanes = dict(flc25_can = True, flc25_abd_lane = True)),
		"FLC25_CAN(R)_FLC20(G)"                : dict(lanes = dict(flc25_can = True, flc20 = True)),
		"FLC25_CAN(R)_POINTCLOUD(B)"             : dict(lanes = dict(flc25_can = True, flc25_point_cloud = True)),
		"FLC25_ABDLANE(G)_POINTCLOUD(B)"        : dict(
						lanes = dict(flc25_abd_lane = True, flc25_point_cloud = True)),
		"FLC25_CAN(R)_ABDLANE(G)_POINTCLOUD(B": dict(
						lanes = dict(flc25_can = True, flc25_abd_lane = True, flc25_point_cloud = True)),
    "FLR25_CURVATOR"                      : dict(lanes = dict(flr25_curvator = True)),
		"FLR25_ROAD_ESTIMATION"               : dict(lanes = dict(flr25_roadestimation = True)),
		"FLR25_CURVATOR_ROAD_ESTIMATION"      : dict(lanes = dict(flr25_curvator = True, flr25_roadestimation = True)),
    "FLC25_PAEBS_EGO_PATH_PREDICTION"           : dict(lanes = dict(flc25_ego_pathpred = True)),
    "FLC25_AOA_LANE"                      : dict(lanes = dict(flc25_aoa_lane = True)),

}


def polyClothoid(A0, A1, A2, A3, Distance):
		# f(dx) = 1/6 * a3 * x^3 + 1/2 * a2 * x^2 + tan(a1) * x + a0
		x = numpy.linspace(0.0, Distance, num = 20)
		y = numpy.empty_like(x)
		y[0] = A0  # avoid computing 0*inf at x=0
		y[1:] = (A3 / 6.0) * numpy.power(x[1:], 3) + (A2 / 2.0) * numpy.power(x[1:], 2) + numpy.tan(A1) * x[1:] + A0
		return y, x


def pointCloud(linex, liney):
		# Extract y, x
		return liney, linex


def calcPredPath(ego_motion, flc20_lines):
		# calculation
		pp = pathpred.pathpredictor.PathPredictor(debug_active = True)
		flc20_lines = flc20_lines.rescale(ego_motion.time)  # TODO: avoid
		line_f, debug = pp.predict(ego_motion, flc20_lines)
		# make viewrange Dataset-compatible
		viewrange_f_x = numpy.vstack((debug.viewrange_f, debug.viewrange_f)).T
		viewrange_f_y = numpy.empty_like(viewrange_f_x)
		viewrange_f_y[:, 0] = -1000.0  # arbitrary small number
		viewrange_f_y[:, 1] = 1000.0  # arbitrary large number
		return line_f.time, line_f, debug.dx_m, debug.dy_m, debug.dy_l, debug.dy_f, viewrange_f_x, viewrange_f_y, \
           debug.sliced_fused_path


class View(interface.iView):
		TRACKNAV_PARAMS = {}

		def init(self, lanes):
				self.lanes = lanes
				optdep = set()
				if self.lanes.get('flc25_ego_pathpred'):
						optdep.add('calc_lanes_flc25_paebs_ego_path_prediction@aebs.fill')
				if self.lanes.get('flr20lf'):
						optdep.add('calc_flr20_pathpred_lf@aebs.fill')
				if self.lanes.get('flr20ro'):
						optdep.add('calc_flr20_pathpred_ro@aebs.fill')
				if self.lanes.get('flc20'):
						optdep.add('calc_flc20_lanes@aebs.fill')
				if self.lanes.get('flc25_can'):
						optdep.add('calc_lanes-flc25@aebs.fill')
				if self.lanes.get('flc25_abd_lane'):
						optdep.add('calc_lanes_flc25_abd@aebs.fill')
				if self.lanes.get('flc25_ld_lane'):
						optdep.add('calc_lanes_flc25_ld@aebs.fill')
				if self.lanes.get('flc25_point_cloud'):
						optdep.add('fill_flc25_polylines@aebs.fill')
				if self.lanes.get('flr20flc20pp'):
						optdep.add('calc_flc20_lanes@aebs.fill')
						optdep.add('calc_flr20_egomotion@aebs.fill')
				if self.lanes.get('vbox'):
						optdep.add('calc_vbox_egopath@aebs.fill')
				if self.lanes.get("flr25_curvator"):
						optdep.add('calc_lanes_flr25_curvator@aebs.fill')
				if self.lanes.get("flr25_roadestimation"):
						optdep.add('calc_lanes_flr25_roadestimation@aebs.fill')
				if self.lanes.get("flc25_aoa_lane"):
						optdep.add('calc_lanes_flc25_aoa@aebs.fill')
				if self.lanes.get('ACC_PED_VIEW'):
						self.TRACKNAV_PARAMS["LengthMin"] = 0.0
						self.TRACKNAV_PARAMS["LengthMax"] = 20.0
						self.TRACKNAV_PARAMS["WidthMin"] = -12
						self.TRACKNAV_PARAMS["WidthMax"] = 12
				self.optdep = tuple(optdep)
				return

		def view(self):
				if 'SLR25_RFB' in self.view_angles or any([bool(True) if 'SLR25_RFB' in modules else bool(False) for modules in list(self.modules._selects)]):
					TN = datavis.cTrackNavigator(LengthMin=-35.0, LengthMax=11.0, WidthMin=-7.0, WidthMax=7.0,
												 **self.TRACKNAV_PARAMS)
				elif 'SLR25_Front' in self.view_angles or any([bool(True) if 'SLR25_Front' in modules else bool(False) for modules in list(self.modules._selects)]):
					TN = datavis.cTrackNavigator(LengthMin=-1.0, LengthMax=8.0, WidthMin=-10.0, WidthMax=10.0,
												 **self.TRACKNAV_PARAMS)
				else:
					TN = datavis.cTrackNavigator(**self.TRACKNAV_PARAMS)
				TN.addGroups(interface.Groups)
				TN.addStyles(interface.Legends)
				TN.AddSynchronizer(interface.Sync)

				for GroupName, (LeftAngle, RightAngle, kwargs) in interface.ViewAngles.iteritems():
						TN.setViewAngle(LeftAngle, RightAngle, GroupName, **kwargs)
				if self.lanes.get("flc25_ego_pathpred"):
						if 'calc_lanes_flc25_paebs_ego_path_prediction@aebs.fill' in self.passed_optdep:

								flr25_line = self.modules.fill('calc_lanes_flc25_paebs_ego_path_prediction@aebs.fill')
								flr25_time = flr25_line.time
								# add as a curve
								Track = TN.addTrack('FLC25 PAEBS ego path prediction track ', flr25_time, color = 'b')
								FuncName = Track.addFunc(polyClothoid)
								Track.addParam(FuncName, 'A0', flr25_time, flr25_line.a0)
								Track.addParam(FuncName, 'A1', flr25_time, flr25_line.a1)
								Track.addParam(FuncName, 'A2', flr25_time, flr25_line.a2)
								Track.addParam(FuncName, 'A3', flr25_time, flr25_line.a3)

								Track.addParam(FuncName, 'Distance', flr25_time, 100.0 * numpy.ones_like(flr25_time))
						else:
								self.logger.warning('FLC25 PAEBS ego path prediction lane cannot be visualized')
				if self.lanes.get("flr25_curvator"):
						if 'calc_lanes_flr25_curvator@aebs.fill' in self.passed_optdep:

								flr25_line = self.modules.fill('calc_lanes_flr25_curvator@aebs.fill')
								flr25_time = flr25_line.time
								# add as a curve
								Track = TN.addTrack('FLR25 Curvator prediction track ', flr25_time, color = 'b')
								FuncName = Track.addFunc(polyClothoid)
								Track.addParam(FuncName, 'A0', flr25_time, flr25_line.a0)
								Track.addParam(FuncName, 'A1', flr25_time, flr25_line.a1)
								Track.addParam(FuncName, 'A2', flr25_time, flr25_line.a2)
								Track.addParam(FuncName, 'A3', flr25_time, flr25_line.a3)
								Track.addParam(FuncName, 'Distance', flr25_time, 100.0 * numpy.ones_like(flr25_time))
						else:
								self.logger.warning('FLR25 Curvator lane cannot be visualized')
				if self.lanes.get("flr25_roadestimation"):

						if 'calc_lanes_flr25_roadestimation@aebs.fill' in self.passed_optdep:

								flr25_line = self.modules.fill('calc_lanes_flr25_roadestimation@aebs.fill')
								flr25_time = flr25_line.time
								# add as a curve
								Track = TN.addTrack('FLR25 Road Estimation track ', flr25_time, color = 'y')
								FuncName = Track.addFunc(polyClothoid)
								Track.addParam(FuncName, 'A0', flr25_time, flr25_line.a0)
								Track.addParam(FuncName, 'A1', flr25_time, flr25_line.a1)
								Track.addParam(FuncName, 'A2', flr25_time, flr25_line.a2)
								Track.addParam(FuncName, 'A3', flr25_time, flr25_line.a3)
								Track.addParam(FuncName, 'Distance', flr25_time, 100.0 * numpy.ones_like(flr25_time))
						else:
								self.logger.warning('FLR25 Road Estimation lane cannot be visualized')
				if self.lanes.get('cvr3'):
						Tracks = []
						try:
								Params = interface.Source.selectSignalGroup(Lines)
						except measparser.signalgroup.SignalGroupError, Error:
								self.logger.warning('CVR3 lanes are not added to the TrackNavigator:\n%s' % Error.message)
						else:
								Tracks.append(('CVR3_SIT_MO', 'CurveLane', (
										('y', (-ROADRMOLanePolyA0, ROADRMOLanePolyA0), 200.0),
										('y', (-(ROADRMOLanePolyA0 + 2 * ROADRMOLanePolyA0), (ROADRMOLanePolyA0 + 2 * ROADRMOLanePolyA0)),
										 200.0),
										('y', (-(ROADRMOLanePolyA0 + 4 * ROADRMOLanePolyA0), (ROADRMOLanePolyA0 + 4 * ROADRMOLanePolyA0)),
										 200.0))))

						for TrackName, CurveAlias, Lanes in Tracks:
								if isinstance(CurveAlias, str):
										TrackTime, Curve = interface.Source.getSignalFromSignalGroup(Params, CurveAlias)
								else:
										TrackTime, Curve = CurveAlias
								for Color, Aliases, Dist in Lanes:
										for Alias in Aliases:
												Track = TN.addTrack(TrackName, TrackTime, color = Color)
												if isinstance(Alias, str):
														Time, Value = interface.Source.getSignalFromSignalGroup(Params, Alias)
												else:
														Time = TrackTime
														Value = Alias * numpy.ones_like(TrackTime)
												FuncName = Track.addFunc(polyClothoid)
												Track.addParam(FuncName, 'A0', Time, Value)
												Track.addParam(FuncName, 'A1', TrackTime, numpy.zeros_like(TrackTime))
												Track.addParam(FuncName, 'A2', TrackTime, Curve)
												Track.addParam(FuncName, 'A3', TrackTime, numpy.zeros_like(TrackTime))
												Track.addParam(FuncName, 'Distance', TrackTime, Dist * numpy.ones_like(TrackTime))
				if self.lanes.get('flc20'):
						if 'calc_flc20_lanes@aebs.fill' in self.passed_optdep:
								flc20_lines = self.modules.fill('calc_flc20_lanes@aebs.fill')
								flc20_time = flc20_lines.time
								# right
								Track = TN.addTrack('FLC20 lanes (Right)', flc20_time, color = 'g')
								FuncName = Track.addFunc(polyClothoid)
								Track.addParam(FuncName, 'A0', flc20_time, flc20_lines.right_line.a0)
								Track.addParam(FuncName, 'A1', flc20_time, flc20_lines.right_line.a1)
								Track.addParam(FuncName, 'A2', flc20_time, flc20_lines.right_line.a2)
								Track.addParam(FuncName, 'A3', flc20_time, flc20_lines.right_line.a3)
								Track.addParam(FuncName, 'Distance', flc20_time, flc20_lines.right_line.view_range)
								# left
								Track = TN.addTrack('FLC20 lanes (Left)', flc20_time, color = 'g')
								FuncName = Track.addFunc(polyClothoid)
								Track.addParam(FuncName, 'A0', flc20_time, flc20_lines.left_line.a0)
								Track.addParam(FuncName, 'A1', flc20_time, flc20_lines.left_line.a1)
								Track.addParam(FuncName, 'A2', flc20_time, flc20_lines.left_line.a2)
								Track.addParam(FuncName, 'A3', flc20_time, flc20_lines.left_line.a3)
								Track.addParam(FuncName, 'Distance', flc20_time, flc20_lines.left_line.view_range)
								# right right
								Track = TN.addTrack('FLC20 lanes (Right Right)', flc20_time, color = 'g')
								FuncName = Track.addFunc(polyClothoid)
								Track.addParam(FuncName, 'A0', flc20_time, flc20_lines.right_right_line.a0)
								Track.addParam(FuncName, 'A1', flc20_time, flc20_lines.right_right_line.a1)
								Track.addParam(FuncName, 'A2', flc20_time, flc20_lines.right_right_line.a2)
								Track.addParam(FuncName, 'A3', flc20_time, flc20_lines.right_right_line.a3)
								Track.addParam(FuncName, 'Distance', flc20_time, flc20_lines.right_right_line.view_range)
								# left left
								Track = TN.addTrack('FLC20 lanes (Left Left)', flc20_time, color = 'g')
								FuncName = Track.addFunc(polyClothoid)
								Track.addParam(FuncName, 'A0', flc20_time, flc20_lines.left_left_line.a0)
								Track.addParam(FuncName, 'A1', flc20_time, flc20_lines.left_left_line.a1)
								Track.addParam(FuncName, 'A2', flc20_time, flc20_lines.left_left_line.a2)
								Track.addParam(FuncName, 'A3', flc20_time, flc20_lines.left_left_line.a3)
								Track.addParam(FuncName, 'Distance', flc20_time, flc20_lines.left_left_line.view_range)
						else:
								self.logger.warning('FLC20 lanes cannot be visualized')
				if self.lanes.get('flc25_can'):
						if 'calc_lanes-flc25@aebs.fill' in self.passed_optdep:
								flc25_lines = self.modules.fill('calc_lanes-flc25@aebs.fill')
								flc25_time = flc25_lines.time
								# right
								Track = TN.addTrack('FLC25 CAN lanes (Right)', flc25_time, color = 'r')
								FuncName = Track.addFunc(polyClothoid)
								Track.addParam(FuncName, 'A0', flc25_time, flc25_lines.right_line.a0)
								Track.addParam(FuncName, 'A1', flc25_time, flc25_lines.right_line.a1)
								Track.addParam(FuncName, 'A2', flc25_time, flc25_lines.right_line.a2)
								Track.addParam(FuncName, 'A3', flc25_time, flc25_lines.right_line.a3)
								Track.addParam(FuncName, 'Distance', flc25_time, flc25_lines.right_line.view_range)
								# left
								Track = TN.addTrack('FLC25 CAN lanes (Left)', flc25_time, color = 'r')
								FuncName = Track.addFunc(polyClothoid)
								Track.addParam(FuncName, 'A0', flc25_time, flc25_lines.left_line.a0)
								Track.addParam(FuncName, 'A1', flc25_time, flc25_lines.left_line.a1)
								Track.addParam(FuncName, 'A2', flc25_time, flc25_lines.left_line.a2)
								Track.addParam(FuncName, 'A3', flc25_time, flc25_lines.left_line.a3)
								Track.addParam(FuncName, 'Distance', flc25_time, flc25_lines.left_line.view_range)
								# right right
								Track = TN.addTrack('FLC25 CAN lanes (Right Right)', flc25_time, color = 'r')
								FuncName = Track.addFunc(polyClothoid)
								Track.addParam(FuncName, 'A0', flc25_time, flc25_lines.right_right_line.a0)
								Track.addParam(FuncName, 'A1', flc25_time, flc25_lines.right_right_line.a1)
								Track.addParam(FuncName, 'A2', flc25_time, flc25_lines.right_right_line.a2)
								Track.addParam(FuncName, 'A3', flc25_time, flc25_lines.right_right_line.a3)
								Track.addParam(FuncName, 'Distance', flc25_time, flc25_lines.right_right_line.view_range)
								# left left
								Track = TN.addTrack('FLC25 CAN lanes (Left Left)', flc25_time, color = 'r')
								FuncName = Track.addFunc(polyClothoid)
								Track.addParam(FuncName, 'A0', flc25_time, flc25_lines.left_left_line.a0)
								Track.addParam(FuncName, 'A1', flc25_time, flc25_lines.left_left_line.a1)
								Track.addParam(FuncName, 'A2', flc25_time, flc25_lines.left_left_line.a2)
								Track.addParam(FuncName, 'A3', flc25_time, flc25_lines.left_left_line.a3)
								Track.addParam(FuncName, 'Distance', flc25_time, flc25_lines.left_left_line.view_range)
						else:
								self.logger.warning('FLC25 CAN lanes cannot be visualized')
				if self.lanes.get('flc25_abd_lane'):
						if 'calc_lanes_flc25_abd@aebs.fill' in self.passed_optdep:
								flc25_lines = self.modules.fill('calc_lanes_flc25_abd@aebs.fill')
								flc25_time = flc25_lines.time
								# right
								Track = TN.addTrack('FLC25 ABD lanes (Right)', flc25_time, color = 'g')
								FuncName = Track.addFunc(polyClothoid)
								Track.addParam(FuncName, 'A0', flc25_time, flc25_lines.right_line.a0)
								Track.addParam(FuncName, 'A1', flc25_time, flc25_lines.right_line.a1)
								Track.addParam(FuncName, 'A2', flc25_time, flc25_lines.right_line.a2)
								Track.addParam(FuncName, 'A3', flc25_time, flc25_lines.right_line.a3)
								Track.addParam(FuncName, 'Distance', flc25_time, flc25_lines.right_line.view_range)
								# left
								Track = TN.addTrack('FLC25 ABD lanes (Left)', flc25_time, color = 'g')
								FuncName = Track.addFunc(polyClothoid)
								Track.addParam(FuncName, 'A0', flc25_time, flc25_lines.left_line.a0)
								Track.addParam(FuncName, 'A1', flc25_time, flc25_lines.left_line.a1)
								Track.addParam(FuncName, 'A2', flc25_time, flc25_lines.left_line.a2)
								Track.addParam(FuncName, 'A3', flc25_time, flc25_lines.left_line.a3)
								Track.addParam(FuncName, 'Distance', flc25_time, flc25_lines.left_line.view_range)
								# right right
								Track = TN.addTrack('FLC25 ABD lanes (Right Right)', flc25_time, color = 'g')
								FuncName = Track.addFunc(polyClothoid)
								Track.addParam(FuncName, 'A0', flc25_time, flc25_lines.right_right_line.a0)
								Track.addParam(FuncName, 'A1', flc25_time, flc25_lines.right_right_line.a1)
								Track.addParam(FuncName, 'A2', flc25_time, flc25_lines.right_right_line.a2)
								Track.addParam(FuncName, 'A3', flc25_time, flc25_lines.right_right_line.a3)
								Track.addParam(FuncName, 'Distance', flc25_time, flc25_lines.right_right_line.view_range)
								# left left
								Track = TN.addTrack('FLC25 ABD lanes (Left Left)', flc25_time, color = 'g')
								FuncName = Track.addFunc(polyClothoid)
								Track.addParam(FuncName, 'A0', flc25_time, flc25_lines.left_left_line.a0)
								Track.addParam(FuncName, 'A1', flc25_time, flc25_lines.left_left_line.a1)
								Track.addParam(FuncName, 'A2', flc25_time, flc25_lines.left_left_line.a2)
								Track.addParam(FuncName, 'A3', flc25_time, flc25_lines.left_left_line.a3)
								Track.addParam(FuncName, 'Distance', flc25_time, flc25_lines.left_left_line.view_range)
						else:
								self.logger.warning('FLC25 ABD lanes cannot be visualized')
				if self.lanes.get('flc25_ld_lane'):
						if 'calc_lanes_flc25_ld@aebs.fill' in self.passed_optdep:
								flc25_lines = self.modules.fill('calc_lanes_flc25_ld@aebs.fill')
								flc25_time = flc25_lines.time
								# right
								Track = TN.addTrack('FLC25 LD lanes (Right)', flc25_time, color = 'r')
								FuncName = Track.addFunc(polyClothoid)
								Track.addParam(FuncName, 'A0', flc25_time, flc25_lines.right_line.a0)
								Track.addParam(FuncName, 'A1', flc25_time, flc25_lines.right_line.a1)
								Track.addParam(FuncName, 'A2', flc25_time, flc25_lines.right_line.a2)
								Track.addParam(FuncName, 'A3', flc25_time, flc25_lines.right_line.a3)
								Track.addParam(FuncName, 'Distance', flc25_time, flc25_lines.right_line.view_range)
								# left
								Track = TN.addTrack('FLC25 LD lanes (Left)', flc25_time, color = 'r')
								FuncName = Track.addFunc(polyClothoid)
								Track.addParam(FuncName, 'A0', flc25_time, flc25_lines.left_line.a0)
								Track.addParam(FuncName, 'A1', flc25_time, flc25_lines.left_line.a1)
								Track.addParam(FuncName, 'A2', flc25_time, flc25_lines.left_line.a2)
								Track.addParam(FuncName, 'A3', flc25_time, flc25_lines.left_line.a3)
								Track.addParam(FuncName, 'Distance', flc25_time, flc25_lines.left_line.view_range)
								# right right
								Track = TN.addTrack('FLC25 LD lanes (Right Right)', flc25_time, color = 'r')
								FuncName = Track.addFunc(polyClothoid)
								Track.addParam(FuncName, 'A0', flc25_time, flc25_lines.right_right_line.a0)
								Track.addParam(FuncName, 'A1', flc25_time, flc25_lines.right_right_line.a1)
								Track.addParam(FuncName, 'A2', flc25_time, flc25_lines.right_right_line.a2)
								Track.addParam(FuncName, 'A3', flc25_time, flc25_lines.right_right_line.a3)
								Track.addParam(FuncName, 'Distance', flc25_time, flc25_lines.right_right_line.view_range)
								# left left
								Track = TN.addTrack('FLC25 LD lanes (Left Left)', flc25_time, color = 'r')
								FuncName = Track.addFunc(polyClothoid)
								Track.addParam(FuncName, 'A0', flc25_time, flc25_lines.left_left_line.a0)
								Track.addParam(FuncName, 'A1', flc25_time, flc25_lines.left_left_line.a1)
								Track.addParam(FuncName, 'A2', flc25_time, flc25_lines.left_left_line.a2)
								Track.addParam(FuncName, 'A3', flc25_time, flc25_lines.left_left_line.a3)
								Track.addParam(FuncName, 'Distance', flc25_time, flc25_lines.left_left_line.view_range)
						else:
								self.logger.warning('FLC25 LD lanes cannot be visualized')
				if self.lanes.get('flc25_point_cloud'):
						if 'fill_flc25_polylines@aebs.fill' in self.passed_optdep:
								lines, common_time = self.modules.fill('fill_flc25_polylines@aebs.fill')
								flc25_pc_time = common_time
								# ego-center
								Track = TN.addTrack('FLC25 POINT CLOUD lanes - ego-center', flc25_pc_time, color = 'y')
								FuncName = Track.addFunc(pointCloud)
								Track.addParam(FuncName, 'linex', flc25_pc_time, lines['ego_centerLine'][:, 0])
								Track.addParam(FuncName, 'liney', flc25_pc_time, lines['ego_centerLine'][:, 1])
								# ego-left
								Track = TN.addTrack('FLC25 POINT CLOUD lanes - ego-left', flc25_pc_time, color = 'b')
								FuncName = Track.addFunc(pointCloud)
								Track.addParam(FuncName, 'linex', flc25_pc_time, lines['ego_leftLine'][:, 0])
								Track.addParam(FuncName, 'liney', flc25_pc_time, lines['ego_leftLine'][:, 1])
								# ego-right
								Track = TN.addTrack('FLC25 POINT CLOUD lanes - ego-right', flc25_pc_time, color = 'b')
								FuncName = Track.addFunc(pointCloud)
								Track.addParam(FuncName, 'linex', flc25_pc_time, lines['ego_rightLine'][:, 0])
								Track.addParam(FuncName, 'liney', flc25_pc_time, lines['ego_rightLine'][:, 1])
								# egoleft-left
								Track = TN.addTrack('FLC25 POINT CLOUD lanes - egoleft-left', flc25_pc_time, color = 'b')
								FuncName = Track.addFunc(pointCloud)
								Track.addParam(FuncName, 'linex', flc25_pc_time, lines['egoleft_leftLine'][:, 0])
								Track.addParam(FuncName, 'liney', flc25_pc_time, lines['egoleft_leftLine'][:, 1])
								# egoleft- right
								Track = TN.addTrack('FLC25 POINT CLOUD lanes - egoleft- right', flc25_pc_time, color = 'b')
								FuncName = Track.addFunc(pointCloud)
								Track.addParam(FuncName, 'linex', flc25_pc_time, lines['egoleft_rightLine'][:, 0])
								Track.addParam(FuncName, 'liney', flc25_pc_time, lines['egoleft_rightLine'][:, 1])
								# egoleftleft-left
								Track = TN.addTrack('FLC25 POINT CLOUD lanes - egoleftleft-left', flc25_pc_time, color = 'b')
								FuncName = Track.addFunc(pointCloud)
								Track.addParam(FuncName, 'linex', flc25_pc_time, lines['egoleftleft_leftLine'][:, 0])
								Track.addParam(FuncName, 'liney', flc25_pc_time, lines['egoleftleft_leftLine'][:, 1])
								# egoleftleft- right
								Track = TN.addTrack('FLC25 POINT CLOUD lanes - egoleftleft- right', flc25_pc_time, color = 'b')
								FuncName = Track.addFunc(pointCloud)
								Track.addParam(FuncName, 'linex', flc25_pc_time, lines['egoleftleft_rightLine'][:, 0])
								Track.addParam(FuncName, 'liney', flc25_pc_time, lines['egoleftleft_rightLine'][:, 1])
								# egoright-left
								Track = TN.addTrack('FLC25 POINT CLOUD lanes - egoright-left', flc25_pc_time, color = 'b')
								FuncName = Track.addFunc(pointCloud)
								Track.addParam(FuncName, 'linex', flc25_pc_time, lines['egoright_leftLine'][:, 0])
								Track.addParam(FuncName, 'liney', flc25_pc_time, lines['egoright_leftLine'][:, 1])
								# egoright- right
								Track = TN.addTrack('FLC25 POINT CLOUD lanes - egoright- right', flc25_pc_time, color = 'b')
								FuncName = Track.addFunc(pointCloud)
								Track.addParam(FuncName, 'linex', flc25_pc_time, lines['egoright_rightLine'][:, 0])
								Track.addParam(FuncName, 'liney', flc25_pc_time, lines['egoright_rightLine'][:, 1])
								# egorightright-left
								Track = TN.addTrack('FLC25 POINT CLOUD lanes - egorightright-left', flc25_pc_time, color = 'b')
								FuncName = Track.addFunc(pointCloud)
								Track.addParam(FuncName, 'linex', flc25_pc_time, lines['egorightright_leftLine'][:, 0])
								Track.addParam(FuncName, 'liney', flc25_pc_time, lines['egorightright_leftLine'][:, 1])
								# egorightright- right
								Track = TN.addTrack('FLC25 POINT CLOUD lanes - egorightright- right', flc25_pc_time, color = 'b')
								FuncName = Track.addFunc(pointCloud)
								Track.addParam(FuncName, 'linex', flc25_pc_time, lines['egorightright_rightLine'][:, 0])
								Track.addParam(FuncName, 'liney', flc25_pc_time, lines['egorightright_rightLine'][:, 1])
						else:
								self.logger.warning('FLC25 POINT CLOUD lanes cannot be visualized')
				if self.lanes.get('flr20lf'):
						if 'calc_flr20_pathpred_lf@aebs.fill' in self.passed_optdep:
								flr20_line = self.modules.fill('calc_flr20_pathpred_lf@aebs.fill')
								flr20_time = flr20_line.time
								# add as a curve
								Track = TN.addTrack('FLR20 LF', flr20_time, color = 'b')
								FuncName = Track.addFunc(polyClothoid)
								Track.addParam(FuncName, 'A0', flr20_time, flr20_line.a0)
								Track.addParam(FuncName, 'A1', flr20_time, flr20_line.a1)
								Track.addParam(FuncName, 'A2', flr20_time, flr20_line.a2)
								Track.addParam(FuncName, 'A3', flr20_time, flr20_line.a3)
								Track.addParam(FuncName, 'Distance', flr20_time, 100.0 * numpy.ones_like(flr20_time))
						else:
								self.logger.warning('FLR20 lane fusion cannot be visualized')
				if self.lanes.get('flr20ro'):
						if 'calc_flr20_pathpred_ro@aebs.fill' in self.passed_optdep:
								flr20_line = self.modules.fill('calc_flr20_pathpred_ro@aebs.fill')
								flr20_time = flr20_line.time
								# add as a curve
								Track = TN.addTrack('FLR20 RO', flr20_time, color = 'r')
								FuncName = Track.addFunc(polyClothoid)
								Track.addParam(FuncName, 'A0', flr20_time, flr20_line.a0)
								Track.addParam(FuncName, 'A1', flr20_time, flr20_line.a1)
								Track.addParam(FuncName, 'A2', flr20_time, flr20_line.a2)
								Track.addParam(FuncName, 'A3', flr20_time, flr20_line.a3)
								Track.addParam(FuncName, 'Distance', flr20_time, 100.0 * numpy.ones_like(flr20_time))
						else:
								self.logger.warning('FLR20 radar-only path prediction cannot be visualized')
				if self.lanes.get('vbox'):
						modules = self.get_modules()
						if 'calc_vbox_egopath@aebs.fill' in self.passed_optdep:
								ego_path = modules.fill('calc_vbox_egopath@aebs.fill')
								ego_path = ego_path.rescale(numpy.arange(ego_path.time[0], ego_path.time[-1], 0.1))
								ego_path = ego_path._smooth()
								ego_path_sliced = ego_path.slice(0, 100)  # .rescale_slices(0.1)
								TN.addDataset(ego_path_sliced.time, ego_path_sliced.get_dxs(), ego_path_sliced.get_dys(),
															'Factual ego path (VBOX)', color = 'k')
						else:
								self.logger.warning('VBox based ego trajectory cannot be visualized')
				if self.lanes.get('flr20lf') and self.lanes.get('vbox'):
						if ('calc_flr20_pathpred_lf@aebs.fill' in self.passed_optdep) and (
										'calc_vbox_egopath@aebs.fill' in self.passed_optdep):
								flr20lf_slpath = flr20_line.rescale(ego_path.time).get_slicedpath(ego_path_sliced.get_dxs())
								# TN.addDataset(flr20lf_slpath.time, flr20lf_slpath.get_dxs(), flr20lf_slpath.get_dys(), 'FLR20 LF',
                # color='b')

								errors = ego_path_sliced.calc_rms_pos_errors(flr20lf_slpath)
								errors[errors > RMS_MAX] = RMS_MAX  # TODO: remove hack
								PN = datavis.cPlotNavigator("flr20lf and vbox")
								ax = PN.addAxis()
								PN.addSignal2Axis(ax, "rms", ego_path.time, errors)
								interface.Sync.addClient(PN)
						else:
								self.logger.warning('FLR20 lane fusion dataset cannot be visualized')

				for StatusName in interface.Objects.get_selected_by_parent(interface.iObjectFill):
						Time, Objects = interface.Objects.fill(StatusName)
						for Object in Objects:
								TN.addObject(Time, Object)
						if Objects:# If no object in environment
							if "signal_mapping" in Objects[0].keys():
								TN.addSignalMappingInfo(StatusName, Objects[0]["signal_mapping"])

				for StatusName in interface.Objects.get_selected_by_parent(interface.iAreaFill):
						Time, Areas = interface.Objects.fill(StatusName)
						for Area in Areas:
								TN.addShape(Time, Area)

				for StatusName in interface.Objects.get_selected_by_parent(interface.iTrajectoryFill):
						Time, Trajectories = interface.Objects.fill(StatusName)
						if isinstance(Trajectories, (tuple, list)):
								for Trajectory in Trajectories:
										TN.addTrajectory(Time, Trajectory)
						else:
								TN.addTrajectory(Time, Trajectories)

				if self.lanes.get('flr20flc20pp'):
						modules = self.get_modules()
						if ('calc_flr20_egomotion@aebs.fill' in self.passed_optdep) and (
										'calc_flc20_lanes@aebs.fill' in self.passed_optdep):
								ego_motion = modules.fill('calc_flr20_egomotion@aebs.fill')
								flc20_lines = modules.fill('calc_flc20_lanes@aebs.fill')
								PathTimePred, clotho, xEgoPred, yEgoPredDyn, yEgoPredRoad, yEgoPredFinal, viewrangeFinal_x, \
                viewrangeFinal_y, fused_pp_sliced = calcPredPath(
										ego_motion, flc20_lines)
								# add predicted paths as a series of positions
								TN.addDataset(PathTimePred, xEgoPred, yEgoPredDyn, 'Predicted ego path (dyn)', color = 'b')
								TN.addDataset(PathTimePred, xEgoPred, yEgoPredRoad, 'Predicted ego path (road)', color = 'g')
								TN.addDataset(PathTimePred, xEgoPred, yEgoPredFinal, 'Predicted ego path (final)', color = 'r')
								# add view range info of the final predicted path
								TN.addDataset(PathTimePred, viewrangeFinal_x, viewrangeFinal_y,
															'View range of predicted ego path (final)', color = 'r')
								# add final predicted path as a curve
								Track = TN.addTrack('Predicted ego path', PathTimePred, color = 'r')
								FuncName = Track.addFunc(polyClothoid)
								Track.addParam(FuncName, 'A0', PathTimePred, clotho.a0)
								Track.addParam(FuncName, 'A1', PathTimePred, clotho.a1)
								Track.addParam(FuncName, 'A2', PathTimePred, clotho.a2)
								Track.addParam(FuncName, 'A3', PathTimePred, clotho.a3)
								Track.addParam(FuncName, 'Distance', PathTimePred, 100.0 * numpy.ones_like(PathTimePred))
						else:
								self.logger.warning('KB lane fusion cannot be visualized')
				if self.lanes.get('flr20flc20pp') and self.lanes.get('vbox'):
						if ('calc_flr20_egomotion@aebs.fill' in self.passed_optdep) and (
										'calc_flc20_lanes@aebs.fill' in self.passed_optdep) and (
										'calc_vbox_egopath@aebs.fill' in self.passed_optdep):
								errors = ego_path_sliced.calc_rms_errors(fused_pp_sliced)
								errors[errors > RMS_MAX] = RMS_MAX  # TODO: remove hack
								PN = datavis.cPlotNavigator("flr20flc20pp and vbox")
								ax = PN.addAxis()
								PN.addSignal2Axis(ax, "rms", ego_path.time, errors)
								interface.Sync.addClient(PN)
						else:
								self.logger.warning('KB lane fusion error cannot be visualized')
				if self.lanes.get('flc25_aoa_lane'):
						if 'calc_lanes_flc25_aoa@aebs.fill' in self.passed_optdep:
								flc25_lines ,flc25_time= self.modules.fill('calc_lanes_flc25_aoa@aebs.fill')
								# flc25_time = flc25_lines.time
								# ego center
								Track = TN.addTrack('FLC25 AOA lanes (Ego(R))', flc25_time, color = 'r')
								FuncName = Track.addFunc(polyClothoid)
								Track.addParam(FuncName, 'A0', flc25_time, flc25_lines[0].a0)
								Track.addParam(FuncName, 'A1', flc25_time, flc25_lines[0].a1)
								Track.addParam(FuncName, 'A2', flc25_time, flc25_lines[0].a2)
								Track.addParam(FuncName, 'A3', flc25_time, flc25_lines[0].a3)
								Track.addParam(FuncName, 'Distance', flc25_time, flc25_lines[1].view_range)
								# left center
								Track = TN.addTrack('FLC25 AOA lanes (Ego Left(R))', flc25_time, color = 'r')
								FuncName = Track.addFunc(polyClothoid)
								Track.addParam(FuncName, 'A0', flc25_time, flc25_lines[1].a0)
								Track.addParam(FuncName, 'A1', flc25_time, flc25_lines[1].a1)
								Track.addParam(FuncName, 'A2', flc25_time, flc25_lines[1].a2)
								Track.addParam(FuncName, 'A3', flc25_time, flc25_lines[1].a3)
								Track.addParam(FuncName, 'Distance', flc25_time, flc25_lines[1].view_range)
								# right center
								Track = TN.addTrack('FLC25 AOA lanes (Ego Right(R))', flc25_time, color = 'r')
								FuncName = Track.addFunc(polyClothoid)
								Track.addParam(FuncName, 'A0', flc25_time, flc25_lines[2].a0)
								Track.addParam(FuncName, 'A1', flc25_time, flc25_lines[2].a1)
								Track.addParam(FuncName, 'A2', flc25_time, flc25_lines[2].a2)
								Track.addParam(FuncName, 'A3', flc25_time, flc25_lines[2].a3)
								Track.addParam(FuncName, 'Distance', flc25_time, flc25_lines[2].view_range)


								# left
								Track = TN.addTrack('FLC25 AOA lanes (Left(B))', flc25_time, color = 'b')
								FuncName = Track.addFunc(polyClothoid)
								Track.addParam(FuncName, 'A0', flc25_time, flc25_lines[3].a0)
								Track.addParam(FuncName, 'A1', flc25_time, flc25_lines[3].a1)
								Track.addParam(FuncName, 'A2', flc25_time, flc25_lines[3].a2)
								Track.addParam(FuncName, 'A3', flc25_time, flc25_lines[3].a3)
								Track.addParam(FuncName, 'Distance', flc25_time, flc25_lines[3].view_range)
								# right
								Track = TN.addTrack('FLC25 AOA lanes (Right(B))', flc25_time, color = 'b')
								FuncName = Track.addFunc(polyClothoid)
								Track.addParam(FuncName, 'A0', flc25_time, flc25_lines[4].a0)
								Track.addParam(FuncName, 'A1', flc25_time, flc25_lines[4].a1)
								Track.addParam(FuncName, 'A2', flc25_time, flc25_lines[4].a2)
								Track.addParam(FuncName, 'A3', flc25_time, flc25_lines[4].a3)
								Track.addParam(FuncName, 'Distance', flc25_time, flc25_lines[4].view_range)

								# left_left
								# left_left
								Track = TN.addTrack('FLC25 AOA lanes (Left Left(G))', flc25_time, color = 'g')
								FuncName = Track.addFunc(polyClothoid)
								Track.addParam(FuncName, 'A0', flc25_time, flc25_lines[5].a0)
								Track.addParam(FuncName, 'A1', flc25_time, flc25_lines[5].a1)
								Track.addParam(FuncName, 'A2', flc25_time, flc25_lines[5].a2)
								Track.addParam(FuncName, 'A3', flc25_time, flc25_lines[5].a3)
								Track.addParam(FuncName, 'Distance', flc25_time, flc25_lines[5].view_range)

								#right right
								Track = TN.addTrack('FLC25 AOA lanes (Right Right(G))', flc25_time, color = 'g')
								FuncName = Track.addFunc(polyClothoid)
								Track.addParam(FuncName, 'A0', flc25_time, flc25_lines[6].a0)
								Track.addParam(FuncName, 'A1', flc25_time, flc25_lines[6].a1)
								Track.addParam(FuncName, 'A2', flc25_time, flc25_lines[6].a2)
								Track.addParam(FuncName, 'A3', flc25_time, flc25_lines[6].a3)
								Track.addParam(FuncName, 'Distance', flc25_time, flc25_lines[6].view_range)
				TN.setLegend()
				interface.Sync.addClient(TN)
				return
