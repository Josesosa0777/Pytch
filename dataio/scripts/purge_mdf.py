"""
python purge_mdf.py -i Input -o Output -p Parameter

 -i input mdf file or directory of mdf files
 -o if -i is an mdf file it must be too
    if -i is a directory of mdf files it must be too
 -s parameter cvs file that contains the signal names to put into output file
 -d parameter cvs file that contains the device names to put into output file
 -t run test over the created file(s)
 -h print this help
"""

def cvs_parser(file_name):
  """
  :Parameters:
    file_name : str
      path of the cvs parameter file
  :ReturnType: list
  :Return: list of the signal names to put into the new mdf file
  """
  s = open(file_name).read()
  l = s.split()
  l = set(l)
  return l

import sys

from measproc.Batch import findMeasurements 
from measparser.MdfParser import cMdfParser

def purge_mdf(input, output, devices, signals):
  """
  :Parameters:
    input : str
      path of the input file
    output : str
      path of the output file
    device : set
      list of the device names that will be in the output file
    signals : set
      list of the signal names that will be in the output file
  """
  parser = cMdfParser(input)
  parser.openOutputFile(output) 
  
  missing = signals.copy()
  kept_devices = set()
  removed_devices = set()
  
  device_names = set(parser.iterDeviceNames())
  device_names = device_names.difference(devices)  
  
  if signals:
    for device in device_names:    
      parser_signals = set(parser.iterSignalNames(device))    
      actual_signals = parser_signals.difference(signals)
      if actual_signals == parser_signals:
        parser.rmDevice(device)
        removed_devices.add(device)
      elif actual_signals:
        for signal in actual_signals:
          parser.rmSignal(device, signal)
        kept_devices.add(device)
      else:  
        kept_devices.add(device)  
      missing = missing.difference(actual_signals)  
  
  device_names = device_names.difference(kept_devices)
  device_names = device_names.difference(removed_devices)
  
  for device in device_names:
    parser.rmDevice(device)    
  
  parser.close()
  return missing, kept_devices
  
def test_mdf(output, signals, devices):
  """
  :Parameters:
    output : str
      created mdf file
    signal : set
      list of the signal names that will be in the output file
  :ReturnType: set, set
  :Return: 
    extra signal names in the created mdf
    missed signal names in the created mdf
  """
  parser = cMdfParser(output)
  parser_signals = set()
  parser_devices = set(parser.iterDeviceNames())
  check_devices = parser_devices.difference(devices)
  for device in check_devices:
    for signal in parser.iterSignalNames(device):
      parser_signals.add(signal)      
  parser.close()
  missed = signals.difference(parser_signals)
  extra = parser_signals.difference(signals)
  missed_devices = devices.difference(parser_devices)
  extra_devices = parser_devices.difference(devices)
  return extra, missed, extra_devices, missed_devices

if __name__ == '__main__':  
  import getopt
  import os

  opts, args = getopt.getopt(sys.argv[1:], 'i:o:s:d:ht')
  opts = dict(opts)

  input     = opts['-i']
  output    = opts['-o']
  help      = '-h' in opts
  test      = '-t' in opts

  if help:
    sys.stdout.write(__doc__)
    exit()
    
  outputs = []

  try:
    parameter = opts['-s']
  except KeyError:
    signals = set()
  else:
    signals = cvs_parser(parameter)

  try:
    parameter = opts['-d']
  except KeyError:
    devices = set()
  else:
    devices = cvs_parser(parameter)

  if not signals and not devices:
    sys.stderr('No signal or device is added to store into the new measurement file')
    exit()
    
  print 'Process\n'
  if os.path.isfile(input):
    print input
    missing, kept_devices = purge_mdf(input, output, devices, signals)
    outputs.append([output, missing, kept_devices])
  else:
    input_dir = input
    output_dir = output
    if not os.path.exists(output_dir):
      os.makedirs(output_dir)
    for input in findMeasurements(input_dir, '*.mdf', Recursively=True):
      print input
      basename = os.path.basename(input)
      output = os.path.join(output_dir, basename)
      missing, kept_devices = purge_mdf(input, output, devices, signals)
      outputs.append([output, missing, kept_devices])
      
  if test:
    print '\nTest\n'
    for output, missing, kept_devices in outputs:
      print output
      print
      OK = True
      extra, missed, extra_devices, missed_devices = test_mdf(output, signals, devices)
      missed = missed.difference(missing)
      extra_devices = extra_devices.difference(kept_devices)
      if kept_devices:
        print 'Kept devices\n'
        print '\n'.join(kept_devices)
        print
      if extra:
        print 'Extra signals\n'
        print '\n'.join(extra)
        print
        OK = False
      if missed:
        print 'Missed signals\n'
        print '\n'.join(missed)
        print
        OK = False
      if extra_devices:
        print 'Extra devices\n'
        print '\n'.join(extra_devices)
        print
        OK = False
      if missed_devices:
        print 'Missed devices\n'
        print '\n'.join(missed_devices)
        print
        OK = False
      if OK:
        print 'OK\n'
