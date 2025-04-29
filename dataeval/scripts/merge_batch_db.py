from datavis import pyglet_workaround  # necessary as early as possible (#164)

import argparse
import tempfile

from measproc.batchsqlite import Batch, RESULTS, update

parser = argparse.ArgumentParser(description="""
  Merge batch database(s) into collector database - without report directory
""")
parser.add_argument('batch', help='Collector batch file')
parser.add_argument('--merge', action='append', help='Batch(es) to be merged')
parser.add_argument('--nodirectsound',  # handled in datavis/pyglet_workaround.py
                    help='do not load DirectSound driver - option might be removed!',
                    action='store_true',
                    default=False)
args = parser.parse_args()

labels, tags, quanames = {}, {}, {}
repdir = tempfile.gettempdir() # report directory not used, will not be modified
collector = Batch(args.batch, repdir, labels, tags, RESULTS, quanames)
for batch in args.merge:
  b = Batch(batch, repdir, labels, tags, RESULTS, quanames)
  collector.merge_db(b)
  b.save()
collector.save()
