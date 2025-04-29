import optparse

import numpy

from measparser.Mf4Parser import cMf4Parser

parser = optparse.OptionParser()
parser.add_option('-m', '--measurement', 
                  help='measurement file, default is %default',
                  default='D:/measurement/jochen/comparison_all_sensors_2012-10-10_13-47-25.MF4')

opts, args = parser.parse_args()

device = 'Multimedia-on_input-CANape-Multimedia-CANape'
signal = 'Multimedia_1'

mf4 = cMf4Parser(opts.measurement)

value, timekey = mf4.getSignal(device, signal)
time = mf4.getTime(timekey)
assert not numpy.isnan(value).any()
assert not numpy.isnan(time).any()

mf4.close()
