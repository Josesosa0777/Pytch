import os
import sys
import argparse as ap

from measproc.batchsqlite import Batch, RESULTS

parser = ap.ArgumentParser(description=
  'Collect the files for the given database and make a zip file from the '
  'given report directory to the given destination.')
parser.add_argument('-b', '--batch',
  required=True,
  help='Batch database to be packed')
parser.add_argument('--repdir',
  required=True,
  help='Report directory to be packed')
parser.add_argument('-o', '--output',
  default='batch.zip',
  help='Output zip file name')
parser.add_argument('--repdir-only',
  action='store_true',
  help='Pack only report directory, skip batch database')
args = parser.parse_args()

assert os.path.isfile(args.batch), 'Invalid batch database: {}'.format(args.batch)
assert os.path.isdir(args.repdir), 'Invalid report directory: {}'.format(args.repdir)

labels, tags, quanames = {}, {}, {}
b = Batch(args.batch, args.repdir, labels, tags, RESULTS, quanames)
try:
  b.pack_batch(args.output, args.repdir_only)
finally:
  b.save()

sys.stderr.write('[INFO] Zip file successfully created: {}\n'.format(args.output))
