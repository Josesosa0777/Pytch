from sys import executable as python
from os import chdir, path, makedirs
from time import strftime
from subprocess import call
from shutil import copyfile, copyfileobj
from utils import SummarybotStoppedError
from portalocker import lock, LOCK_SH, LOCK_NB, LockException
import logging


log = logging.getLogger('summarybot')


def replext(filename, new_ext):
    return path.extsep.join((path.splitext(filename)[0], new_ext))


class Backup(object):
    def __init__(self, batches, config):
        self.batches = batches
        self.copy_needed = config['backup']['copy']
        self.backup_needed = config['backup']['backup']
        self.script_path = path.dirname(__file__)
        self.repo = config['global']['repo']

    def copy(self):
        if not self.copy_needed:
            log.info('Skipping copy of batches')
            return
        log.info('Starting copy of batches')
        for batch in self.batches:
            remote = batch['remote']
            log.info('copying {}...'.format(remote))
            local = path.join(self.script_path, 'local', batch['local'])
            dirn = path.dirname(local)
            # create local directory if it doesn't exist yet
            if not path.exists(dirn):
                log.debug('Creating destination folder: {}'.format(dirn))
                makedirs(dirn)
            # copy remote db to local folder
            with open(remote, 'rb') as rfh, open(local, 'wb') as lfh:
                try:
                    lock(rfh, LOCK_SH | LOCK_NB)
                    log.debug('File locked')
                except LockException:
                    log.warning('Could not lock file, it might be modified during copying')
                try:
                    copyfileobj(rfh, lfh)
                except IOError as copyerr:
                    raise SummarybotStoppedError('Copy failed: {}'.format(copyerr))

    def backup(self):
        if not self.backup_needed:
            log.info('Skipping backup of batches')
            return
        log.info('Starting backup of batches')
        git_pull = ['git', 'pull']
        try:
            chdir(self.repo)
            call(git_pull)
        except (WindowsError, OSError) as e:
            raise SummarybotStoppedError('Git pull failed: {}'.format(e))
        for batch in self.batches:
            log.info('Creating dump of: {}'.format(batch['local']))
            local = path.join(self.script_path, 'local', batch['local'])
            local_sql = replext(local, 'sql')
            create_dump = [python, '-m', 'dump_batch_db', '-b', local, '-o', local_sql]
            try:
                call(create_dump)
            except OSError as e:
                raise SummarybotStoppedError('Dump failed: {}'.format(e))
            log.info('Staging files: {}'.format( replext(batch['local'], 'sql') ))
            repo_sql = replext(batch['local'], 'sql')
            try:
                copyfile(local_sql, repo_sql)
            except IOError as ioerr:
                raise SummarybotStoppedError('Copy failed: {}'.format(ioerr))
            git_add = ['git', 'add', repo_sql]
            try:
                call(git_add)
            except OSError as e:
                raise SummarybotStoppedError('Stage failed: {}'.format(e))
        log.info('Committing and pushing staged dump files')
        git_commit = ['git', 'commit', '-m', 'summarybot {}'.format(strftime('%Y-%m-%d %H-%M-%S'))]
        git_push = ['git', 'push']
        try:
            call(git_commit)
            call(git_push)
        except OSError as e:
            raise SummarybotStoppedError('Git backup failed: {}'.format(e))
        chdir(self.script_path)
