# -*- dataeval: init -*-

import logging

import numpy as np
from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList
from measproc.report2 import Report

logger = logging.getLogger('search_events_aebsresimcsvoutput')


class Search(iSearch):
		dep = "calc_common_time-aebsresimcsvoutputeval@aebs.fill", "calc_aebs_resim_csv_output@aebs.fill",

		def fill(self):
				reports = []
				self.time = self.modules.fill(self.dep[0])
				report_list = self.modules.fill(self.dep[1])
				if report_list == 0:
						logger.info("No labels to add")
						return None

				for item in report_list:
						self.quantity_group = 'AEBS resim'
						quanames = self.batch.get_quanamegroup(self.quantity_group)
						report = Report(cIntervalList(self.time), 'AEBS warnings')
						interval = self.get_index((long(item["start_time_abs"]), long(item["end_time_abs"]),))
						idx = report.addInterval(interval)
						report.setNames(self.quantity_group, quanames)
						report.set(idx, self.quantity_group, 'ego_velocity_x', item['ego_velocity_x'])
						report.set(idx, self.quantity_group, 'obj_width', item['obj_width'])
						report.set(idx, self.quantity_group, 'obj_length', item['obj_length'])
						report.set(idx, self.quantity_group, 'obj_distance_x', item['obj_distance_x'])
						report.set(idx, self.quantity_group, 'obj_distance_y', item['obj_distance_y'])
						report.set(idx, self.quantity_group, 'obj_relative_velocity_x', item['obj_relative_velocity_x'])
						report.set(idx, self.quantity_group, 'obj_relative_velocity_y', item['obj_relative_velocity_y'])
						report.set(idx, self.quantity_group, 'object_id', item['object_id'])
						report.set(idx, self.quantity_group, 'e_dynamic_property', item['e_dynamic_property'])
						report.set(idx, self.quantity_group, 'ui_stopped_confidence', item['ui_stopped_confidence'])
						reports.append(report)

				return reports

		def get_index(self, interval):
				st_time, ed_time = interval
				st_time = st_time / 1000000.0
				ed_time = ed_time / 1000000.0
				st_index = (np.abs(self.time - st_time)).argmin()
				ed_index = (np.abs(self.time - ed_time)).argmin()
				if st_index == ed_index:
						ed_index += 1
				return (st_index, ed_index)

		def search(self, reports):
				for report in reports:
						self.batch.add_entry(report)
				return
