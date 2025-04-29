import unittest

import numpy as np

from measparser import signalproc

class TestSignalProc(unittest.TestCase):
  def setUp(self):
    self.MIN = 0
    self.MAX = 10
    self.N = 1000
    self.arr = np.linspace(self.MIN, self.MAX, self.N)
    self.arr0 = np.array([])
    self.arr1 = np.array([1.0])
    return 

  def test_isSameTime_equality(self):
    other = np.copy(self.arr)
    self.assertTrue( signalproc.isSameTime(self.arr, other) )
    return

  def test_isSameTime_identity(self):
    other = self.arr
    self.assertTrue( signalproc.isSameTime(self.arr, other) )
    return

  def test_isSameTime_disturbed_ok(self):
    other = np.copy(self.arr)
    other += 1e-9
    self.assertTrue( signalproc.isSameTime(self.arr, other) )
    return

  def test_isSameTime_disturbed_fails(self):
    other = np.copy(self.arr)
    other += 1e-6
    self.assertFalse( signalproc.isSameTime(self.arr, other) )
    return

  def test_isSameTime_findUniqueValues(self):
    self.assertTrue( signalproc.findUniqueValues(self.arr) == set(self.arr) )
    return

  def test_isSameTime_findUniqueValues_exclude(self):
    self.assertTrue( signalproc.findUniqueValues(self.arr, exclude=0) == set(self.arr[1:]) )
    return

  def test_isSameTime_isSorted_increasing(self):
    self.assertTrue( signalproc.isSorted(self.arr, 'increasing') )
    return

  def test_isSameTime_isSorted_increasing_strict(self):
    self.assertTrue( signalproc.isSorted(self.arr, 'increasing', strict=True) )
    return

  def test_isSameTime_isSorted_increasing_partial_by_default(self):
    self.assertTrue( signalproc.isSorted([0,1,1,3], 'increasing') )
    return

  def test_isSameTime_isSorted_decreasing(self):
    self.assertTrue( signalproc.isSorted(self.arr[::-1], 'decreasing') )
    return
  
  def test_isSameTime_isSorted_decreasing_strict(self):
    self.assertTrue( signalproc.isSorted(self.arr[::-1], 'decreasing', strict=True) )
    return

  def test_backwarddiff(self):
    sig = signalproc.backwarddiff(self.arr)
    self.assertTrue(
      np.allclose(sig[1:], float(self.MAX - self.MIN) / float(self.N - 1)) and 
      sig[0] == 0.0)
    return
    
  def test_backwarddiff_initial(self):
    sig = signalproc.backwarddiff(self.arr, initial = 2.0)
    self.assertTrue( 
      np.allclose(sig[1:], float(self.MAX - self.MIN) / float(self.N - 1)) and 
      sig[0] == 2.0)
    return

  def test_backwarddiff_initialmode(self):
    sig = signalproc.backwarddiff(self.arr, initialmode='copy_back')
    self.assertTrue( 
      np.allclose(sig, float(self.MAX - self.MIN) / float(self.N - 1)))
    return
    
  def test_backwarddiff_bad_initialmode(self):
    with self.assertRaises(AssertionError):
      signalproc.backwarddiff(self.arr, initialmode='bad_initialmode')
    return
    
  def test_backwarddiff_zerolength(self):
    sig = signalproc.backwarddiff(self.arr0)
    self.assertTrue(sig.size == self.arr0.size)
    return
    
  def test_backwarddiff_onelength(self):
    sig = signalproc.backwarddiff(self.arr1)
    self.assertTrue(sig.size == self.arr1.size and sig[0] == 0.0)
    return
    
  def test_backwardderiv(self):
    sig = signalproc.backwardderiv(self.arr, self.arr)
    self.assertTrue(
      np.allclose(sig[1:], 1.0) and 
      sig[0] == 0.0)
    return

  def test_backwardderiv_initial(self):
    sig = signalproc.backwardderiv(self.arr, self.arr, initial=2.0)
    self.assertTrue( 
      np.allclose(sig[1:], 1.0) and
      sig[0] == 2.0)
    return
    
  def test_backwardderiv_initialmode(self):
    sig = signalproc.backwardderiv(self.arr, self.arr, initialmode='copy_back')
    self.assertTrue( 
      np.allclose(sig, 1.0))
    return

  def test_backwardderiv_bad_initialmode(self):
    with self.assertRaises(AssertionError):
      signalproc.backwardderiv(self.arr, self.arr, initialmode='bad_initialmode')
    return
    
  def test_backwardderiv_zerolength(self):
    sig = signalproc.backwardderiv(self.arr0, self.arr0)
    self.assertTrue(sig.size == self.arr0.size)
    return

  def test_backwardderiv_onelength(self):
    sig = signalproc.backwardderiv(self.arr1, self.arr1)
    self.assertTrue(sig.size == self.arr1.size and sig[0] == 0.0)
    return
    
  def test_backwardderiv_different_shape(self):
    with self.assertRaises(AssertionError):
      signalproc.backwardderiv(self.arr, self.arr0)
    return

