import os
import sys
import csv
import shutil
import logging
import argparse
import subprocess


# default values
CONFIG_NAME = "databases.csv"
BATCH_DIR = "batches"
COLLECTOR_BATCH_NAME = os.path.join(BATCH_DIR, "batch_all.db")

# parse arguments
parser = argparse.ArgumentParser(description="""
  Copy and merge batch database(s) into collector database - without report directory
""")
parser.add_argument('--config',
  default=CONFIG_NAME,
  help='Configuration CSV file with list of batches')
parser.add_argument('--batchdir',
  default=BATCH_DIR,
  help='Directory to store the source and destination batches')
parser.add_argument('--collectorbatch',
  default=COLLECTOR_BATCH_NAME,
  help='Collector batch file')
parser.add_argument('--nocopy',
  action='store_true',
  default=False,
  help='Do not copy batch files, only merge')
parser.add_argument('--nomerge',
  action='store_true',
  default=False,
  help='Do not merge batch files, only copy')
args = parser.parse_args()

# init logger
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger()

# functions
def read_config(config_name):
  with open(config_name) as csvfile:
    reader = csv.DictReader(csvfile, delimiter=";")
    bfrds = []
    for row in reader:
      if bool(int(row['enabled'])):
        bfrds.append(row['batchfile'])
      else:
        logger.info("Skip %s" % row['batchfile'])
  return bfrds

def copy_batches(bfrds, batchdir):
  if bfrds and not os.path.isdir(args.batchdir):
    os.makedirs(batchdir)
  for bf in bfrds:
    logger.info("Copying %s..." % bf)
    bf_local = _get_local_batch_name(bf, batchdir)
    try:
      shutil.copy(bf, bf_local)
    except BaseException, e:
      logger.error(e.message)
  return

def merge_batches(bfrds, batchdir, collectorbatch):
  for bf in bfrds:
    logger.info("Merging %s..." % bf)
    bf_local = _get_local_batch_name(bf, batchdir)
    try:
      subprocess.call('"%s" -m merge_batch_db "%s" --merge "%s" --nodirectsound' %
                      (sys.executable, collectorbatch, bf_local))
    except BaseException, e:
      logger.error(e.message)
  return

def _get_local_batch_name(batch, batchdir):
  base, ext = os.path.splitext(os.path.basename(batch))
  sfx = os.path.normpath(os.path.dirname(batch)).replace(os.path.sep, "_").replace("$", "").replace(" ", "")  # TODO: extend & restruct
  local_batch_basename = "%s__%s%s" % (base, sfx, ext)
  return os.path.join(batchdir, local_batch_basename)

bfrds = read_config(args.config)
if not args.nocopy:
  copy_batches(bfrds, args.batchdir)
if not args.nomerge:
  merge_batches(bfrds, args.batchdir, args.collectorbatch)
