import csv
import sys
import glob
import os.path
from collections import OrderedDict

import numpy as np

from datavis import pyglet_workaround
from sim_mbt_mat import sim_mat
from measproc.IntervalList import cIntervalList


def get_warn_start(aebs_sys_state):
  COLLISION_WARNING_ACTIVE = 5 # TODO: code duplicated from AEBS_C/test/sil/test_util.py
  warn, = np.where(aebs_sys_state == COLLISION_WARNING_ACTIVE)
  return warn[0]

csv_path = sys.argv[1]
csv_dirname = os.path.dirname(csv_path)
csv_path_wo_ext, csv_ext = os.path.splitext(csv_path)
csv_out_path = csv_path_wo_ext + '_lin_regr' + csv_ext

# parse csv file
with open(csv_path, 'r') as f:
  reader = csv.DictReader(f, delimiter=',')
  rows_off = OrderedDict( (row['Name'], row) for row in reader if 'aOff' in row['Name'] ) # keep original order

with open(csv_out_path, 'wb') as f: # 'wb' mode is needed to avoid empty lines btw rows
  fieldnames_new = ['name', 't', 'dx', 'vrel', 'arel', 'tWarnDt', 'aAvoidOff', 'aAvoidOn']
  writer = csv.DictWriter(f, fieldnames_new, delimiter=';')
  writer.writeheader()
  for name, row in rows_off.iteritems():
    # skip failed test cases
    if 'FAILED' in row['coll_in_casc']:
      continue
    # simulate arel OFF
    mat_path, = glob.glob( os.path.join(csv_dirname, name+'_*') )
    t, inp, out, par, out_sim, internals = sim_mat(mat_path, UseAccelerationInfo=False)
    # skip simulation if warning start difference is more than 1 cycle
    warn_st     = get_warn_start( out['AEBS1_SystemState'] )
    warn_st_sim = get_warn_start( out_sim['AEBS1_SystemState'] )
    if abs(warn_st_sim - warn_st) > 1:
      print '%s skipped as warning start is different in simulation' %name
      continue
    # start to collect data form simulation
    # find timestamps where dt formula gives valid result
    tWarnDt = internals['tWarnDtForPred']
    aAvoidOff  = internals['aAvoidDynWarn']
    mask_dt_valid = (tWarnDt > 0.) & (tWarnDt < 3.)
    # skip simulation if no valid dt value found (i.e. warning started with saturated dt)
    if not np.any(mask_dt_valid):
      continue
    valid_dt_intervals = cIntervalList.fromMask(t, mask_dt_valid)
    # skip simulation if warning start is not in any valid dt interval
    try:
      st,end = valid_dt_intervals.findInterval(warn_st_sim)
    except ValueError:
      continue
    idx = np.arange(st, warn_st_sim) # take every data point until warning start (considering 1-cycle delay)
    # simulate arel ON (TODO: check at least warning start agreement with orig. meas.)
    mat_path, = glob.glob( os.path.join(csv_dirname, name.replace('aOff', 'aOn')+'_*') )
    _, _, _, _, _, internals = sim_mat(mat_path, UseAccelerationInfo=True)
    aAvoidOn  = internals['aAvoidDynWarn']
    # write new row for each data point during approach
    for i in idx:
      row_new = {'name'      : name,
                 't'         : t[i],
                 'dx'        : inp['dxv'][i],
                 'vrel'      : inp['vxv'][i],
                 'arel'      : round( inp['axv'][i], 1),
                 'tWarnDt'   : tWarnDt[i],
                 'aAvoidOff' : aAvoidOff[i],
                 'aAvoidOn'  : aAvoidOn[i],
                }
      writer.writerow(row_new)
