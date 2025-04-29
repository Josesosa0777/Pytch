import os
import logging
from redmine import Redmine
# from redminelib import Redmine
from requests.exceptions import ConnectionError


logger = logging.getLogger('end_run_state.upload')


class RedmineUpload(object):
    def __init__(self, conf):
        self.conf = conf

    def checkError(self):
        labels = ['WARNING', 'ERROR', 'CRITICAL']
        backgrounds = ['yellow', 'red', 'red']
        colors = ['black', 'white', 'white']
        files = ['search.log', 'issue.log', 'report.log', '%s.log' % self.conf.measDate]
        ret = ['h2. Log files\n\n']
        header = ['|Log name|',]
        for l in labels:
            header.append('Number of %s(s)|' % l.title())
        ret.append(''.join(header))
        for logFile in files:
            tableLine = ['|attachment:"%s"|' % logFile,]
            try:
                f = open(os.path.join(self.conf.logFolderPath, logFile), 'r')
                log = f.readlines()
                f.close()
            except IOError:
                log = None
            if log:
                for label, background, color in zip(labels, backgrounds, colors):
                    cntr = 0
                    for line in log:
                        if '[%s]' % label in line:
                            cntr += 1
                    if cntr > 0:
                        tableLine.append('%%{background:%s; color:%s} %d%%|' % (background, color, cntr))
                    else:
                        tableLine.append('%d|' % cntr)
                ret.append(''.join(tableLine))
        return ret

    def citePdf(self):
        return "h2. PDF report\n\nattachment:report.pdf\n\n"

    def hasSubIssue(self, parentIssue, subIssue):
        for i in parentIssue.children:
            if subIssue == str(i.subject):
                return True
        return False

    def readIssueFile(self, issueFile):
        try:
            f = open(issueFile, 'r')
        except:
            return False
        issueTextLines = f.readlines()
        f.close()
        issueTextLinesChop = []
        lineCntr = 0
        for line in issueTextLines:
            if 'h2.' in line:
                lineCntr = 0
            else:
                lineCntr += 1
            if lineCntr < 153:
                issueTextLinesChop.append(line)
            if lineCntr == 153:
                issueTextLinesChop.append('\n_[This section is too long and truncated here. Check attachment:report.pdf for the complete section.]_\n\n')

        return '%s%s%s' % (''.join(issueTextLinesChop), self.citePdf(), '\n'.join(self.checkError()))

    def searchAttachments(self):
        att = []
        for fileName in os.listdir(self.conf.issueFolderPath):
            if '.png' in fileName or fileName == 'report.pdf':
                fileDict = {'path' : os.path.join(self.conf.issueFolderPath, fileName), 'filename' : fileName}
                att.append(fileDict)
        # for fileName in os.listdir(self.conf.logFolderPath):
        #     if '.log' in fileName:
        #         fileDict = {'path' : os.path.join(self.conf.logFolderPath, fileName), 'filename' : fileName}
        #         att.append(fileDict)
        return att

    def addSubIssue(self):
        try:
            f = open(os.path.expanduser('~/redmine_api_access_key'), 'r')
            apiKey = f.read()
            f.close()
            if len(apiKey) != 40:
                logger.error('Redmine API Access Key is not correct')
                return 'Error - Upload - Redmine API Access Key is not correct'
        except IOError:
            logger.error('Redmine API Access Key not found')
            return 'Error - Upload - Redmine API Access Key not found'
        for i in range(10):
            try:
                redmine = Redmine('http://leonidas/redmine/', key=apiKey, version='3.3', requests={'timeout': 30})
                name = 'Endurance run: %s %s' % (self.conf.group, self.conf.measDate)
                logger.debug('Acquiring parent issue: {}'.format(self.conf.parentIssueId))
                parentIssue = redmine.issue.get(self.conf.parentIssueId, include='watchers')
                if self.hasSubIssue(parentIssue, name):
                    logger.error("Issue already exists: '{}'".format(name))
                    return 'Error - Upload - Issue already exists'
                logger.info("Uploading issue '{}'".format(name))
                issue_file_path = os.path.join(self.conf.issueFolderPath, 'issue')
                issue_file = self.readIssueFile(issue_file_path)
                if not issue_file:
                    logger.critical("Issue file not found: {}".format(issue_file_path))
                    break
                redmine.issue.create(project_id=self.conf.projectId, subject=name, parent_issue_id=self.conf.parentIssueId,
                                     tracker_id=6, description=issue_file,
                                     status_id=1, priority_id=4, uploads=self.searchAttachments(),
                                     watcher_user_ids=[user['id'] for user in parentIssue.watchers.resources])
            except ConnectionError:
                logger.debug('Could not connect, retrying ({} of 10 attempts)'.format(i+1))
                continue
            else:
                return 'Success'
        logger.error('Server did not respond after 10 attempts')
        return 'Error - Upload - Server did not respond after 10 attempts'

    def uploadIssue(self):
        if self.conf.redmineUploadNeeded:
            return self.addSubIssue()
        else:
            return 'Success'
