#!/usr/bin/python

import optparse

from measparser.Mf4Parser import cMf4Parser

parser = optparse.OptionParser()
parser.add_option('-m', '--measurement', 
                  help='measurement file, default is %default',
                  default='d:/measurement/379/comparison_all_sensors_2012-07-31_23-11-33.MF4')

opts, args = parser.parse_args()

dev_name = 'RadarFC-tc---RadarFC'
sig_name = 'evi.General_TC.psiDtOpt'

parser = cMf4Parser(opts.measurement)
value, timekey = parser.getSignal(dev_name, sig_name)
time = parser.getTime(timekey)

assert parser.getSignalLength(dev_name, sig_name) == value.size

parser.close()
