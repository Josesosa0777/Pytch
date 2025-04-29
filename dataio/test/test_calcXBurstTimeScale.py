import unittest

import numpy as np

from measparser.signalproc import \
  calcOrderedBurstTimeScale, calcUnorderedBurstTimeScale

class TestOrderedBurstTimeScale(unittest.TestCase):
  """
  Example:
  
  t1:  -----x------x------x------x------x-
  t2:  ------x------x------x------x------x
  t3:  x------x------x------x------x------

  out:      x------x------x------x
  """
  
  def test_empties(self):
    t1 = np.array(())
    t2 = np.array(())
    out = calcOrderedBurstTimeScale((t1, t2))
    self.assertEqual(out.size, 0)
    return
  
  def test_size1_incomplete_packets(self):
    t1 = np.array((3.,))
    t2 = np.array((2.,))
    out = calcOrderedBurstTimeScale((t1, t2))
    self.assertEqual(out.size, 0)
    return
  
  def test_size1_complete_packets(self):
    t1 = np.array((3.,))
    t2 = np.array((4.,))
    out = calcOrderedBurstTimeScale((t1, t2))
    self.assertTrue(np.array_equal(out, t1))
    return
  
  def test_onetime(self):
    t1 = np.array((3., 10., 17.))
    out = calcOrderedBurstTimeScale((t1,))
    self.assertTrue(np.array_equal(out, t1))
    return
  
  def test_incomplete_packets_start(self):
    t1 = np.array((    3., 10., 17., 24.))
    t2 = np.array((0., 4., 11., 18., 25.))
    out = calcOrderedBurstTimeScale((t1, t2))
    self.assertTrue(np.array_equal(out, t1))
    return
  
  def test_incomplete_packets_end(self):
    t1 = np.array((3., 10., 17., 24.))
    t2 = np.array((4., 11., 18.     ))
    out = calcOrderedBurstTimeScale((t1, t2))
    self.assertTrue(np.array_equal(out, t1[:-1]))
    return
  
  def test_incomplete_packets_start_end(self):
    t1 = np.array((    3., 10., 17., 24.))
    t2 = np.array((0., 4., 11., 18.     ))
    out = calcOrderedBurstTimeScale((t1, t2))
    self.assertTrue(np.array_equal(out, t1[:-1]))
    return
  
  def test_complete_packets(self):
    t1 = np.array((3., 10., 17.))
    t2 = np.array((4., 11., 18.))
    out = calcOrderedBurstTimeScale((t1, t2))
    self.assertTrue(np.array_equal(out, t1))
    return

class TestUnorderedBurstTimeScale(unittest.TestCase):
  """
  Example:
  
  t1:  -----x------x------x------x------x-
  t2:  ------x----x--------x------x------x
  t3:  x------x------x------x------x------

  out:      x-----x-------x------x
  """
  
  def test_empties(self):
    t1 = np.array(())
    t2 = np.array(())
    with self.assertRaises(AssertionError):
      out = calcUnorderedBurstTimeScale((t1, t2))
    return
  
  def test_size1(self):
    t1 = np.array((3.,))
    t2 = np.array((2.,))
    with self.assertRaises(AssertionError):
      out = calcUnorderedBurstTimeScale((t1, t2))
    return
  
  def test_onetime(self):
    t1 = np.array((3., 10., 17.))
    out_exp = t1
    out = calcUnorderedBurstTimeScale((t1,))
    self.assertTrue(np.array_equal(out, out_exp))
    return
  
  def test_incomplete_packets_start(self):
    t1 = np.array((    3., 10., 17., 24.))
    t2 = np.array((0., 4.,  9., 18., 25.))
    out_exp = np.array((3., 9., 17., 24.))
    out = calcUnorderedBurstTimeScale((t1, t2))
    self.assertTrue(np.array_equal(out, out_exp))
    return
  
  def test_incomplete_packets_end(self):
    t1 = np.array((3., 10., 17., 24.))
    t2 = np.array((4., 11., 16.     ))
    out_exp = np.array((3., 10., 16.))
    out = calcUnorderedBurstTimeScale((t1, t2))
    self.assertTrue(np.array_equal(out, out_exp))
    return
  
  def test_incomplete_packets_start_end(self):
    t1 = np.array((    3., 10., 17., 24.))
    t2 = np.array((0., 2., 11., 16.     ))
    out_exp = np.array((2., 10., 16.))
    out = calcUnorderedBurstTimeScale((t1, t2))
    self.assertTrue(np.array_equal(out, out_exp))
    return
  
  def test_complete_packets(self):
    t1 = np.array((3., 10., 17.))
    t2 = np.array((4.,  9., 18.))
    out_exp = np.array((3., 9., 17.))
    out = calcUnorderedBurstTimeScale((t1, t2))
    self.assertTrue(np.array_equal(out, out_exp))
    return
  
  def test_complete_packets_ordered(self):
    t1 = np.array((3., 10., 17.))
    t2 = np.array((4., 11., 18.))
    out_exp = t1
    out = calcUnorderedBurstTimeScale((t1, t2))
    self.assertTrue(np.array_equal(out, out_exp))
    return

if __name__ == '__main__':
  unittest.main()
