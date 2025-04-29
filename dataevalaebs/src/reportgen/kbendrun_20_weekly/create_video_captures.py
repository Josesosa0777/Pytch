import os
import sys
import csv
import time
import shutil
import logging
import argparse
import tempfile
import subprocess


# default values
CONFIG_NAME = None  # stdin
OUTPUT_DIR = time.strftime(r"\\strs0004\Measure1\DAS\EnduranceRun\AEBS_Warning_Videos\Labeling_%Y-%m-%d", time.localtime())

# parse arguments
parser = argparse.ArgumentParser(description="""
  Create local video captures and copy combined captures to the given directory
""")
parser.add_argument('--config',
  default=CONFIG_NAME,
  help='Configuration CSV file (interval table) with list of events')
parser.add_argument('--outputdir',
  default=OUTPUT_DIR,
  help='Directory to store the final (combined) captures')
parser.add_argument('--localonly',
  action='store_true',
  default=False,
  help='Do not copy captures to the final directory but keep temporary directory')
parser.add_argument('--noclean',
  action='store_true',
  default=False,
  help='Do not delete temporary directory')
args = parser.parse_args()

# init logger
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger()

# functions
def read_config(config_name):
  def read_config_from_fp(fp):
    logger.info("Reading configuration file: %s" %fp.name)
    reader = csv.DictReader(fp, delimiter="|")
    bfrds = []
    for row in reader:
      bfrds.append((row['fullmeas'],
                    float(row['start [s]']),
                    float(row['duration [s]'])))
    return bfrds
  
  if config_name is None:
    bfrds = read_config_from_fp(sys.stdin)
  else:
    with open(config_name) as fp:
      bfrds = read_config_from_fp(fp)
  return bfrds

def create_captures(bfrds,selected_module_list):
  has_param =[]
  no_param=[]
  for selected_module in selected_module_list[0][0]:
    result = selected_module.rsplit("@",1)
    if result[0].find("-")>0:
      has_param.append(selected_module)

    else:
      no_param.append(selected_module)

  local_capture_dir = os.path.join(tempfile.gettempdir(), time.strftime(
    "captures__%%Y-%%m-%%d_%%H-%%M-%%S" % time.localtime()))
  if bfrds and not os.path.isdir(local_capture_dir):
    logger.info("Temporary capture directory created: %s" % local_capture_dir)
    os.makedirs(local_capture_dir)
  for fullmeas, start, duration in bfrds:
    result = ""
    for inter in has_param:
      substart = '-'
      subend = '@'
      result+= " -i "+  (inter.split(substart)[0] +"@"+ inter.split(substart)[1].split(subend)[1]) \
               +" -n "+( inter.split(substart)[0] +"@"+ inter.split(substart)[1].split(subend)[1]) \
               +" -p "+(inter.split(substart)[0] +"@"+ inter.split(substart)[1].split(subend)[1]+"."+inter.split(substart)[1].split(subend)[0])
    for exter in no_param :
      result += " -i "+ exter

    logger.info("Creating captures for %s..." % os.path.basename(fullmeas))
    try:
      cmd = \
        '%(python)s -m view --nosave --nonav --nodirectsound ' \
        '-m %(fullmeas)s ' \
        '--record %(start).1f %(end).1f %(capdir)s --combine ' \
        '-n iView ' \
        '%(resultcmd)s' \
        % dict(
                python = sys.executable,
                fullmeas = fullmeas,
                start = max(start- 10.0, 0.0),
                end = start + duration + 10.0,
                capdir = local_capture_dir,
                resultcmd = result,

        )
      subprocess.call(cmd)
    except BaseException, e:
      logger.error(e.message)
  return local_capture_dir

def copy_final_captures(bfrds, local_capture_dir, output_dir):
  if bfrds and not os.path.isdir(output_dir):
    os.makedirs(output_dir)
  
  #for fullmeas, start, duration in bfrds:
  #  logger.info("Copying capture for %s..." % os.path.basename(fullmeas))
  #  try:
  #    shutil.copy(bf, output_dir)
  #  except BaseException, e:
  #    logger.error(e.message)
  
  for dirpath, dirs, files in os.walk(local_capture_dir):
    for filename in files:
      if filename.endswith("__allNavs.avi"):
        logger.info("Copying %s..." % filename)
        try:
          shutil.copy(os.path.join(dirpath, filename), output_dir)
        except BaseException, e:
          logger.error(e.message)
  return

def clean(local_capture_dir):
  shutil.rmtree(local_capture_dir)
  logger.info("Temporary capture directory removed: %s" % local_capture_dir)
  return

# main
if __name__ == "__main__":
  bfrds = read_config(args.config)
  local_capture_dir = create_captures(bfrds)
  if not args.localonly:
    copy_final_captures(bfrds, local_capture_dir, args.outputdir)
  if not args.noclean and not args.localonly:
    clean(local_capture_dir)
