# -*- dataeval: init -*-
import logging

import numpy as np
from interface import iObjectFill
from measproc.IntervalList import intervalsToMask
from measproc.Object import colorByVelocity
from pyutils.cache_manager import get_modules_cache, store_modules_cache

logger = logging.getLogger('fillFLC25_CEM_TPF')

INVALID_ID = 255


class cFill(iObjectFill):
		dep = 'fill_flc25_cem_tpf_tracks','fill_flc25_ars_fcu_tracks','fill_flc25_em_tracks','calc_radar_egomotion-flc25'

		def check(self):
				modules = self.get_modules()
				tracks, signals = modules.fill("fill_flc25_cem_tpf_tracks")
				fcu_tracks, fcu_signals = modules.fill("fill_flc25_ars_fcu_tracks")
				em_tracks, em_signals = modules.fill("fill_flc25_em_tracks")
				ego_orig = modules.fill("calc_radar_egomotion-flc25")
				egomotion = ego_orig.rescale(tracks.time)
				return tracks,signals,fcu_tracks,fcu_signals,em_tracks,em_signals, egomotion

		def fill(self, tracks,signals, fcu_tracks,fcu_signals,em_tracks,em_signals, egomotion):
				import time
				start = time.time()
				logger.info("FLC25 CEM TPF Fusion object retrieval is started, Please wait...")
				cem_tpf_fusion_objects = []
				em_objects = []
				fcu_objects = []
				for id, track in tracks.iteritems():
						cem_tpf_object = {}
						cem_tpf_object["signal_mapping"] = {}
						cem_tpf_object["id"] = np.where(track.dx.mask, INVALID_ID, id)
						cem_tpf_object["valid"] = track.tr_state.valid.data & ~track.tr_state.valid.mask

						object_type = np.empty(track.dx.shape, dtype = 'string')
						object_type[:] = 'U'
						car = np.where(track.obj_type.car, 1, 0)
						truck = np.where(track.obj_type.truck, 2, 0)
						motorcycle = np.where(track.obj_type.motorcycle, 3, 0)
						pedestrian = np.where(track.obj_type.pedestrian, 4, 0)
						bicycle = np.where(track.obj_type.bicycle, 5, 0)
						unknown = np.where(track.obj_type.unknown, 6, 0)
						point = np.where(track.obj_type.point, 7, 0)
						wide = np.where(track.obj_type.wide, 8, 0)

						object_type[car == 1] = 'C'
						object_type[truck == 2] = 'T'
						object_type[motorcycle == 3] = 'M'
						object_type[pedestrian == 4] = 'P'
						object_type[bicycle == 5] = 'B'
						object_type[unknown == 6] = 'U'
						object_type[point == 7] = 'POINT'
						object_type[wide == 8] = 'WIDE'

						cem_tpf_object["label"] = np.array(
										["FLC25_CEM_TPF_%d_%s" % (idx, obj_type) for idx, obj_type in zip(cem_tpf_object["id"], object_type.data)])
						track.dx.data[track.dx.mask] = 0
						track.dy.data[track.dy.mask] = 0
						cem_tpf_object["dx"] = track.dx.data
						cem_tpf_object["signal_mapping"]["dx"] = signals[id][0]["fDistX"]
						cem_tpf_object["dy"] = track.dy.data
						cem_tpf_object["signal_mapping"]["dy"] = signals[id][0]["fDistY"]
						cem_tpf_object["type"] = np.where(track.mov_state.stat.data & ~track.mov_state.stat.mask,
																 self.get_grouptype('FLC25_CEM_TPF_STAT'),
																 self.get_grouptype('FLC25_CEM_TPF_MOV'))
						cem_tpf_object["signal_mapping"]["type"] = signals[id][0]["eDynamicProperty"]
						init_intervals = [(st, st + 1) for st, end in track.alive_intervals]
						cem_tpf_object["init"] = intervalsToMask(init_intervals, track.dx.size)
						# ongoing: green, stationary: red, oncoming: blue
						cem_tpf_object["color"] = colorByVelocity(egomotion.vx, track.vx.data,[0, 255, 0], [255, 0, 0], [0, 0, 255])  # [R, G, B]

						cem_tpf_object["ax_abs"] = track.ax_abs.data
						cem_tpf_object["signal_mapping"]["ax_abs"] = signals[id][0]["fAabsX"]
						cem_tpf_object["ay_abs"] = track.ay_abs.data
						cem_tpf_object["signal_mapping"]["ay_abs"] = signals[id][0]["fAabsY"]
						cem_tpf_object["ax"] = track.ax.data
						cem_tpf_object["signal_mapping"]["ax"] = signals[id][0]["fArelX"]
						cem_tpf_object["ay"] = track.ay.data
						cem_tpf_object["signal_mapping"]["ay"] = signals[id][0]["fArelY"]
						cem_tpf_object["vx_abs"] = track.vx_abs.data
						cem_tpf_object["signal_mapping"]["vx_abs"] = signals[id][0]["fVabsX"]
						cem_tpf_object["vy_abs"] = track.vy_abs.data
						cem_tpf_object["signal_mapping"]["vy_abs"] = signals[id][0]["fVabsY"]
						cem_tpf_object["vx"] = track.vx.data
						cem_tpf_object["signal_mapping"]["vx"] = signals[id][0]["fVrelX"]
						cem_tpf_object["vy"] = track.vy.data
						cem_tpf_object["signal_mapping"]["vy"] = signals[id][0]["fVrelY"]

						cem_tpf_object["lane"] = track.lane.join()
						cem_tpf_object["signal_mapping"]["lane"] = signals[id][0][
							"eAssociatedLane"]
						cem_tpf_object["mov_state"] = track.mov_state.join()
						cem_tpf_object["signal_mapping"]["mov_state"] = signals[id][0][
							"eDynamicProperty"]
						cem_tpf_object["video_conf"] = track.video_conf.data
						cem_tpf_object["signal_mapping"]["video_conf"] = signals[id][0][
							"uiProbabilityOfExistence"]
						cem_tpf_object["lane_conf"]= track.lane_conf.data
						cem_tpf_object["signal_mapping"]["lane_conf"] = signals[id][0][
							"uiAssociatedLaneConfidence"]
						cem_tpf_object["class_conf"] = track.class_conf.data
						cem_tpf_object["signal_mapping"]["class_conf"] = signals[id][0][
							"uiClassConfidence"]
						cem_tpf_object["obj_type"] = track.obj_type.join()
						cem_tpf_object["signal_mapping"]["obj_type"] = signals[id][0][
							"eClassification"]
						cem_tpf_object["measured_by"] = track.measured_by.join()
						cem_tpf_object["signal_mapping"]["measured_by"] = signals[id][0][
							"eMeasuredBy"]
						cem_tpf_object["contributing_sensors"] = track.contributing_sensors.join()
						cem_tpf_object["signal_mapping"]["contributing_sensors"] = signals[id][0][
								"contributingSensors"]
						cem_tpf_object["life_time"] = track.life_time.data
						cem_tpf_object["signal_mapping"]["life_time"] = signals[id][0]['fLifeTime']
						cem_tpf_object["camera_id"] = track.camera_id.data
						cem_tpf_object["signal_mapping"]["camera_id"] = signals[id][0]['cameraId']
						cem_tpf_object["radar_id"] = track.radar_id.data
						cem_tpf_object["signal_mapping"]["radar_id"] = signals[id][0]['radarId']
						cem_tpf_object["custom_labels"] = {'video_conf': 'Probability Of Existence',"lane_conf" : "Associated Lane Confidence","lane" :"Associated Lane"}
						cem_tpf_object["obj_type_mapping"] = {0: 'car', 1: 'truck', 2: 'motorcycle', 3: 'pedestrian', 4: 'bicycle',
												 5: 'unknown', 6: 'point', 7: 'wide'}
						cem_tpf_fusion_objects.append(cem_tpf_object)

				for id, track in em_tracks.iteritems():
						# create object
						o = {}
						o["signal_mapping"] = {}
						o["id"] = np.where(track.dx.mask, INVALID_ID, id)
						o["valid"] = track.tr_state.valid.data & ~track.tr_state.valid.mask

						object_type = np.empty(track.dx.shape, dtype = 'string')
						object_type[:] = 'U'
						car = np.where(track.obj_type.car, 1, 0)
						truck = np.where(track.obj_type.truck, 2, 0)
						motorcycle = np.where(track.obj_type.motorcycle, 3, 0)
						pedestrian = np.where(track.obj_type.pedestrian, 4, 0)
						bicycle = np.where(track.obj_type.bicycle, 5, 0)
						unknown = np.where(track.obj_type.unknown, 6, 0)
						point = np.where(track.obj_type.point, 7, 0)
						wide = np.where(track.obj_type.wide, 8, 0)

						object_type[car == 1] = 'C'
						object_type[truck == 2] = 'T'
						object_type[motorcycle == 3] = 'M'
						object_type[pedestrian == 4] = 'P'
						object_type[bicycle == 5] = 'B'
						object_type[unknown == 6] = 'U'
						object_type[point == 7] = 'POINT'
						object_type[wide == 8] = 'WIDE'

						o["label"] = np.array(
										["FLC25_EM_%d_%s" % (idx, obj_type) for idx, obj_type in zip(o["id"], object_type.data)])
						track.dx.data[track.dx.mask] = 0
						track.dy.data[track.dy.mask] = 0
						o["dx"] = track.dx.data
						o["signal_mapping"]["dx"] = em_signals[id][0]["fDistX"]
						o["dy"] = track.dy.data
						o["signal_mapping"]["dy"] = em_signals[id][0]["fDistY"]
						o["type"] = np.where(track.mov_state.stat.data & ~track.mov_state.stat.mask,
																 self.get_grouptype('FLC25_EM_STAT'),
																 self.get_grouptype('FLC25_EM_MOV'))
						o["signal_mapping"]["type"] = em_signals[id][0]["eDynamicProperty"]
						init_intervals = [(st, st + 1) for st, end in track.alive_intervals]
						o["init"] = intervalsToMask(init_intervals, track.dx.size)
						# ongoing: green, stationary: red, oncoming: blue
						o["color"] = colorByVelocity(egomotion.vx, track.vx.data,
																				 [0, 255, 0], [255, 0, 0], [0, 0, 255])  # [R, G, B]

						o["ax_abs"] = track.ax_abs.data
						o["signal_mapping"]["ax_abs"] = em_signals[id][0]["fAabsX"]
						o["ay_abs"] = track.ay_abs.data
						o["signal_mapping"]["ay_abs"] = em_signals[id][0]["fAabsY"]
						o["ax"] = track.ax.data
						o["signal_mapping"]["ax"] = em_signals[id][0]["fArelX"]
						o["ay"] = track.ay.data
						o["signal_mapping"]["ay"] = em_signals[id][0]["fArelY"]
						o["vx_abs"] = track.vx_abs.data
						o["signal_mapping"]["vx_abs"] = em_signals[id][0]["fVabsX"]
						o["vy_abs"] = track.vy_abs.data
						o["signal_mapping"]["vy_abs"] = em_signals[id][0]["fVabsY"]
						o["vx"] = track.vx.data
						o["signal_mapping"]["vx"] = em_signals[id][0]["fVrelX"]
						o["vy"] = track.vy.data
						o["signal_mapping"]["vy"] = em_signals[id][0]["fVrelY"]
						o["dx"] = track.dx.data
						o["signal_mapping"]["dx"] = em_signals[id][0]["fDistX"]
						o["dy"] = track.dy.data
						o["signal_mapping"]["dy"] = em_signals[id][0]["fDistY"]
						o["dx_std"] = track.dx_std.data
						o["signal_mapping"]["dx_std"] = em_signals[id][0]["fDistXStd"]
						o["dy_std"] = track.dy_std.data
						o["signal_mapping"]["dy_std"] = em_signals[id][0]["fDistYStd"]
						o["dz"] = track.dz.data
						o["signal_mapping"]["dz"] = em_signals[id][0]["fDistZ"]
						o["dz_std"] = track.dx_std.data
						o["signal_mapping"]["dz_std"] = em_signals[id][0]["fDistZStd"]
						o["yaw"] = track.yaw.data
						o["signal_mapping"]["yaw"] = em_signals[id][0]["fYaw"]
						o["yaw_std"] = track.yaw_std.data
						o["signal_mapping"]["yaw_std"] = em_signals[id][0]["fYawStd"]

						o["lane"] = track.lane.join()
						o["signal_mapping"]["lane"] = em_signals[id][0][
							"eAssociatedLane"]
						o["mov_state"] = track.mov_state.join()
						o["signal_mapping"]["mov_state"] = em_signals[id][0][
							"eDynamicProperty"]
						o["video_conf"] = track.video_conf.data
						o["signal_mapping"]["video_conf"] = em_signals[id][0][
							"uiProbabilityOfExistence"]
						o["lane_conf"] = track.lane_conf.data
						o["signal_mapping"]["lane_conf"] = em_signals[id][0][
							"uiAssociatedLaneConfidence"]
						o["obj_type"] = track.obj_type.join()
						o["signal_mapping"]["obj_type"] = em_signals[id][0][
							"eEbaObjClass"]
						o["custom_labels"] = {'video_conf': 'Probability Of Existence',"lane_conf" : "Associated Lane Confidence","lane" :"Associated Lane"}
						em_objects.append(o)

				for id, track in fcu_tracks.iteritems():
						# create object
						o = {}
						o["signal_mapping"] = {}
						o["id"] = np.where(track.dx.mask, INVALID_ID, id)
						o["valid"] = track.tr_state.valid.data & ~track.tr_state.valid.mask

						object_type = np.empty(track.dx.shape, dtype = 'string')
						object_type[:] = 'U'
						car = np.where(track.obj_type.car, 1, 0)
						truck = np.where(track.obj_type.truck, 2, 0)
						motorcycle = np.where(track.obj_type.motorcycle, 3, 0)
						pedestrian = np.where(track.obj_type.pedestrian, 4, 0)
						bicycle = np.where(track.obj_type.bicycle, 5, 0)
						unknown = np.where(track.obj_type.unknown, 6, 0)
						point = np.where(track.obj_type.point, 7, 0)
						wide = np.where(track.obj_type.wide, 8, 0)

						object_type[car == 1] = 'C'
						object_type[truck == 2] = 'T'
						object_type[motorcycle == 3] = 'M'
						object_type[pedestrian == 4] = 'P'
						object_type[bicycle == 5] = 'B'
						object_type[unknown == 6] = 'U'
						object_type[point == 7] = 'POINT'
						object_type[wide == 8] = 'WIDE'

						o["label"] = np.array(
										["FLC25_ARS_FCU_%d_%s" % (idx, obj_type) for idx, obj_type in zip(o["id"], object_type.data)])
						track.dx.data[track.dx.mask] = 0
						track.dy.data[track.dy.mask] = 0
						o["dx"] = track.dx.data
						o["signal_mapping"]["dx"] = fcu_signals[id][0]["fDistX"]
						o["dy"] = track.dy.data
						o["signal_mapping"]["dy"] = fcu_signals[id][0]["fDistY"]
						o["type"] = np.where(track.mov_state.stat.data & ~track.mov_state.stat.mask,
																 self.get_grouptype('FLC25_ARS_FCU_STAT'),
																 self.get_grouptype('FLC25_ARS_FCU_MOV'))
						init_intervals = [(st, st + 1) for st, end in track.alive_intervals]
						o["init"] = intervalsToMask(init_intervals, track.dx.size)
						# ongoing: green, stationary: red, oncoming: blue
						o["color"] = colorByVelocity(egomotion.vx, track.vx.data,
																				 [0, 255, 0], [255, 0, 0], [0, 0, 255])  # [R, G, B]

						# Extra changes

						# Object Kinematic
						o["ax_abs"] = track.ax_abs.data
						o["signal_mapping"]["ax_abs"] = fcu_signals[id][0]["fAabsX"]
						o["ay_abs"] = track.ay_abs.data
						o["signal_mapping"]["ay_abs"] = fcu_signals[id][0]["fAabsY"]
						o["ax"] = track.ax.data
						o["signal_mapping"]["ax"] = fcu_signals[id][0]["fArelX"]
						o["ay"] = track.ay.data
						o["signal_mapping"]["ay"] = fcu_signals[id][0]["fArelY"]
						o["vx_abs"] = track.vx_abs.data
						o["signal_mapping"]["vx_abs"] = fcu_signals[id][0]["fVabsX"]
						o["vy_abs"] = track.vy_abs.data
						o["signal_mapping"]["vy_abs"] = fcu_signals[id][0]["fVabsY"]
						o["vx"] = track.vx.data
						o["signal_mapping"]["vx"] = fcu_signals[id][0]["fVrelX"]
						o["vy"] = track.vy.data
						o["signal_mapping"]["vy"] = fcu_signals[id][0]["fVrelY"]

						o["lane"] = track.lane.join()
						o["signal_mapping"]["lane"] = fcu_signals[id][0][
							"eAssociatedLane"]
						o["mov_state"] = track.mov_state.join()
						o["signal_mapping"]["mov_state"] = fcu_signals[id][0][
							"eDynamicProperty"]
						o["video_conf"] = track.video_conf.data
						o["signal_mapping"]["video_conf"] = fcu_signals[id][0][
							"uiProbabilityOfExistence"]
						o["obj_type"] = track.obj_type.join()
						o["signal_mapping"]["obj_type"] = fcu_signals[id][0][
							"eClassification"]
						try:
							o["fusion_quality"] = track.fusion_quality.data
							o["signal_mapping"]["fusion_quality"] = \
							fcu_signals[id][0][
								"ucFusionQuality"]
						except:
							pass
						o["acc_obj_quality"] = track.acc_obj_quality.data
						o["signal_mapping"]["acc_obj_quality"] = fcu_signals[id][0][
							"uiAccObjQuality"]
						o["aeb_obj_quality"] = track.aeb_obj_quality.data
						o["signal_mapping"]["aeb_obj_quality"] = fcu_signals[id][0][
							"uiEbaObjQuality"]
						o["custom_labels"] = {'video_conf': 'Probability Of Existence',"lane" :"Associated Lane"}
						fcu_objects.append(o)

				done = time.time()
				elapsed = done - start
				# logger.info("FLC25 CEM TPF object retrieval is completed in " + str(elapsed) + " seconds")
				return tracks.time, em_tracks.time, fcu_tracks.time, cem_tpf_fusion_objects,em_objects,fcu_objects

if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"C:\KBData\Python_Toolchain_2\Evaluation_data\LDWS\LD_state\2022-04-12\mi5id786__2022-04-12_14-31-02.h5"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		conti, objects = manager_modules.calc('fillFLC25_CEM_TPF_Fusion@aebs.fill', manager)
		print(objects)
