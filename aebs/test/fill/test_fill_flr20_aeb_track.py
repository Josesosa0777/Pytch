import unittest
import random

import numpy as np

from test_fill_flr20_flc20_raw import parse_arguments, modules, TestFillResult
from aebs.fill import fill_flr20_aeb_track, fill_flr20_raw_tracks


class TestFillFlr20VirtualTrack(object):
  def test__attribs_caching__should_run_first(self):
    # REMARK: this needs to run first, before any test (ensured by alphabetical order)
    for name in self.o._attribs:
      self._test_method_caching(self.o, name)
    return

  def test_methods_caching(self):
    for name in self.o._methods:
      self._test_method_caching(self.o, name)
    return

  def test_attribs_dict_style_access(self):
    for name in self.o._attribs:
      self._test_attrib_dict_style_access(self.o, name)
    return

  def test_required_attribs(self):
    req_attrib_names = self.test_modules.itervalues().next() # dirty hack
    for req_attrib_name in req_attrib_names:
      self.assertTrue( hasattr(self.o, req_attrib_name),
                       msg="required attrubute '%s' missing" %req_attrib_name )
    return

  def test_methods_required_properties(self):
    for name in self.o._methods:
      self._test_attrib_required_properties(self.o, name)
    return

  def test_attribs_type_maskedarray(self):
    for name in self.o._attribs:
      # load attribute
      res = self.o[name]
      if name == 'time':
        self._test_obj_type(self.o, name, res, required_type=np.ndarray)
      else:
        if isinstance(res, tuple):
          # composite attribute
          for v in res:
            self._test_obj_type(self.o, name, v, required_type=np.ma.MaskedArray)
        else:
          self._test_obj_type(self.o, name, res, required_type=np.ma.MaskedArray)
    return

  def test_attribs_mask_same_per_object(self):
    self._test_attribs_mask_same_in_object(self.o, self.o._attribs)
    return

  def test_tracking_state_valid_agrees_mask(self):
    self._test_tracking_state_valid_agrees_mask(self.o)
    return

  def test_attribs_size_agrees_obj_time_size(self):
    for name in self.o._attribs:
      res = self.o[name]
      if isinstance(res, tuple):
        for arr in res:
          self._test_arr_size_agrees_obj_time_size(self.o, name, arr)
      else:
        self._test_arr_size_agrees_obj_time_size(self.o, name, res)
    return

  def test_rescale_same_time(self):
    oo = self.o.rescale(self.o.time)
    self._test_rescale_same_time(oo)
    return

  def _test_rescale_same_time(self, oo):
    o = self.o
    # check if rescaled object is the same as original
    self.assertFalse(o is oo, msg="rescaled object %s is same as original" %oo)
    # check rescaled object's time
    self.assertTrue(oo.time is o.time, msg="rescaled object %s time error" %oo)
    for name in o._attribs:
      # load attribute
      original = getattr(o, name)
      rescaled = getattr(oo, name)
      # check identity
      self.assertTrue( self.attr_identical(original, rescaled, agree=False),
                       msg="attribute %s of %s: rescale identity error" %(name,o) )
      # check equality
      self.assertTrue( self.attr_equal(original, rescaled),
                       msg="attribute %s of %s: rescale equality error" %(name,o) )
      # check size
      self.assertTrue( self.attr_size(rescaled, o.time.size),
                       msg="attribute %s of %s: rescale size error" %(name,o) )
    return

  def test_rescale_different_time(self):
    o = self.o
    otherScaleTime = np.arange(o.time[0], o.time[-1], 3*o.time.size)
    oo = self.o.rescale(otherScaleTime)
    self._test_rescale_different_time(oo, otherScaleTime)
    return

  def _test_rescale_different_time(self, oo, otherScaleTime):
    o = self.o
    # check if rescaled object is the same as original
    self.assertFalse(o is oo, msg="rescaled object %s is same as original" %oo)
    # check rescaled object's time
    self.assertTrue(oo.time is otherScaleTime, msg="rescaled object %s time error" %oo)
    for name in o._attribs:
      # load attribute
      original = getattr(o, name)
      rescaled = getattr(oo, name)
      # check identity
      self.assertTrue( self.attr_identical(original, rescaled, agree=False),
                       msg="attribute %s of %s: rescale identity error" %(name,o) )
      # check equality
      self.assertTrue( self.attr_equal(original, rescaled, agree=False),
                       msg="attribute %s of %s: rescale equality error" %(name,o) )
      # check size
      self.assertTrue( self.attr_size(rescaled, otherScaleTime.size),
                       msg="attribute %s of %s: rescale size error" %(name,o) )
    return

  def test_is_empty(self):
    self.assertFalse( self.o.is_empty,
                      msg="Virtual track is NOT empty, but `is_empty` is %s!" %self.o.is_empty)
    return

  def test_composite_attribute_join(self):
    for name in self.o._attribs:
      attrib = self.o[name]
      if name != 'tr_state' and isinstance(attrib, tuple):
        self._test_composite_attribute_join(self.o, name, attrib)
    return


