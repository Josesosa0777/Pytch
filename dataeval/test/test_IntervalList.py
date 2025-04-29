import unittest

import numpy

from measproc.IntervalList import cIntervalList, maskToIntervals, findSingles
from measproc import EventFinder, relations

class TestIntervalList(unittest.TestCase):
  def setUp(self):
    self.time = numpy.arange(0, 20, 1e-1)
    return
  
  def test__merge(self):
    intervals = [(0, 6), (16, 17), (4, 10)]
    intervallist = cIntervalList(self.time)
    merged = intervallist._merge(intervals)
    self.assertListEqual(merged, [(0, 10), (16, 17)])
    return

  def test__merge_join_second_round(self):
    intervals = [(0, 6), (16, 17), (4, 10), (9, 17)]
    intervallist = cIntervalList(self.time)
    merged = intervallist._merge(intervals)
    self.assertListEqual(merged, [(0, 17)])
    return

  def test__merge_single_last(self):
    intervals = [(0, 6), (4, 10), (9, 17), (16, 17)]
    intervallist = cIntervalList(self.time)
    merged = intervallist._merge(intervals)
    self.assertListEqual(merged, [(0, 17)])
    return

  def test_merge(self):
    intervals = [(0, 6), (16, 17), (4, 10)]
    intervallist = cIntervalList.fromList(self.time, intervals)
    merged = intervallist.merge()
    self.assertTrue(merged == [(0, 10), (16, 17)])
    return

  def test_merge_join_second(self):
    intervals = [(0, 6), (16, 17), (4, 10), (9, 17)]
    intervallist = cIntervalList.fromList(self.time, intervals)
    merged = intervallist.merge()
    self.assertTrue(merged == [(0, 17)])
    return

  def test_merge_single_last(self):
    intervals = [(0, 6), (4, 10), (9, 17), (16, 17)]
    intervallist = cIntervalList.fromList(self.time, intervals)
    merged = intervallist.merge()
    self.assertTrue(merged == [(0, 17)])
    return

  def test_merge_with_margin(self):
    intervals = [(0, 6), (17, 27), (142, 156), (168, 195)]
    intervallist = cIntervalList.fromList(self.time, intervals)
    merged = intervallist.merge(1.2)
    self.assertTrue(merged == [(0, 27), (142, 156), (168, 195)])
    return

  def test_join(self):
    intervals = [(0, 6), (16, 17), (5, 16)]
    intervallist = cIntervalList.fromList(self.time, intervals)
    merged = intervallist.join()
    self.assertTrue(merged == [(0, 16), (16, 17)])
    return

  def test_join_join_second(self):
    intervals = [(0, 6), (16, 17), (4, 10), (9, 17)]
    intervallist = cIntervalList.fromList(self.time, intervals)
    merged = intervallist.join()
    self.assertTrue(merged == [(0, 17)])
    return

  def test_join_single_last(self):
    intervals = [(0, 6), (4, 10), (9, 17), (16, 17)]
    intervallist = cIntervalList.fromList(self.time, intervals)
    merged = intervallist.join()
    self.assertTrue(merged == [(0, 17)])
    return

  def test_join_with_shift(self):
    intervals = [(0, 6), (17, 27), (142, 156), (168, 195)]
    intervallist = cIntervalList.fromList(self.time, intervals)
    merged = intervallist.join(12)
    self.assertTrue(merged == [(0, 27), (142, 156), (168, 195)])
    return

  def test_group(self):
    intervals = [(0, 6), (16, 17), (4, 10)]
    intervallist = cIntervalList.fromList(self.time, intervals)
    group = intervallist.group()
    self.assertListEqual(group, [[(0, 6), (4, 10)], [(16, 17)]])
    return
  pass


