import os
import glob
import logging
import time
import argparse
import datetime

from state_machine import processCfgFile

def processCfgFiles(cfgFiles, wait4meas=True):
    startTime = time.time()
    mainLogger = logging.getLogger('end_run_state')
    mainLogger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    chFormatter = logging.Formatter('[%(levelname)s] %(message)s')
    ch.setFormatter(chFormatter)
    logDirname = os.path.expanduser(os.path.join('~',
      '.%s' % os.getenv('DATAEVAL_NAME', 'dataeval'),
      'evalbot_logs'))
    if not os.path.exists(logDirname):
        os.makedirs(logDirname)
    logFilename = 'evalbot_%s.log' % datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    fh = logging.FileHandler(os.path.join(logDirname, logFilename))
    fh.setLevel(logging.DEBUG)
    fhFormatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    fh.setFormatter(fhFormatter)
    mainLogger.addHandler(ch)
    mainLogger.addHandler(fh)
    
    logger = logging.getLogger('end_run')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    chFormatter = logging.Formatter('[%(levelname)s] %(message)s')
    ch.setFormatter(chFormatter)
    logger.addHandler(ch)
    
    for cfgFile in cfgFiles:
        processCfgFile(cfgFile, wait4meas=wait4meas)
    
    logger.removeHandler(ch)
    executionTime = (time.time() - startTime)
    print('Total Execution time in minutes: ' + str(executionTime/60))


if __name__ == '__main__':
    # parse arguments
    parser = argparse.ArgumentParser(description=
      "evalbot - Automatic measurement evaluation")
    parser.add_argument('cfgfiles',
      nargs='+',
      help='evalbot config files to be processed')
    parser.add_argument('--no-wait',
      action='store_true',
      default=False,
      help='Do not wait for measurement files, run immediately on existing ones')
    args = parser.parse_args()
    
    cfgFiles = []
    for arg in args.cfgfiles:
        for cfgFile in glob.glob(arg):
            cfgFiles.append(cfgFile)
    
    processCfgFiles(cfgFiles, wait4meas=not args.no_wait)