class RescaleSetBoundaries(unittest.TestCase):
  def test_setboundaries_same_timestamps(self):
    timescale = np.linspace(0,1,11)
    valuescale = np.random.rand(timescale.size)
    slicer = slice(2,-2)
    time = timescale[slicer]
    left, right = -1, -2
    reference_data = [ (left,left), valuescale[slicer], (right,right) ]
    reference = np.concatenate(reference_data)
    valuescale = valuescale.copy()
    signalproc.setBoundaries(time, timescale, valuescale, left, right)
    self.assertTrue( np.array_equal(reference,valuescale) )
    return

  def test_setboundaries_rescale_left(self):
    time = np.array([0.1, 1.1, 2.1, 3.1, 4.1])
    value = np.random.rand(time.size)
    scaletime = np.array([0., 1., 2., 3., 4.])
    left = -1
    _, scalevalue = signalproc.rescale(time, value, scaletime, Left=left)
    reference = np.concatenate( [(left,), value[:-1]] )
    self.assertTrue( np.array_equal(reference,scalevalue) )
    return

  def test_setboundaries_rescale_right(self):
    time = np.array([0.1, 1.1, 2.1, 3.1, 4.1])
    value = np.random.rand(time.size)
    scaletime = np.array([0., 1., 2., 3., 4.2])
    right = -1
    _, scalevalue = signalproc.rescale(time, value, scaletime, Right=right)
    reference = np.concatenate( [(value[0],), value[:-2], (right,)] )
    self.assertTrue( np.array_equal(reference,scalevalue) )
    return

  def test_setboundaries_rescale_both_side(self):
    time = np.array([0.1, 1.1, 2.1, 3.1])
    value = np.random.rand(time.size)
    scaletime = np.array([0., 1., 2., 3., 4.])
    left, right = -1, -2
    _, scalevalue = signalproc.rescale(time, value, scaletime, Left=left, Right=right)
    reference = np.concatenate( [(left,), value[:-1], (right,)] )
    self.assertTrue( np.array_equal(reference,scalevalue) )
    return

