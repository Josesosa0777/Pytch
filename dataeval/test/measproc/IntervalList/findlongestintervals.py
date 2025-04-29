import unittest

import numpy

from measproc.IntervalList import cIntervalList
from measproc import EventFinder, relations

class TestFindLongestIntervals(unittest.TestCase):
  def setUp(self):
    self.time = numpy.linspace(0., 1., 1000)
    limit = 0.5
    a1 = numpy.random.rand(self.time.size)
    self.intervals1 = EventFinder.cEventFinder.compare(self.time,
      a1, relations.greater, limit)
    return
  
  def test_longest(self):
    lens = [Upper-Lower for Lower, Upper in self.intervals1]
    lonints = self.intervals1.findLongestIntervals()
    maxlens = [Upper-Lower for Lower, Upper in lonints]
    maxlen = maxlens[0]
    self.assertTrue(    all([len == maxlen for len in maxlens])
                    and all([len <= maxlen for len in lens]))
    return
  
  def test_emptylist(self):
    il = cIntervalList(numpy.empty(0), [])
    lonints = il.findLongestIntervals()
    self.assertTrue(len(lonints) == 0)
    return

class TestFindLongestIntervalsIds(unittest.TestCase):
  def setUp(self):
    self.time = numpy.linspace(0., 1., 1000)
    limit = 0.5
    a1 = numpy.random.rand(self.time.size)
    self.intervals1 = EventFinder.cEventFinder.compare(self.time,
      a1, relations.greater, limit)
    return
  
  def test_longest(self):
    lens = [Upper-Lower for Lower, Upper in self.intervals1]
    lonintids = self.intervals1.findLongestIntervalsIds()
    maxlens = [self.intervals1[i][1]-self.intervals1[i][0] for i in lonintids]
    maxlen = maxlens[0]
    self.assertTrue(    all([len == maxlen for len in maxlens])
                    and all([len <= maxlen for len in lens]))
    return
  
  def test_emptylist(self):
    il = cIntervalList(numpy.empty(0), [])
    lonintids = il.findLongestIntervalsIds()
    self.assertTrue(len(lonintids) == 0)
    return

if __name__ == '__main__':
  unittest.main()
