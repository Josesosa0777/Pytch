import sys

import numpy

import measparser

parsers = []
for name in sys.argv[1:]:
  Parser = measparser.SignalSource.findParser(name)
  parser = Parser(name)
  parsers.append(parser)

if len(parsers) == 2:
  mdf, hdf = parsers
else:
  sys.stderr.write('invalid argument\n')
  exit(1)

status = 0
times = set()
for dev in mdf.iterDeviceNames():
  for sig in mdf.iterSignalNames(dev):
    if not mdf.getSignalLength(dev, sig):
      continue
    valueMdf, timekey = mdf.getSignal(dev, sig)
    times.add(timekey)
    try:
      valueHdf, timekey =  hdf.getSignal(dev, sig)
    except KeyError:
      status |= 1
      sys.stdout.write('NameError: %s %s\n' %(dev, sig))
      sys.stdout.flush()
    else:
      if valueMdf.dtype != valueHdf.dtype:
        status |= 8
        sys.stdout.write('DtypeError: %s %s (%s != %s)\n' %(dev, 
                                                            sig, 
                                                            valueMdf.dtype.descr, 
                                                            valueHdf.dtype.descr))
        sys.stdout.flush()
      else:
        kind = valueMdf.dtype.kind
        if kind in ('i', 'u'): 
          if not (valueMdf == valueHdf).all():
            status |= 2
            sys.stdout.write('ValueError: %s %s\n' %(dev, sig))
            sys.stdout.flush()
        elif kind == 'f':
          if not numpy.allclose(valueMdf, valueHdf):
            status |= 2
            sys.stdout.write('ValueError: %s %s\n' %(dev, sig))
            sys.stdout.flush()
        else:
          if valueMdf.size != valueHdf.size:
            status |= 4
            sys.stdout.write('SizeError: %s %s\n' %(dev, sig))
            sys.stdout.flush()

for timekey in sorted(times):
  timeMdf = mdf.getTime(timekey)
  timeHdf = hdf.getTime(timekey)
  if not numpy.allclose(timeMdf, timeHdf):
    status |= 2
    sys.stdout.write('ValueError: %s \n' %(timekey))
    sys.stdout.flush()

mdf.close()
hdf.close()

exit(status)

