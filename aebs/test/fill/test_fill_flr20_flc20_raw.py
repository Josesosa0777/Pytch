import unittest
import argparse

import numpy as np

from config.Config import init_dataeval
from interface.modules import ModuleName
from measparser.signalgroup import SignalGroupError
from measproc.IntervalList import cIntervalList, intervalsToMask
from aebs.fill import (fill_flr20_raw_targets,
                       fill_flr20_raw_tracks,
                       fill_flc20_raw_tracks,
                       calc_mb79_raw_tracks,
                       calc_mb79_raw_targets)
from obj_attrib_props import attrib_props


def parse_arguments( measpath=r'\\file\Messdat\DAS\EnduranceRun\H566PP\2013-04-09\H566_2013-04-09_06-52-13.mf4',
                     backupdir=None,
                     verbosity=0 ):
  parser = argparse.ArgumentParser()
  parser.add_argument('-m', '--measurement',
                      help='measurement file',
                      default=measpath)
  parser.add_argument('--backupdir',
                      help='backup directory',
                      default=backupdir)
  parser.add_argument('-v',
                      help='verbosity level',
                      default=verbosity)
  args = parser.parse_args()
  return args

modules = {
  # module object        : required method names
  fill_flr20_raw_targets : ('angle',
                            'dx',
                            'dy',
                            'id',
                            'power',
                            'range',
                            'range_rate',
                            'target_flags',
                            'time',
                            'vx'),
  calc_mb79_raw_targets  : ('angle',
                            'dx',
                            'dy',
                            'id',
                            'power',
                            'range',
                            'range_rate',
                            'time',
                            'vx',
                            'vy'),
  fill_flr20_raw_tracks  : ('acc_track',
                            'aeb_track',
                            'angle',
                            'ax',
                            'ax_abs',
                            'credib',
                            'dx',
                            'dy',
                            'dy_corr',
                            'fused',
                            'id',
                            'invttc',
                            'lane',
                            'mov_dir',
                            'mov_state',
                            'power',
                            'radar_conf',
                            'radar_id',
                            'range',
                            'refl_id',
                            'secondary',
                            'time',
                            'tr_state',
                            'ttc',
                            'video_conf',
                            'video_id',
                            'vx',
                            'vx_abs',
                            'width'),
  fill_flc20_raw_tracks  : ('angle',
                            'angle_left',
                            'angle_right',
                            'blinker',
                            'brake_light',
                            'dx',
                            'dy',
                            'dy_left',
                            'dy_right',
                            'id',
                            'invttc',
                            'lane',
                            'mov_dir',
                            'mov_state',
                            'obj_type',
                            'range',
                            'time',
                            'tr_state',
                            'ttc',
                            'vx',
                            'width'),
  calc_mb79_raw_tracks   : ('id',
                            'angle',
                            'range',
                            'dx',
                            'dy',
                            'vx',
                            'vy',
                            'ax',
                            'ay',
                            'obj_type',
                            'mov_state',
                            'ref_point',
                            'yaw_rate',
                            'length',
                            'width',
                            'tr_state',
                            'ttc')
}

class TestSetup(unittest.TestCase):
  " runtime environment setup of fill module(s) "
  test_modules = modules
  args = None

  @classmethod
  def setUpClass(cls):
    config, manager, manager_modules = init_dataeval(
      ['-u', cls.args.backupdir, '-m', cls.args.measurement] )
    manager.set_measurement(cls.args.measurement)
    manager.set_backup(cls.args.backupdir)
    cls.manager = manager
    cls.results = {}
    for module in cls.test_modules:
      short_module_name = module.__name__.split('.')[-1]
      short_module_name = ModuleName.create(short_module_name, '', 'aebs.fill')
      try:
        result = manager_modules.calc(short_module_name, manager)
      except (IOError, SignalGroupError, AssertionError), error:
        print 'Warning: module %s skipped' % module
        if int(cls.args.v) > 1:
          print '  reason:\n', error.message
      else:
        cls.results[module] = result
    if not cls.results:
      cls.tearDownClass()
      raise unittest.SkipTest('Warning: no module result could be calculated')
    return

  @classmethod
  def tearDownClass(cls):
    cls.manager.close()
    return


