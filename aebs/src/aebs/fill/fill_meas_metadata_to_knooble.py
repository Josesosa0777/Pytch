# -*- dataeval: init -*-
import csv
import logging
import os
from datetime import time

import numpy as np
from interface import iCalc
from knooble.knooblemongodb import DatabaseManagement

from knooble.knooble_utils import getFilenameHash

logger = logging.getLogger("fill_meas_metadata_to_knooble@aebs.fill")


class cFill(iCalc):
		optdep = dict(
						postmarker_data = 'calc_postmarker_json_data@aebs.fill',
						sw_version = 'calc_flc25_sw_version@aebs.fill',
						fusion_protocol = 'calc_flc25_fusion_protocol@aebs.fill',
						sample_point ='calc_flc25_sample_point@aebs.fill'
		)

		def check(self):
				self.databaseManagement = DatabaseManagement()
				modules = self.get_modules()
				source = self.get_source()

				postmarker_json_data = {}
				meas_name = os.path.basename(source.FileName)
				file_name, extension = os.path.splitext(source.FileName)
				json_file_path = file_name + ".json"
				if os.path.isfile(json_file_path):
						meta_info_reports, traffic_sign_report = modules.fill(self.optdep['postmarker_data'])
						postmarker_json_data["meta_info_reports"] = meta_info_reports
						postmarker_json_data["traffic_sign_report"] = traffic_sign_report
						base_file_name, _ = os.path.splitext(meas_name)
						postmarker_json_data["file_name"] = base_file_name + ".json"

				collected_meas_metadata = []
				sourceFileId = getFilenameHash(meas_name)
				if self.optdep['sw_version'] in self.passed_optdep:
					try:
						swVersion, camera_alignment_mapped, camera_state_mapped = modules.fill(self.optdep['sw_version'])
						swVersion = np.unique(swVersion)

						camera_alignment_mapped = np.unique(camera_alignment_mapped)
						camera_state_mapped = np.unique(camera_state_mapped)

						collected_meas_metadata.append("sw_version_"+str(swVersion[0]))
					except:
						pass
						# collected_meas_metadata.append("camera_alignment@"+str(camera_alignment_mapped[0]))
						# collected_meas_metadata.append("camera_state@"+str(camera_state_mapped[0]))
				# collected_meas_metadata["meas_status"] = "UNPROCESSED"

				if self.optdep['fusion_protocol'] in self.passed_optdep:
					try:
						fusionProtocol = modules.fill(self.optdep['fusion_protocol'])
						fusionProtocol = list(set(fusionProtocol))

						collected_meas_metadata.append("fusion_protocol_"+str(int(fusionProtocol[0])))
					except:
						pass

				if self.optdep['sample_point'] in self.passed_optdep:
					try:
						sample_point = modules.fill(self.optdep['sample_point'])
						if sample_point is not None:
							collected_meas_metadata.append(sample_point)
					except:
						pass

				print(collected_meas_metadata)
				return postmarker_json_data, collected_meas_metadata, sourceFileId,meas_name

		def fill(self, postmarker_json_data, collected_meas_metadata, sourceFileId,meas_name):
				# meas_extraction_status = "INCOMPLETE"
				collected_json_data = {}
				if len(postmarker_json_data) == 0:
						logger.info("JSON missing")
				else:
						collected_json_data = self.get_json_meta(postmarker_json_data)
						# self.databaseManagement.updateFileProcessingStatus(postmarker_json_data["file_name"], sourceFileId)

				collected_meas_metadata.extend(collected_json_data)
				# self.databaseManagement.updateMetadata(collected_meas_metadata,"hashtags HAS highway ",meas_name)

				meas_extraction_status = "COMPLETED"
				return collected_meas_metadata,meas_extraction_status

		def get_json_meta(self, postmarker_json_data):
				"""
				Refer aebs/src/aebs/par/postmarker_enums.py for more details about enums used in postmarker tool:

				:param postmarker_json_data:
				:return:
				"""
				time = []
				road_type = []
				vehicle_headlamp = []
				weather_conditions = []
				road_edge = []
				street_objects = []
				object_on_side_of_road = []
				traffic_event = []
				moving_objects = []
				country_code = []

				traffic_sign_list = []

				meta_info_reports, traffic_sign_report = postmarker_json_data['meta_info_reports'], postmarker_json_data[
						'traffic_sign_report']
				for meta_info in meta_info_reports:
						if meta_info["Name"] == "Time" and meta_info["Value"] not in time:
								time.append(meta_info["Value"])
						elif meta_info["Name"].lower() == "road type" and meta_info["Value"] not in road_type:
								road_type.append(meta_info["Value"])
						elif meta_info["Name"].lower() == "vehicle headlamp" and meta_info["Value"] not in vehicle_headlamp:
								vehicle_headlamp.append(meta_info["Value"])
						elif meta_info["Name"].lower() == "weather conditions" and meta_info["Value"] not in weather_conditions:
								weather_conditions.append(meta_info["Value"])
						elif meta_info["Name"].lower() == "road edge" and meta_info["Value"] not in road_edge:
								road_edge.append(meta_info["Value"])
						elif meta_info["Name"].lower() == "street objects" and meta_info["Value"] not in street_objects:
								street_objects.append(meta_info["Value"])
						elif meta_info["Name"].lower() == "object on side of roads" and meta_info[
								"Value"] not in object_on_side_of_road:
								object_on_side_of_road.append(meta_info["Value"])
						elif meta_info["Name"].lower() == "traffic event" and meta_info["Value"] not in traffic_event:
								traffic_event.append(meta_info["Value"])
						elif meta_info["Name"].lower() == "moving objects" and meta_info["Value"] not in moving_objects:
								moving_objects.append(meta_info["Value"])
						elif meta_info["Name"].lower() == "country code" and meta_info["Value"] not in country_code:
								country_code.append(meta_info["Value"])
				for traffic_sign in traffic_sign_report:
						traffic_sign_list.append(traffic_sign['conti_sign_class'])

				collected_json_data = [{"name": "time", "value": time},
				                       {"name": "road_type", "value": road_type},
				                       {"name": "vehicle_headlamp", "value": vehicle_headlamp},
				                       {"name": "weather_conditions", "value": weather_conditions},
				                       {"name": "road_edge", "value": road_edge},
				                       {"name": "street_objects", "value": street_objects},
				                       {"name": "object_on_side_of_road", "value": object_on_side_of_road},
				                       {"name": "traffic_event", "value": traffic_event},
				                       {"name": "moving_objects", "value": moving_objects},
				                       {"name": "country_code", "value": country_code},
				                       {"name": "traffic_sign_list", "value": list(set(traffic_sign_list))}
				                       ]

				return collected_json_data

if __name__ == "__main__":
		from config.Config import init_dataeval

		meas_path = r"C:\Users\ext-gorea\Downloads\HMC-QZ-STR__2021-03-02_13-47-55.h5"
		config, manager, manager_modules = init_dataeval(["-m", meas_path])
		tracks = manager_modules.calc("fill_meas_metadata_to_knooble@aebs.fill", manager)
		print(tracks)
