from datavis import pyglet_workaround  # necessary as early as possible (#164)

import sys
import sqlite3
import argparse
import tempfile

from measproc.batchsqlite import (_get_measurementid_4_basename,
                                  _get_entryid_4_measurementid,
                                  _get_moduleid_4_classname,
                                  _rm_entry, _rm_measurement, _rm_module)


parser = argparse.ArgumentParser(description="""
  Manage batch database - add, remove, modify
""")
parser.add_argument('-b', '--batch',
  required=True,
  help='Batch database to be managed')
parser.add_argument('--repdir',
  default=tempfile.gettempdir(),
  help='Report directory for the managed batch')
parser.add_argument('--rm-entry-by-basename',
  nargs='+',
  metavar='BASENAME',
  help='Entries (by measurement basename) to be deleted. '
       'Referencing intervals, tags, etc. will also be deleted recursively.')
parser.add_argument('--rm-meas-by-basename',
  nargs='+',
  metavar='BASENAME',
  help='Measurements (by basename) to be deleted. '
       'Referencing entries will also be deleted recursively.')
parser.add_argument('--rm-module-by-classname',
  nargs='+',
  metavar='CLASSNAME',
  help='Modules to be deleted. '
       'Referencing entries will also be deleted recursively.')
args = parser.parse_args()


def rm_entry_by_basename(con, cur, basenames):
  "Remove entries from batch completely, based on measurement basename"
  for basename in basenames:
    try:
      meas_id = _get_measurementid_4_basename(cur, basename)
    except ValueError:
      sys.stderr.write("[WARNING] Measurement not found: '%s'\n" % basename)
      continue
    sys.stderr.write("[DEBUG] Deleting entries for measurement: '%s'\n" % basename)
    for entryid in _get_entryid_4_measurementid(cur, meas_id):
      _rm_entry(cur, entryid)
  con.commit()
  sys.stderr.write("[DEBUG] COMMIT\n")
  return

def rm_meas_by_basename(con, cur, basenames):
  "Remove measurements from batch completely"
  for basename in basenames:
    try:
      meas_id = _get_measurementid_4_basename(cur, basename)
    except ValueError:
      sys.stderr.write("[WARNING] Measurement not found: '%s'\n" % basename)
      continue
    sys.stderr.write("[DEBUG] Deleting measurement: '%s'\n" % basename)
    _rm_measurement(cur, meas_id)
  con.commit()
  sys.stderr.write("[DEBUG] COMMIT\n")
  return

def rm_module_by_classname(con, cur, classnames):
  "Remove modules from batch completely"
  for classname in classnames:
    module_ids = _get_moduleid_4_classname(cur, classname)
    if not module_ids:
      sys.stderr.write("[WARNING] Module class not found: '%s'\n" % classname)
      continue
    sys.stderr.write("[DEBUG] Deleting modules for class: '%s'\n" % classname)
    for module_id in module_ids:
      _rm_module(cur, module_id)
  con.commit()
  sys.stderr.write("[DEBUG] COMMIT\n")
  return


con = sqlite3.connect(args.batch)
try:
  cur = con.cursor()
  try:
    sys.stderr.write("[INFO] Connected to batch: '%s'\n" % args.batch)
    if args.rm_entry_by_basename is not None:
      rm_entry_by_basename(con, cur, args.rm_entry_by_basename)
    if args.rm_meas_by_basename is not None:
      rm_meas_by_basename(con, cur, args.rm_meas_by_basename)
    if args.rm_module_by_classname is not None:
      rm_module_by_classname(con, cur, args.rm_module_by_classname)
  finally:
    cur and cur.close()
finally:
  con and con.close()

sys.stderr.write("[INFO] Operations finished.\n")