class TestGetTimeIndexWithMargin(unittest.TestCase):
  def setUp(self):
    time = numpy.arange(0, 20, 1e-1)
    self.intervallist = cIntervalList(time)
    return
  
  def test_over_upper_bound(self):
    index = self.intervallist.getTimeIndexWithMargin(15, 1.15, True)
    self.assertEqual(index, 26)
    return

  def test_on_upper_bound(self):
    index = self.intervallist.getTimeIndexWithMargin(15, 1.1, True)
    self.assertEqual(index, 26)
    return

  def test_on_upper_limit(self):
    index = self.intervallist.getTimeIndexWithMargin(150, 5.0, True)
    self.assertEqual(index, 200)
    return

  def test_over_upper_limit(self):
    index = self.intervallist.getTimeIndexWithMargin(150, 5.1, True)
    self.assertEqual(index, 200)
    return

  def test_upper_at_end(self):
    print
    index = self.intervallist.getTimeIndexWithMargin(199, 0.0, True)
    self.assertEqual(index, 199)
    return

  def test_on_lower_bound(self):
    index = self.intervallist.getTimeIndexWithMargin(15, 1.1, False)
    self.assertEqual(index, 4)
    return

  def test_over_lower_bound(self):
    index = self.intervallist.getTimeIndexWithMargin(15, 1.15, False)
    self.assertEqual(index, 4)
    return

  def test_on_lower_limit(self):
    index = self.intervallist.getTimeIndexWithMargin(15, 1.5, False)
    self.assertEqual(index, 0)
    return

  def test_over_lower_limit(self):
    index = self.intervallist.getTimeIndexWithMargin(15, 1.6, False)
    self.assertEqual(index, 0)
    return

  def test_lower_at_end(self):
    index = self.intervallist.getTimeIndexWithMargin(199, 0.0, False)
    self.assertEqual(index, 199)
    return
  pass


class TestGetTimeIndexWithShift(unittest.TestCase):
  def setUp(self):
    time = numpy.arange(0, 20, 1e-1)
    self.intervallist = cIntervalList(time)
    return
  
  def test_on_upper_bound(self):
    index = self.intervallist.getTimeIndexWithShift(15, 11, True)
    self.assertEqual(index, 26)
    return

  def test_on_upper_limit(self):
    index = self.intervallist.getTimeIndexWithShift(150, 50, True)
    self.assertEqual(index, 200)
    return

  def test_over_upper_limit(self):
    index = self.intervallist.getTimeIndexWithShift(150, 51, True)
    self.assertEqual(index, 200)
    return

  def test_upper_at_end(self):
    index = self.intervallist.getTimeIndexWithShift(199, 0, True)
    self.assertEqual(index, 199)
    return

  def test_on_lower_bound(self):
    index = self.intervallist.getTimeIndexWithShift(15, 11, False)
    self.assertEqual(index, 4)
    return

  def test_on_lower_limit(self):
    index = self.intervallist.getTimeIndexWithShift(15, 15, False)
    self.assertEqual(index, 0)
    return

  def test_over_lower_limit(self):
    index = self.intervallist.getTimeIndexWithShift(15, 16, False)
    self.assertEqual(index, 0)
    return

  def test_lower_at_end(self):
    index = self.intervallist.getTimeIndexWithShift(199, 0, False)
    self.assertEqual(index, 199)
    return
  pass


class TestAddMargin(unittest.TestCase):
  def setUp(self):
    time = numpy.arange(0, 12, 1e-1)
    intervals = [(12, 23), (45, 98)]
    self.intervallist = cIntervalList.fromList(time, intervals)
    return

  def test_addMargin_margin(self):
    intervallist = self.intervallist.addMargin(TimeMargins=[1.2, 1.8])
    self.assertTrue(intervallist == [(1, 41), (33, 116)])
    return

  def test_addMargin_over_margin(self):
    intervallist = self.intervallist.addMargin(TimeMargins=[1.5, 2.4])
    self.assertTrue(intervallist == [(0, 47), (30, 120)])
    return

  def test_addMargin_shift(self):
    intervallist = self.intervallist.addMargin(CycleMargins=[11, 18])
    self.assertTrue(intervallist == [(1, 41), (34, 116)])
    return

  def test_addMargin_over_shift(self):
    intervallist = self.intervallist.addMargin(CycleMargins=[14, 22])
    self.assertTrue(intervallist == [(0, 45), (31, 120)])
    return
  pass


