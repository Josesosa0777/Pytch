# -*- dataeval: init -*-

"""
Interactive video visualizer (VideoNavigator) with object overlay
visualization capabilities.
The selected parameter determines the name of the video file:
* DefParam: assumes the same video basename as the measurement file
* VideoSuffix_m0: assumes an "_m0" suffix at the end of the video basename
* CustomVideo: requires explicit video file name specification
"""

import os
import numpy as np
import datavis
import interface
import numpy as np
from evaltools.view_videonav import SignalGroups, getVideoName


# TODO: remove inferface.*

init_params = {
		"NO_LANES"                                      : dict(sensors = dict()),
		"FLC25_CAN"                                     : dict(sensors = dict(flc25_can = True)),
		"FLC25_ABD_LANE"                                : dict(sensors = dict(flc25_abd_lane = True)),
    	"FLC25_LD_LANE"                                : dict(sensors = dict(flc25_ld_lane = True)),
		"FLC25_POINT_CLOUD"                             : dict(sensors = dict(flc25_point_cloud = True)),
		"FLC20"                                         : dict(sensors = dict(flc20 = True)),
		"FLC20LDW"                                      : dict(sensors = dict(flc20 = True, ldw = True)),
		"FLC20_FLR20LF"                                 : dict(sensors = dict(flc20 = True, flr20lf = True)),
		"FLC20_FLR20LF_FLR20RO"                         : dict(
						sensors = dict(flc20 = True, flr20lf = True, flr20ro = True)),
		"FLC25_CAN(R)_FLC20(G)"                : dict(sensors = dict(flc25_can = True, flc20 = True)),
		"FLC25_CAN(R)_ABDLANE(G)"                : dict(sensors = dict(flc25_can = True, flc25_abd_lane = True)),
		"FLC25_CAN(R)_POINTCLOUD(B)"             : dict(sensors = dict(flc25_can = True, flc25_point_cloud = True)),
		"FLC25_ABDLANE(G)_POINTCLOUD(B)"        : dict(
						sensors = dict(flc25_abd_lane = True, flc25_point_cloud = True)),
		"FLC25_CAN(R)_ABDLANE(G)_POINTCLOUD(B)": dict(
						sensors = dict(flc25_can = True, flc25_abd_lane = True, flc25_point_cloud = True)),
    "FLR25_CURVATOR"                       : dict(sensors = dict(flr25_curvator = True)),
		"FLR25_ROAD_ESTIMATION"                : dict(sensors = dict(flr25_roadestimation = True)),
		"FLR25_CURVATOR_ROAD_ESTIMATION"       : dict(sensors = dict(flr25_curvator = True, flr25_roadestimation = True)),
    "FLC25_EGO_PATH_PREDICTION": dict(sensors = dict(flc25_ego_pathpred = True)),
		"FLC25_AOA_LANE": dict(sensors = dict(flc25_aoa_lane = True)),
}

color_set = {'green' : [0, 255, 0], 'red': [255, 0, 0], 'blue': [0, 0, 255], 'orange': [0, 0, 0],
						 'yellow': [255, 255, 0]
}

