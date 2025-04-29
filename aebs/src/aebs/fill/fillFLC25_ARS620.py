# -*- dataeval: init -*-
import logging

import numpy as np
from interface import iObjectFill
from measproc.IntervalList import intervalsToMask
from measproc.Object import colorByVelocity

logger = logging.getLogger('fillFLC25_ARS620')

INVALID_ID = -1


class cFill(iObjectFill):
		dep = 'fill_flc25_ars620_tracks', 'calc_egomotion'

		def check(self):
				modules = self.get_modules()
				tracks, signals = modules.fill("fill_flc25_ars620_tracks")
				ego_orig = modules.fill("calc_egomotion")
				egomotion = ego_orig.rescale(tracks.time)
				return tracks,signals, egomotion

		def fill(self, tracks,signals, egomotion):

				objects = []
				# loop through all tracks
				for id, track in tracks.iteritems():
						# create object
						o = {}
						o["signal_mapping"] = {}
						o["id"] = np.where(track.dx.mask, INVALID_ID, id)
						o["valid"] = track.tr_state.valid.data & ~track.tr_state.valid.mask

						o["label"] = np.array(
							["FLC25_ARS620_%d_%d" % (idx, general_uid) for idx,  general_uid in
							 zip(o["id"], track.general_uid.data)])
						track.dx.data[track.dx.mask] = 0
						track.dy.data[track.dy.mask] = 0
						o["dx"] = track.dx.data
						o["signal_mapping"]["dx"] = signals[id][0]["distX"]
						o["dy"] = track.dy.data
						o["signal_mapping"]["dy"] = signals[id][0]["distY"]
						o["type"] = np.where(track.mov_state.stat.data & ~track.mov_state.stat.mask,
																 self.get_grouptype('FLC25_ARS620_STAT'),
																 self.get_grouptype('FLC25_ARS620_MOV'))
						init_intervals = [(st, st + 1) for st, end in track.alive_intervals]
						o["init"] = intervalsToMask(init_intervals, track.dx.size)
						# ongoing: green, stationary: red, oncoming: blue
						o["color"] = colorByVelocity(egomotion.vx, track.vx.data,
																				 [0, 255, 0], [255, 0, 0], [0, 0, 255])  # [R, G, B]

						# Extra changes

						# Object Kinematic
						o["ax_abs"] = track.ax_abs.data
						o["signal_mapping"]["ax_abs"] = signals[id][0]["absAccelX"]
						o["ay_abs"] = track.ay_abs.data
						o["signal_mapping"]["ay_abs"] = signals[id][0]["absAccelY"]
						o["ax"] = track.ax.data
						o["signal_mapping"]["ax"] = signals[id][0]["relAccelX"]
						o["ay"] = track.ay.data
						o["signal_mapping"]["ay"] = signals[id][0]["relAccelY"]
						o["vx_abs"] = track.vx_abs.data
						o["signal_mapping"]["vx_abs"] = signals[id][0]["absVelX"]
						o["vy_abs"] = track.vy_abs.data
						o["signal_mapping"]["vy_abs"] = signals[id][0]["absVelY"]
						o["vx"] = track.vx.data
						o["signal_mapping"]["vx"] = signals[id][0]["relVelX"]
						o["vy"] = track.vy.data
						o["signal_mapping"]["vy"] = signals[id][0]["relVelY"]

						o["mov_state"] = track.mov_state.join()
						o["maintenance_state"] = track.maintenance_state.join()
						o["signal_mapping"]["mov_state"] = signals[id][0][
							"dynamicProperty"]
						o["video_conf"] = track.video_conf.data
						o["signal_mapping"]["video_conf"] = signals[id][0][
							"existProbability"]

						o["custom_labels"] = {'video_conf': 'Probability Of Existence',"lane" :"Associated Lane"}
						objects.append(o)
				return tracks.time, objects


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"C:\KBData\Pytch2_evaluation_data\ARS620_radar_evaluation\mi5id5511__2024-08-06_12-44-33.h5"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		conti, objects = manager_modules.calc('fillFLC25_ARS620@aebs.fill', manager)
		print(objects)
