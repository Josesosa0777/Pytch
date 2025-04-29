from datavis import pyglet_workaround  # necessary as early as possible (#164)

import argparse

from measproc.batchsqlite import Batch, RESULTS, update

parser = argparse.ArgumentParser(description="""
  Merge batch database(s) into collector database
""")
parser.add_argument('batch', help='Collector batch file')
parser.add_argument('repdir', help='Report directory of the collector batch')
parser.add_argument('--merge', nargs=2, action='append',
                    metavar=('BATCH', 'REPDIR'),
                    help='Batch(es) and repdir(s) to be merged (pairwise)')
parser.add_argument('--batch-update', action='store_true', default=False)
parser.add_argument('--nodirectsound',  # handled in datavis/pyglet_workaround.py
                    help='do not load DirectSound driver - option might be removed!',
                    action='store_true',
                    default=False)
args = parser.parse_args()

labels, tags, quanames = {}, {}, {}
collector = Batch(args.batch, args.repdir, labels, tags, RESULTS, quanames)
for batch, repdir in args.merge:
  try:
    b = Batch(batch, repdir, labels, tags, RESULTS, quanames)
  except ValueError, error:
    if not args.batch_update: raise error

    update(batch, repdir)
    b = Batch(batch, repdir, labels, tags, RESULTS, quanames)
  collector.merge(b)
  b.save()
collector.save()
