# -*- dataeval: init -*-
import logging

import numpy as np
from interface import iObjectFill
from measproc.IntervalList import intervalsToMask
from measproc.Object import colorByVelocity
from pyutils.cache_manager import get_modules_cache, store_modules_cache

logger = logging.getLogger('fillFLC25_CEM_TPF_MG_AOA_ACC')

INVALID_ID = 255


class cFill(iObjectFill):
		dep = 'fill_flc25_cem_tpf_tracks','fill_flc25_aoa_acc_tracks', 'calc_egomotion'

		def check(self):
				modules = self.get_modules()
				cem_tpf_tracks, _ = modules.fill("fill_flc25_cem_tpf_tracks")
				aoa_acc_tracks = modules.fill("fill_flc25_aoa_acc_tracks")
				ego_orig = modules.fill("calc_egomotion")
				egomotion = ego_orig.rescale(cem_tpf_tracks.time)
				return cem_tpf_tracks, aoa_acc_tracks, egomotion

		def fill(self, cem_tpf_tracks,aoa_acc_tracks, egomotion):
				import time
				start = time.time()
				logger.info("FLC25 CEM TPF with AOA ACC selection object retrieval is started, Please wait...")
				objects = []
				aoa_acc_track = aoa_acc_tracks[0]
				for id, track in cem_tpf_tracks.iteritems():

						o = {}
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
										["FLC25_CEM_TPF_MG_AOA_ACC_%d_%s" % (index, obj_type) for index, obj_type in zip(o["id"], object_type.data)])
						track.dx.data[track.dx.mask] = 0
						track.dy.data[track.dy.mask] = 0
						o["dx"] = track.dx.data
						o["dy"] = track.dy.data
						o["type"] = np.where(track.mov_state.stat.data & ~track.mov_state.stat.mask,
																 self.get_grouptype('FLC25_CEM_TPF_MG_AOA_ACC_STAT'),
																 self.get_grouptype('FLC25_CEM_TPF_MG_AOA_ACC_MOV'))
						init_intervals = [(st, st + 1) for st, end in track.alive_intervals]
						o["init"] = intervalsToMask(init_intervals, track.dx.size)
						# ongoing: green, stationary: red, oncoming: blue
						o["color"] = colorByVelocity(egomotion.vx, track.vx.data, [0, 255, 0], [255, 0, 0], [0, 0, 255])  # [R,  G, B]
						color_mask = np.reshape(np.repeat(aoa_acc_track.object_id.data == id, 3),	(-1, 3))
						o["color"] = np.where(color_mask, [255, 0, 255], o["color"])  #

						o["ax_abs"] = track.ax_abs.data
						o["ay_abs"] = track.ay_abs.data
						o["ax"] = track.ax.data
						o["ay"] = track.ay.data
						o["vx_abs"] = track.vx_abs.data
						o["vy_abs"] = track.vy_abs.data
						o["vx"] = track.vx.data
						o["vy"] = track.vy.data

						o["lane"] = track.lane.join()
						o["mov_state"] = track.mov_state.join()
						o["video_conf"] = track.video_conf.data
						o["lane_conf"]= track.lane_conf.data
						o["obj_type"] = track.obj_type.join()
						o["measured_by"] = track.measured_by.join()
						o["contributing_sensors"] = track.contributing_sensors.join()
						o["custom_labels"] = {'video_conf': 'Probability Of Existence',"lane" :"Associated Lane","lane_conf" : "Associated Lane Confidence"}
						# for index in range(len(aoa_acc_track.object_id)):
						# 	if aoa_acc_track.object_id.data[index] == id:
						# 		print(id)
						# 		print(index)
						# 		print(o["color"][index])
						# 		o["color"][index]=[0, 255, 0]
						# 		print(o["color"][index])
						# 		o["label"][index] = "HI"
						objects.append(o)

				done = time.time()
				elapsed = done - start
				# logger.info("FLC25 CEM TPF object retrieval is completed in " + str(elapsed) + " seconds")
				return cem_tpf_tracks.time, objects


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"C:\KBData\Data\Development\PythonToolchainSupport\ContiMeasurementsSuport\aoa_acc_issue\mi5id787__2021-08-04_14-13-53.h5"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		conti, objects = manager_modules.calc('fillFLC25_CEM_TPF_MG_AOA_ACC@aebs.fill', manager)
		print(objects)
