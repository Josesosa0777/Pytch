import unittest
import os
import sys
import argparse


import numpy

from measparser.SignalSource import cSignalSource

conv_table = {
              '-0.20' : 0.2,
              '-0.15' : 0.25,
              '-0.10' : 0.3,
              '-0.05' : 0.35
              }

parser = argparse.ArgumentParser()
parser.add_argument('--mf4', default=r'C:\KBData\measurement\H566_2013-03-21_16-40-21.mf4')
parser.add_argument('--mdf', default=r'C:\KBData\measurement\comparison_all_sensors_2012-05-24_16-10-51.MDF')
args = parser.parse_args()

if not os.path.isfile(args.mf4) or not os.path.isfile(args.mdf):
  sys.stderr.write('Measurement file does not exist\n')
  sys.exit(-1)

class Tests(object):
  def test_dtype(self):
    _, modifieds = self.source.getSignal(self.device, self.signal, dtype='<u1')

    for original, modified in zip(self.originals, modifieds):
      if original < 0:
        value = '%.2f' % original
        original = conv_table[value]
        self.assertTrue(numpy.allclose([original], [modified]))
    return

  def test_offset(self):
    _, modifieds = self.source.getSignal(self.device, self.signal, offset=1)

    for original, modified in zip(self.originals, modifieds):
      original = original + 1
      self.assertTrue(numpy.allclose([original], [modified]))
    return

  def test_factor(self):
    _, modifieds = self.source.getSignal(self.device, self.signal, factor=1)

    for original, modified in zip(self.originals, modifieds):
      original = original * 20
      self.assertTrue(numpy.allclose([original], [modified]))
    return


class TestMF4(unittest.TestCase, Tests):
  def setUp(self):
    self.source = cSignalSource(args.mf4)
    self.device = r'Targets--Message--A087MB_V3_3draft_MH1'
    self.signal = 'ta0_angle_LSB'
    _, self.originals = self.source.getSignal(self.device,
                                                  self.signal)
    return

class TestMdf(unittest.TestCase, Tests):
  def setUp(self):
    self.source = cSignalSource(args.mdf)
    self.device = r'Targets-662-2-'
    self.signal = 'ta0_angle_LSB'
    _, self.originals = self.source.getSignal(self.device, self.signal)
    return

if __name__ == '__main__':
  unittest.main(argv=sys.argv[:1])