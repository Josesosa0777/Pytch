# -*- dataeval: init -*-

import numpy as np

from interface import iObjectFill
from measproc.IntervalList import intervalsToMask

from measproc.Object import colorByBitField

INVALID_ID = -1

class cFill(iObjectFill):
		dep = 'fill_flc25_aebs_first_obj', 'calc_egomotion'

		def check(self):
				modules = self.get_modules()
				tracks = modules.fill("fill_flc25_aebs_first_obj")
				ego_orig = modules.fill("calc_egomotion")
				egomotion = ego_orig.rescale(tracks.time)
				return tracks, egomotion

		def fill(self, tracks, egomotion):
				objects = []
				for id, track in tracks.iteritems():
						o = {}
						track.object_id.data[track.object_id.mask] = 0
						o["id"] = np.where(track.dx.mask, INVALID_ID, track.object_id) # np.where(track.id.mask, INVALID_TRACK_ID, track.id.data)
						o["valid"] = track.tr_state.valid.data & ~track.tr_state.valid.mask
						o["label"] = np.array( ["FLC25_MLAEB_RIGHT_FIRST_OBJ_%d" %id for id in o["id"]] )
						track.dx.data[track.dx.mask] = 0
						track.dy.data[track.dy.mask] = 0
						o["dx"] = track.dx.data
						o["dy"] = track.dy.data
						o["type"] = np.where(track.id.mask,
								self.get_grouptype('NONE_TYPE'),
								self.get_grouptype('FLC25_MLAEB_RIGHT_FIRST_OBJ'))
						init_intervals = [(st, st + 1) for st, end in track.alive_intervals]
						o["init"] = intervalsToMask(init_intervals, track.dx.size)
						o["color"] = colorByBitField(track.bitfield_value.data, [0, 255, 0], [255, 0, 0])
						o["vx"] = track.vx.data
						o["vy"] = track.vy.data
						o["mov_state"] = track.mov_state.join()
						o["measured_by"] = track.measured_by.join()
						objects.append(o)
				return tracks.time, objects


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"C:\Users\wattamwa\Desktop\measurments\bitfield_aebs\new\mi5id787__2022-02-15_07-13-31.h5"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		time,objects = manager_modules.calc('fillFLC25_AEBS_FIRST_OBJ@aebs.fill', manager)
		print(objects)