from sys import executable as python
from os import path, makedirs
from subprocess import call
from shutil import copyfile
from utils import SummarybotStoppedError
import logging


log = logging.getLogger('summarybot')
    

class Merge(object):
    def __init__(self, batches, config):
        self.batches = batches
        self.merge_needed = config['merge']['merge']
        self.script_path = path.dirname(__file__)
        self.backup_needed = config['merge']['backup']
        self.merged_backup_path = config['merge']['backup_path']
        self.merged_db_path = path.join(self.script_path, 'local', 'batch_merged.db')

    def merge(self):
        if not self.merge_needed:
            log.info('Skipping database merge')
            return
        log.info('Starting database merge')
        merge_db = [python, '-m', 'merge_batch_db']
        for batch in self.batches:
            local = path.join(self.script_path, 'local', batch['local'])
            merge_db.append('--merge')
            merge_db.append(local)
        merge_db.append(self.merged_db_path)
        try:
            call(merge_db)
        except OSError as e:
            raise SummarybotStoppedError('Merge failed: {}'.format(e))

    def backup(self):
        if not self.backup_needed:
            log.info('Skipping merged database backup')
            return
        log.info('Backing up merged database to {}'.format(self.merged_backup_path))
        dirn = path.dirname(self.merged_backup_path)
        if not path.exists(dirn):
            log.debug('Creating destination folder: {}', dirn)
            makedirs(dirn)
        try:
            copyfile(self.merged_db_path, self.merged_backup_path)
        except IOError as ioerr:
            log.error('Copy failed with IOError: {}'.format(ioerr))
            log.warning('Skipping backup of merged database!')
            # raise SummarybotStoppedError
