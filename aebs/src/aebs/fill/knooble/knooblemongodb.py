
import logging
from pymongo import MongoClient

logger = logging.getLogger(__name__)


class DatabaseManagement:
    connectionString = (
        "mongodb://admin:Knooble@strw0003.corp.knorr-bremse.com:27017/?authSource=admin"
    )
    # connectionString = (
    #     "mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&directConnection"
    #     "=true&ssl=false"
    # )

    def __init__(self):
        try:
            # self.mongoClient = MongoClient(DatabaseManagement.connectionString)
            self.mongoClient = MongoClient(self.connectionString)
            self.database = self.mongoClient.knooble_v3
            logger.info("Connected to database successfully")
        except Exception as err:
            self.mongoClient = None
            self.database = None
            logger.error(err)

    def updateMetadata(self, collected_meas_metadata, sourceFileId):
        self.database.measurements.update_one({"sourceFileId": sourceFileId}, {
            "$addToSet": {"metadata": { "$each": collected_meas_metadata}}
        }, upsert = True)

    def updateFileProcessingStatus(self, convFileName, sourceFileId):
        self.database.measurements.update_one({"sourceFileId": sourceFileId, "convertedFiles.fileName" : convFileName}, {
            "$set": {"convertedFiles.$.fileProcessingStatus": True}
        })

    def getUnprocessedData(self):
        unprocessed_meas_data = self.database.measurements.find({"convertedFiles.fileProcessingStatus": False},
                                                                {"_id": 0, "convertedFiles": 1})
        return unprocessed_meas_data
