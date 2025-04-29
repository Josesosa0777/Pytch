# -*- dataeval: init -*-

import numpy as np
from interface.Interfaces import iSearch
from measparser.filenameparser import FileNameParser
from measproc.IntervalList import cIntervalList
from measproc.report2 import Report


class Search(iSearch):
		dep = {
				'yaca_hits': 'calc_database_hits_from_yaca@aebs.fill'
		}

		def fill(self):
				yaca_event, common_time = self.modules.fill(self.dep['yaca_hits'])

				try:
						measurement_file_name = FileNameParser(self.source.BaseName).date_underscore
				except:
						measurement_file_name = self.source.BaseName.replace('.', '-').replace('_at_', '_').rsplit('_', 2)[0]
				# valid_intervals = []
				yaca_valid_data = self.data_preprocessing(measurement_file_name, yaca_event)

				YACA_verdict = 'YACA Verdict'
				Status = 'Status'
				Trigger = 'Trigger'
				votes = self.batch.get_labelgroups(YACA_verdict, Status, Trigger)
				report = Report(cIntervalList(common_time), 'ACC event', votes = votes)

				for yaca_db_hit in yaca_valid_data:
						event_idx_interval = self.get_index((float(yaca_db_hit["CanTime"]), float(yaca_db_hit["EndTime"])),common_time)
						event_verdict = yaca_db_hit['Verdict']
						event_status = yaca_db_hit['Status']
						event_trigger = yaca_db_hit['Name']
						idx = report.addInterval(event_idx_interval)
						report.vote(idx, YACA_verdict, event_verdict)
						report.vote(idx, Status, event_status)
						report.vote(idx, Trigger, event_trigger)

				return report

		def data_preprocessing(self, measurement_file_name, yaca_event):
				valid_data_from_csv = []

				for rows_from_yaca_csv in yaca_event:
						measurement_name_from_csv = ""
						if 'camera' in rows_from_yaca_csv['DateTime']:
								measurement_name_from_csv = rows_from_yaca_csv['DateTime'].replace('.','-').replace('_at_','_').split('_camera')[0]
						elif 'radar' in rows_from_yaca_csv['DateTime']:
								measurement_name_from_csv = rows_from_yaca_csv['DateTime'].replace('.','-').replace('_at_','_').split('_radar')[0]
						if measurement_name_from_csv == measurement_file_name:
								valid_data_from_csv.append(rows_from_yaca_csv)
				return valid_data_from_csv

		def get_index(self, interval_time, time):
				st_time, ed_time = interval_time
				# st_time = st_time / 1000000.0
				# ed_time = ed_time / 1000000.0
				start_index = (np.abs(time - st_time)).argmin()
				end_index = (np.abs(time - ed_time)).argmin() + 1
				if start_index == end_index:
						end_index += 1
				return (start_index, end_index,)

		def search(self, report):
				self.batch.add_entry(report)
				return