flr20_aeb_track_req_attrs = list( modules[fill_flr20_raw_tracks] )
flr20_aeb_track_req_attrs.extend(
  ['unique_ids', 'is_empty', 'refl_asso_masks', 'video_asso_masks',
   'selection_intervals', 'alive_intervals', 'sleeping_counter']
)
necessary_modules = { fill_flr20_aeb_track : tuple(flr20_aeb_track_req_attrs) }

class TestFillFlr20AebTrack(TestFillResult, TestFillFlr20VirtualTrack):
  test_modules = necessary_modules

  @classmethod
  def setUpClass(cls):
    super(TestFillFlr20AebTrack, cls).setUpClass()
    cls.o = cls.results[fill_flr20_aeb_track]
    return

  def test_unique_ids_uniqueness(self):
    unique_ids = set(self.o.unique_ids)
    self.assertEqual( len(unique_ids), len(self.o.unique_ids) )
    return

  def test_unique_ids_agree_ids(self):
    if not np.any(self.o.id.mask):
      self.skipTest('Makes no sense on empty AEBS track')
    unique_ids_from_ids = np.unique( self.o.id.compressed() )
    unique_ids = np.array(self.o.unique_ids, dtype=self.o.id.dtype)
    unique_ids_from_ids.sort()
    unique_ids.sort()
    self.assertTrue( np.array_equal(unique_ids_from_ids, unique_ids) )
    return

  def test_get_selection_timestamp(self):
    random_valid_timestamp = self._pick_random_timestamp_from_mask(~self.o.id.mask)
    timestamp = self.o.get_selection_timestamp(random_valid_timestamp)
    self.assertFalse( timestamp > random_valid_timestamp,
                      msg="returned timestamp %d is after given %d" %(timestamp, random_valid_timestamp) )
    return

  def test_get_selection_timestamp_raises_error_on_invalid_timestamp(self):
    if not np.any(self.o.id.mask):
      self.skipTest('Makes no sense to do test, as AEBS track is present the whole time')
    random_invalid_timestamp = self._pick_random_timestamp_from_mask(self.o.id.mask)
    with self.assertRaises(ValueError, msg="Error NOT raised on invalid timestamp %d" %random_invalid_timestamp):
      self.o.get_selection_timestamp(random_invalid_timestamp)
    return

  def _pick_random_timestamp_from_mask(self, mask):
    timestamps, = np.where(mask)
    if timestamps.size == 0:
      self.skipTest('No timestamp found')
    random_timestamp = random.choice(timestamps)
    return random_timestamp


class TestFillFlr20AebTrackEmpty(TestFillFlr20AebTrack):

  @classmethod
  def setUpClass(cls):
    super(TestFillFlr20AebTrackEmpty, cls).setUpClass()
    if not all(cls.o.id.mask):
      raise unittest.SkipTest("AEBS track is not empty, makes no sense to do empty track tests")
    return

  def test_unique_ids(self):
    self.assertTrue( len(self.o.unique_ids) == 0,
                     msg="AEBS track is empty, but ids '{0}' referenced!".format(self.o.unique_ids) )
    return

  def test_is_empty(self):
    self.assertTrue( self.o.is_empty,
                     msg="AEBS track is empty, but `is_empty` is %s!" %self.o.is_empty)
    return


if __name__ == '__main__':
  import sys

  args = parse_arguments()
  TestFillFlr20AebTrack.args = args
  TestFillFlr20AebTrackEmpty.args = parse_arguments(
    measpath=r'\\file\Messdat\DAS\EnduranceRun\H566PP\2013-05-16\H566_2013-05-16_17-24-12.mf4'
  )
  unittest.main(argv=[sys.argv[0]], verbosity=args.v)
