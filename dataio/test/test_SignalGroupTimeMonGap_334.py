import sys
import os
import getopt

from measparser.SignalSource import cSignalSource
from measparser.signalgroup  import str_errors
 

SignalGroups = [{'VidTime': ('Multimedia', 'Multimedia_1')}]

opts, args = getopt.getopt(sys.argv[1:], 'u:m:')
optdict = dict(opts)

meas   = optdict.get('-m', r'D:\measurement\334\MQB_MRR_2012-06-21_10-17_0004.MF4')
backup = optdict.get('-u', r'D:\measurement\backup')

if not os.path.exists(meas):
  sys.stderr.write('Test data %s is missing!\n' %meas)
  sys.stderr.flush()
  exit(1)
if not os.path.exists(backup):
  sys.stderr.write('Default backup directory %s is invalid !\n' %backup)
  sys.stderr.flush()
  exit(2)

source = cSignalSource(meas, backup)

groups, errors = source._filterSignalGroups(SignalGroups, StrictTime=True)
group, = groups
assert not group
error, = errors
invalid_times = error['Invalid times']
invalid_time_values = invalid_times.values()[0]
assert 'Multimedia_1' in  invalid_time_values

groups, errors = source._filterSignalGroups(SignalGroups, StrictTime=True, 
                                                          TimeMonGapIdx=2, 
                                                          TimeMonGapEps=1e-8)
group, = groups
assert 'VidTime' in group
error, = errors
invalid_times = error['Invalid times']
assert not invalid_times

group = source.selectSignalGroup(SignalGroups, StrictTime=True,
                                               TimeMonGapIdx=2, 
                                               TimeMonGapEps=1e-8)
assert 'VidTime' in group
source.save()  