class cView(interface.iView):
		def init(self, sensors):
				self.sensors = sensors
				optdep = []
				if self.sensors.get("flr25_roadestimation"):
						optdep.append('calc_lanes_flr25_roadestimation@aebs.fill')
				if self.sensors.get("flc20"):
						optdep.append('calc_flc20_lanes@aebs.fill')
				if self.sensors.get('flc25_can'):
						optdep.append('calc_lanes-flc25@aebs.fill')
				if self.sensors.get('flc25_abd_lane'):
						optdep.append('calc_lanes_flc25_abd@aebs.fill')
				if self.sensors.get('flc25_ld_lane'):
						optdep.append('calc_lanes_flc25_ld@aebs.fill')
				if self.sensors.get('flc25_point_cloud'):
						optdep.append('fill_flc25_polylines@aebs.fill')
				if self.sensors.get("flr20lf"):
						optdep.append('calc_flr20_pathpred_lf@aebs.fill')
				if self.sensors.get("flr20ro"):
						optdep.append('calc_flr20_pathpred_ro@aebs.fill')
				if self.sensors.get("flr25_curvator"):
						optdep.append('calc_lanes_flr25_curvator@aebs.fill')
				if self.sensors.get("flr25_roadestimation"):
						optdep.append('calc_lanes_flr25_roadestimation@aebs.fill')
				if self.sensors.get("flc25_aoa_lane"):
						optdep.append('calc_lanes_flc25_aoa@aebs.fill')
				self.optdep = tuple(optdep)
				return

		def check(self):
				Name, Ext = os.path.splitext(interface.Source.FileName)
				avi_filename = getVideoName(Name + "" + Ext)
				self.logger.debug("Selected video file: %s" % avi_filename)
				multimedia_sgs = SignalGroups
				vidtime_group = self.source.selectLazySignalGroup(multimedia_sgs,
																													StrictTime = interface.StrictlyGrowingTimeCheck,
																													TimeMonGapIdx = 5)
				if 'VidTime' not in vidtime_group:
						vidtime_group = self.source.selectSignalGroup(multimedia_sgs,
																													StrictTime = False, TimeMonGapIdx = 5)
						if 'VidTime' in vidtime_group:
								self.logger.warning("Corrupt multimedia signal; video synchronization might be incorrect!")
						else:
								self.logger.warning("No multimedia signal; video synchronization might be incorrect!")
				# ldw signals
				if self.sensors.get("ldw"):
						ldw_sgs = [{
								"FLI1_LDI_Right": ("FLI1_E8", "FLI1_LaneDepartImminentRight_E8"),

								"FLI1_LDI_Left": ("FLI1_E8", "FLI1_LaneDepartImminentLeft_E8"),

						}]
						ldw_group = self.source.selectLazySignalGroup(ldw_sgs)
				else:
						ldw_group = None


				return avi_filename, vidtime_group, ldw_group

		def fill(self, avi_filename,vidtime_group,ldw_group):
				return avi_filename,vidtime_group,ldw_group

		def view(self, avi_filename,vidtime_group,ldw_group):
				group = None
				if 'VidTime' in vidtime_group:
						TimeVidTime, VidTime = vidtime_group.get_signal('VidTime')
				# VidTime = TimeVidTime - TimeVidTime[0]
				else:
						TimeVidTime = vidtime_group.get_time('Time')
				VidTime = TimeVidTime - TimeVidTime[0]

				if 'SLR25_RFB' in self.view_angles or any([bool(True) if 'SLR25_RFB' in modules else bool(False) for modules in list(self.modules._selects)]):
					group = 'SLR25_RFB'
				elif 'SLR25_Front' in self.view_angles or any([bool(True) if 'SLR25_Front' in modules else bool(False) for modules in list(self.modules._selects)]):
					group = 'SLR25_Front'

				objNxtVideoNavigator = datavis.cNxtVideoEventGrabberNavigator(avi_filename, TimeVidTime, VidTime, self.vidcalibs, group)
				objNxtVideoNavigator.setDisplayTime(TimeVidTime, VidTime)

				objNxtVideoNavigator.setLegend(interface.ShapeLegends)
				objNxtVideoNavigator.addGroups(interface.Groups)
				for Status in interface.Objects.get_selected_by_parent(interface.iObjectFill):
						ScaleTime_, Objects = interface.Objects.fill(Status)
						objNxtVideoNavigator.setObjects(ScaleTime_, Objects)

				time_scale = None
				lines = []
				if self.sensors.get("flc25_ego_pathpred"):
						if 'calc_lanes_flc25_paebs_ego_path_prediction@aebs.fill' in self.passed_optdep:
								flr25_line = self.modules.fill('calc_lanes_flc25_paebs_ego_path_prediction@aebs.fill')
								time_scale = flr25_line.time if time_scale is None else time_scale
								flr25_line = flr25_line.rescale(time_scale)
								line = {}
								line["range"] = 100.0 * np.ones_like(flr25_line.time)
								line["C0"] = flr25_line.c0
								line["C1"] = flr25_line.c1
								line["C2"] = flr25_line.c2
								line["C3"] = flr25_line.c3
								line["color"] = color_set['blue']
								lines.append(line)

						else:
								self.logger.warning('FLC25 PAEBS ego path prediction lane  cannot be visualized')
				if self.sensors.get("flr25_curvator"):
						if 'calc_lanes_flr25_curvator@aebs.fill' in self.passed_optdep:
								flr25_line = self.modules.fill('calc_lanes_flr25_curvator@aebs.fill')
								time_scale = flr25_line.time if time_scale is None else time_scale
								flr25_line = flr25_line.rescale(time_scale)
								line = {}
								line["range"] = 100.0 * np.ones_like(flr25_line.time)
								line["C0"] = flr25_line.c0
								line["C1"] = flr25_line.c1
								line["C2"] = flr25_line.c2
								line["C3"] = flr25_line.c3
								line["color"] = color_set['blue']
								lines.append(line)

						else:
								self.logger.warning('FLR25 curvator lane  cannot be visualized')
				if self.sensors.get("flr25_roadestimation"):
						if 'calc_lanes_flr25_roadestimation@aebs.fill' in self.passed_optdep:
								flr25_line = self.modules.fill('calc_lanes_flr25_roadestimation@aebs.fill')
								time_scale = flr25_line.time if time_scale is None else time_scale
								flr25_line = flr25_line.rescale(time_scale)
								line = {}
								line["range"] = 100.0 * np.ones_like(flr25_line.time)
								line["C0"] = flr25_line.c0
								line["C1"] = flr25_line.c1
								line["C2"] = flr25_line.c2
								line["C3"] = flr25_line.c3
								line["color"] = color_set['yellow']
								lines.append(line)

						else:
								self.logger.warning('FLR25 ROAD Estimation lane  cannot be visualized')
				if self.sensors.get("flr20lf"):
						if 'calc_flr20_pathpred_lf@aebs.fill' in self.passed_optdep:
								flr20_line = self.modules.fill('calc_flr20_pathpred_lf@aebs.fill')
								time_scale = flr20_line.time if time_scale is None else time_scale
								flr20_line = flr20_line.rescale(time_scale)
								line = {}
								line["range"] = 100.0 * np.ones_like(flr20_line.time)
								line["C0"] = flr20_line.c0
								line["C1"] = flr20_line.c1
								line["C2"] = flr20_line.c2
								line["C3"] = flr20_line.c3
								line["color"] = [0, 0, 255]
								lines.append(line)
								lines.append(line)  # dirty but necessary
						else:
								self.logger.warning('FLR20 lane fusion cannot be visualized')
				if self.sensors.get("flr20ro"):
						if 'calc_flr20_pathpred_ro@aebs.fill' in self.passed_optdep:
								flr20_line = self.modules.fill('calc_flr20_pathpred_ro@aebs.fill')
								time_scale = flr20_line.time if time_scale is None else time_scale
								flr20_line = flr20_line.rescale(time_scale)
								line = {}
								line["range"] = 100.0 * np.ones_like(flr20_line.time)
								line["C0"] = flr20_line.c0
								line["C1"] = flr20_line.c1
								line["C2"] = flr20_line.c2
								line["C3"] = flr20_line.c3
								line["color"] = [255, 0, 0]  # [0, 0, 100]
								lines.append(line)
								lines.append(line)  # dirty but necessary
						else:
								self.logger.warning('FLR20 radar-only path prediction cannot be visualized')
				if self.sensors.get("flc20"):
						if 'calc_flc20_lanes@aebs.fill' in self.passed_optdep:
								flc20_lines = self.modules.fill('calc_flc20_lanes@aebs.fill')
								time_scale = flc20_lines.time if time_scale is None else time_scale
								flc20_lines = flc20_lines.rescale(time_scale)
								left_line = {}
								left_line["range"] = flc20_lines.left_line.view_range
								left_line["C0"] = flc20_lines.left_line.c0
								left_line["C1"] = flc20_lines.left_line.c1
								left_line["C2"] = flc20_lines.left_line.c2
								left_line["C3"] = flc20_lines.left_line.c3
								left_line["color"] = [0, 255, 0]
								lines.append(left_line)
								right_line = {}
								right_line["range"] = flc20_lines.right_line.view_range
								right_line["C0"] = flc20_lines.right_line.c0
								right_line["C1"] = flc20_lines.right_line.c1
								right_line["C2"] = flc20_lines.right_line.c2
								right_line["C3"] = flc20_lines.right_line.c3
								right_line["color"] = [0, 255, 0]
								lines.append(right_line)
								left_left_line = {}
								left_left_line["range"] = flc20_lines.left_left_line.view_range
								left_left_line["C0"] = flc20_lines.left_left_line.c0
								left_left_line["C1"] = flc20_lines.left_left_line.c1
								left_left_line["C2"] = flc20_lines.left_left_line.c2
								left_left_line["C3"] = flc20_lines.left_left_line.c3
								left_left_line["color"] = [0, 255, 0]
								lines.append(left_left_line)
								right_right_line = {}
								right_right_line["range"] = flc20_lines.right_right_line.view_range
								right_right_line["C0"] = flc20_lines.right_right_line.c0
								right_right_line["C1"] = flc20_lines.right_right_line.c1
								right_right_line["C2"] = flc20_lines.right_right_line.c2
								right_right_line["C3"] = flc20_lines.right_right_line.c3
								right_right_line["color"] = [0, 255, 0]
								lines.append(right_right_line)
						else:
								self.logger.warning('FLC20 lanes cannot be visualized')
				if self.sensors.get("flc25_can"):
						if 'calc_lanes-flc25@aebs.fill' in self.passed_optdep:
								flc25_lines = self.modules.fill('calc_lanes-flc25@aebs.fill')
								time_scale = flc25_lines.time if time_scale is None else time_scale
								flc25_lines = flc25_lines.rescale(time_scale)
								left_line = {}
								left_line["range"] = flc25_lines.left_line.view_range
								left_line["C0"] = flc25_lines.left_line.c0
								left_line["C1"] = flc25_lines.left_line.c1
								left_line["C2"] = flc25_lines.left_line.c2
								left_line["C3"] = flc25_lines.left_line.c3
								left_line["color"] = color_set['red']
								lines.append(left_line)
								right_line = {}
								right_line["range"] = flc25_lines.right_line.view_range
								right_line["C0"] = flc25_lines.right_line.c0
								right_line["C1"] = flc25_lines.right_line.c1
								right_line["C2"] = flc25_lines.right_line.c2
								right_line["C3"] = flc25_lines.right_line.c3
								right_line["color"] = color_set['red']
								lines.append(right_line)
								left_left_line = {}
								left_left_line["range"] = flc25_lines.left_left_line.view_range
								left_left_line["C0"] = flc25_lines.left_left_line.c0
								left_left_line["C1"] = flc25_lines.left_left_line.c1
								left_left_line["C2"] = flc25_lines.left_left_line.c2
								left_left_line["C3"] = flc25_lines.left_left_line.c3
								left_left_line["color"] = color_set['red']
								lines.append(left_left_line)
								right_right_line = {}
								right_right_line["range"] = flc25_lines.right_right_line.view_range
								right_right_line["C0"] = flc25_lines.right_right_line.c0
								right_right_line["C1"] = flc25_lines.right_right_line.c1
								right_right_line["C2"] = flc25_lines.right_right_line.c2
								right_right_line["C3"] = flc25_lines.right_right_line.c3
								right_right_line["color"] = color_set['red']
								lines.append(right_right_line)
						else:
								self.logger.warning('FLC25 CAN lanes cannot be visualized')
				if self.sensors.get("flc25_abd_lane"):
						if 'calc_lanes_flc25_abd@aebs.fill' in self.passed_optdep:
								flc25_lines = self.modules.fill('calc_lanes_flc25_abd@aebs.fill')
								time_scale = flc25_lines.time if time_scale is None else time_scale
								flc25_lines = flc25_lines.rescale(time_scale)
								left_line = {}
								left_line["range"] = flc25_lines.left_line.view_range
								left_line["C0"] = flc25_lines.left_line.c0
								left_line["C1"] = flc25_lines.left_line.c1
								left_line["C2"] = flc25_lines.left_line.c2
								left_line["C3"] = flc25_lines.left_line.c3
								left_line["color"] = color_set['green']
								lines.append(left_line)
								right_line = {}
								right_line["range"] = flc25_lines.right_line.view_range
								right_line["C0"] = flc25_lines.right_line.c0
								right_line["C1"] = flc25_lines.right_line.c1
								right_line["C2"] = flc25_lines.right_line.c2
								right_line["C3"] = flc25_lines.right_line.c3
								right_line["color"] = color_set['green']
								lines.append(right_line)
								left_left_line = {}
								left_left_line["range"] = flc25_lines.left_left_line.view_range
								left_left_line["C0"] = flc25_lines.left_left_line.c0
								left_left_line["C1"] = flc25_lines.left_left_line.c1
								left_left_line["C2"] = flc25_lines.left_left_line.c2
								left_left_line["C3"] = flc25_lines.left_left_line.c3
								left_left_line["color"] = color_set['green']
								lines.append(left_left_line)
								right_right_line = {}
								right_right_line["range"] = flc25_lines.right_right_line.view_range
								right_right_line["C0"] = flc25_lines.right_right_line.c0
								right_right_line["C1"] = flc25_lines.right_right_line.c1
								right_right_line["C2"] = flc25_lines.right_right_line.c2
								right_right_line["C3"] = flc25_lines.right_right_line.c3
								right_right_line["color"] = color_set['green']
								lines.append(right_right_line)
						else:
								self.logger.warning('FLC25 ABD lanes cannot be visualized')
				if self.sensors.get("flc25_ld_lane"):
						if 'calc_lanes_flc25_ld@aebs.fill' in self.passed_optdep:
								flc25_lines = self.modules.fill('calc_lanes_flc25_ld@aebs.fill')
								time_scale = flc25_lines.time if time_scale is None else time_scale
								flc25_lines = flc25_lines.rescale(time_scale)
								left_line = {}
								left_line["range"] = flc25_lines.left_line.view_range
								left_line["C0"] = flc25_lines.left_line.c0
								left_line["C1"] = flc25_lines.left_line.c1
								left_line["C2"] = flc25_lines.left_line.c2
								left_line["C3"] = flc25_lines.left_line.c3
								left_line["color"] = color_set['green']
								lines.append(left_line)
								right_line = {}
								right_line["range"] = flc25_lines.right_line.view_range
								right_line["C0"] = flc25_lines.right_line.c0
								right_line["C1"] = flc25_lines.right_line.c1
								right_line["C2"] = flc25_lines.right_line.c2
								right_line["C3"] = flc25_lines.right_line.c3
								right_line["color"] = color_set['green']
								lines.append(right_line)
								left_left_line = {}
								left_left_line["range"] = flc25_lines.left_left_line.view_range
								left_left_line["C0"] = flc25_lines.left_left_line.c0
								left_left_line["C1"] = flc25_lines.left_left_line.c1
								left_left_line["C2"] = flc25_lines.left_left_line.c2
								left_left_line["C3"] = flc25_lines.left_left_line.c3
								left_left_line["color"] = color_set['green']
								lines.append(left_left_line)
								right_right_line = {}
								right_right_line["range"] = flc25_lines.right_right_line.view_range
								right_right_line["C0"] = flc25_lines.right_right_line.c0
								right_right_line["C1"] = flc25_lines.right_right_line.c1
								right_right_line["C2"] = flc25_lines.right_right_line.c2
								right_right_line["C3"] = flc25_lines.right_right_line.c3
								right_right_line["color"] = color_set['green']
								lines.append(right_right_line)
						else:
								self.logger.warning('FLC25 LD lanes cannot be visualized')
				if self.sensors.get("flc25_point_cloud"):
						if 'fill_flc25_polylines@aebs.fill' in self.passed_optdep:
								all_lines, common_time = self.modules.fill('fill_flc25_polylines@aebs.fill')
								time_scale = common_time if time_scale is None else time_scale
								# flc25_lines = flc25_lines.rescale(time_scale)
								# ego-center
								center_line = {}
								center_line["linex"] = all_lines['ego_centerLine'][:, 0]
								center_line["liney"] = all_lines['ego_centerLine'][:, 1]
								center_line["color"] = color_set['yellow']
								lines.append(center_line)
								# ego-right
								right_line = {}
								right_line["linex"] = all_lines['ego_rightLine'][:, 0]
								right_line["liney"] = all_lines['ego_rightLine'][:, 1]
								right_line["color"] = color_set['blue']
								lines.append(right_line)
								# ego-left
								left_line = {}
								left_line["linex"] = all_lines['ego_leftLine'][:, 0]
								left_line["liney"] = all_lines['ego_leftLine'][:, 1]
								left_line["color"] = color_set['blue']
								lines.append(left_line)
								# egoleft-left
								egoleft_left_line = {}
								egoleft_left_line["linex"] = all_lines['egoleft_leftLine'][:, 0]
								egoleft_left_line["liney"] = all_lines['egoleft_leftLine'][:, 1]
								egoleft_left_line["color"] = color_set['blue']
								lines.append(egoleft_left_line)
								# egoleft-right
								egoleft_right_line = {}
								egoleft_right_line["linex"] = all_lines['egoleft_rightLine'][:, 0]
								egoleft_right_line["liney"] = all_lines['egoleft_rightLine'][:, 1]
								egoleft_right_line["color"] = color_set['blue']
								lines.append(egoleft_right_line)
								# egoleftleft-left
								egoleftleft_left_line = {}
								egoleftleft_left_line["linex"] = all_lines['egoleftleft_leftLine'][:, 0]
								egoleftleft_left_line["liney"] = all_lines['egoleftleft_leftLine'][:, 1]
								egoleftleft_left_line["color"] = color_set['blue']
								lines.append(egoleftleft_left_line)
								# egoleftleft-right
								egoleftleft_right_line = {}
								egoleftleft_right_line["linex"] = all_lines['egoleftleft_rightLine'][:, 0]
								egoleftleft_right_line["liney"] = all_lines['egoleftleft_rightLine'][:, 1]
								egoleftleft_right_line["color"] = color_set['blue']
								lines.append(egoleftleft_right_line)

								# egoright-left
								egoright_left_line = {}
								egoright_left_line["linex"] = all_lines['egoright_leftLine'][:, 0]
								egoright_left_line["liney"] = all_lines['egoright_leftLine'][:, 1]
								egoright_left_line["color"] = color_set['blue']
								lines.append(egoright_left_line)
								# egoright-right
								egoright_right_line = {}
								egoright_right_line["linex"] = all_lines['egoright_rightLine'][:, 0]
								egoright_right_line["liney"] = all_lines['egoright_rightLine'][:, 1]
								egoright_right_line["color"] = color_set['blue']
								lines.append(egoright_right_line)
								# egorightright-left
								egorightright_left_line = {}
								egorightright_left_line["linex"] = all_lines['egorightright_leftLine'][:, 0]
								egorightright_left_line["liney"] = all_lines['egorightright_leftLine'][:, 1]
								egorightright_left_line["color"] = color_set['blue']
								lines.append(egorightright_left_line)
								# egorightright-right
								egorightright_right_line = {}
								egorightright_right_line["linex"] = all_lines['egorightright_rightLine'][:, 0]
								egorightright_right_line["liney"] = all_lines['egorightright_rightLine'][:, 1]
								egorightright_right_line["color"] = color_set['blue']
								lines.append(egorightright_right_line)
						else:
								self.logger.warning('FLC25_POINT_CLOUD lanes cannot be visualized')
				if self.sensors.get("flc20") and self.sensors.get("ldw"):
						if ('calc_flc20_lanes@aebs.fill' in self.passed_optdep and
										"FLI1_LDI_Left" in ldw_group and "FLI1_LDI_Right" in ldw_group):
								flc20_lines = self.modules.fill('calc_flc20_lanes@aebs.fill')
								time_scale = flc20_lines.time if time_scale is None else time_scale

								ldw_left = ldw_group.get_value("FLI1_LDI_Left", ScaleTime=time_scale)
								ldw_right = ldw_group.get_value("FLI1_LDI_Right", ScaleTime=time_scale)

								flc20_lines = flc20_lines.rescale(time_scale)
								left_line = {}
								left_line["range"] = np.where(ldw_left,
										flc20_lines.left_line.view_range, 0.0)
								left_line["C0"] = flc20_lines.left_line.c0
								left_line["C1"] = flc20_lines.left_line.c1
								left_line["C2"] = flc20_lines.left_line.c2
								left_line["C3"] = flc20_lines.left_line.c3
								left_line["color"] = [255, 0, 0]
								lines.append(left_line)
								right_line = {}
								right_line["range"] = np.where(ldw_right,
										flc20_lines.right_line.view_range, 0.0)
								right_line["C0"] = flc20_lines.right_line.c0
								right_line["C1"] = flc20_lines.right_line.c1
								right_line["C2"] = flc20_lines.right_line.c2
								right_line["C3"] = flc20_lines.right_line.c3
								right_line["color"] = [255, 0, 0]
								lines.append(right_line)
						else:
								self.logger.warning('LDW events cannot be visualized')
				if self.sensors.get("flc25_aoa_lane"):
						if 'calc_lanes_flc25_aoa@aebs.fill' in self.passed_optdep:
								all_lines, common_time = self.modules.fill('calc_lanes_flc25_aoa@aebs.fill')
								time_scale = common_time if time_scale is None else time_scale

								# ego-center
								ego_centerline = {}
								ego_centerline["range"] = all_lines[0].view_range
								ego_centerline["C0"] = all_lines[0].c0
								ego_centerline["C1"] = all_lines[0].c1
								ego_centerline["C2"] = all_lines[0].c2
								ego_centerline["C3"] = all_lines[0].c3
								ego_centerline["color"] = [255, 0, 0]
								lines.append(ego_centerline)

								# left_centerline
								left_centerline = {}
								left_centerline["range"] = all_lines[1].view_range
								left_centerline["C0"] = all_lines[1].c0
								left_centerline["C1"] = all_lines[1].c1
								left_centerline["C2"] = all_lines[1].c2
								left_centerline["C3"] = all_lines[1].c3
								left_centerline["color"] = [255, 0, 0]
								lines.append(left_centerline)

								# right_centerline
								right_centerline = {}
								right_centerline["range"] = all_lines[2].view_range
								right_centerline["C0"] = all_lines[2].c0
								right_centerline["C1"] = all_lines[2].c1
								right_centerline["C2"] = all_lines[2].c2
								right_centerline["C3"] = all_lines[2].c3
								right_centerline["color"] = [255, 0, 0]
								lines.append(right_centerline)

								# left_marking
								left_marking = {}
								left_marking["range"] = all_lines[3].view_range
								left_marking["C0"] = all_lines[3].c0
								left_marking["C1"] = all_lines[3].c1
								left_marking["C2"] = all_lines[3].c2
								left_marking["C3"] = all_lines[3].c3
								left_marking["color"] = [0, 0, 255]
								lines.append(left_marking)

								# right_marking
								right_marking = {}
								right_marking["range"] = all_lines[4].view_range
								right_marking["C0"] = all_lines[4].c0
								right_marking["C1"] = all_lines[4].c1
								right_marking["C2"] = all_lines[4].c2
								right_marking["C3"] = all_lines[4].c3
								right_marking["color"] = [0, 0, 255]
								lines.append(right_marking)

								# next_left_marking
								next_left_marking = {}
								next_left_marking["range"] = all_lines[5].view_range
								next_left_marking["C0"] = all_lines[5].c0
								next_left_marking["C1"] = all_lines[5].c1
								next_left_marking["C2"] = all_lines[5].c2
								next_left_marking["C3"] = all_lines[5].c3
								next_left_marking["color"] = [0, 255, 0]
								lines.append(next_left_marking)

								# next_right_marking
								next_right_marking = {}
								next_right_marking["range"] = all_lines[6].view_range
								next_right_marking["C0"] = all_lines[6].c0
								next_right_marking["C1"] = all_lines[6].c1
								next_right_marking["C2"] = all_lines[6].c2
								next_right_marking["C3"] = all_lines[6].c3
								next_right_marking["color"] = [0, 255, 0]
								lines.append(next_right_marking)

						else:
								self.logger.warning('FLC25_POINT_CLOUD lanes cannot be visualized')

				if lines:
						objNxtVideoNavigator.setLanes(time_scale, lines)

				interface.Sync.addClient(objNxtVideoNavigator, (TimeVidTime, VidTime))

				# interface.Sync.addClient(VN)
				# VN.setDisplayTime(TimeVidTime, VidTime)

				return

