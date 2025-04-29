"""
This is knooble windows task service, it looks for unprocessed measurements in mongodb database and stores extracted
metadata back to database collection
"""
import logging
import os

import numpy
from config.Config import init_dataeval
from knooblemongodb import DatabaseManagement
from knooble_utils import getFilenameHash, PYTCH_SUPPORTED_FILE_FORMATS
logger = logging.getLogger("knoobleservice")


class MetaExtractorService:
		def __init__(self):
				self.databaseManagement = DatabaseManagement()
				self.database = self.databaseManagement.database

		def get_all_meas_data(self):
				all_meas_data = self.database.measurements.find({"existance": False})
				return all_meas_data

		def add_new_field_meas_data(self, whereToUpdate, whatToAdd):
				self.database.measurements.update(whereToUpdate, {"$set": whatToAdd})


		def delete_existing_field_meas_data(self, whereToUpdate, whatToDelete):
				self.database.measurements.update(whereToUpdate, {"$unset": whatToDelete})


		def rename_existing_field_meas_data(self, whereToUpdate, whatToRename):
				self.database.measurements.update(whereToUpdate, {'$rename': whatToRename})


		def process_unprocessed_measurements(self, meas_data):
				for unprocessedSourceMeas in meas_data:
						unprocessed_data = unprocessedSourceMeas["convertedFiles"]
						for unprocessed_meas in unprocessed_data:
								if unprocessed_meas["fileType"] in PYTCH_SUPPORTED_FILE_FORMATS and not unprocessed_meas["fileProcessingStatus"]:
										config, manager, manager_modules = init_dataeval(["-m", str(unprocessed_meas["filePath"])])
										logger.info("Processing {}".format(unprocessed_meas["filePath"]))
										try:
												meas_name = os.path.basename(unprocessed_meas["filePath"])
												sourceFileId = getFilenameHash(meas_name)
												if sourceFileId == False:
														continue
												status = manager_modules.calc("fill_meas_metadata_to_knooble@aebs.fill", manager)
												logger.info("Processed {} : status- {}".format(unprocessed_meas["filePath"], status))

												self.databaseManagement.updateFileProcessingStatus(meas_name, sourceFileId)
										except Exception as e:
												logger.error("Exception while processing {}".format(unprocessed_meas["filePath"]))
												logger.critical(str(e))


		def addfield_in_processed_metadata(self, processed_meas_data):
				for processed_meas in processed_meas_data:
						config, manager, manager_modules = init_dataeval(["-m", str(processed_meas["meas_path"])])
						sensorstatus = manager_modules.calc("calc_flc25_sensor_status@aebs.fill", manager)
						if sensorstatus is not None:
								whereToUpdate = {"meas_id": processed_meas["meas_id"]}
								whatToAdd = {"sensor_status": str(numpy.unique(sensorstatus)[0])}
								self.add_new_field_meas_data(whereToUpdate, whatToAdd)


		def deletefield_from_processed_metadata(self, processed_meas_data):
				for processed_meas in processed_meas_data:
						whereToUpdate = {"meas_id": processed_meas["meas_id"]}
						if 'sensor_status' in processed_meas:
								whatToDelete = {"sensor_status": processed_meas['sensor_status']}
								self.delete_existing_field_meas_data(whereToUpdate, whatToDelete)


		def renamefield_from_processed_metadata(self, processed_meas_data):
				for processed_meas in processed_meas_data:
						whereToUpdate = {"meas_id": processed_meas["meas_id"]}
						if 'sensorStatus' in processed_meas:
								whatToRename = {"sensor_status": "sensorStatus"}
								self.rename_existing_field_meas_data(whereToUpdate, whatToRename)

if __name__ == "__main__":
		#TODO parameterize:: unprocessed, all
		metaExtractor = MetaExtractorService()
		unprocessed_meas_data = metaExtractor.databaseManagement.getUnprocessedData()
		meas_data = [{"meas_path" : r"C:\KBData\__PythonToolchain\Development\knooble\testfolder\2021-07-22\mi5id787__2021-07-22_05-46-55.h5"}]

		metaExtractor.process_unprocessed_measurements(unprocessed_meas_data)

		# previously_processed_meas_data = metaExtractor.get_all_meas_data()
		# metaExtractor.addfield_in_processed_metadata(previously_processed_meas_data)
		#
		# previously_processed_meas_data = get_all_meas_data()
		# metaExtractor.renamefield_from_processed_metadata(previously_processed_meas_data)

		# metaExtractor.deletefield_from_processed_metadata(previously_processed_meas_data)
