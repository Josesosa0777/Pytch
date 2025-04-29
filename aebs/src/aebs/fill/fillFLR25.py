# -*- dataeval: init -*-

import numpy as np

from interface import iObjectFill
from measproc.Object import colorByVelocity
from measproc.IntervalList import intervalsToMask

INVALID_TRACK_ID = -1


class cFill(iObjectFill):
		dep = 'fill_flr25_raw_tracks', 'calc_radar_egomotion-flr25'

		def check(self):
				modules = self.get_modules()
				tracks = modules.fill("fill_flr25_raw_tracks")
				egomotion = modules.fill("calc_radar_egomotion-flr25")
				return tracks, egomotion

		def fill(self, tracks, egomotion):
				objects = []
				# loop through all tracks

				for id, track in tracks.iteritems():
						# create object
						o = {}
						o["id"] = np.where(track.range.mask, -1, id)
						o["valid"] = ~track.range.mask

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
						o["label"] = np.array(["FLR25_%d_%s" % (id, obj_type) for id, obj_type in zip(o["id"], object_type.data)])
						# np.array(["CONTI_track_%d_%c" % (id, letter) if id != -1 else "" for (id, letter) in zip(o[
						# "id"],
						# track.which)])
						o["dx"] = track.dx
						o["dy"] = track.dy

						o["type"] = np.where(track.dx.mask,
																 self.get_grouptype('NONE_TYPE'),
																 np.where(track.mov_state.moving,
																					self.get_grouptype('FLR25_MOV'),
																					np.where(track.mov_state.stopped,
																									 self.get_grouptype('FLR25_STOPPED'),
																									 self.get_grouptype('FLR25_STAT'))
																					)
																 )

						init_intervals = [(st, st + 1) for st, end in track.alive_intervals]
						# init_intervals = [(st, st + 1) for st, end in [(x, x + 10) for x in range(248)]]
						o["init"] = intervalsToMask(init_intervals, track.dx.size)
						# ongoing: green, stationary: red, oncoming: blue
						o["color"] = colorByVelocity(egomotion.vx, track.vx,
																				 [0, 255, 0], [255, 0, 0], [0, 0, 255])

						o["ax"] = track.ax.data
						o["ay"] = track.ay.data
						o["vx"] = track.vx.data
						o["vy"] = track.vy.data

						# o["lane"] = track.lane.join()
						o["mov_state"] = track.mov_state.join()
						o["radar_conf"] = track.radar_conf.data
						o["obj_type"] = track.obj_type.join()
						# o["measured_by"] = track.measured_by.join()

						o["custom_labels"] = {'radar_conf': 'Probability Of Existence'}
						objects.append(o)
				return tracks.time, objects


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"C:\KBData\Data\Development\PythonToolchainSupport\ContiMeasurementsSuport\ars_mapping\2020-01-16" \
								r"\CONTI__2020-01-16_13-55-12.mat"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		conti, objects = manager_modules.calc('fillFLR25@aebs.fill', manager)
		print(conti)