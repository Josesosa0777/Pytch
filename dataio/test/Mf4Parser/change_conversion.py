import unittest
import os
import sys
import argparse


import numpy

from measparser.Mf4Parser import cMf4Parser

conv_table = {
              '-0.20' : 0.2,
              '-0.15' : 0.25,
              '-0.10' : 0.3,
              '-0.05' : 0.35
              }

parser = argparse.ArgumentParser()
parser.add_argument('-m', default=r'C:\KBData\measurement\H566_2013-03-21_16-40-21.mf4')
args = parser.parse_args()

if not os.path.isfile(args.m):
  sys.stderr.write('Measurement file does not exist\n')
  sys.exit(-1)

class Build(unittest.TestCase):
  def setUp(self):
    self.mf4_parser = cMf4Parser(args.m)
    self.device_mf4 = r'Targets--Message--A087MB_V3_3draft_MH1'
    self.signal_mf4 = 'ta0_angle_LSB'
    self.originals, _ = self.mf4_parser.getSignal(self.device_mf4,
                                                  self.signal_mf4)
    return

class TestDtype(Build):
  def test_dtype(self):
    modifieds, _ = self.mf4_parser.getSignal(self.device_mf4, self.signal_mf4,
                                             dtype='<u1')

    for original, modified in zip(self.originals, modifieds):
      if original < 0:
        value = '%.2f' % original
        original = conv_table[value]
        self.assertTrue(numpy.allclose([original], [modified]))
    return

class TestOffset(Build):
  def test_offset(self):
    modifieds, _ = self.mf4_parser.getSignal(self.device_mf4, self.signal_mf4,
                                             offset=1)

    for original, modified in zip(self.originals, modifieds):
      original = original + 1
      self.assertTrue(numpy.allclose([original], [modified]))
    return

class TestFactor(Build):
  def test_factor(self):
    modifieds, _ = self.mf4_parser.getSignal(self.device_mf4, self.signal_mf4,
                                             factor=1)

    for original, modified in zip(self.originals, modifieds):
      original = original * 20
      self.assertTrue(numpy.allclose([original], [modified]))
    return

if __name__ == '__main__':
  unittest.main(argv=sys.argv[:1])