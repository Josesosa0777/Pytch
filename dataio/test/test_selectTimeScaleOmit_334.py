import sys
import os
import getopt

from measparser.Mf4Parser import cMf4Parser
from measparser.signalproc  import selectTimeScale
 

dev_name = 'Multimedia'
sig_name = 'Multimedia_1'

opts, args = getopt.getopt(sys.argv[1:], 'u:m:')
optdict = dict(opts)

meas = optdict.get('-m', r'D:\measurement\334\MQB_MRR_2012-06-21_10-17_0004.MF4')
if not os.path.exists(meas):
  sys.stderr.write('Test data %s is missing!\n' %meas)
  sys.stderr.flush()
  exit(1)


parser = cMf4Parser(meas)
dev_name, = parser.getNames(sig_name, dev_name)
timekey = parser.getTimeKey(dev_name, sig_name)
time = parser.getTime(timekey)

times = [time]
try:
  selectTimeScale(times, True)
except IndexError, error:
  pass
else:
  sys.stderr.write('Missing IndexError\n')
  sys.stderr.flush()
  exit(1)
parser.close()
