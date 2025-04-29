# -*- dataeval: init -*-
import logging
import numpy.ma as ma
import numpy as np
from interface import iObjectFill
from measproc.IntervalList import intervalsToMask
from measproc.Object import colorByVelocity
from pyutils.cache_manager import get_modules_cache, store_modules_cache

logger = logging.getLogger('fillFLC25_AOA_ACC')

INVALID_ID = 255


class cFill(iObjectFill):
		dep = 'fill_flc25_aoa_acc_tracks','fill_flc25_cem_tpf_tracks', 'calc_egomotion'

		def check(self):
				modules = self.get_modules()
				tracks_aoa_acc = modules.fill("fill_flc25_aoa_acc_tracks")
				tracks_cem_tpf, _ = modules.fill("fill_flc25_cem_tpf_tracks")
				ego_orig = modules.fill("calc_egomotion")
				egomotion = ego_orig.rescale(tracks_aoa_acc.time)
				return tracks_aoa_acc,tracks_cem_tpf, egomotion

		def fill(self, tracks_aoa_acc, tracks_cem_tpf, egomotion):
				import time
				start = time.time()
				logger.info("FLC25  AOA ACC object retrieval is started, Please wait...")
				objects = []
				for id, track_aoa_acc in tracks_aoa_acc.iteritems():
						# cem_track = tracks_cem_tpf[id]
						o = {}
						o["id"] = track_aoa_acc.object_id #np.where(track_aoa_acc.dx.mask, INVALID_ID, id)
						o["valid"] = track_aoa_acc.tr_state.valid.data & ~track_aoa_acc.tr_state.valid.mask
						track_aoa_acc.dx.data[track_aoa_acc.dx.mask] = 0
						track_aoa_acc.dy.data[track_aoa_acc.dy.mask] = 0
						o["dx"] = track_aoa_acc.dx.data
						o["dy"] = track_aoa_acc.dy.data
						init_intervals = [(st, st + 1) for st, end in track_aoa_acc.alive_intervals]
						o["init"] = intervalsToMask(init_intervals, track_aoa_acc.dx.size)
						# ongoing: green, stationary: red, oncoming: blue
						o["color"] = colorByVelocity(egomotion.vx, track_aoa_acc.vx.data,
																				 [0, 255, 0], [255, 0, 0], [0, 0, 255])  # [R, G, B]

						o["ax_abs"] = track_aoa_acc.ax_abs.data
						o["vx_abs"] = track_aoa_acc.vx_abs.data
						o["vx"] = track_aoa_acc.vx.data

						new_object_type = ma.array(np.zeros(track_aoa_acc.dx.shape), mask = track_aoa_acc.dx.mask)
						new_move_state = ma.array(np.zeros(track_aoa_acc.dx.shape), mask = track_aoa_acc.dx.mask)
						new_vy_abs = ma.array(np.zeros(track_aoa_acc.dx.shape), mask = track_aoa_acc.dx.mask)
						new_vy = ma.array(np.zeros(track_aoa_acc.dx.shape), mask = track_aoa_acc.dx.mask)
						new_lane = ma.array(np.zeros(track_aoa_acc.dx.shape), mask = track_aoa_acc.dx.mask)
						new_ay_abs = ma.array(np.zeros(track_aoa_acc.dx.shape), mask = track_aoa_acc.dx.mask)
						new_video_conf = ma.array(np.zeros(track_aoa_acc.dx.shape), mask = track_aoa_acc.dx.mask)
						new_lane_conf = ma.array(np.zeros(track_aoa_acc.dx.shape), mask = track_aoa_acc.dx.mask)
						new_measured_by = ma.array(np.zeros(track_aoa_acc.dx.shape), mask = track_aoa_acc.dx.mask)
						new_contributing_sensors = ma.array(np.zeros(track_aoa_acc.dx.shape), mask = track_aoa_acc.dx.mask)
						new_ax = ma.array(np.zeros(track_aoa_acc.dx.shape), mask = track_aoa_acc.dx.mask)
						new_ay = ma.array(np.zeros(track_aoa_acc.dx.shape), mask = track_aoa_acc.dx.mask)

						for index in range(len(track_aoa_acc.object_id)):
							for id, track in tracks_cem_tpf.iteritems():
								if track_aoa_acc.object_id.data[index]==id:
									obj_type = track.obj_type.join()
									new_object_type[index]=obj_type.data[index]

									mov_state = track.mov_state.join()
									new_move_state[index] = mov_state.data[index]
									new_vy_abs[index] = track.vy_abs.data[index]
									new_vy[index] = track.vy.data[index]
									lane = track.lane.join()
									new_lane[index] = lane.data[index]
									new_ay_abs[index]= track.ay_abs.data[index]
									new_ax[index] = track.ax.data[index]
									new_ay[index] = track.ay.data[index]
									new_video_conf[index] = track.video_conf.data[index]
									new_lane_conf[index] = track.lane_conf.data[index]
									new_measured_by[index] = track.measured_by.join().data[index]
									new_contributing_sensors[index]=track.contributing_sensors.join().data[index]

						object_type = np.empty(track_aoa_acc.dx.shape, dtype = 'string')
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
										["FLC25_AOA_ACC%d_%s" % (id, obj_type) for id, obj_type in zip(o["id"], object_type)])

						o["type"] = np.where(new_move_state.data==0 & ~new_move_state.mask,
																 self.get_grouptype('FLC25_AOA_ACC_STAT'),
																 self.get_grouptype('FLC25_AOA_ACC_MOV'))

						o["vy_abs"] = new_vy_abs
						o["ay_abs"] = new_ay_abs
						o["vy"] = new_vy
						o["ay"] = new_ay
						o["ax"] = new_ax
						o["lane"] = new_lane
						o["mov_state"] = new_move_state
						o["obj_type"] = new_object_type
						o["video_conf"] = new_video_conf
						o["lane_conf"] = new_lane_conf
						o["measured_by"] = new_measured_by
						o["contributing_sensors"] = new_contributing_sensors
						o["custom_labels"] = {'video_conf': 'Probability Of Existence'}

						objects.append(o)
				done = time.time()
				elapsed = done - start
				logger.info("FLC25 AOA ACC object retrieval is completed in " + str(elapsed) + " seconds")
				return tracks_aoa_acc.time, objects


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"C:\KBData\Data\Development\PythonToolchainSupport\ContiMeasurementsSuport\aoa_acc_issue\mi5id787__2021-08-04_14-13-53.h5"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		conti, objects = manager_modules.calc('fillFLC25_AOA_ACC@aebs.fill', manager)
		print(objects)
