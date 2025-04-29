"""
usage: python compare_mdf.py -s S [-m M] [-h] [-e E] [-b B] F [F ...]

Compare the signal names in F and list those who are not equal.

arguments:
 -s S csv file which contains the signal names which will be checked.
 F    Path of the measurement files that will be processed.
      This list can be extended or replaced with M.
 
optional arguments:
 -h   Show this help message and exit.
 -m M csv file which contains measurement file paths which will extend the F.
 -e E Eps for floating point number comparison. Default is 1e-12.
 -b B Path of the backup directory. Default option store the backup beside the 
      measurement.
"""
import measparser
import purge_mdf

def checkSignal(source_a, source_b, devname, signame, eps):
  ta, va = source_a.getSignal(devname, signame)
  tb, vb = source_b.getSignal(devname, signame)
  if va.size != vb.size:
    raise ValueError('The %s %s\n'
                     'in\n'
                     '%s\n'
                     'and\n'
                     '%s\n'
                     'has different size (%d != %d)' %(devname, signame, source_a.FileName, source_b.FileName, va.size, vb.size))
  check = va == vb
  check = check.all()
  if not check:
    diff = va - vb
    diff = diff.mean()
    diff = abs(diff)
    check = diff < eps
  return check

def getNames(source, signals):
  allsignal = set()
  source.loadParser()
  parser = source.Parser
  for devname in parser.iterDeviceNames():
    names = parser.iterSignalNames(devname)
    names = signals.intersection(names)
    for name in names:
      name = devname, name
      allsignal.add(name)
  return allsignal
  
if __name__ == '__main__':
  import sys
  import getopt
  import os
  
  opts, args = getopt.getopt(sys.argv[1:], 'hs:b:e:m:')
  opts = dict(opts)
  
  if '-h' in opts or '-s' not in opts or (not args and '-m' not in opts):
    sys.stderr.write(__doc__)
    exit()
  exit()  
  try:
    NpyHomeDir = opts['-b']
  except KeyError:
    NpyHomeDir = None
  try:
    eps = opts['-e']
  except KeyError:
    eps = 1e-12
  else:
    eps = float(eps)
  try:
    paths = purge_mdf.cvs_parser(opts['-m'])
  except KeyError:
    paths = set()
  paths = paths.union(args)  
  sources = [measparser.cSignalSource(path, NpyHomeDir) for path in paths]
  
  signals = purge_mdf.cvs_parser(opts['-s'])
  source_signals = {}
  for source in sources:
    source_signals[source] = getNames(source, signals)
  allresult = {}
  while sources:
    source_a = sources.pop()
    signals_a = source_signals[source_a]
    for source_b in sources:
      print 'Compare %-60s with %s' %(os.path.basename(source_a.FileName), os.path.basename(source_b.FileName))
      signals_b = source_signals[source_b]
      result = []
      for devname, signame in signals_a.intersection(signals_b):
        if not checkSignal(source_a, source_b, devname, signame, eps):
          result.append((devname, signame))
      if result:
        allresult[(source_a.FileName, source_b.FileName)] = result
    source_a.save()  
  
  if allresult:
    print 'The following signals are not equal'
  for (file_a, file_b), result in allresult.iteritems():
    print os.path.basename(file_a), os.path.basename(file_b)
    for devname, signame in result:
      print '  %-42s %s' %(devname, signame)
