# -*- dataeval: init -*-
import logging

import numpy as np
from interface import iObjectFill
from measproc.IntervalList import intervalsToMask
from measproc.Object import colorByVelocity
from numpy import ma
from pyutils.cache_manager import get_modules_cache, store_modules_cache

logger = logging.getLogger('fillFLC25_AOA_AEBS')

INVALID_ID = 255


class cFill(iObjectFill):
		dep = 'fill_flc25_aoa_aebs_tracks','fill_flc25_cem_tpf_tracks', 'calc_egomotion'

		def check(self):
				modules = self.get_modules()
				tracks = modules.fill("fill_flc25_aoa_aebs_tracks")
				tracks_cem_tpf, _ = modules.fill("fill_flc25_cem_tpf_tracks")
				ego_orig = modules.fill("calc_egomotion")
				egomotion = ego_orig.rescale(tracks.time)
				return tracks, tracks_cem_tpf, egomotion

		def fill(self, tracks, tracks_cem_tpf, egomotion):
				import time
				start = time.time()
				logger.info("FLC25  AOA AEBS object retrieval is started, Please wait...")
				objects = []
				for id, track_aoa_aeb in tracks.iteritems():
						o = {}
						o["id"] = track_aoa_aeb.object_id
						o["valid"] = track_aoa_aeb.tr_state.valid.data & ~track_aoa_aeb.tr_state.valid.mask
						track_aoa_aeb.dx.data[track_aoa_aeb.dx.mask] = 0
						track_aoa_aeb.dy.data[track_aoa_aeb.dy.mask] = 0
						o["dx"] = track_aoa_aeb.dx.data
						o["dy"] = track_aoa_aeb.dy.data
						o["type"] = np.where(track_aoa_aeb.mov_state.stat.data & ~track_aoa_aeb.mov_state.stat.mask,
																 self.get_grouptype('FLC25_AOA_AEBS_STAT'),
																 self.get_grouptype('FLC25_AOA_AEBS_MOV'))
						init_intervals = [(st, st + 1) for st, end in track_aoa_aeb.alive_intervals]
						o["init"] = intervalsToMask(init_intervals, track_aoa_aeb.dx.size)
						# ongoing: green, stationary: red, oncoming: blue
						o["color"] = colorByVelocity(egomotion.vx, track_aoa_aeb.vx.data,
																				 [0, 255, 0], [255, 0, 0], [0, 0, 255])  # [R, G, B]
						o["ax_abs"] = track_aoa_aeb.ax_abs.data
						o["ax"] = track_aoa_aeb.ax.data
						o["vx"] = track_aoa_aeb.vx.data
						o["vy"] = track_aoa_aeb.vy.data
						o["mov_state"] = track_aoa_aeb.mov_state.join()

						new_object_type = ma.array(np.zeros(track_aoa_aeb.dx.shape), mask = track_aoa_aeb.dx.mask)
						new_vy_abs = ma.array(np.zeros(track_aoa_aeb.dx.shape), mask = track_aoa_aeb.dx.mask)
						new_vx_abs = ma.array(np.zeros(track_aoa_aeb.dx.shape), mask = track_aoa_aeb.dx.mask)
						new_lane = ma.array(np.zeros(track_aoa_aeb.dx.shape), mask = track_aoa_aeb.dx.mask)
						new_ay_abs = ma.array(np.zeros(track_aoa_aeb.dx.shape), mask = track_aoa_aeb.dx.mask)
						new_ay = ma.array(np.zeros(track_aoa_aeb.dx.shape), mask = track_aoa_aeb.dx.mask)
						new_video_conf = ma.array(np.zeros(track_aoa_aeb.dx.shape), mask = track_aoa_aeb.dx.mask)
						new_lane_conf = ma.array(np.zeros(track_aoa_aeb.dx.shape), mask = track_aoa_aeb.dx.mask)
						new_measured_by = ma.array(np.zeros(track_aoa_aeb.dx.shape), mask = track_aoa_aeb.dx.mask)
						new_contributing_sensors = ma.array(np.zeros(track_aoa_aeb.dx.shape), mask = track_aoa_aeb.dx.mask)
						for index in range(len(track_aoa_aeb.object_id)):
								for id, track in tracks_cem_tpf.iteritems():
										if track_aoa_aeb.object_id.data[index] == id:
												obj_type = track.obj_type.join()
												new_object_type[index] = obj_type.data[index]
												new_vy_abs[index] = track.vy_abs.data[index]
												new_vx_abs[index] = track.vx_abs.data[index]
												lane = track.lane.join()
												new_lane[index] = lane.data[index]
												new_ay_abs[index] = track.ay_abs.data[index]
												new_ay[index] = track.ay.data[index]
												new_video_conf[index] = track.video_conf.data[index]
												new_lane_conf[index] = track.lane_conf.data[index]
												new_measured_by[index] = track.measured_by.join().data[index]
												new_contributing_sensors[index] = track.contributing_sensors.join().data[index]
						object_type = np.empty(track_aoa_aeb.dx.shape, dtype = 'string')
						object_type[:] = 'U'
						object_type[new_object_type.data == 0] = 'C'
						object_type[new_object_type.data == 1] = 'T'
						object_type[new_object_type.data == 2] = 'M'
						object_type[new_object_type.data == 3] = 'P'
						object_type[new_object_type.data == 4] = 'B'
						object_type[new_object_type.data == 5] = 'U'
						object_type[new_object_type.data == 6] = 'POINT'
						object_type[new_object_type.data == 7] = 'WIDE'

						o["label"] = np.array(
										["FLC25_AOA_AEBS%d_%s" % (id, obj_type) for id, obj_type in zip(o["id"], object_type)])
						o["vx_abs"] = new_vx_abs
						o["vy_abs"] = new_vy_abs
						o["lane"] = new_lane
						o["obj_type"] = new_object_type
						o["ay_abs"] = new_ay_abs
						o["ay"] = new_ay
						o["video_conf"] = new_video_conf
						o["lane_conf"] = new_lane_conf
						o["measured_by"] = new_measured_by
						o["contributing_sensors"] = new_contributing_sensors
						o["custom_labels"] = {'video_conf': 'Probability Of Existence'}
						objects.append(o)
				done = time.time()
				elapsed = done - start
				logger.info("FLC25 AOA AEBS object retrieval is completed in " + str(elapsed) + " seconds")
				return tracks.time, objects


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"\\pu2w6168\shared-drive\measurements\pAEBS\new_requirment\HMC-QZ-STR__2021-02-16_09-40-07.mat"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		conti, objects = manager_modules.calc('fillFLC25_AOA_AEBS@aebs.fill', manager)
		print(objects)
