import os
import time
import argparse

from measproc.batchsqlite import Batch, RESULTS
from measproc.batchconv import KbtoolsConv
from aebs.par.labels import default as labels
from aebs.par.tags import default as tags
from aebs.par.quanames import default as quanames

parser = argparse.ArgumentParser(description="""
  Convert xls result of kbtools to dataeval sqlite database
""")
parser.add_argument('xls', nargs='+',
                    help='Name of the MS excel spread sheet files')
parser.add_argument('--meas-root', help='Root directory of the measurement')
parser.add_argument('--meas-dir', help='parent directory of the measurement',
                    default='*')
parser.add_argument('--server', action='store_true', default=False,
                    help='Measurements are stored on server')
parser.add_argument('-b', '--batch',
                    help='Name of the collector batch sqlite file')
parser.add_argument('--repdir',
                    help='Name of the report directory for the collector batch')

args = parser.parse_args()

meas_colname = 'FileName'
time_colname = 't start'
duration_colname = 'dura'
time_signal = 'General_radar_status', 'cm_system_status'
start = time.strftime(Batch.TIME_FORMAT)

col2label = {
  ('AEBS_cascade', 'AEBS cascade phase'): {
     1: 'warning',
     2: 'partial braking',
     3: 'emergency braking',
  },
  ('Stationary_at_t_start', 'moving state'): {
    0: 'moving',
    1: 'stationary',
  },
  ('is_video_associated_at_t_start', 'asso state'): {
    0: 'radar only',
    1: 'fused',
  },
}
col2qua = {
  'v_ego_at_t_start': ('ego vehicle', 'speed start', 1.0/3.6),
  'dx_at_t_start': ('target', 'dx start', 1.0),
  't_start_cw_track_before_AEBS_warning': ('target', 'pure aeb duration', 1.0),
  'dx_at_cw_track_start': ('target', 'dx aeb', 1.0),
}


conv = KbtoolsConv(args.meas_root, args.meas_dir, *time_signal)
main = Batch(args.batch, args.repdir, labels, tags, RESULTS, quanames)
batches = []
for xls in args.xls:
  batch, ext = os.path.splitext(xls)
  batch += '.db'
  batches.append(batch)
  batch = Batch.from_xls(xls, batch, args.repdir, labels, tags, RESULTS,
                         quanames, start, not args.server, meas_colname,
                         time_colname, duration_colname, col2label, col2qua,
                         conv)
  main.merge(batch)
  batch.save()
main.save()
for batch in batches:
  os.remove(batch)

