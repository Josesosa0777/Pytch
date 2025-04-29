import os
import sys
import sqlite3
import argparse as ap

from measproc.batchsqlite import _dump_db

parser = ap.ArgumentParser(description=
  'Collect the files for the given database and make a zip file from the '
  'given report directory to the given destination.')
parser.add_argument('-b', '--batch',
  required=True,
  help='Batch database to be dumped')
parser.add_argument('-o', '--output',
  help='Output sql file name')
args = parser.parse_args()

if args.output is not None:
  output = args.output
else:
  output = os.path.extsep.join((os.path.splitext(args.batch)[0], 'sql'))

con = sqlite3.connect(args.batch)
try:
  _dump_db(con, output)
finally:
  con and con.close()

sys.stderr.write("[INFO] Dump file successfully created: {}\n".format(output))
