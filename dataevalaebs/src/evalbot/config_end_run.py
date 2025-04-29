import os
import logging
import ConfigParser
from ConfigParser import NoOptionError, NoSectionError

from aebs.dbc import dbc2filename
from measparser import dcnvt

logger = logging.getLogger('end_run_state')


class ConfigEndRun:
    def __init__(self, filePath):
        self.valid = True
        conf = ConfigParser.ConfigParser()
        conf.read(filePath)
        # video convert
        self.videoConvertNeeded = conf.getboolean('video convert', 'videoConvertNeeded')
        # Read csv and json file path
        try:
            self.csvResimOutPath = conf.get('resim', 'csvResimOutPath')
            self.csvMileagePath = conf.get('resim', 'csvMileagePath')
            self.jsonParamPath = conf.get('resim', 'jsonParamPath')
        except:
            logger.info(".csv and/or .json file path(s) for (P)AEBS resimulation are not available.")
            self.csvResimOutPath = ''
            self.csvMileagePath = ''
            self.jsonParamPath = ''
            pass

        if self.videoConvertNeeded:
            try:
                self.inputFormat = conf.get('video convert', 'inputFormat')
                self.outputFormat = conf.get('video convert', 'outputFormat')
            except NoOptionError:
                logger.error('Please specify both "inputFormat" and "outputFormat" for video conversion')
                self.valid = False
                return
        # can2mat convert
        conv_section = 'can2mat convert'
        try:
            self.canConvertNeeded = conf.getboolean(conv_section, 'canConvertNeeded')
        except NoSectionError:
            # legacy
            conv_section = 'blf2mat convert'
            try:
                self.canConvertNeeded = conf.getboolean(conv_section, 'blfConvertNeeded')
            except NoOptionError:
                # hybrid legacy
                self.canConvertNeeded = conf.getboolean(conv_section, 'canConvertNeeded')
        except NoOptionError:
            # hybrid legacy
            self.canConvertNeeded = conf.getboolean(conv_section, 'blfConvertNeeded')

        if self.canConvertNeeded:
            self.dcnvt = dcnvt.executable
            this_dir = os.path.abspath(os.path.dirname(__file__))
            try:
                self.measFormat = conf.get(conv_section, 'measFormat')
            except NoOptionError:
                self.measFormat = '.blf'  # default to BLF
            if self.measFormat == '.blf':  # CANape measurement
                self.dcnvtSelect = os.path.join(this_dir, 'convert_select.txt')
                self.dcnvtRename = os.path.join(this_dir, 'convert_rename.txt')
            else:  # other
                self.dcnvtSelect = None
                self.dcnvtRename = None
            dbcListString = os.path.normpath(conf.get(conv_section, 'dbcList'))
            dbcListRaw = dbcListString.split(';')
            self.dbcList = []
            try:
                for listElement in dbcListRaw:
                    if not listElement.strip():
                        continue  # ignore empty input
                    if '<' in listElement:
                        line = listElement.split('<')
                        self.dbcList.append((dbc2filename[line[1].strip()], line[0].strip()))
                    else:
                        self.dbcList.append((dbc2filename[listElement.strip()], None))
            except KeyError:
                self.dbcList = None
            canChannels_string = conf.get(conv_section, 'canChannels')
            self.canChannels = [ch.strip() for ch in canChannels_string.split(';') if ch.strip()]
        self.convertClass = conf.get(conv_section, 'convertClass')
        # search
        self.searchNeeded = conf.getboolean('search', 'searchNeeded')
        self.fileExtension = conf.get('search', 'fileExtension')
        self.searchClass = conf.get('search', 'searchClass')
        try:
            self.searchStartDate = conf.get('search', 'startDate')
            self.searchEndDate = conf.get('search', 'endDate')
        except:
            logger.warning(
                "No option 'startDate', 'endDate' in section: 'search'. Taking default dates interval(2000-01-01 to 2050-01-01).")
            self.searchStartDate = "2000-01-01"
            self.searchEndDate = "2050-01-01"
        # issuegen
        self.issuegenNeeded = conf.getboolean('issuegen', 'issuegenNeeded')
        self.issueClass = conf.get('issuegen', 'issueClass')
        # docgen
        self.docgenNeeded = conf.getboolean('docgen', 'docgenNeeded')
        if self.docgenNeeded:
            self.docClass = conf.get('docgen', 'docClass')
            try:
                doc_types_string = conf.get('docgen', 'docTypes')
                self.docTypes = [ch.strip() for ch in doc_types_string.split(';') if ch.strip()]
                if len(self.docTypes) == 0:
                    logger.critical("Report cannot be generated. Please use ';' delimiter to specify docTypes.")
            except:
                logger.warning("No option 'docTypes' in section: 'docgen'. Taking pdf as default report type.")
                self.docTypes = ["pdf"]
        # summaryreportgen
        try:
            self.summaryReportGenNeeded = conf.getboolean('summaryreportgen', 'summaryReportGenNeeded')
            self.summaryReportPath = ''
            self.summaryLogFolderPath = ''
        except:
            self.summaryReportGenNeeded = False
            self.summaryReportPath = ''
            self.summaryLogFolderPath = ''

        if self.summaryReportGenNeeded:
            try:
                self.startDate = conf.get('summaryreportgen', 'startDate')
                self.endDate = conf.get('summaryreportgen', 'endDate')
            except:
                logger.warning(
                    "No option 'startDate', 'endDate' in section: 'summaryreportgen'. Taking default dates interval(2000-01-01 to 2050-01-01).")
                self.startDate = "2000-01-01"
                self.endDate = "2050-01-01"
            try:
                self.docClass = conf.get('summaryreportgen', 'docClass')
                doc_types_string = conf.get('summaryreportgen', 'docTypes')
                self.summaryDocTypes = [ch.strip() for ch in doc_types_string.split(';') if ch.strip()]
                if len(self.summaryDocTypes) == 0:
                    logger.critical("Report cannot be generated. Please use ';' delimiter to specify docTypes.")
            except:
                logger.warning(
                    "No option 'docTypes' in section: 'summaryreportgen'. Taking pdf as default report type.")
                self.summaryDocTypes = ["pdf"]
            try:
                self.summaryReportPath = os.path.normpath(conf.get('summaryreportgen', 'summaryReportPath'))
            except:
                logger.warning(
                    "No option 'summaryReportPath' in section: 'summaryreportgen'. Taking issueRootFolderPath as default in setMeas")

            try:
                self.summaryLogFolderPath = os.path.normpath(conf.get('summaryreportgen', 'summaryLogFolderPath'))
            except:
                logger.warning(
                    "No option 'summaryLogFolderPath' in section: 'summaryreportgen'. Taking logRootFolderPath as default in setMeas")

        # redmine
        self.redmineUploadNeeded = conf.getboolean('redmine', 'redmineUploadNeeded')
        if self.redmineUploadNeeded:
            self.projectId = conf.get('redmine', 'projectId')
            self.parentIssueId = conf.get('redmine', 'parentIssueId')

        # global
        self.group = conf.get('global', 'group')
        self.dbFolderPath = os.path.normpath(conf.get('global', 'dbFolderPath'))
        self.logRootFolderPath = os.path.normpath(conf.get('global', 'logRootFolderPath'))
        self.measRootFolderPath = os.path.normpath(conf.get('global', 'measRootFolderPath'))
        try:
            self.convMeasRootFolderPath = os.path.normpath(conf.get('global', 'convMeasRootFolderPath'))
        except NoOptionError:
            self.convMeasRootFolderPath = ''
        if self.searchNeeded or self.issuegenNeeded or self.docgenNeeded or self.summaryReportGenNeeded:
            self.batchFile = os.path.normpath(conf.get('global', 'batchFile'))
            self.repDir = os.path.normpath(conf.get('global', 'repDir'))
        if self.issuegenNeeded or self.docgenNeeded or self.redmineUploadNeeded or self.summaryReportGenNeeded:
            self.issueRootFolderPath = os.path.normpath(conf.get('global', 'issueRootFolderPath'))

    def setMeas(self, measDate):
        self.measDate = measDate
        self.dbFilePath = os.path.join(self.dbFolderPath, "%s.db" % measDate[:4])
        if self.group == 'Trailer_Evaluation':
            if os.path.exists(self.dbFilePath):
                os.remove(self.dbFilePath)

        self.logFolderPath = os.path.join(self.logRootFolderPath, measDate)
        if not os.path.exists(self.logFolderPath):
            os.makedirs(self.logFolderPath)
        self.measFolderPath = os.path.join(self.measRootFolderPath, measDate)
        if self.issuegenNeeded or self.docgenNeeded or self.redmineUploadNeeded or self.summaryReportGenNeeded:
            if not self.summaryLogFolderPath:
                self.summaryLogFolderPath = self.logRootFolderPath
            if not os.path.exists(self.summaryLogFolderPath):
                os.makedirs(self.summaryLogFolderPath)
            if not self.summaryReportPath:
                self.summaryReportPath = self.issueRootFolderPath
            self.issueFolderPath = os.path.join(self.issueRootFolderPath, measDate)
            if not os.path.exists(self.issueFolderPath):
                os.makedirs(self.issueFolderPath)
            if not os.path.exists(self.summaryReportPath):
                os.makedirs(self.summaryReportPath)
        self.logFilePath = os.path.join(self.logFolderPath, '%s.log' % measDate)

    def setConvPath(self):
        if self.convMeasRootFolderPath:
            self.convMeasFolderPath = os.path.join(self.convMeasRootFolderPath, self.measDate)
            if not os.path.exists(self.convMeasFolderPath):
                os.makedirs(self.convMeasFolderPath)