class TestNeighbour(unittest.TestCase):
  def setUp(self):
    self.time = numpy.arange(0, 12, 1e-1)
    intervals = [(12, 23), (45, 98)]
    self.intervallist = cIntervalList.fromList(self.time, intervals)
    return

  def test_neighbour(self):
    intervals = [(23, 40), (98, 100)]
    intervallist = cIntervalList.fromList(self.time, intervals)
    neighbours = self.intervallist.neighbour(intervallist)
    self.assertTrue(neighbours == [(22, 23), (97, 98)])
    return
  pass

class TestIntervalListInitFromList(unittest.TestCase):
  def setUp(self):
    self.time = numpy.linspace(0., 1., 100)
    self.original = [(0,2), (4,5)]
    self.intervals = cIntervalList.fromList(self.time, self.original)
    return

  def test_fromlist_equality(self):
    self.assertTrue( self.intervals == self.original )
    return

  def test_fromlist_identity(self):
    self.assertFalse( self.intervals.Intervals is self.original )
    return

  def test_copy_equality(self):
    copied = self.intervals.copy()
    self.assertTrue( copied == self.intervals )
    return

  def test_copy_identity(self):
    copied = self.intervals.copy()
    self.assertFalse( copied.Intervals is self.intervals.Intervals )
    return

class TestMaskToIntervalConversion(unittest.TestCase):
  def setUp(self):
    self.mask = numpy.array([1, 0, 1,1, 0,0, 1,1,1], dtype=numpy.bool)
    self.intervals = [(0,1), (2,4), (6,9)]
    self.intervalsNoSingles = self.intervals[1:]
    return

  def test_mask_to_interval_does_not_harm(self):
    orig = self.mask.copy()
    self._test_mask_to_interval_does_not_harm(orig, self.mask)
    return

  def test_mask_to_interval_does_not_harm_int8(self):
    mask = self.mask.astype(numpy.int8)
    orig = mask.copy()
    self._test_mask_to_interval_does_not_harm(orig, mask)
    return

  def _test_mask_to_interval_does_not_harm(self, orig, mask):
    myintervals = maskToIntervals(mask)
    self.assertTrue( numpy.array_equal(mask, orig) )
    self.assertTrue( mask.dtype is orig.dtype )
    return

  def test_mask_to_interval(self):
    myintervals = maskToIntervals(self.mask)
    self.assertTrue( myintervals == self.intervals )
    return

  def test_mask_to_interval_exclude_singles(self):
    intervalsNoSingles = self.intervals[1:]
    myintervalsNoSingles = maskToIntervals(self.mask, ExcludeSingles=True)
    self.assertTrue( myintervalsNoSingles == intervalsNoSingles )
    return

  def test_mask_to_interval_dtype_not_bool(self):
    mask = self.mask.astype(numpy.uint8)
    myintervals = maskToIntervals(mask)
    self.assertTrue( myintervals == self.intervals )
    return

  def test_mask_to_interval_masked_array_none_masked(self):
    mask = numpy.ma.masked_array(self.mask, mask=numpy.zeros_like(self.mask))
    myintervals = maskToIntervals(mask)
    self.assertTrue( myintervals == self.intervals )
    return

  def test_mask_to_interval_masked_array_all_masked(self):
    mask = numpy.ma.masked_array(self.mask, mask=numpy.ones_like(self.mask))
    myintervals = maskToIntervals(mask)
    self.assertTrue( myintervals == [] )
    return

  def test_mask_to_interval_masked_array_self_masked(self):
    mask = numpy.ma.masked_array(self.mask, mask=self.mask)
    myintervals = maskToIntervals(mask)
    self.assertTrue( myintervals == [] )
    return

  def test_mask_to_interval_masked_array_not_bool(self):
    ma = numpy.ma.masked_array(numpy.array([0,1,1,0,1,1], dtype=numpy.uint8),
                               mask=[True, True, False, False, False, False])
    myintervals = maskToIntervals(ma)
    self.assertTrue( myintervals == [(2,3), (4,6)] )
    return


