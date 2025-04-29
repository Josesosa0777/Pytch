from datavis import pyglet_workaround  # necessary as early as possible (#164)

import sys
import os
import argparse

from measproc.Batch import cBatch as BatchXml
from measproc.batchsqlite import Batch as BatchSqlite, RESULTS
from aebs.par.labels import default as labels
from aebs.par.tags import default as tags
from aebs.par.quanames import default as quanames

delete = ['M_Unnecessary', 'M_False detection', 'M_Other']
                                 
rename = {
  'Stationary':            'stationary',
  'Moving':                'moving',
  
  'scam-unavailable':      'S-Cam',
  
  'fw-red-with-sdf':       'fw red with sdf',
  
  'parking_car':           'parking car',
  'road_exit':             'road exit',
  'high_curvature':        'high curvature',
  'traffic_island':        'traffic island',
  'approaching_curve':     'approaching curve',
  'straight_road':         'straight road',
  'construction_site':     'construction site',
  'braking_fw_vehicle':    'braking fw vehicle',
  
  'CVR3W_sels_wo_SDF':     'CVR3W sels w/o SDF',
}

vote2label = {
  'invalid':               'standard',
  'missed':                'standard',
  'valid':                 'standard',
  
  'stationary':            'moving state',
  'moving':                'moving state',
  
  'fw red with sdf':       'false warning reduction',
  
  'S-Cam':                 'sensor n/a',
  
  'bridge':                'false warning cause',
  'tunnel':                'false warning cause',
  'infrastructure':        'false warning cause',
  'parking car':           'false warning cause',
  'road exit':             'false warning cause',
  'high curvature':        'false warning cause',
  'traffic island':        'false warning cause',
  'approaching curve':     'false warning cause',
  'straight road':         'false warning cause',
  'construction site':     'false warning cause',
  'braking fw vehicle':    'false warning cause',
  
  'CVR3W sels w/o SDF':     'sels warning',
}


parser = argparse.ArgumentParser(
           description="""Converts xml batches into sqlite batches with the same
           name. If MAIN_BATCH and REPDIR is given merge the converted databases
           into MAIN_BATCH.""")
parser.add_argument('batch', nargs='+', help='name of the batch xml file')
parser.add_argument('--main-batch',
                    help='Name of the collector batch sqlite file')
parser.add_argument('--repdir',
                    help='Name of the report directory for the collector batch')
parser.add_argument('--no-save', default=False, action='store_true',
                    help="""Do not save the converted batch, only the MAIN_BATCH
                         will contain the converted result, if its selected.""")

args = parser.parse_args()
merge_batch = args.main_batch and args.repdir
_dbnames = []

if merge_batch:
  main = BatchSqlite(args.main_batch, args.repdir, labels, tags, RESULTS,
                     quanames)

for name in args.batch:
  xml = BatchXml(name, 'now')
  sqlite = BatchSqlite.from_batchxml(xml, delete, rename, vote2label, labels)
  _dbnames.append(sqlite.dbname)
  if merge_batch:
    main.merge(sqlite)
  sqlite.save()

if args.no_save:
  for name in _dbnames:
    os.remove(name)

if merge_batch:
  main.save()

