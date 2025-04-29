# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import csv
import logging

from interface import iCalc

logger = logging.getLogger('calc_fcw_resim_csv_output')


class cFill(iCalc):

		def check(self):
				source = self.get_source()
				data = []
				column_names = []
				try:
						with open("".join(source.FileName.split(".")[:-1]) + ".csv") as csv_file:
								csv_file_object = csv.reader(csv_file)

								column_list = next(csv_file_object)
								column_names = column_list[0].split(";")

								for row in csv_file_object:
										data.append(row[0].split(";"))
				except:
						logger.error(
								"Resimulation output of FCW i.e csv file not found, Keep the csv file along with the measurement")

				return data, column_names

		def fill(self, data, column_names):
			fcw_events = []

			for row in data:
					fcw_event = {}
					fcw_event['measurement_file'] = row[0]
					fcw_event['start_time'] = row[1]
					fcw_event['end_time'] = row[2]
					fcw_event['start_time_abs'] = row[3]
					fcw_event['end_time_abs'] = row[4]
					fcw_event['event_duration'] = row[5]
					fcw_event['event_type'] = row[6]
					fcw_event['ego_velocity_x'] = row[7]
					fcw_event['obj_width'] = row[8]
					fcw_event['obj_length'] = row[9]
					fcw_event['obj_distance_x'] = row[10]
					fcw_event['obj_distance_y'] = row[11]
					fcw_event['obj_relative_velocity_x'] = row[12]
					fcw_event['obj_relative_velocity_y'] = row[13]
					fcw_event['object_id'] = row[14]
					fcw_event['e_dynamic_property'] = row[15]
					fcw_event['ui_stopped_confidence'] = row[16]
					fcw_event['safety_distance'] = row[17]
					fcw_event['obj_rcs'] = row[18]
					fcw_event['obj_ttc'] = row[19]
					fcw_event['obj_quality'] = row[20]
					fcw_event['obj_qualifier'] = row[21]
					fcw_event['obj_class'] = row[22]
					fcw_event['obj_lane_info'] = row[23]
					fcw_event['obj_proj_dist_y'] = row[24]
					fcw_event['obj_life_time'] = row[25]

					fcw_events.append(fcw_event)

			return fcw_events


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"C:\KBData\Measurement\fcw_test\test\2020-11-03\UFO__2020-11-03_17-24-58.mat"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		flr25_common_time = manager_modules.calc('calc_fcw_resim_csv_output@aebs.fill', manager)
		print (flr25_common_time)
