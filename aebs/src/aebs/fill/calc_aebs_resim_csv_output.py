# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import csv
import logging

from interface import iCalc

logger = logging.getLogger('calc_aebs_resim_csv_output')


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
								"Resimulation output of AEB i.e csv file not found, Keep the csv file along with the measurement")

				return data, column_names

		def fill(self, data, column_names):
				aebs_events = []

				for row in data:
						aebs_event = {}
						aebs_event['measurement_file'] = row[0]
						aebs_event['start_time_abs'] = row[3]
						aebs_event['end_time_abs'] = row[4]
						aebs_event['event_duration'] = row[5]
						aebs_event['event_type'] = row[6]
						aebs_event['ego_velocity_x'] = row[7]
						aebs_event['obj_width'] = row[8]
						aebs_event['obj_length'] = row[9]
						aebs_event['obj_distance_x'] = row[10]
						aebs_event['obj_distance_y'] = row[11]
						aebs_event['obj_relative_velocity_x'] = row[12]
						aebs_event['obj_relative_velocity_y'] = row[13]
						aebs_event['object_id'] = row[14]
						aebs_event['e_dynamic_property'] = row[15]
						aebs_event['ui_stopped_confidence'] = row[16]
						aebs_events.append(aebs_event)

				return aebs_events


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"C:\KBData\report\Resimulation_integration\CONTI__2019-08-21_08-45-57.mat"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		flr25_common_time = manager_modules.calc('calc_csv_data@aebs.fill', manager)
		print (flr25_common_time)
