import unittest

import numpy

from measproc.report2 import Report
from measproc.IntervalList import cIntervalList


class TestRescale(unittest.TestCase):
  def setUp(self):
    time = numpy.arange(0, 1, 1e-2)
    intervals = cIntervalList(time)
    
    quantities = {'foo': {'bar', 'baz'}}
    labels = {'spam': (True, {'egg', 'eggegg'})}
    self.report = Report(intervals, 'pyon', votes=labels, names=quantities)

    self.report.setEntryComment('nyam')

    idx = self.report.addInterval((0, 11))
    self.report.vote(idx, 'spam', 'egg')
    self.report.set(idx, 'foo', 'bar', 0.5)
    self.report.setComment(idx, 'atomsk')

    idx = self.report.addInterval((5, 15))
    self.report.vote(idx, 'spam', 'eggegg')
    self.report.set(idx, 'foo', 'baz', 1.0)
    return

  def test(self):
    time = numpy.arange(0, 1, 5e-2)
    report = self.report.rescale(time)
    
    self.assertEqual(report.getEntryComment(), 'nyam')
    self.assertEqual(report.title, 'pyon')

    self.assertEqual(report.get(0, 'foo', 'bar'), 0.5)
    self.assertTrue(report.checkVote(0, 'spam', 'egg'))
    self.assertEqual(report.getComment(0), 'atomsk')

    self.assertEqual(report.get(1, 'foo', 'baz'), 1.0)
    self.assertTrue(report.checkVote(1, 'spam', 'eggegg'))
    self.assertEqual(report.getComment(1), '')
    return

unittest.main()
