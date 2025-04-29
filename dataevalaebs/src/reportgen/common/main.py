import os
import sys
import argparse
import tempfile
import subprocess

def main(module_file_name):
  dirname, modulename = os.path.split(os.path.abspath(module_file_name))
  modulename = os.path.splitext(modulename)[0]
  prj = 'dataevalaebs%(sep)ssrc%(sep)s' % dict(sep=os.path.sep)
  subprj = dirname[(dirname.rfind(prj) + len(prj)) : ].replace(os.path.sep, '.')
  fullmodulename = "%s@%s" % (modulename, subprj)
  
  # parse arguments
  parser = argparse.ArgumentParser(description=
    "Generate report")
  parser.add_argument('-b', '--batch',
    required=True,
    help='set BATCH as batch database')
  parser.add_argument('--repdir',
    default=os.path.join(tempfile.gettempdir(), "repdir"),
    help='set REPDIR as report directory for BATCH')
  parser.add_argument('--doc-name',
    default="report.pdf",
    help='Name of the generated pdf document')
  parser.add_argument('--start-date',
    help='Store \'start_date\' attribute to use for filtering query results')
  parser.add_argument('--mid-date-1',
    help='Store date #1 into \'datelist\' global parameter to use for filtering query results')
  parser.add_argument('--mid-date-2',
    help='Store date #2 into \'datelist\' global parameter to use for filtering query results')
  parser.add_argument('--end-date',
    help='Store \'end_date\' attribute to use for filtering query results')
  args = parser.parse_args()
  
  if (args.mid_date_1 is None) ^ (args.mid_date_2 is None):
    parser.error("Either both or neither mid dates shall be defined")
  
  cmd = \
    '%(python)s -m analyze --nosave --nodirectsound --nonav -n iAnalyze '\
     '-i %(module)s '\
     '-b %(batch)s --repdir %(repdir)s '\
     '--doc-name %(outfile)s '\
     % dict(
          python=sys.executable,
          module=fullmodulename,
          outfile=args.doc_name,
          batch=args.batch,
          repdir=args.repdir,
      )
  if args.start_date is not None:
    cmd += "--start-date %s " % args.start_date
  if args.end_date is not None:
    cmd += "--end-date %s " % args.end_date
  if args.mid_date_1 is not None and args.mid_date_2 is not None:
    cmd += "--global-param datelist \"%s %s\" " % (args.mid_date_1, args.mid_date_2)
  
  print >> sys.stderr, "Executing:\n%s\n" % cmd
  subprocess.call(cmd)