class RescaleValidToCommonTime(unittest.TestCase):
  def setUp(self):
    self.scaletime = np.arange(0, 1, 1e-2)
    self.time = self.scaletime + 1e-3
    self.value = np.arange(self.time.size)
    return

  def test_input_not_modified(self):
    self.scaletime.flags.writeable = False
    self.time.flags.writeable = False
    self.value.flags.writeable = False
    try:
      scalevalue = signalproc.rescaleValidToCommonTime(
                        self.time, self.value, self.scaletime)
    except ValueError:
      self.fail('input arrays were modified')
    return

  def test_basic(self):
    scalevalue = signalproc.rescaleValidToCommonTime(
                      self.time, self.value, self.scaletime)
    self.assertTrue(     np.array_equal(self.value,scalevalue)
                     and not np.any(scalevalue.mask) )
    return

  def test_basic_using_rescale(self):
    _, scalevalue = signalproc.rescale(self.time, self.value, self.scaletime,
                                       Order='valid')
    self.assertTrue(     np.array_equal(self.value,scalevalue)
                     and not np.any(scalevalue.mask) )
    return

  def test_sametime_using_rescale(self):
    scaletime = self.time.copy()
    _, scalevalue = signalproc.rescale(self.time, self.value, scaletime,
                                       Order='valid')
    self.assertTrue(     np.array_equal(self.value,scalevalue)
                     and not np.any(scalevalue.mask) )
    self.assertEqual( scalevalue.data.shape, scalevalue.mask.shape )
    return

  def test_sametime_identical(self):
    scalevalue = signalproc.rescaleValidToCommonTime(
                      self.scaletime, self.value, self.scaletime)
    self.assertTrue(     np.array_equal(self.value,scalevalue)
                     and not np.any(scalevalue.mask) )
    return

  def test_sametime_equal(self):
    scalevalue = signalproc.rescaleValidToCommonTime(
                      self.scaletime.copy(), self.value, self.scaletime)
    self.assertTrue(     np.array_equal(self.value,scalevalue)
                     and not np.any(scalevalue.mask) )
    return

  def test_almost_sametime(self):
    time = self.scaletime.copy()
    time[0] = self.time[0]
    scalevalue = signalproc.rescaleValidToCommonTime(
                      time, self.value, self.scaletime)
    self.assertTrue(     np.array_equal(self.value,scalevalue)
                     and not np.any(scalevalue.mask) )
    return

  def test_basic_invalidvalue(self):
    scalevalue = signalproc.rescaleValidToCommonTime(
                      self.time, self.value, self.scaletime, InvalidValue=-1)
    self.assertTrue(     np.array_equal(self.value,scalevalue)
                     and not np.any(scalevalue.mask) )
    return

  def test_basic_invalidvalue_using_rescale(self):
    _, scalevalue = signalproc.rescale(self.time, self.value, self.scaletime,
                                       Order='valid', InvalidValue=-1)
    self.assertTrue(     np.array_equal(self.value,scalevalue)
                     and not np.any(scalevalue.mask) )
    return

  def test_missing_values_before_without_invalidvalue(self):
    slicer = slice(10, None)
    time = self.time[slicer]
    value = self.value[slicer]
    mask = np.ones_like(self.scaletime, dtype=np.bool)
    mask[slicer] = False
    scalevalue = signalproc.rescaleValidToCommonTime(time, value, self.scaletime)
    self.assertTrue(     np.array_equal( self.value[slicer], scalevalue.compressed() )
                     and np.array_equal( mask, scalevalue.mask ) )
    return

  def test_missing_values_before_with_invalidvalue(self):
    slicer = slice(10, None)
    time = self.time[slicer]
    value = self.value[slicer]
    mask = np.ones_like(self.scaletime, dtype=np.bool)
    mask[slicer] = False
    invalid = -1
    scalevalue = signalproc.rescaleValidToCommonTime(
                      time, value, self.scaletime, InvalidValue=invalid)
    reference = np.concatenate( [[invalid]*10, value] )
    self.assertTrue(     np.array_equal( reference, scalevalue )
                     and np.array_equal( mask, scalevalue.mask ) )
    return

  def test_missing_values_inside_without_invalidvalue(self):
    time = np.array([0.1, 1.1, 4.1])
    value = np.random.rand(time.size)
    scaletime = np.array([0., 1., 2., 3., 4.])
    scalevalue = signalproc.rescaleValidToCommonTime(time, value, scaletime)
    self.assertTrue( np.array_equal(value,scalevalue.compressed()) )
    return

  def test_missing_values_inside_with_invalidvalue(self):
    time = np.array([0.1, 1.1, 4.1])
    value = np.random.rand(time.size)
    scaletime = np.array([0., 1., 2., 3., 4.])
    invalid = -1
    scalevalue = signalproc.rescaleValidToCommonTime(time, value, scaletime, InvalidValue=invalid)
    reference = np.array([value[0], value[1], invalid, invalid, value[-1]])
    mask = np.array([False, False, True, True, False])
    self.assertTrue(     np.array_equal(reference,scalevalue)
                     and np.array_equal(mask,scalevalue.mask) )
    return

  def test_missing_values_every_2_steps_without_invalidvalue(self):
    slicer = slice(None, None, 2)
    time = self.time[slicer]
    value = self.value[slicer]
    mask = np.ones_like(self.scaletime, dtype=np.bool)
    mask[slicer] = False
    scalevalue = signalproc.rescaleValidToCommonTime(time, value, self.scaletime)
    self.assertTrue(     np.array_equal( self.value[slicer], scalevalue.compressed() )
                     and np.array_equal( mask, scalevalue.mask ) )
    return

  def test_missing_values_every_2_steps_with_invalidvalue(self):
    slicer = slice(None, None, 2)
    time = self.time[slicer]
    value = self.value[slicer]
    mask = np.ones_like(self.scaletime, dtype=np.bool)
    mask[slicer] = False
    invalid = -1
    scalevalue = signalproc.rescaleValidToCommonTime(
                      time, value, self.scaletime, InvalidValue=invalid)
    reference = np.concatenate( zip(value, [invalid]*value.size) )
    self.assertTrue(     np.array_equal( reference, scalevalue )
                     and np.array_equal( mask, scalevalue.mask ) )
    return

  def test_missing_values_after_without_invalidvalue(self):
    slicer = slice(90)
    time = self.time[slicer]
    value = self.value[slicer]
    mask = np.ones_like(self.scaletime, dtype=np.bool)
    mask[slicer] = False
    scalevalue = signalproc.rescaleValidToCommonTime(time, value, self.scaletime)
    self.assertTrue(     np.array_equal( self.value[slicer], scalevalue.compressed() )
                     and np.array_equal( mask, scalevalue.mask ) )
    return

  def test_missing_values_after_with_invalidvalue(self):
    slicer = slice(90)
    time = self.time[slicer]
    value = self.value[slicer]
    mask = np.ones_like(self.scaletime, dtype=np.bool)
    mask[slicer] = False
    invalid = -1
    scalevalue = signalproc.rescaleValidToCommonTime(
                      time, value, self.scaletime, InvalidValue=invalid)
    reference = np.concatenate( [value, [invalid]*10] )
    self.assertTrue(     np.array_equal( reference, scalevalue )
                     and np.array_equal( mask, scalevalue.mask ) )
    return

  def test_time_shorter(self):
    slicer = slice(10,90)
    time = self.time[slicer]
    value = self.value[slicer]
    mask = np.ones_like(self.scaletime, dtype=np.bool)
    mask[slicer] = False
    scalevalue = signalproc.rescaleValidToCommonTime(
                      time, value, self.scaletime)
    self.assertTrue(     np.array_equal( self.value[slicer], scalevalue.compressed() )
                     and np.array_equal( mask, scalevalue.mask ) )
    return

  def test_scaletime_shorter(self):
    slicer = slice(10,90)
    scaletime = self.scaletime[slicer]
    mask = np.zeros_like(scaletime, dtype=np.bool)
    scalevalue = signalproc.rescaleValidToCommonTime(
                      self.time, self.value, scaletime)
    self.assertTrue(     np.array_equal( self.value[slicer], scalevalue )
                     and np.array_equal( mask, scalevalue.mask ) )
    return

  def test_scaletime_shorter_time_single_element(self):
    scaletime = np.array([0.0,  0.1,  0.2 ])
    time      = np.array([            0.21])
    mask      = np.array([True, True, False])
    value = 2*time
    scalevalue = signalproc.rescaleValidToCommonTime(
                      time, value, scaletime)
    self.assertTrue(     np.array_equal( value, scalevalue.compressed() )
                     and np.array_equal( mask, scalevalue.mask ) )
    return

  @unittest.skip("feature to be defined")
  def test_duplicate_select_leftmost_value(self):
    scaletime = np.array([0.0,   0.1,   0.2,         0.3  ])
    time      = np.array([0.01,  0.11,  0.21,  0.22, 0.31 ])
    value     = np.array([0,     1,     2,     3,    4    ])
    mask      = np.array([False, False, False, True, False])
    reference = np.array([0,     1,     2,           4    ])
    scalevalue = signalproc.rescaleValidToCommonTime(time, value, scaletime)
    self.assertTrue(     np.array_equal( reference, scalevalue.compressed() )
                     and np.array_equal( mask, scalevalue.mask ) )
    return


