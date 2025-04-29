# -*- coding: utf-8 -*-
import unittest
import os
import sys
import argparse

from measparser.SignalSource import findParser
from measparser.namedump import NameDump

parser = argparse.ArgumentParser()
parser.add_argument('-m', default=r'C:\KBData\DB_test\2013-08-17-00-03-10.MF4')
args = parser.parse_args()

if not os.path.isfile(args.m):
  sys.stderr.write('Measurement file does not exist\n')
  sys.exit(-1)

namedump = NameDump.fromMeasurement(args.m)
cParser = findParser(args.m)
parser = cParser(args.m)

class Test(unittest.TestCase):
  def test_iter_device_names(self):
    i = 0
    for orig, nd in zip(parser.iterDeviceNames(), namedump.iterDeviceNames()):
      self.assertEqual(orig, nd)
      i += 1
    self.assertNotEqual(i, 0)
    return

  def test_iter_time_keys(self):
    i = 0
    for orig, nd in zip(parser.iterTimeKeys(), namedump.iterTimeKeys()):
      self.assertEqual(orig, nd)
      i += 1
    self.assertNotEqual(i, 0)
    return

  def test_contains(self):
    for dev in parser.iterDeviceNames():
      for signal in parser.iterSignalNames(dev):
        self.assertTrue(namedump.contains(dev, signal))
    self.assertFalse(namedump.contains('Random device foo', 'Rand signal bar'))
    return

  def test_get_physical_unit(self):
    for dev in parser.iterDeviceNames():
      for signal in parser.iterSignalNames(dev):
        self.assertEqual(parser.getPhysicalUnit(dev, signal),
                         namedump.getPhysicalUnit(dev, signal))
    return

  def test_iter_signal_names(self):
    i = 0
    for dev in parser.iterDeviceNames():
      for orig, nd in zip(parser.iterSignalNames(dev),
                          namedump.iterSignalNames(dev)):
        self.assertEqual(orig, nd)
        i += 1
    self.assertNotEqual(i, 0)
    return

  def test_get_device_names(self):
    for dev in parser.iterDeviceNames():
      for signal in parser.iterSignalNames(dev):
        self.assertEqual(parser.getDeviceNames(signal),
                         namedump.getDeviceNames(signal))
    return

  def test_extended_device_names(self):
    self.assertEqual(parser.getExtendedDeviceNames('XBR_2A'),
                     namedump.getExtendedDeviceNames('XBR_2A'))
    return

  def test_get_names(self):
    self.assertEqual(parser.getNames('XBREBIMode', 'XBR'),
                     namedump.getNames('XBREBIMode', 'XBR'))

    return

  def test_get_time_key(self):
    for dev in parser.iterDeviceNames():
      for signal in parser.iterSignalNames(dev):
        self.assertEqual(parser.getTimeKey(dev, signal),
                         namedump.getTimeKey(dev, signal))
    return

  def test_get_signal_length(self):
    for dev in parser.iterDeviceNames():
      for signal in parser.iterSignalNames(dev):
        self.assertEqual(parser.getSignalLength(dev, signal),
                         namedump.getSignalLength(dev, signal))
    return

  def test_is_missing_signal(self):
    for dev in parser.iterDeviceNames():
      for signal in parser.iterSignalNames(dev):
        self.assertFalse(namedump.isMissingSignal(dev, signal))
    self.assertTrue(namedump.isMissingSignal('Invalid dev', 'Invalid sig'))
    return

  def test_is_missig_device(self):
    for dev in parser.iterDeviceNames():
        self.assertFalse(namedump.isMissingDevice(dev))
    self.assertTrue(namedump.isMissingDevice('Invalid dev'))
    return

  def test_is_missing_time(self):
    for time in parser.iterTimeKeys():
        self.assertFalse(namedump.isMissingTime(time))
    self.assertTrue(namedump.isMissingTime('Invalid time'))
    return

  def test_query_signal_names(self):
    self.assertEqual(parser.querySignalNames(['XBR'], ['2B'], ['XBR'], ['Mode'],
                                              False, False),
                   namedump.querySignalNames(['XBR'], ['2B'], ['XBR'], ['Mode'],
                                               False, False))
    return

  def test_query_signal_names_match_case(self):
    self.assertEqual(parser.querySignalNames(['XBR'], ['2B'], ['XBR'], ['Mode'],
                                              True, False),
                   namedump.querySignalNames(['XBR'], ['2B'], ['XBR'], ['Mode'],
                                               True, False))
    return

  def test_query_signal_names_disable_empty_signal(self):
    self.assertEqual(parser.querySignalNames(['XBR'], ['2B'], ['XBR'], ['Mode'],
                                              False, True),
                   namedump.querySignalNames(['XBR'], ['2B'], ['XBR'], ['Mode'],
                                               False, True))
    return

  def test_query_signal_names_disable_empty_signal_and_match_case(self):
    self.assertEqual(parser.querySignalNames(['XBR'], ['2B'], ['XBR'], ['Mode'],
                                              True, True),
                   namedump.querySignalNames(['XBR'], ['2B'], ['XBR'], ['Mode'],
                                               True, True))
    return


def tearDownModule():
  namedump.close()
  os.remove('namedump.db')

if __name__ == '__main__':
  unittest.main(argv=sys.argv[:1])