class TestFindSingles(unittest.TestCase):
  def setUp(self):
    self.mask    = numpy.array([1,0,1,1,0,1,0,1], dtype=numpy.bool)
    self.singles = numpy.array([1,0,0,0,0,1,0,1], dtype=numpy.bool)
    return

  def test_does_not_harm(self):
    orig = self.mask.copy()
    self._test_does_not_harm(orig, self.mask)
    return

  def test_does_not_harm_int8(self):
    mask = self.mask.astype(numpy.int8)
    orig = mask.copy()
    self._test_does_not_harm(orig, mask)
    return

  def _test_does_not_harm(self, orig, mask):
    singles = findSingles(mask)
    self.assertTrue( numpy.array_equal(mask, orig) )
    self.assertTrue( mask.dtype is orig.dtype )
    return

  def test_mark_singles(self):
    singles = findSingles(self.mask)
    self.assertTrue( numpy.array_equal(singles, self.singles) )
    return

  def test_mark_singles_masked_array(self):
    mask = numpy.zeros_like(self.mask)
    mask[-1] = True
    ma = numpy.ma.masked_array(self.mask, mask)
    singles = findSingles(ma)
    reference = self.singles.copy()
    reference[-1] = False
    self.assertTrue( numpy.array_equal(singles, reference) )
    return


class TestIntervalListInitFromMask(unittest.TestCase):
  def setUp(self):
    self.time = numpy.linspace(0., 1., 100)
    self.limit = 0.5
    self.a = numpy.random.rand(self.time.size)
    self.mask = self.a > self.limit
    return

  def frommask_tomask_equality(self, arr):
    intervals = cIntervalList.fromMask(self.time, arr)
    mymask = intervals.toMask(dtype=arr.dtype)
    condition = numpy.array_equal(mymask, arr) and mymask.dtype == arr.dtype
    return condition

  def test_frommask_tomask_equality_bool(self):
    condition = self.frommask_tomask_equality(self.mask)
    self.assertTrue(condition)
    return

  def test_frommask_tomask_equality_uint8(self):
    arr = self.mask.astype(numpy.uint8)
    condition = self.frommask_tomask_equality(arr)
    self.assertTrue(condition)
    return

  def test_frommask_tomask_equality_int8(self):
    arr = self.mask.astype(numpy.int8)
    condition = self.frommask_tomask_equality(arr)
    self.assertTrue(condition)
    return

  def test_frommask_tomask_equality_float32(self):
    arr = self.mask.astype(numpy.float32)
    condition = self.frommask_tomask_equality(arr)
    self.assertTrue(condition)
    return

  def test_frommask_tomask_identity(self):
    """ interval list should not store the mask it was initialized from """
    intervals = cIntervalList.fromMask(self.time, self.mask)
    mymask = intervals.toMask(dtype=self.mask.dtype)
    self.assertFalse( mymask is self.mask )
    return

  def test_tomask_default_dtype_bool(self):
    intervals = cIntervalList.fromMask(self.time, self.mask)
    mymask = intervals.toMask()
    self.assertTrue( mymask.dtype == self.mask.dtype )

  def test_frommask_eventfinder_compare_equality(self):
    intervalsFromMask = cIntervalList.fromMask(self.time, self.mask)
    intervalsFromCompare = EventFinder.cEventFinder.compare(self.time, self.a, relations.greater, self.limit)
    self.assertTrue( intervalsFromMask == intervalsFromCompare )
    return

  def test_frommask_exception_with_array_other_than_0_or_1(self):
    mymask = numpy.where(self.mask, 1, 2)
    self.assertRaises(ValueError, cIntervalList.fromMask, self.time, mymask)
    return

