#!/usr/bin/python

import os
import sys
import optparse

import numpy

import datavis
import measproc

parser = optparse.OptionParser()
parser.add_option('-m', '--measurement', 
                  help='measurement file, default is %default',
                  default=r'D:/measurement/dataeval-test/CVR3_B1_2011-02-10_16-53_020.mdf')
parser.add_option('-u', '--backup-dir',
                  help='backup directory for SignalSource, default is %default',
                  default=r'D:/measurement/dataeval-test/backup')
parser.add_option('-d', '--stat-dir',
                  help='direcory to store statistics, default is %default',
                  default=r'D:/measurement/dataeval-test')
parser.add_option('-c', '--check-array', 
                  help='Array that srores the required value of the statistic, default is %default',
                  default=r'D:/measurement/dataeval-test/E_CreateStatistic.npy')
parser.add_option('-p', '--hold-navigator', 
                  help='Hold the navigator, default is %default',
                  default=False,
                  action='store_true')
Opts, Args = parser.parse_args()

status = 0
if not os.path.isfile(Opts.measurement):
  sys.stderr.write('%s: %s is not present\n' %(__file__, Opts.measurement))
  status += 1
if not os.path.isdir(Opts.backup_dir):
  sys.stderr.write('%s: %s is not present\n' %(__file__, Opts.backup_dir))
  status += 2
if not os.path.isdir(Opts.stat_dir):
  sys.stderr.write('%s: %s is not present\n' %(__file__, Opts.stat_dir))
  status += 4
if not os.path.isfile(Opts.check_array):
  sys.stderr.write('%s: %s is not present\n' %(__file__, Opts.check_array))
  status += 8
if status: exit(status)

measproc.Statistic.StatDir = Opts.stat_dir

Source = measproc.cEventFinder(Opts.measurement, Opts.backup_dir)

Time, Value = Source.getSignal('MRR1plus-0-0', 'csi.VelocityData_T20.vxwflRaw')
CoDomain_FL = Source.splitCoDomain(Time, Value, 0.0, 20.0, 5.0)

Time, Value = Source.getSignal('MRR1plus-0-0', 'csi.VelocityData_T20.vxwfrRaw')
CoDomain_FR = Source.splitCoDomain(Time, Value, 0.0, 20.0, 5.0)

Statistic = Source.convCoDomains('Wheel speeds', 'Front Left',  CoDomain_FL,
                                                 'Front Right', CoDomain_FR)
# create navigator for the statistic
StatNav = datavis.cStatisticNavigator()
StatNav.addStatistic(Statistic)
StatNav.start()
if Opts.hold_navigator:
  raw_input('Press enter to close the navigator.')
  sys.stdout.flush()
StatNav.close()

Statistic.save()
Source.save()

# compare the saved npy file with the actual statistic
TestArray = Opts.check_array
Array = numpy.load(TestArray)
assert (Statistic.Array == Array).all()

NpyPath = Statistic.PathToSave.replace('.xml', '.npy')
os.remove(Statistic.PathToSave)
os.remove(NpyPath)
