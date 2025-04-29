import unittest

import numpy

from measproc.IntervalList import cIntervalList
from measproc.report2 import IntervalListContainer

class SetUpIntervalList(unittest.TestCase):
  def setUp(self):
    time = numpy.arange(0, 1, 1e-1)
    self.intervals = cIntervalList.fromList(time, [(2, 5), (4, 7), (9, 10)])
    return

class TestIntervalList(SetUpIntervalList):
  def test_overlapping(self):
    ids = self.intervals.findIntervalIdsWithin(4, 6)
    self.assertListEqual(ids, [0, 1])
    return

  def test_last(self):
    ids = self.intervals.findIntervalIdsWithin(8, 10)
    self.assertListEqual(ids, [2])
    return

  def test_inner(self):
    ids = self.intervals.findIntervalIdsWithin(3, 4)
    self.assertListEqual(ids, [0])
    return
    
  def test_empty(self):
    ids = self.intervals.findIntervalIdsWithin(7, 9)
    self.assertListEqual(ids, [])
    return
    
class TestIntervalListContainer(SetUpIntervalList):
  def setUp(self):
    SetUpIntervalList.setUp(self)
    self.container = IntervalListContainer(self.intervals, 'foo')
    return

  def test_overlapping(self):
    ids = self.container.findIntervalIdsWithin((4, 6))
    self.assertListEqual(ids, [0, 1])
    return

unittest.main()