class TestRandomIntervalOperations(unittest.TestCase):
  """ Tests for random, disjoint, non-adjacent intervals """
  def setUp(self):
    self.time = numpy.linspace(0., 1., 1000)
    limit = 0.5
    a1 = numpy.random.rand(self.time.size)
    a2 = numpy.random.rand(self.time.size)
    a3 = numpy.random.rand(self.time.size)
    self.intervals1 = EventFinder.cEventFinder.compare(self.time, a1, relations.greater, limit)
    self.intervals2 = EventFinder.cEventFinder.compare(self.time, a2, relations.greater, limit)
    self.intervals3 = EventFinder.cEventFinder.compare(self.time, a3, relations.greater, limit)
    self.mask1 = a1 > limit
    self.mask2 = a2 > limit
    return

  def test_negate_by_numpy(self):
    neg  = self.intervals1.negate()
    myNegMask = neg.toMask()
    negMask = ~self.intervals1.toMask()
    self.assertTrue( numpy.all(myNegMask == negMask) )
    return

  def test_double_negate_identity(self):
    neg  = self.intervals1.negate()
    neg2 = neg.negate()
    self.assertTrue( neg2 == self.intervals1 )
    return

  def test_intersection_by_numpy(self):
    intersection12 = self.intervals1.intersect(self.intervals2)
    myIntersectMask = intersection12.toMask()
    intersectMask = self.mask1 & self.mask2
    self.assertTrue( numpy.all(myIntersectMask == intersectMask) )
    return

  def test_intersection_identity(self):
    self.assertTrue( self.intervals1.intersect(self.intervals1)==self.intervals1 )
    return

  def test_intersection_commutativity(self):
    intersection12 = self.intervals1.intersect(self.intervals2)
    intersection21 = self.intervals2.intersect(self.intervals1)
    self.assertTrue( intersection12 == intersection21 )
    return

  def test_intersection_associativity(self):
    intersection12 = self.intervals1.intersect(self.intervals2)
    intersection23 = self.intervals2.intersect(self.intervals3)
    intersection1_23 = self.intervals1.intersect( intersection23 )
    intersection12_3 = intersection12.intersect( self.intervals3 )
    self.assertTrue( intersection1_23 == intersection12_3 )
    return

  def test_union_by_numpy(self):
    union12 = self.intervals1.union(self.intervals2)
    myUnionMask = union12.toMask()
    unionMask = self.mask1 | self.mask2
    self.assertTrue( numpy.all(myUnionMask == unionMask) )
    return

  def test_union_identity(self):
    self.assertTrue( self.intervals1.union(self.intervals1)==self.intervals1 )
    return

  def test_union_commutativity(self):
    union12 = self.intervals1.union(self.intervals2)
    union21 = self.intervals2.union(self.intervals1)
    self.assertTrue( union12 == union21 )
    return

  def test_union_associativity(self):
    union12 = self.intervals1.union(self.intervals2)
    union23 = self.intervals2.union(self.intervals3)
    union1_23 = self.intervals1.union( union23 )
    union12_3 = union12.union( self.intervals3 )
    self.assertTrue( union1_23 == union12_3 )
    return

  def test_join_identity(self):
    self.assertFalse( self.intervals1.join() is self.intervals1 )
    return

  def test_disjoint(self):
    self.assertTrue( self.intervals1.isDisjoint() )
    return

  def test_sort(self):
    intervals = self.intervals1.copy()
    intervals.sort()
    self.assertTrue( intervals == self.intervals1 )
    return

  def test_sort_reverse(self):
    intervals = self.intervals1.copy()
    intervals.sort(reverse=True)
    self.assertTrue( intervals == self.intervals1[::-1] )
    return

  def test_argsort_reorder_equality(self):
    intervals = self.intervals1.copy()
    indices = intervals.argsort()
    intervals.reorder(indices)
    self.assertTrue( intervals == self.intervals1 )
    return

  def test_argsort_reorder_identity(self):
    intervals = self.intervals1
    indices = intervals.argsort()
    intervals.reorder(indices)
    self.assertTrue( intervals is self.intervals1 )
    return