class IsSameTimeSmall(unittest.TestCase):
  def setUp(self):
    self.time = np.arange(0, 10, 1e-3)
    return

  def test_same_time(self):
    self.assertTrue( signalproc.isSameTime(self.time, self.time) )
    return

  def test_same_time_copy(self):
    self.assertTrue( signalproc.isSameTime(self.time, self.time.copy()) )
    return

  def test_slightly_different_time(self):
    self.assertTrue( signalproc.isSameTime(self.time, self.time + 1e-9) )
    return

  def test_different_time(self):
    self.assertFalse( signalproc.isSameTime(self.time, self.time + 1e-7) )
    return

  def test_one_value_slightly_different_time(self):
    othertime = self.time.copy()
    othertime[0] += 1e-9
    self.assertTrue( signalproc.isSameTime(self.time, othertime) )
    return

  def test_one_value_different_time(self):
    othertime = self.time.copy()
    othertime[0] += 1e-7
    self.assertFalse( signalproc.isSameTime(self.time, othertime) )
    return


class IsSameTimeLarge(IsSameTimeSmall):
  def setUp(self):
    self.time = np.arange(1e4, 1e4+10, 1e-3)
    return


class CalcDutyCycle(unittest.TestCase):
  def test_empty_arrays(self):
    time = np.empty(0)
    activity = np.empty(0)
    with self.assertRaises(ValueError):
      duty = signalproc.calcDutyCycle(time, activity)
    return
  
  def test_nonbool(self):
    time = np.arange(10)
    activity = np.arange(10)
    with self.assertRaises(AssertionError):
      duty = signalproc.calcDutyCycle(time, activity)
    return
  
  def test_one_element_active(self):
    time = np.array((0.,))
    activity = np.array((1.,))
    self.assertEqual(signalproc.calcDutyCycle(time, activity), 1.0)
    return
  
  def test_one_element_inactive(self):
    time = np.array((0.,))
    activity = np.array((False,))
    self.assertEqual(signalproc.calcDutyCycle(time, activity), 0.0)
    return
  
  def test_equal_dt(self):
    time = np.arange(10)
    activity = np.array((0,1,1,0,1,1,1,1,0,0))
    self.assertAlmostEqual(signalproc.calcDutyCycle(time, activity), 0.667,
                           places=3)
    return
  
  def test_custom_dt(self):
    time = np.array((0,1,3,4,4.1,5,6,6.5,8,12))
    activity = np.array((0,1,1,0,1,1,1,1,0,0))
    self.assertAlmostEqual(signalproc.calcDutyCycle(time, activity), 0.517,
                           places=3)
    return
  
  def test_all_active(self):
    time = np.array((0,1,3,4,4.1,5,6,6.5,8,12))
    activity = np.ones_like(time)
    self.assertEqual(signalproc.calcDutyCycle(time, activity), 1.0)
    return
  
  def test_all_inactive(self):
    time = np.array((0,1,3,4,4.1,5,6,6.5,8,12))
    activity = np.zeros_like(time)
    self.assertEqual(signalproc.calcDutyCycle(time, activity), 0.0)
    return


