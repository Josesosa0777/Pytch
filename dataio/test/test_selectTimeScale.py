import unittest

import numpy

from measparser.signalproc import selectTimeScale

class Test(unittest.TestCase):
  def test_simple_select(self):
    times = [
             numpy.arange( 0, 100, 20e-3),
             numpy.arange(10, 200, 20e-3),
            ]
    iter_times = iter(times)
    time = selectTimeScale(iter_times, True)
    self.assertIs(time, times[1])
    return

  def test_one_length_times(self):
    times = [
             numpy.array([1.2]),
             numpy.array([3.2]),
             numpy.array([2.3]),
            ]
    iter_times = iter(times)
    time = selectTimeScale(iter_times, True)
    self.assertIs(time, times[1])
    return

  def test_select_with_one_length_time(self):
    times = [
             numpy.array([1.2, 2.3]),
             numpy.array([3.2]),
            ]
    iter_times = iter(times)
    time = selectTimeScale(iter_times, True)
    self.assertIs(time, times[0])
    return

  def test_strickly_growing_check(self):
    times = [
             numpy.array([0.2, 0.3, 0.4, 0.4]),
             numpy.array([0.2, 0.3, 0.3, 0.5]),
            ]
    iter_times = iter(times)
    self.assertRaises(IndexError, selectTimeScale, iter_times, True)
    iter_times = iter(times)
    time = selectTimeScale(iter_times, False)
    self.assertIs(time, times[1])
    return

  def test_select_with_empty(self):
    times = [
             numpy.array([]),
             numpy.array([1]),
             numpy.array([2]),
            ]
    iter_times = iter(times)
    time = selectTimeScale(iter_times, True)
    self.assertIs(time, times[2])
    return
    
  def test_select_from_empties(self):
    times = [
             numpy.array([]),
             numpy.array([]),
            ]
    iter_times = iter(times)
    self.assertRaises(IndexError, selectTimeScale, iter_times, True)
    return

if __name__ == '__main__':
  unittest.main()
