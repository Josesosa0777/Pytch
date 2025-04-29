# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

from interface import iCalc
from collections import OrderedDict
import logging
import os
CONFIG_DIRECTORY = os.path.join(os.path.dirname(__file__), "config")
logger = logging.getLogger("calc_json_data")

class cFill(iCalc):

		def check(self):
				return

		def fill(self, marker_data):
				marker_data = {}
				source = self.get_source()
				import json
				try:
						f = open("".join(source.FileName.split(".")[:-1]) + ".json")
						marker_data = json.load(f)
						f.close()
				except:
						logger.warning("Postmarker data not found, Place the json file along with the input measurement")

				meta_info_reports = []
				if 'Meta Information' in marker_data:
						label_metadata = marker_data['Meta Information']
						recording_name = marker_data['Meta Information']["Recording Name"]
						del label_metadata["Recording Name"]
						markers = [str(x) for x in sorted([int(label) for label in label_metadata.keys()])]
						tmp_label_metadata = OrderedDict()
						# Prepare ordered dict to iterate on
						for key in markers:
								tmp_label_metadata[key] = label_metadata[key]

						for row_index, value in tmp_label_metadata.items():
								pytch_report = {}
								marker = []
								if row_index not in markers:
										continue
								if  "Single" in value:
										pytch_report["Name"] = value[0]
										pytch_report["Value"] = value[1]
										pytch_report["Start"] = row_index
										pytch_report["End"] = row_index
										meta_info_reports.append(pytch_report)
										continue

								pytch_report["Name"] = value[0]
								pytch_report["Value"] = value[1]
								pytch_report[str(value[2])] = row_index
								label_metadata_value = value[2].lower()
								for marker in markers:
										if label_metadata[marker][0] == pytch_report["Name"] and label_metadata[marker][1] == pytch_report["Value"] and label_metadata[marker][2].lower().lower() != label_metadata_value:
												pytch_report[str(label_metadata[marker][2])] = marker
												markers.remove(marker)
												markers.remove(row_index)
												break
								if len(pytch_report) == 4:
										if pytch_report not in meta_info_reports:
												meta_info_reports.append(pytch_report)
								else:
										print("Missing info for marker %s"%pytch_report["Name"] + "_" + marker)
				return meta_info_reports


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"Y:\eval_team\pytch\utilities\matwritter\mat_export.mat"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		flr25_common_time = manager_modules.calc('get_json_data@aebs.fill', manager)
		print flr25_common_time
