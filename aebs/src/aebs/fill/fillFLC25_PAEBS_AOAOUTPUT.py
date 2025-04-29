# -*- dataeval: init -*-
import logging

import numpy as np
from interface import iObjectFill
from measproc.IntervalList import intervalsToMask
from measproc.Object import colorByVelocity
from pyutils.cache_manager import get_modules_cache, store_modules_cache

logger = logging.getLogger('fillFLC25_PAEBS_AOAOUTPUT')

INVALID_ID = 300


class cFill(iObjectFill):
		dep = 'fill_flc25_paebs_aoaoutput_tracks', 'calc_egomotion'

		def check(self):
				modules = self.get_modules()
				tracks = modules.fill("fill_flc25_paebs_aoaoutput_tracks")
				ego_orig = modules.fill("calc_egomotion")
				egomotion = ego_orig.rescale(tracks.time)
				return tracks, egomotion

		def fill(self, tracks, egomotion):
				import time
				start = time.time()
				logger.info("FLC25 PAEBS AOA object retrieval is started, Please wait...")
				objects = []
				for id, track in tracks.iteritems():
						o = {}
						o["id"] = np.where(track.dx.mask, INVALID_ID, id)
						o["valid"] = track.tr_state.valid.data & ~track.tr_state.valid.mask

						o["label"] = np.array(
										["FLC25_PAEBS_AOA_%d" % (id) for id in zip(o["id"])])
						track.dx.data[track.dx.mask] = 0
						track.dy.data[track.dy.mask] = 0
						o["dx"] = track.dx.data
						o["dy"] = track.dy.data
						o["type"] = np.where(track.mov_state.stat.data & ~track.mov_state.stat.mask,
																 self.get_grouptype('FLC25_PAEBS_AOAOUTPUT_STAT'),
																 self.get_grouptype('FLC25_PAEBS_AOAOUTPUT_MOV'))
						init_intervals = [(st, st + 1) for st, end in track.alive_intervals]
						o["init"] = intervalsToMask(init_intervals, track.dx.size)
						# ongoing: green, stationary: red, oncoming: blue
						o["color"] = colorByVelocity(egomotion.vx, track.vx.data,
																				 [0, 255, 0], [255, 0, 0], [0, 0, 255])  # [R, G, B]


						o["vx_abs"] = track.vx_abs.data
						o["vy_abs"] = track.vy_abs.data
						o["vx"] = track.vx.data

						o["lane"] = track.lane.join()
						o["mov_state"] = track.mov_state.join()




						objects.append(o)
				done = time.time()
				elapsed = done - start
				logger.info("FLC25 PAEBS AOA object retrieval is completed in " + str(elapsed) + " seconds")
				return tracks.time, objects


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"\\pu2w6168\shared-drive\measurements\pAEBS\new_requirment\HMC-QZ-STR__2021-02-16_09-40-07.mat"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		conti, objects = manager_modules.calc('fillFLC25_PAEBS_AOAOUTPUT@aebs.fill', manager)
		print(objects)
