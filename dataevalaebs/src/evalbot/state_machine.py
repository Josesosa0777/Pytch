import json
import os
import re
import logging
import datetime
import glob

from redmine_upload import RedmineUpload
from config_end_run import ConfigEndRun
from os.path import expanduser
from manage_db import ManageDb
from convert import Convert
from eval import Search, Issue, Doc

mainLogger = logging.getLogger('end_run_state')
logger = logging.getLogger('end_run')

def processCfgFile(cfgFile, wait4meas=True):
    mainLogger.info('Config file: %s' % cfgFile)
    conf = ConfigEndRun(cfgFile)
    newMeasList = []
    if not conf.valid:
        mainLogger.warning('Skipping {}:invalid configuration file'.format(cfgFile))
        return
    if conf.group == 'Trailer_Evaluation':
        folder = max(os.listdir(conf.measRootFolderPath))
        if not isValidMeasDir(conf.measRootFolderPath, folder):
            logger.info("Invalid measurement directory name")
            # continue

        conf.setMeas(folder)

        fh = logging.FileHandler(conf.logFilePath)
        fh.setLevel(logging.INFO)
        fhFormatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        fh.setFormatter(fhFormatter)
        logger.addHandler(fh)

        mainLogger.info('Actual folder: %s' % folder)
        db = ManageDb(conf)
        if db.getStatus() == 'New':
            db.detectNewFiles()

        firstStatus = re.search(
            r'(\w*)\s\((\d{4}-\d{2}-\d{2}\s\d{2}-\d{2}-\d{2})\)',
            db.getStatus())
        if firstStatus and firstStatus.group(1) == 'New':
            waitTimeOk = (datetime.datetime.now() -
                          datetime.datetime.strptime(firstStatus.group(2),
                                                     '%Y-%m-%d %H-%M-%S')) > \
                         datetime.timedelta(minutes=55)
            if not wait4meas or (waitTimeOk and not db.detectNewFiles()):
                db.setStatus('Convert')
        try:
            if db.getStatus() == 'Convert':
                if conf.canConvertNeeded or conf.videoConvertNeeded:
                    conf.setConvPath()
                    conv = Convert(conf)
                    status = conv.convert(db)
                    if 'Error' in status:
                        db.setStatus(status)
                        logger.removeHandler(fh)
                        # continue
                db.setStatus('Search')
        except:
            logger.info("Error while conversion")

        try:
            if db.getStatus() == 'Search':
                if conf.searchNeeded:
                    conf.setConvPath()
                    e = Search(conf)
                    status = e.search()
                    if 'Error' in status:
                        db.setStatus(status)
                        logger.removeHandler(fh)
                        # continue
                db.setStatus('Issue Generation')
        except:
            logger.info("Error while issue generation")

        try:
            if db.getStatus() == 'Issue Generation':
                if conf.issuegenNeeded:
                    i = Issue(conf)
                    status = i.issueGen()
                    if 'Error' in status:
                        db.setStatus(status)
                        logger.removeHandler(fh)
                        # continue
                db.setStatus('PDF Generation')
        except:
            logger.info("Error while PDF generation")

        try:
            if db.getStatus() == 'PDF Generation':
                if conf.docgenNeeded:
                    d = Doc(conf)
                    status = d.docGen()
                    if 'Error' in status:
                        db.setStatus(status)
                        logger.removeHandler(fh)
                        # continue
                db.setStatus('Upload')
        except:
            logger.info("Error while uploading document")

        try:
            if db.getStatus() == 'Upload':
                if conf.redmineUploadNeeded:
                    redm = RedmineUpload(conf)
                    status = redm.uploadIssue()
                    if 'Error' in status:
                        db.setStatus(status)
                        logger.removeHandler(fh)
                        # continue
                db.setStatus('Finished')
                mainLogger.info('Finished')
        except:
            logger.info("Error for redmine upload")

        logger.removeHandler(fh)

        if conf.summaryReportGenNeeded:
            d = Doc(conf)
            status = d.summaryReportGen()
            if 'Error' in status:
                logger.warning(status)
            else:
                logger.info(status)

        try:
            home_user_path = expanduser("~")
            measurement_signals_json = (home_user_path + r'\measurement_valid_signals.json')

            if os.path.exists(measurement_signals_json):
                os.remove(measurement_signals_json)
        except:
            pass
    else:
        for folder in os.listdir(conf.measRootFolderPath):
            if not isValidMeasDir(conf.measRootFolderPath, folder):
                continue

            conf.setMeas(folder)

            fh = logging.FileHandler(conf.logFilePath)
            fh.setLevel(logging.INFO)
            fhFormatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
            fh.setFormatter(fhFormatter)
            logger.addHandler(fh)

            mainLogger.info('Actual folder: %s' % folder)
            db = ManageDb(conf)
            if db.getStatus() == 'New':
                db.detectNewFiles()

            firstStatus = re.search(
                r'(\w*)\s\((\d{4}-\d{2}-\d{2}\s\d{2}-\d{2}-\d{2})\)',
                db.getStatus())
            if firstStatus and firstStatus.group(1) == 'New':
                waitTimeOk = (datetime.datetime.now() -
                              datetime.datetime.strptime(firstStatus.group(2),
                                                         '%Y-%m-%d %H-%M-%S')) > \
                             datetime.timedelta(minutes=55)
                if not wait4meas or (waitTimeOk and not db.detectNewFiles()):
                    db.setStatus('Convert')

            if db.getStatus() == 'Finished':
                measurement_files = []
                file_types = ['*.h5', '*.mat', '*.avi']
                for file_type in file_types:
                    for meas_name in glob.glob(os.path.join(conf.measFolderPath, file_type)):
                        measurement_files.append(os.path.basename(meas_name))
                dbFileList = db.getFileNames()
                newMeasList = list(set(measurement_files) - set(dbFileList))
                db.addNewFilesIntoDB(newMeasList)
                db.setStatus('SearchOnNewFile')
            if db.getStatus() == 'SearchOnNewFile':
                if conf.searchNeeded:
                    conf.setConvPath()
                    e = Search(conf)
                    status = e.searchRun(newMeasList)
                    if 'Error' in status:
                        db.setStatus(status)
                        logger.removeHandler(fh)
                        continue
                db.setStatus('Issue Generation')
            if db.getStatus() == 'Convert':
                if conf.canConvertNeeded or conf.videoConvertNeeded:
                    conf.setConvPath()
                    conv = Convert(conf)
                    status = conv.convert(db)
                    if 'Error' in status:
                        db.setStatus(status)
                        logger.removeHandler(fh)
                        continue
                db.setStatus('Search')
            if db.getStatus() == 'Search':
                if conf.searchNeeded:
                    conf.setConvPath()
                    e = Search(conf)
                    status = e.search()
                    if 'Error' in status:
                        db.setStatus(status)
                        logger.removeHandler(fh)
                        continue
                db.setStatus('Issue Generation')
            if db.getStatus() == 'Issue Generation':
                if conf.issuegenNeeded:
                    i = Issue(conf)
                    status = i.issueGen()
                    if 'Error' in status:
                        db.setStatus(status)
                        logger.removeHandler(fh)
                        continue
                db.setStatus('PDF Generation')
            if db.getStatus() == 'PDF Generation':
                if conf.docgenNeeded:
                    d = Doc(conf)
                    status = d.docGen()
                    if 'Error' in status:
                        db.setStatus(status)
                        logger.removeHandler(fh)
                        continue
                db.setStatus('Upload')
            if db.getStatus() == 'Upload':
                if conf.redmineUploadNeeded:
                    redm = RedmineUpload(conf)
                    status = redm.uploadIssue()
                    if 'Error' in status:
                        db.setStatus(status)
                        logger.removeHandler(fh)
                        continue
                db.setStatus('Finished')
                mainLogger.info('Finished')
            logger.removeHandler(fh)

        if conf.summaryReportGenNeeded:
            d = Doc(conf)
            status = d.summaryReportGen()
            if 'Error' in status:
                logger.warning(status)
            else:
                logger.info(status)

        try:
            home_user_path = expanduser("~")
            measurement_signals_json = (home_user_path + r'\measurement_valid_signals.json')

            if os.path.exists(measurement_signals_json):
                os.remove(measurement_signals_json)
        except:
            pass

def isValidMeasDir(root, folder):
    # is directory?
    fullfolder = os.path.join(root, folder)
    if not os.path.isdir(fullfolder):
        return False
    # looks like date?
    if not re.match('\d{4}-\d{2}-\d{2}', folder):
        return False
    # is date valid?
    try:
        datetime.datetime.strptime(folder, '%Y-%m-%d')
    except ValueError:
        return False
    # contains files?
    if not any(os.path.isfile(os.path.join(fullfolder, f))
               for f in os.listdir(fullfolder)):
        return False
    # should be valid...
    return True
