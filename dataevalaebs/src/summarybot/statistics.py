from sys import executable as python
from os import path
from subprocess import call
from utils import SummarybotStoppedError
import requests
import logging


log = logging.getLogger('summarybot')


class Statistics(object):
    def __init__(self, config):
        self.config = config
        self.analyze_needed = config['statistics']['analyze']
        self.upload_needed = config['statistics']['upload']
        redmine_url = config['statistics']['redmine_url']
        api_key_path = config['statistics']['api_key_path']
        self.redmine = RedmineWikiUploader(redmine_url, api_key_path)
        self.script_path = path.dirname(__file__)
        self.merged_db_path = path.join(self.script_path, 'local', 'batch_merged.db')
        self.page = None

    def analyze(self):
        if not self.analyze_needed:
            log.info('Skipping statistics creation')
            return None
        log.info('Creating statistics')
        analyze_db = [python, '-m', 'analyze', self.merged_db_path]
        try:
            call(analyze_db)
        except OSError as e:
            raise SummarybotStoppedError('Creating statistics failed: {}'.format(e))
        # TODO fill page with data

    def upload(self):
        if not self.upload_needed or self.page is None:
            log.info('Skipping wiki update')
            return
        log.info('Updating wiki')
        self.redmine.upload(self.page)


class RedmineWikiUploader(object):
    def __init__(self, project, api_key_path):
        self.key = self._read_api_access_key(api_key_path)
        self.wiki_url = project + '/projects/endurance-run/wiki/wiki_name.json?key=' + self.key
        self.upload_url = project + '/uploads.json?key=' + self.key
        self.wiki = {
            'wiki_page': {
                'text': ''
            },
            'attachments': []
        }

    def upload(self, wiki_page):
        log.debug('Reading analyze output')
        # text = self.wiki['wiki_page']['text']
        # for line in page:
        #     if line is text:
        #         text += line
        #     else:
        #         self._add_file('C:/KBData/img.png', 'stat_00.png')
        # self._upload_wiki_page()

    def _upload_wiki_page(self):
        log.debug('Uploading wiki')
        response = requests.post(self.wiki_url, json=self.wiki)
        answer = response.json()
        c = response.status_code
        if c == 200:
            pass
        elif c == 422:
            log.error('422 ({}) while uploading wiki: {}'.format(response.reason, answer))

    def _read_api_access_key(self, fpath):
        api_key = None
        with open(fpath) as key_file:
            api_key = key_file.readline()
        return api_key

    def _add_file(self, fpath, name):
        log.debug('Uploading {} to redmine as {}'.format(fpath, name))
        with open(path, 'rb') as data:
            headers = {'content-type': 'application/octet-stream'}
            log.debug('sending request: {}'.format(self.upload_url))
            response = requests.post(self.upload_url, data=data, headers=headers)
            answer = response.json()
            log.debug('answer is: {}'.format(answer))
            c = response.status_code
            if c == 422:
                log.error('422 ({}) while uploading {}'.format(response.reason, path))
                return False
            elif c == 201:
                token = answer['upload']['token']
                attachment = {'token': token, 'filename': name, 'content-type': 'image/png'}
                self.wiki['attachments'].append(attachment)
                return True
