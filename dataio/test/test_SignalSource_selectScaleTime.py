import os
import shutil
import unittest

import numpy

from measparser.BackupParser import BackupParser
from measparser.SignalSource import cSignalSource

backup   = os.path.abspath('backup')
measname = os.path.abspath('foo.mdf')

foo = numpy.arange( 0, 100, 20e-3)
bar = numpy.arange(10, 200, 20e-3)

def setUpModule():
  global measurement
  measurement = BackupParser.fromFile(measname, backup)

  measurement.addTime('foo', foo)
  measurement.addTime('bar', bar)

  measurement.addSignal('spam', 'egg', 'foo', numpy.sin(foo))
  measurement.addSignal('spam', 'ehh', 'foo', numpy.cos(foo))
  measurement.addSignal('zpam', 'egg', 'bar', numpy.cos(bar))

  measurement.save()
  return

def tearDownModule():
  shutil.rmtree(backup)
  return


class Test(unittest.TestCase):
  def setUp(self):
    self.source = cSignalSource(measurement.NpyDir, backup)
    return

  def tearDown(self):
    self.source.save()
    return

  def test(self):
    signals = [['spam', 'egg'], ['spam', 'ehh'], ['zpam', 'egg']]
    time = self.source.selectScaleTime(signals, True) 
    self.assertTrue(numpy.allclose(time, bar))
    return

if __name__ == '__main__':
  unittest.main()