class RescaleDd(unittest.TestCase):
  def setUp(self):
    self.kwargss = [
      {'Order': 'zoh'},
      {'Order': 'foh'},
      {'Left': 5.0, 'Right': -3.0},
    ]
    # data for permanent tests
    self.value_2d = np.array(((1,2),(3,4),(5,6),(7,8),(9,0)))
    self.time = np.array((0.0, 1.0, 2.0, 3.0, 4.0))
    self.scaletime = np.array((1.5, 3.0, 9.5))
    # data for random tests
    N_TIMESTAMPS = 1000
    self.value_1d_r = np.random.random(N_TIMESTAMPS)
    self.value_2d_r = np.random.random((N_TIMESTAMPS, 4))
    self.value_3d_r = np.random.random((N_TIMESTAMPS, 4, 3))
    self.time_r      = np.arange(N_TIMESTAMPS, dtype=np.float)
    self.scaletime_r = self.time_r[1:] + np.random.random(N_TIMESTAMPS-1)*0.1
    return
  
  def _check_partial_equality(self, time1, time2, value1, value2):
    self.assertTrue(np.allclose(time1, time2), "time arrays do not equal")
    self.assertTrue(np.allclose(value1, value2), "value arrays do not equal")
    return
  
  
  def test_rescale1d_equality_random(self):
    """Check if rescaledd behaves like rescale in 1-D case."""
    for kwargs in self.kwargss:
      self._test_rescale1d_equality(
        self.time_r, self.value_1d_r, self.scaletime_r, **kwargs)
    return
  
  def _test_rescale1d_equality(self, time, value, scaletime, **kwargs):
    rescale_result = signalproc.rescale(time, value, scaletime, **kwargs)
    rescaledd_result = signalproc.rescaledd(time, value, scaletime, **kwargs)
    self._check_partial_equality(
      rescale_result[0], rescaledd_result[0],
      rescale_result[1], rescaledd_result[1])
    return
  
  
  def test_rescale2d_equality_random(self):
    """Check behavior with 2-D arrays."""
    for kwargs in self.kwargss:
      self._test_rescale2d_equality(
        self.time_r, self.value_2d_r, self.scaletime_r)
    return
  
  def _test_rescale2d_equality(self, time, value, scaletime, **kwargs):
    rescaledd_result = signalproc.rescaledd(time, value, scaletime, **kwargs)
    for i_col in xrange(value.shape[1]):
      rescale_result_i = signalproc.rescale(
        time, value[:,i_col], scaletime, **kwargs)
      self._check_partial_equality(
        rescale_result_i[0], rescaledd_result[0],
        rescale_result_i[1], rescaledd_result[1][:,i_col])
    return
  
  
  def test_rescale3d_equality_random(self):
    """Check behavior with 3-D arrays."""
    for kwargs in self.kwargss:
      self._test_rescale3d_equality(
        self.time_r, self.value_3d_r, self.scaletime_r)
    return
  
  def _test_rescale3d_equality(self, time, value, scaletime, **kwargs):
    rescaledd_result = signalproc.rescaledd(time, value, scaletime, **kwargs)
    for i_col in xrange(value.shape[1]):
      for j_depth in xrange(value.shape[2]):
        rescale_result_ij = signalproc.rescale(
          time, value[:,i_col,j_depth], scaletime, **kwargs)
        self._check_partial_equality(
          rescale_result_ij[0], rescaledd_result[0],
          rescale_result_ij[1], rescaledd_result[1][:,i_col,j_depth])
    return
  
  
  def test_rescale2d_T_equality_random(self):
    """Test the case where the time is increasing column-wise (TimeAxis=1)."""
    for kwargs in self.kwargss:
      self._test_rescale2d_T_equality(
        self.time_r, self.value_2d_r.T, self.scaletime_r)
    return
  
  def _test_rescale2d_T_equality(self, time, value, scaletime, **kwargs):
    rescaledd_result = signalproc.rescaledd(
      time, value, scaletime, TimeAxis=1, **kwargs)
    for i_row in xrange(value.shape[0]):
      rescale_result_i = signalproc.rescale(
        time, value[i_row,:], scaletime, **kwargs)
      self._check_partial_equality(
        rescale_result_i[0], rescaledd_result[0],
        rescale_result_i[1], rescaledd_result[1][i_row,:])
    return
  
  
  def test_rescale2d_static(self):
    """Static test with pre-defined expected result."""
    rescaledd_result = signalproc.rescaledd(
      self.time, self.value_2d, self.scaletime)
    exp_value = np.array(((3,4),(7,8),(9,0)))
    for row, exp_row in zip(rescaledd_result[1], exp_value):
      self._check_partial_equality(
        self.scaletime, rescaledd_result[0],
        exp_row, row)
    return