class TestXtremeIntervalOperations(unittest.TestCase):
  """ Tests for operations between empty, full and random intervals """
  def setUp(self):
    self.time = numpy.linspace(0., 1., 1000)
    a1 = numpy.random.rand(self.time.size)
    limit = 0.5
    self.intervals = cIntervalList.fromMask(self.time, a1 > limit)
    self.emptyIntervals = cIntervalList(self.time)
    self.fullIntervals = cIntervalList(self.time)
    self.fullIntervals.add(0, self.time.size)
    return

  # empty interval tests
  def test_empty_negate(self):
    self.assertTrue( self.emptyIntervals.negate() == self.fullIntervals )
    return

  def test_empty_intersect_empty(self):
    self.assertTrue( self.emptyIntervals.intersect(self.emptyIntervals) == self.emptyIntervals )
    return

  def test_empty_intersect_regular(self):
    self.assertTrue( self.emptyIntervals.intersect(self.intervals) == self.emptyIntervals )
    return

  def test_regular_intersect_empty(self):
    self.assertTrue( self.intervals.intersect(self.emptyIntervals) == self.emptyIntervals )
    return

  def test_empty_union_empty(self):
    self.assertTrue( self.emptyIntervals.union(self.emptyIntervals) == self.emptyIntervals )
    return

  def test_empty_union_regular(self):
    self.assertTrue( self.emptyIntervals.union(self.intervals) == self.intervals )
    return

  def test_regular_union_empty(self):
    self.assertTrue( self.intervals.union(self.emptyIntervals) == self.intervals )
    return

  def test_empty_join(self):
    self.assertTrue( self.emptyIntervals.join() == self.emptyIntervals )
    return

  # full interval tests
  def test_full_negate(self):
    self.assertTrue( self.fullIntervals.negate() == self.emptyIntervals )
    return

  def test_full_intersect_full(self):
    self.assertTrue( self.fullIntervals.intersect(self.fullIntervals) == self.fullIntervals )
    return

  def test_full_intersect_regular(self):
    self.assertTrue( self.fullIntervals.intersect(self.intervals) == self.intervals )
    return

  def test_regular_intersect_full(self):
    self.assertTrue( self.intervals.intersect(self.fullIntervals) == self.intervals )
    return

  def test_full_union_full(self):
    self.assertTrue( self.fullIntervals.union(self.fullIntervals) == self.fullIntervals )
    return

  def test_full_union_regular(self):
    self.assertTrue( self.fullIntervals.union(self.intervals) == self.fullIntervals )
    return

  def test_regular_union_full(self):
    self.assertTrue( self.intervals.union(self.fullIntervals) == self.fullIntervals )
    return

  def test_full_join(self):
    self.assertTrue( self.fullIntervals.join() == self.fullIntervals )
    return

  # mixed tests
  def test_full_intersect_empty(self):
    self.assertTrue( self.fullIntervals.intersect(self.emptyIntervals) == self.emptyIntervals )
    return

  def test_empty_intersect_full(self):
    self.assertTrue( self.emptyIntervals.intersect(self.fullIntervals) == self.emptyIntervals )
    return

  def test_full_union_empty(self):
    self.assertTrue( self.fullIntervals.union(self.emptyIntervals) == self.fullIntervals )
    return

  def test_empty_union_full(self):
    self.assertTrue( self.emptyIntervals.union(self.fullIntervals) == self.fullIntervals )
    return

if __name__ == '__main__':
  unittest.main()

