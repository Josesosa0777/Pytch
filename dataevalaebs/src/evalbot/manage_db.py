import os
import glob
import sqlite3
from datetime import datetime, timedelta
import logging
import fnmatch
from convert import CAN_EXTENSIONS, VIDEO_EXTENSIONS


logger = logging.getLogger('end_run.manage_db')
mainLogger = logging.getLogger('end_run_state.manage_db')


class ManageDb:
    def __init__(self, conf):
        self.conf = conf
        
        self.con = sqlite3.connect(self.conf.dbFilePath)
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT * FROM sqlite_master WHERE name ='Status' and type='table'")
            if not len(cur.fetchall()):
                cur.execute("CREATE TABLE Status(`Id` INTEGER PRIMARY KEY AUTOINCREMENT, `VehicleGroup` TEXT, `Measurement` NUMERIC, `Status` TEXT)")
                logger.info('Status table created')
            cur.execute("SELECT * FROM sqlite_master WHERE name ='%s' and type='table'" % self.conf.group)
            if not len(cur.fetchall()):
                cur.execute("CREATE TABLE %s(`ID` INTEGER PRIMARY KEY AUTOINCREMENT, `Measurement` NUMERIC, `FileName` TEXT, `ConvStatus` TEXT)" %\
                             self.conf.group)
                logger.info('Group table created: %s' % self.conf.group)
            cur.execute("SELECT * FROM %s WHERE Measurement='%s'" % (self.conf.group, self.conf.measDate))
            if not len(cur.fetchall()):
                cur.execute("INSERT INTO Status VALUES(NULL, '%s', '%s', 'New')" % (self.conf.group, self.conf.measDate))
                logger.info('New measurement: %s added to group: %s' % (self.conf.measDate, self.conf.group))
            # workaround for deleted status, but existing group meas
            cur.execute("SELECT * FROM Status WHERE Measurement= '%s' AND VehicleGroup = '%s'" % (self.conf.measDate, self.conf.group))
            if not len(cur.fetchall()):
                status = 'New (%s)' % (datetime.now() - timedelta(minutes=56)).strftime('%Y-%m-%d %H-%M-%S')
                cur.execute("INSERT INTO Status VALUES(NULL, '%s', '%s', '%s')" % (self.conf.group, self.conf.measDate, status))
                logger.info('New measurement: %s %s added to Status' % (self.conf.group, self.conf.measDate))
    
    def detectNewFiles(self):
        newElementFlag = False
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT FileName FROM %s WHERE Measurement='%s'" % (self.conf.group, self.conf.measDate))
            fileList = []
            for fileName in cur.fetchall():
                fileList.append(fileName[0])
            if self.conf.group == 'Trailer_Evaluation':
                extension = r'\*.blf'
                f = max(glob.glob(self.conf.measFolderPath + extension), key=os.path.getctime)
                # for f in os.listdir(self.conf.measFolderPath):
                if os.path.isfile(os.path.join(self.conf.measFolderPath, f)) and f not in fileList:
                    fileExt = os.path.splitext(f)[1].lower()
                    if fileExt in VIDEO_EXTENSIONS and self.conf.videoConvertNeeded and fileExt == self.conf.inputFormat:
                        convert = 'Wait'
                    elif fileExt in CAN_EXTENSIONS and self.conf.canConvertNeeded and fileExt == self.conf.measFormat and \
                            self.conf.canChannels[0] in f:
                        convert = 'Wait'
                    else:
                        convert = 'Not needed'

                    cur.execute("INSERT INTO %s VALUES(NULL, '%s', '%s', '%s')" % (
                    self.conf.group, self.conf.measDate, f, convert))
                    logger.info('New file found: %s' % f)
                    newElementFlag = True
            else:
                for f in os.listdir(self.conf.measFolderPath):
                    if os.path.isfile(os.path.join(self.conf.measFolderPath, f)) and f not in fileList:
                        fileExt = os.path.splitext(f)[1].lower()
                        if fileExt in VIDEO_EXTENSIONS and self.conf.videoConvertNeeded and fileExt == self.conf.inputFormat:
                            convert = 'Wait'
                        elif fileExt in CAN_EXTENSIONS and self.conf.canConvertNeeded and fileExt == self.conf.measFormat and self.conf.canChannels[0] in f:
                            convert = 'Wait'
                        else:
                            convert = 'Not needed'

                        cur.execute("INSERT INTO %s VALUES(NULL, '%s', '%s', '%s')" % (self.conf.group, self.conf.measDate, f, convert))
                        logger.info('New file found: %s' % f)
                        newElementFlag = True
            
            if newElementFlag:
                status = 'New (%s)' % datetime.now().strftime('%Y-%m-%d %H-%M-%S')
                cur.execute("UPDATE Status SET Status='%s' WHERE VehicleGroup='%s' and Measurement='%s'" % (status, self.conf.group, self.conf.measDate))
                mainLogger.info('New file found')
        return newElementFlag

    def addNewFilesIntoDB(self, new_file_list):
        newElementFlag = False
        with self.con:
            cur = self.con.cursor()
            for f in new_file_list:
                fileExt = os.path.splitext(f)[1].lower()
                if fileExt in VIDEO_EXTENSIONS and self.conf.videoConvertNeeded and fileExt == self.conf.inputFormat:
                    convert = 'Wait'
                elif fileExt in CAN_EXTENSIONS and self.conf.canConvertNeeded and fileExt == self.conf.measFormat and \
                        self.conf.canChannels[0] in f:
                    convert = 'Wait'
                else:
                    convert = 'Not needed'

                cur.execute("INSERT INTO %s VALUES(NULL, '%s', '%s', '%s')" % (
                    self.conf.group, self.conf.measDate, f, convert))
                logger.info('New file found: %s' % f)
                newElementFlag = True

        if newElementFlag:
            status = 'New (%s)' % datetime.now().strftime('%Y-%m-%d %H-%M-%S')
            cur.execute("UPDATE Status SET Status='%s' WHERE VehicleGroup='%s' and Measurement='%s'" % (
                status, self.conf.group, self.conf.measDate))
            mainLogger.info('New file found')
        return newElementFlag

    def setConvertStatus(self, fileName, convStatus):
        with self.con:
            cur = self.con.cursor()
            cur.execute("UPDATE %s SET ConvStatus='%s' WHERE Measurement='%s' and FileName='%s'" % (self.conf.group, convStatus, self.conf.measDate, fileName))
        log = 'File: %s conversion status changed to: %s' % (fileName, convStatus)
        if 'Error' in convStatus:
            logger.error(log)
        else:
            logger.info(log)
    
    def setStatus(self, status):
        with self.con:
            cur = self.con.cursor()
            cur.execute("UPDATE Status SET Status='%s' WHERE VehicleGroup='%s' and Measurement='%s'" % (status, self.conf.group, self.conf.measDate))
        log = 'Status changed to: %s' % status
        if 'Error' in status:
            logger.error(log)
            mainLogger.info(log)
        else:
            logger.info(log)
    
    def getStatus(self):
        with self.con:
            self.con.row_factory = sqlite3.Row
            cur = self.con.cursor()
            cur.execute("SELECT * FROM Status WHERE VehicleGroup='%s' and Measurement='%s'" % (self.conf.group, self.conf.measDate))
            rows = cur.fetchall()
        return rows[0]['Status']

    def getFileNames(self):
        with self.con:
            self.con.row_factory = sqlite3.Row
            cur = self.con.cursor()
            cur.execute("SELECT FileName FROM {} WHERE FileName like '%.h5' OR FileName like '%.mat' OR FileName like '%.avi'".format(self.conf.group))
            fileList = []
            for fileName in cur.fetchall():
                fileList.append(fileName[0])
        return fileList

    def getWaitForConvertFileList(self, status):
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT [FileName] FROM %s WHERE Measurement='%s' and ConvStatus='%s'" % (self.conf.group, self.conf.measDate, status))
            fileList = []
            for fileName in cur.fetchall():
                fileList.append(fileName[0])
        return fileList