class Histogram2d(unittest.TestCase):
  def setUp(self):
    # data for permanent tests
    self.xdata = np.array((1.0, 1.1, 1.5, 2.5, 0.2))
    self.ydata = np.array((1.5, 1.5, 1.0, 0.3, 1.9))
    self.xbins = np.array((0.0, 0.5, 2.0, 3.0, 4.0))
    self.ybins = np.array((0.0, 1.2, 2.0, 3.0))
    # data for random tests
    self.xdata_r = np.random.rand(1000)
    self.ydata_r = np.random.rand(1000)
    self.xbins_r = np.arange(0.0, 1.0, 0.1)
    self.ybins_r = np.arange(-0.5, 1.5, 0.15)
    return
  
  def test_invalid_condgivenaxis(self):
    with self.assertRaises(AssertionError):
      H, xedges, yedges = signalproc.histogram2d(self.xdata, self.ydata,
        bins=(self.xbins, self.ybins), cond_givenaxis='X')
    return
  
  def test_cont_condx(self):
    H, xedges, yedges = signalproc.histogram2d(self.xdata, self.ydata,
      bins=(self.xbins, self.ybins), continuous=True, cond_givenaxis='x')
    H_exp = np.array(((0.0,    1.25,   0.0),
                      (0.3571, 0.7143, 0.0),
                      (0.8333, 0.0,    0.0),
                      (0.0,    0.0,    0.0)))
    self.assertTrue(np.allclose(H, H_exp, atol=1e-3))
    return
  
  def test_cont_condy(self):
    H, xedges, yedges = signalproc.histogram2d(self.xdata, self.ydata,
      bins=(self.xbins, self.ybins), continuous=True, cond_givenaxis='y')
    H_exp = np.array(((0.0,    0.2857, 0.0),
                      (0.4,    0.5714, 0.0),
                      (0.4,    0.0,    0.0),
                      (0.0,    0.0,    0.0)))
    self.assertTrue(np.allclose(H, H_exp, atol=1e-3))
    return
  
  def test_cont_normed(self):
    H, xedges, yedges = signalproc.histogram2d(self.xdata, self.ydata,
      bins=(self.xbins, self.ybins), continuous=True, normed=True)
    H_exp = np.array(((0.0,    0.1724, 0.0),
                      (0.1724, 0.3448, 0.0),
                      (0.1724, 0.0,    0.0),
                      (0.0,    0.0,    0.0)))
    self.assertTrue(np.allclose(H, H_exp, atol=1e-3))
    return
  
  def test_disc_condx(self):
    H, xedges, yedges = signalproc.histogram2d(self.xdata, self.ydata,
      bins=(self.xbins, self.ybins), continuous=False, cond_givenaxis='x')
    H_exp = np.array(((0.0,    1.0,    0.0),
                      (0.3333, 0.6667, 0.0),
                      (1.0,    0.0,    0.0),
                      (0.0,    0.0,    0.0)))
    self.assertTrue(np.allclose(H, H_exp, atol=1e-3))
    return
  
  def test_disc_condy(self):
    H, xedges, yedges = signalproc.histogram2d(self.xdata, self.ydata,
      bins=(self.xbins, self.ybins), continuous=False, cond_givenaxis='y')
    H_exp = np.array(((0.0,    0.3333, 0.0),
                      (0.5,    0.6667, 0.0),
                      (0.5,    0.0,    0.0),
                      (0.0,    0.0,    0.0)))
    self.assertTrue(np.allclose(H, H_exp, atol=1e-3))
    return
  
  def test_disc_normed(self):
    H, xedges, yedges = signalproc.histogram2d(self.xdata, self.ydata,
      bins=(self.xbins, self.ybins), continuous=False, normed=True)
    H_exp = np.array(((0.0,    0.2,    0.0),
                      (0.2,    0.4,    0.0),
                      (0.2,    0.0,    0.0),
                      (0.0,    0.0,    0.0)))
    self.assertTrue(np.array_equal(H, H_exp))
    return

  def test_nonnormed(self):
    H_c, xedges, yedges = signalproc.histogram2d(self.xdata, self.ydata,
      bins=(self.xbins, self.ybins), continuous=True)
    H_d, xedges, yedges = signalproc.histogram2d(self.xdata, self.ydata,
      bins=(self.xbins, self.ybins), continuous=False)
    H_exp = np.array(((0, 1, 0),
                      (1, 2, 0),
                      (1, 0, 0),
                      (0, 0, 0)))
    self.assertTrue(    np.array_equal(H_c, H_exp)
                    and np.array_equal(H_d, H_exp)
                    and H_c.dtype is H_d.dtype)
    return

  def test_equals_with_numpy_normed(self):
    # another test for "test_cont_normed"
    self._test_equals_with_numpy(True)
    return
  
  def test_equals_with_numpy_nonnormed(self):
    # another test for "test_nonnormed"
    self._test_equals_with_numpy(False)
    return
  
  def _test_equals_with_numpy(self, normed):
    H1, xedges1, yedges1 = signalproc.histogram2d(self.xdata_r, self.ydata_r,
      bins=(self.xbins_r, self.ybins_r), normed=normed)
    H2, xedges2, yedges2 = np.histogram2d(self.xdata_r, self.ydata_r,
      bins=(self.xbins_r, self.ybins_r), normed=normed)
    self.assertTrue(    np.allclose(H1, H2)
                    and H1.dtype is H2.dtype
                    and np.array_equal(xedges1, xedges2)
                    and np.array_equal(yedges1, yedges2))
    return

