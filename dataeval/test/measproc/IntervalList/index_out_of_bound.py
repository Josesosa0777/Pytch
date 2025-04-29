import os
import unittest

import numpy

from measproc.IntervalList import cIntervalList


testmeas = os.getenv('testmeas', 'merge_crash_sample_time.npy')

class Test(unittest.TestCase):
  @unittest.skipUnless(os.path.isfile(testmeas), '%s does not exists' %testmeas)
  def setUp(self):
    self.intervals = [(98, 99), (100, 141)]
    time = numpy.load(testmeas)
    self.intervallist = cIntervalList.fromList(time, self.intervals)
    return

  def test_merge_with_2_sec(self):
    intervals = [(self.intervals[0][0], self.intervals[1][1])]
    self.assertListEqual(self.intervallist.merge(2.0).Intervals, intervals)
    return

if __name__ == '__main__':
  unittest.main()