class TestFillResult(TestSetup):
  def _test_attrib_cached(self, o, name, cached=True):
    method = self.assertTrue if cached else self.assertFalse
    err_msg = 'not' if cached else 'already'
    method( name in o.__dict__, msg="attribute '%s' %s cached on %s" %(name,err_msg,o) )
    return

  def _test_attrib_loaded(self, o, name, res):
    self.assertFalse( res is None, msg="attribute '%s' of %s is None" %(name,o) )
    return

  def _test_attrib_caching(self, o, name):
    # check that attribute is not loaded (attributes are independent of each other)
    self._test_attrib_cached(o, name, cached=False)
    # load attribute
    res = getattr(o, name)
    # check result
    self._test_attrib_loaded(o, name, res)
    # check cache
    self._test_attrib_cached(o, name, cached=True)
    return

  def _test_method_caching(self, o, name):
    # skip checking if method is not cached (as methods may depend on each other)
    # load method
    res = getattr(o, name)
    # check result
    self._test_attrib_loaded(o, name, res)
    # check cache
    self._test_attrib_cached(o, name, cached=True)
    return

  def _test_attrib_dict_style_access(self, o, name):
    # get attribute
    res = o[name]
    # check result
    self._test_attrib_loaded(o, name, res)
    return

  def _test_attrib_required_properties(self, o, name):
    # skip non-necessary object attribute
    if name not in attrib_props:
      return
    # load attribute
    res = getattr(o, name)
    # get required attribute properties
    prop = attrib_props[name]
    if isinstance(prop, dict):
      for name_, prop_ in prop.iteritems():
        res_ = getattr(res, name_)
        self._test_array_props(res_, prop_, o, name+'.'+name_)
    else:
      self._test_array_props(res, prop, o, name)
    return

  def _test_array_props(self, arr, prop, o, name):
    # dtype
    self.__test_array_props_dtype(arr, prop, o, name)
    # min
    min = arr.min()
    if prop.min is not None and min is not np.ma.masked:
      self.__test_array_props_min(min, prop, o, name)
    # max
    max = np.max(arr)
    if prop.max is not None and max is not np.ma.masked:
      self.__test_array_props_max(arr, prop, o, name)
    return

  def __test_array_props_dtype(self, arr, prop, o, name):
    self.assertTrue( np.issubdtype(arr.dtype, prop.dtype),
                     msg="dtype %s of attribute '%s' of %s differs from required %s"
                         %(arr.dtype, name, o, prop.dtype) )
    return

  def __test_array_props_min(self, minimum, prop, o, name):
    self.assertTrue( np.all(minimum >= prop.min),
                     msg="min %s of attribute '%s' of %s is below limit %s"
                         %(minimum, name, o, prop.min) )
    return

  def __test_array_props_max(self, maximum, prop, o, name):
    self.assertTrue( np.all(maximum <= prop.max),
                     msg="max %s of attribute '%s' of %s is above limit %s"
                         %(maximum, name, o, prop.max) )
    return

  def _test_obj_type(self, o, name, obj, required_type=None):
    o_type = type(obj)
    self.assertTrue( o_type is required_type,
                     msg="attribute %s of %s is of type %s" %(name,o,o_type) )
    if required_type is np.ma.MaskedArray:
      mask_size = obj.mask.size
      self.assertTrue( mask_size == o.time.size,
                       msg="attribute %s of %s: invalid mask size %d" %(name,o,mask_size) )
    return

  def _test_composite_attribute_join(self, o, name, attrib):
    join_wo_args = attrib.join()
    self.assertTrue( isinstance(join_wo_args, np.ma.MaskedArray),
                     msg="composite attribute %s of %s: join results inconsistent class" %(name,o) )
    self.assertTrue( join_wo_args.size == o.time.size,
                     msg="composite attribute %s of %s: join results inconsistent size" %(name,o) )
    self.assertTrue( np.array_equal(attrib[0].mask, join_wo_args.mask),
                     msg="composite attribute %s of %s: join results inconsistent mask" %(name,o) )
    join_w_def_mapping = attrib.join(mapping=attrib.mapping)
    self.assertTrue( np.array_equal(join_wo_args.mask, join_w_def_mapping.mask),
                     msg="composite attribute %s of %s: mask differs from default mapping" %(name,o) )
    self.assertTrue( np.array_equal(join_wo_args.compressed(), join_w_def_mapping.compressed()),
                     msg="composite attribute %s of %s: data differs from default mapping" %(name,o) )
    self.assertTrue( np.array_equal(join_wo_args.compressed(), join_w_def_mapping.compressed()),
                     msg="composite attribute %s of %s: data differs from default mapping" %(name,o) )
    return

  def _test_attribs_mask_same_in_object(self, o, names):
    lastname = None
    lastmask = None
    for name in names:
      # load attribute
      res = getattr(o, name)
      if not hasattr(res, 'mask'):
        continue
      if lastmask is None:
        lastmask = res.mask
        lastname = name
        continue
      self.assertTrue( np.array_equal(lastmask[:-1], res.mask[:-1]), # last value might be different if recording ended during message burst
                       msg="attribute %s of %s #%d: mask mismatch with %s at %s" %(name, o, o._id, lastname, o.time[lastmask[:-1]!=res.mask[:-1]]) )
    return

  def _test_tracking_state_valid_agrees_mask(self, o):
    " data should not be masked where object tracking state is valid "
    valid = o.tr_state.valid
    self.assertTrue( not np.any(valid.mask[valid.data]),
                     msg="problem with %s tracking state's `valid` attribute" %(o))
    return

  def _test_arr_size_agrees_obj_time_size(self, o, name, res):
    self.assertEqual( res.size, o.time.size,
                      msg="attribute %s size %d of %s differs from required %d"
                          %(name,res.size,o,o.time.size) )
    return

  @staticmethod
  def attr_identical(original, rescaled, agree=True):
    if isinstance(rescaled, tuple):
      conds = [ v_ is v for v_,v in zip(rescaled, original) ]
      cond = all(conds) if agree else not any(conds)
    else:
      cond = rescaled is original
      cond = cond if agree else not cond
    return cond

  @staticmethod
  def attr_equal(original, rescaled, agree=True):
    if isinstance(rescaled, tuple):
      conds = [ np.array_equal(v_, v) for v_,v in zip(rescaled, original) ]
      cond = all(conds) if agree else not any(conds)
    else:
      cond = np.array_equal(rescaled, original)
      cond = cond if agree else not cond
    return cond

  @staticmethod
  def attr_size(rescaled, size, agree=True):
    if isinstance(rescaled, tuple):
      conds = [ v.size == size for v in rescaled ]
      cond = all(conds) if agree else not any(conds)
    else:
      cond = rescaled.size == size
      cond = cond if agree else not cond
    return cond


