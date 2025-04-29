import logging
from ConfigParser import ConfigParser, NoOptionError, NoSectionError
from csv import DictReader, Error as csvError
from time import strftime
from os import path, makedirs, getenv
from backup import Backup
from merge import Merge
from statistics import Statistics
from utils import SummarybotStoppedError


log = logging.getLogger('summarybot')


def configure_logging():
    log.setLevel(logging.DEBUG)
    aebs = '.' + getenv('DATAEVAL_NAME', 'dataeval')
    log_dirname = path.expanduser(path.join('~', aebs, 'summarybot_logs'))
    if not path.exists(log_dirname):
        makedirs(log_dirname)
    log_filename = 'summarybot_{}.log'.format(strftime('%Y-%m-%d_%H-%M-%S'))
    fh = logging.FileHandler(path.join(log_dirname, log_filename))
    fh.setLevel(logging.DEBUG)
    fh_formatter = logging.Formatter('%(asctime)s [%(levelname)s]\t%(module)s, L%(lineno)d:\t%(message)s')
    fh.setFormatter(fh_formatter)
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    chFormatter = logging.Formatter('[%(levelname)s] %(message)s')
    sh.setFormatter(chFormatter)
    log.addHandler(fh)
    log.addHandler(sh)


def read_config(filename):
    log.info('Reading config file: {}'.format(filename))
    confp = ConfigParser()
    filenames_read = confp.read(filename)
    if filenames_read[0] != filename:
        raise SummarybotStoppedError("Could not read configuration file: '{}'".format(filename))
    try:
        cfg = {'global': {}, 'backup': {}, 'merge': {}, 'statistics': {}}
        cfg['global']['repo'] = confp.get('global', 'repository')
        cfg['global']['log_level'] = confp.get('global', 'log_level')
        cfg['backup']['copy'] = confp.getboolean('backup', 'copy')
        cfg['backup']['backup'] = confp.getboolean('backup', 'backup')
        cfg['merge']['merge'] = confp.getboolean('merge', 'merge')
        cfg['merge']['backup'] = confp.getboolean('merge', 'backup')
        cfg['merge']['backup_path'] = confp.get('merge', 'backup_path')
        cfg['statistics']['analyze'] = confp.getboolean('statistics', 'analyze')
        cfg['statistics']['upload'] = confp.getboolean('statistics', 'upload')
        cfg['statistics']['redmine_url'] = confp.get('statistics', 'redmine_url')
        cfg['statistics']['api_key_path'] = confp.get('statistics', 'api_key_path')
    except (NoOptionError, NoSectionError) as noxerr:
        raise SummarybotStoppedError("Invalid configuration file '{}': {}".format(filename, noxerr))
    return cfg


def read_batches(filename):
    log.info('Reading batches: {}'.format(filename))
    bts = []
    with open(filename, 'rb') as batch_csv:
        try:
            dictreader = DictReader(batch_csv, delimiter=';', skipinitialspace=True)
            for row in dictreader:
                bts.append(row)
        except csvError as ce:
            raise SummarybotStoppedError('Could not read batches: {}'.format(ce))
    return bts


# --------------------------------------------------------------------------------------
if __name__ == '__main__':
    configure_logging()
    log.info('\n-----------------------------------------------------------\n'
               '               The summarybot has been awaken              \n'
               '-----------------------------------------------------------')
    try:
        config = read_config('botconfigs/config.cfg')
        new_level = config['global']['log_level']
        log.info('Setting log level to {}'.format(new_level))
        log.setLevel(new_level)
        batches = read_batches('botconfigs/batches.csv')
        backup = Backup(batches, config)
        merge = Merge(batches, config)
        statistics = Statistics(config)
        backup.copy()
        backup.backup()
        merge.merge()
        merge.backup()
        statistics.analyze()
        statistics.upload()
    except SummarybotStoppedError as stoperr:
        log.error('The summarybot encountered an error, and stopped excution: {}'.format(stoperr))
    finally:
        log.info('\n-----------------------------------------------------------\n'
                   '              The summarybot goes back to sleep            \n'
                   '-----------------------------------------------------------')
