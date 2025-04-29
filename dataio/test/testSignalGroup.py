#!/usr/bin/python

import measparser
import os
import optparse

from measparser.signalgroup import SignalGroupError

parser = optparse.OptionParser()
parser.add_option('-m', '--measurement', 
                  help='measurement file, default is %default',
                  default=r'D:/measurement/dataeval-test/CVR3_B1_2011-02-10_16-53_020.mdf')
parser.add_option('-u', '--backup-dir',
                  help='backup directory for SignalSource, default is %default',
                  default=r'D:/measurement/backup')
Opts, Args = parser.parse_args()

ShortDeviceName = 'Tracks'

ValidSignalGroups = []
SignalGroup = {}
for i in xrange(5):
  SignalName = 'tr%d_range' %i
  SignalGroup[SignalName] = ShortDeviceName, SignalName
ValidSignalGroups.append(SignalGroup)

ExtraSignalGroups = []
SignalGroup = {}
for i in xrange(6):
  SignalName = 'tr%d_range' %i
  SignalGroup[SignalName] = ShortDeviceName, SignalName
ExtraSignalGroups.append(SignalGroup)

Source = measparser.cSignalSource(Opts.measurement, Opts.backup_dir)

# test the valid signal group list
try:
  Group = Source.selectSignalGroup(ValidSignalGroups)
except ValueError, error:
  # no exception can be risen in this case
  raise error
else:
  # get a signal from the selected signal group
  Time, Value = Source.getSignalFromSignalGroup(Group, 'tr0_range')

# validate the whole valid signal groups list
try:
  Groups = Source.validateSignalGroups(ValidSignalGroups)
except SignalGroupError, error:
  raise error
else:
  # get the signals from the validated signal groups
  for Group in Groups:
    Time, Value = Source.getSignalFromSignalGroup(Group, 'tr0_range')

  
Groups = Source.filterSignalGroups(ValidSignalGroups)
for Original, Filtered in zip(ValidSignalGroups, Groups):
  assert set(Original.keys()) == set(Filtered.keys())

# test the signal group list with extra not valid signals
try:
  Group = Source.selectSignalGroup(ExtraSignalGroups)
except SignalGroupError, error:
  pass
else:
  raise ValueError('exception has to be risen because ve have an invalid signal name')

# validate the whole extra signal groups list
try:
  Groups = Source.validateSignalGroups(ExtraSignalGroups)
except SignalGroupError, error:
  # an exception is thrown here (there is at least one invalid signal)
  pass
else:
  raise ValueError('exception has to be risen because ve have an invalid signal name')
  
Check = set()
Check.add('tr5_range')
Groups = Source.filterSignalGroups(ExtraSignalGroups)
for Original, Filtered in zip(ExtraSignalGroups, Groups):
  assert set(Original.keys()).difference(Filtered.keys()) == Check

Source.save()
