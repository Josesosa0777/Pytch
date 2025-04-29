# -*- coding: utf-8 -*-
import unittest
import os
import sys
import shutil
import argparse

from measparser.SignalSource import cSignalSource
from measparser.namedump import NameDump

parser = argparse.ArgumentParser()
parser.add_argument('-m', default=r'C:\KBData\DB_test\2013-08-17-00-03-10.MF4')
args = parser.parse_args()

if not os.path.isfile(args.m):
  sys.stderr.write('Measurement file does not exist\n')
  sys.exit(-1)

source_with_nd = cSignalSource(args.m,
                        NpyHomeDir=os.path.dirname(os.path.realpath(__file__)),
                        NeedMemoryParser=False)
source_wo_nd = cSignalSource(args.m, NpyHomeDir=None,
                             NeedMemoryParser=False)

class Test(unittest.TestCase):
  def test_nd(self):
    self.assertTrue(isinstance(source_with_nd.NameDump, NameDump))
    self.assertFalse(isinstance(source_wo_nd.NameDump, NameDump))
    return

  def test_contains(self):
    self.assertEqual(source_with_nd.contains('Foo-', 'Bar'),
                     source_wo_nd.contains('Foo-', 'Bar'))
    return

  def test_get_short_device_name(self):
    self.assertEqual(source_with_nd.getShortDeviceName('RQST2--Message--H566_All_Messages_v_04'),
                     source_wo_nd.getShortDeviceName('RQST2--Message--H566_All_Messages_v_04'))
    return

  def test_get_extended_device_names(self):
    self.assertEqual(source_with_nd.getExtendedDeviceNames('CCVS_11'),
                     source_wo_nd.getExtendedDeviceNames('CCVS_11'))
    return

  def test_get_alias(self):
    self.assertEqual(source_with_nd.getAlias('ParameterGroupNumber',
                                      'RQST2--Message--H566_All_Messages_v_04'),
                     source_wo_nd.getAlias('ParameterGroupNumber',
                                      'RQST2--Message--H566_All_Messages_v_04'))
    return

  def test_get_device_names(self):
    self.assertEqual(source_with_nd.getDeviceNames('ParameterGroupNumber'),
                     source_wo_nd.getDeviceNames('ParameterGroupNumber'))
    return

  def test_get_all_device_names(self):
    self.assertEqual(source_with_nd.getAllDeviceNames('ParameterGroupNumber'),
                     source_wo_nd.getAllDeviceNames('ParameterGroupNumber'))
    return

  def test_get_names(self):
    self.assertEqual(source_with_nd.getNames('ParameterGroupNumber', 'RQST'),
                     source_wo_nd.getNames('ParameterGroupNumber', 'RQST'))
    return

  def test_get_physical_unit(self):
    self.assertEqual(source_with_nd.getPhysicalUnit(
                  'CCVS_11-Cruise_Control-Message-Cruise_Control-J1939_Common',
                  'CCVS_ParkingBrakeSwitch_11'),
                     source_wo_nd.getPhysicalUnit(
                  'CCVS_11-Cruise_Control-Message-Cruise_Control-J1939_Common',
                  'CCVS_ParkingBrakeSwitch_11'))
    return

  def test_get_time_key(self):
    self.assertEqual(source_with_nd.getTimeKey(
                                      'RQST2--Message--H566_All_Messages_v_04',
                                      'ParameterGroupNumber'),
                     source_wo_nd.getTimeKey(
                                      'RQST2--Message--H566_All_Messages_v_04',
                                      'ParameterGroupNumber'))
    return

  def test_query_signal_names(self):
    return

def tearDownModule():
    source_with_nd.save()
    base = os.path.basename(args.m)
    base, exr = os.path.splitext(base)
    dir = os.path.join(source_with_nd.NpyHomeDir, base)
    dbname = dir  + '.db'
    h5name = dir  + '.h5'
    os.remove(dbname)
    os.remove(h5name)
    return

if __name__ == '__main__':
  unittest.main(argv=sys.argv[:1])