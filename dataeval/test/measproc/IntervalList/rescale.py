import unittest

import numpy

from measproc.IntervalList import cIntervalList
from measparser import signalproc

class SetUpRescale(unittest.TestCase):
  def setUp(self):
    self.time = numpy.arange(0, 1, 1e-1)
    self.Intervals = [(0, 1), (3, 9), (6, 10), (4, 8)]
    self.intervals = cIntervalList.fromList(self.time, self.Intervals)
    return

class TestRescale(SetUpRescale):
  def test_rescale_on_same_time(self):
    intervals = self.intervals.rescale(self.time)
    self.assertListEqual(intervals.Intervals, self.Intervals)
    return

  def test_remain(self):
    time = numpy.arange(0, 1, 3e-1)
    intervals = self.intervals.rescale(time)
    self.assertListEqual(self.intervals.Intervals, self.Intervals)
    return

class TestConvertIndices(SetUpRescale):
  def test_convertIndices(self):
    time = numpy.arange(0, 1, 2e-1)
    intervals = cIntervalList(time)
    converted = intervals.convertIndices(self.intervals)
    self.assertListEqual(converted.Intervals, [(0, 1), (2, 5), (3, 5), (2, 4)])
    return
    
class TestZeroLengthInterval(unittest.TestCase):
  def setUp(self):
    time = numpy.arange(0, 1, 1e-1)
    self.intervals = cIntervalList.fromList(time, [(0, 1), (3, 4), (6, 10)])
    return

  def test(self):
    time = numpy.arange(0, 1, 2e-1)
    intervals = self.intervals.rescale(time)
    self.assertListEqual(intervals.Intervals, [(0, 1), (2, 3), (3, 5)])
    return

class TestLowerIndexLimit(unittest.TestCase):
  def setUp(self):
    time = numpy.arange(0, 1, 1e-1)
    self.intervals = cIntervalList.fromList(time, [(1, 5), (6, 8), (9, 10)])
    return

  def test(self):
    time = numpy.arange(0, 1, 2e-1)
    intervals = self.intervals.rescale(time)
    self.assertListEqual(intervals.Intervals, [(1, 3), (3, 4), (4, 5)])
    return

unittest.main()
