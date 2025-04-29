# -*- dataeval: init -*-

import numpy as np

from interface import iObjectFill
from measproc.Object import colorByVelocity
from measproc.IntervalList import intervalsToMask

INVALID_ID = -1


class cFill(iObjectFill):
		dep = 'calc_acc_ped_resim_output', 'calc_radar_egomotion-flr25'

		def check(self):
				modules = self.get_modules()
				acc_ped_events,time = modules.fill("calc_acc_ped_resim_output")
				egomotion = modules.fill("calc_radar_egomotion-flr25")
				return acc_ped_events, time, egomotion

		def fill(self, acc_ped_events, time, egomotion):
				# create object
				o = {}
				mask = np.zeros(len(time),dtype=bool)
				dx = np.zeros(len(time))
				dy = np.zeros(len(time))
				vx = np.zeros(len(time))

				alive_intervals = []

				for event in acc_ped_events:
						interval = self.get_index((long(event["Start Time Abs"]), long(event["End Time Abs"]),), time)
						mask[interval[0]:interval[1]]=True
						dx[interval[0]:interval[1]] = event["obj_distance_x"]
						dy[interval[0]:interval[1]] = event["obj_distance_y"]
						vx[interval[0]:interval[1]] = event["obj_relative_velocity_x"]

						alive_intervals.append((interval[0],interval[1]))

				o["dx"] = np.ma.array(dx, mask=~mask)
				o["dy"] = np.ma.array(dy, mask=~mask)
				o["vx"] = np.ma.array(vx, mask=~mask)
				o["id"] = np.where(~mask, INVALID_ID, 0)  # np.where(track.id.mask, INVALID_TRACK_ID, track.id.data)
				o["valid"] = mask
				o["label"] = np.array(["FLR25_ACC_PED_%d" % id for id in o["id"]])

				o["type"] = np.where(~mask,
						self.get_grouptype('NONE_TYPE'),
						self.get_grouptype('FLR25_ACC_PED'))
				init_intervals = [(st, st + 1) for st, end in alive_intervals]
				o["init"] = intervalsToMask(init_intervals, len(time))
				o["color"] = colorByVelocity(egomotion.vx, o["vx"], [0, 255, 0], [255, 0, 0], [0, 0, 255])
				objects = [o]
				return time, objects

		def get_index(self, interval, time):
				st_time, ed_time = interval
				st_time = st_time / 1000000.0
				ed_time = ed_time / 1000000.0
				start_index = (np.abs(time - st_time)).argmin()
				end_index = (np.abs(time - ed_time)).argmin()
				if start_index == end_index:
						end_index += 1
				return (start_index, end_index)


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"C:\KBData\Measurement\oliver_endurance_run\2021-04-21\mi5id787__2021-04-21_13-07-33.mat"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		conti, objects = manager_modules.calc('fillFLR25_accped@aebs.fill', manager)
		print(conti)