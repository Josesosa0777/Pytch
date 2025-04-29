#!C:\Python27\python.exe
from datavis import pyglet_workaround  # necessary as early as possible (#164)

import sys
import glob
import logging
import argparse

from config.Config import cScan
from config.helper import getConfigPath, getScanDirs
from config.modules import Modules
from config.logger import Logger

parser = argparse.ArgumentParser()
parser.add_argument('--main-pth', default='dataevalaebs',
                    help='Select registered directory for DATAEVAL_SCAN_DIR')
parser.add_argument('--verbose', '-v', action='count', default=0)
parser.add_argument('--config', action='append', default=[],
                    help='''scan/refresh the specified config with NAME which
                         has TYPE from {view, search, analyze}''')
parser.add_argument('--log-file', default='',
                    help='Logging file path pattern')
parser.add_argument('--nocolor',
                        help='Disable the stderr coloring function of logger',
                        action='store_true',
                        default=False)
parser.add_argument('--nodirectsound', #handled in datavis/pyglet_workaround.py
                    help='do not load DirectSound driver - '
                         'option might be removed!',
                    action='store_true',
                    default=False)
args = parser.parse_args()

scan_dirs = getScanDirs()

modules = Modules()

if args.verbose > 1:
  logger = Logger(args.log_file, logging.DEBUG, colorful_stderr=not args.nocolor)
elif args.verbose > 0:
  logger = Logger(args.log_file, logging.INFO, colorful_stderr=not args.nocolor)
else:
  logger = Logger(args.log_file, logging.WARNING,
                  colorful_stderr=not args.nocolor)


for prj_name, dir_name in scan_dirs.iteritems():
  msg = modules.scan(prj_name, dir_name)
  for name in sorted(msg):
    if not name.endswith('.py'): continue

    logger.log('skip %s' %name, logging.INFO)
    logger.log(msg[name], logging.DEBUG)

modules.write( getConfigPath('modules', '.csv') )

cfgs = glob.glob(getConfigPath('*.params', '.cfg'))

if args.config:
  for name in args.config:
    config = cScan(modules, scan_dirs, cfgs, args.main_pth)
    config.save(name)
else:
  config = cScan(modules, scan_dirs, cfgs, args.main_pth)
  config.save( getConfigPath('dataeval') )

logger.close()