class MaskedAllLikeFill(unittest.TestCase):
  def setUp(self):
    self.arr = np.random.rand(100)
    return

  def test_basics(self):
    arr = self.arr
    out = signalproc.masked_all_like_fill(arr)
    self._test_basics(out, arr)
    return

  def _test_basics(self, out, arr):
    self.assertFalse( out is arr )
    self.assertTrue( np.all(out.mask), msg='not all entries are masked' )
    self.assertTrue( np.all(out.data == 0), msg='default filled values are not 0' )
    self.assertTrue( out.shape == arr.shape, msg='shape mismatch' )
    self.assertTrue( out.dtype == arr.dtype, msg='dtype mismatch' )
    return

  def test_non_default_value(self):
    value = 5
    out = signalproc.masked_all_like_fill(self.arr, value=value)
    self.assertTrue( np.all(out.data == value) )
    return

  def test_from_random_ma(self):
    arr = np.ma.masked_array(self.arr, mask=np.random.rand(self.arr.size))
    out = signalproc.masked_all_like_fill(arr)
    self._test_basics(out, arr)
    return

class SetMaReadOnly(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.arr = np.ma.masked_array(xrange(4), [0,1,0,1])
    signalproc.set_ma_read_only(cls.arr)
    return

  def test_basic(self):
    with self.assertRaises(ValueError):
      self.arr[1] = 5
    return

  def test_data(self):
    with self.assertRaises(ValueError):
      self.arr.data[1] = 5
    return

  def test_mask(self):
    with self.assertRaises(ValueError):
      self.arr.mask[0] = True
    return

  def test_unmask(self):
    with self.assertRaises(ValueError):
      self.arr.mask[1] = False
    return


if __name__ == '__main__':
  unittest.main()
