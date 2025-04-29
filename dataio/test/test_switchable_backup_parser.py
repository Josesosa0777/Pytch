import os
import shutil
import unittest
import argparse

from measparser.SignalSource import cSignalSource
from measparser.Hdf5Parser import cHdf5Parser
from measparser.iParser import iParser

parser = argparse.ArgumentParser()

parser.add_argument('-m', default=r'C:\KBData\DB_test\2013-07-23\2013-07-23-18-05-26.MF4')
args = parser.parse_args()

class TestSwitchableBackUpParser(unittest.TestCase):
  @unittest.skipUnless(os.path.isfile(args.m), '%s does not exists' % args.m)
  def test_turned_off_back_up_parser(self):
    signal_source = cSignalSource(args.m)
    self.assertFalse(isinstance(signal_source.BackupParser, cHdf5Parser))
    self.assertTrue(isinstance(signal_source.BackupParser, iParser))
    signal_source.save()
    return

  @unittest.skipUnless(os.path.isfile(args.m), '%s does not exists' % args.m)
  def test_turned_on_backup_parser(self):
    dir = os.path.dirname(os.path.realpath(__file__))
    signal_source = cSignalSource(args.m, NpyHomeDir=dir)
    self.assertTrue(isinstance(signal_source.BackupParser, cHdf5Parser))
    signal_source.save()
    return

  @classmethod
  def tearDownClass(self):
    basename = os.path.basename(args.m)
    name, ext = os.path.splitext(basename)
    dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), name)
    namedump = dir + '.db'
    h5 = dir + '.h5'
    os.remove(namedump)
    os.remove(h5)
    return

if __name__ == '__main__':
  unittest.main()