class TestFlr20Flc20Raw(TestFillResult):
  def test_ids(self):
    for objs in self.results.itervalues():
      for id, o in objs.iteritems():
        self.assertTrue( np.all( (id == o.id) & ~o.id.mask),
                         msg="ids inconsistent with %d on %s" %(id,o) )
    return

  def test__attribs_caching__should_run_first(self):
    # REMARK: this needs to run first, before any test (ensured by alphabetical order)
    for objs in self.results.itervalues():
      for o in objs.itervalues():
        for name in o._attribs:
          self._test_attrib_caching(o, name)
    return

  def test_methods_caching(self):
    for objs in self.results.itervalues():
      for o in objs.itervalues():
        for name in o._methods:
          self._test_method_caching(o, name)
    return

  def test_attribs_dict_style_access(self):
    for objs in self.results.itervalues():
      for o in objs.itervalues():
        for name in o._attribs:
          self._test_attrib_dict_style_access(o, name)
    return

  def test_methods_required_properties(self):
    for objs in self.results.itervalues():
      for o in objs.itervalues():
        for name in o._methods:
          self._test_attrib_required_properties(o, name)
    return

  def test_attribs_type_maskedarray(self):
    for objs in self.results.itervalues():
      for o in objs.itervalues():
        for name in o._attribs:
          res = getattr(o, name)
          self._test_obj_type(o, name, res, required_type=np.ma.MaskedArray)
    return

  def test_methods_type_maskedarray_except_time(self):
    for objs in self.results.itervalues():
      for o in objs.itervalues():
        for name in o._methods:
          # load attribute
          res = getattr(o, name)
          if name == 'time':
            self._test_obj_type(o, name, res, required_type=np.ndarray)
          else:
            if isinstance(res, tuple):
              # composite attribute
              for v in res:
                self._test_obj_type(o, name, v, required_type=np.ma.MaskedArray)
            else:
              self._test_obj_type(o, name, res, required_type=np.ma.MaskedArray)
    return

  def test_composite_attribute_join(self):
    for objs in self.results.itervalues():
      for o in objs.itervalues():
        for name in o._methods:
          attrib = getattr(o, name)
          if name != 'tr_state' and isinstance(attrib, tuple):
            self._test_composite_attribute_join(o, name, attrib)
    return

  def test_attribs_mask_same_per_object(self):
    for objs in self.results.itervalues():
      for o in objs.itervalues():
        self._test_attribs_mask_same_in_object(o, o._attribs)
    return

  def test_tracking_state_valid_agrees_mask(self):
    for module, objs in self.results.iteritems():
      req_method_names = self.test_modules[module]
      if 'tr_state' not in req_method_names:
        continue # targets don't have `tr_state` attribute
      for o in objs.itervalues():
        self._test_tracking_state_valid_agrees_mask(o)
    return

  def test_alive_intervals(self):
    for module, objs in self.results.iteritems():
      if module not in (fill_flr20_raw_tracks, fill_flc20_raw_tracks):
        continue # targets don't have this attribute
      for o in objs.itervalues():
        self._test_alive_intervals(o)
    return

  def _test_alive_intervals(self, o):
    intervals = o.alive_intervals
    self.assertTrue( isinstance(intervals, cIntervalList),
                     msg='%s is of type %s' %(o,type(o)) )
    mask = intervalsToMask(intervals, o.time.size)
    self.assertTrue( np.array_equal(mask, o.tr_state.valid.data),
                     msg='%s `alive_intervals` does not fit `tr_state.valid`' %o)

  def test_sleeping_counter(self):
    for module, objs in self.results.iteritems():
      if 'targets' in module.__name__:
        continue # targets don't have this attribute
      for o in objs.itervalues():
        self._test_sleeping_counter(o)
    return

  def _test_sleeping_counter(self, o):
    sleeping_counter = o.sleeping_counter
    self.assertTrue( isinstance(sleeping_counter, np.ma.MaskedArray),
                     msg='%s is of type %s' %(o,type(o)) )
    sleeping_mask = ~o.tr_state.measured
    if np.any(sleeping_mask):
      self.assertTrue( np.all(sleeping_counter[sleeping_mask] > 0),
                       msg='%s %d `sleeping_counter` does not fit `tr_state.measured`' %(o, o._id))
    return

  def test_attribs_size_agrees_obj_time_size(self):
    for objs in self.results.itervalues():
      for o in objs.itervalues():
        for name in o._attribs:
          res = getattr(o, name)
          self._test_arr_size_agrees_obj_time_size(o, name, res)
    return

  def test_object_time_agrees_scaletime(self):
    for objs in self.results.itervalues():
      for o in objs.itervalues():
        self.assertTrue( o.time is objs.time,
                          msg="object %s scaletime doesn't reference original" %o )
    return

  def test_scaletime_type_ndarray(self):
    for objs in self.results.itervalues():
      self._test_obj_type(objs.__class__, 'time', objs.time, required_type=np.ndarray)
    return

  def test_required_methods(self):
    for module, objs in self.results.iteritems():
      req_method_names = self.test_modules[module]
      for req_method_name in req_method_names:
        for o in objs.itervalues():
          self.assertTrue( hasattr(o, req_method_name),
                           msg="required method '%s' missing %s" %(req_method_name,o) )
    return

  def test_empty_message_masks(self):
    id, scaleTime, source, optgroups = [None] * 4
    messageMasks = {}
    dirCorr = 1
    with self.assertRaises(AssertionError):
      fill_flr20_raw_tracks.TrackFromMessage(id, scaleTime, messageMasks, source, optgroups, dirCorr)
    return

  def test_rescale_same_time(self):
    for objs in self.results.itervalues():
      newobjs = objs.rescale(objs.time)
      for id, oo in newobjs.iteritems():
        o = objs[id]
        # check if rescaled object is the same as original
        self.assertFalse(o is oo, msg="rescaled object %s is same as original" %oo)
        # check rescaled object's time
        self.assertTrue(oo.time is o.time, msg="rescaled object %s time error" %oo)
        for name in o._attribs + o._methods:
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
    for module, objs in self.results.iteritems():
      try:
        otherScaleTime = self._get_different_time(objs.time)
      except ValueError:
        self.skipTest("No other time scale found for %s module" %module)
      newobjs = objs.rescale(otherScaleTime)
      for id, oo in newobjs.iteritems():
        o = objs[id]
        # check if rescaled object is the same as original
        self.assertFalse(o is oo, msg="rescaled object %s is same as original" %oo)
        # check rescaled object's time
        self.assertTrue(oo.time is otherScaleTime, msg="rescaled object %s time error" %oo)
        for name in o._attribs + o._methods:
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

  def _get_different_time(self, time):
    for objs in self.results.itervalues():
      othertime = objs.time
      if(    othertime is not time
         and othertime.size != time.size
         and not np.array_equal(othertime, time) ):
        return othertime
    raise ValueError

if __name__ == '__main__':
  import sys

  args = parse_arguments(
    # measpath=r'\\file\Messdat\DAS\EnduranceRun\H566PP\2013-04-09\H566_2013-04-09_06-52-13.mf4',
    # measpath=r'\\file\Messdat\DAS\EnduranceRun\H566PP\2013-07-05\2013-07-05-17-32-23.MF4', # recording ended during CAN message burst (target 4 affected)
    # measpath=r'\\file\Messdat\DAS\EnduranceRun\H05_2604\2012-10-05\comparison_all_sensors_2012-10-05_17-17-08.MF4'
    # measpath=r'\\file\messdat\das\RaIL\22.01.2014_ManRun_015.mdf' # RAIL signals
    # measpath=r'\\file\messdat\das\Customer\Ford\H566PP\2014-03-20_Boxberg\2014-03-20_13-35-09_covi_H566.mf4' # modified dbc signals
    measpath=r'\\corp.knorr-bremse.com\str\measure1\DAS\Turning_Assist\internal\06xB365\2016-06-21_MB79_SDS_Tracker_300detections\B365__2016-06-21_15-52-12.MF4'  # MB79 test
  )
  TestSetup.args = args
  unittest.main(argv=[sys.argv[0]], verbosity=args.v)
