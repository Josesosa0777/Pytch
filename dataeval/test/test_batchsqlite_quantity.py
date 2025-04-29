import unittest
import shutil
import time
import os

import numpy

from measproc.batchsqlite import Batch, RESULTS
from measproc.IntervalList import cIntervalList
from measproc.report2 import Report

db_name = 'batch.db'
dir_name = 'files'
labels = {'foo': (False, ['bar', 'baz'])}
tags = {'spam': ['egg', 'eggegg']}
quanames = {'pyon': ['atomsk', 'naota']}
measurement = 'c:/KBData/measurement/test/CVR3_B1_2011-02-10_16-53_020.mdf'
start = time.strftime(Batch.TIME_FORMAT)

title = 'foo is never bar'
intervals = {
  ( 13,  78): ('pyon', 'atomsk', 5.6), 
  (113, 182): ('pyon', 'naota',  4.2),
}

module = 'searchFoo.cSearch'
param = 'foo="bar"'
version = '0.1.0'
result = 'none'
entry_tags = 'egg',


def setUpModule():
  batch = Batch(db_name, dir_name, labels, tags, RESULTS, quanames)
  batch.save()
  return

def tearDownModule():
  os.remove(db_name)
  shutil.rmtree(dir_name)
  return


class TestCase(unittest.TestCase):
  def setUp(self):
    self.batch = Batch(db_name, dir_name, labels, tags, RESULTS, quanames)
    self.batch.set_start(start)
    self.batch.set_measurement(measurement, True)
    self.batch.set_module(module, param, version)

    time = numpy.arange(0, 2*numpy.pi, 20e-3)
    intervallist = cIntervalList(time)
    self.quantity = Report(intervallist, title, names=quanames)

    for interval, (groupname, valuename, value) in intervals.iteritems():
      intervalid = self.quantity.addInterval(interval)
      self.quantity.set(intervalid, groupname, valuename, value)

    self.entryid = self.batch.add_entry(self.quantity, result, entry_tags)
    return

  def tearDown(self):
    self.batch.save()
    return

  def test_wake_quantity(self):
    waked = self.batch.wake_entry(self.entryid)

    for intervalid in self.quantity.iterIntervalIds():
      self.assertDictEqual(self.quantity.getQuantities(intervalid),
                           waked.getQuantities(intervalid))
    return

  def test_quantity_timestamps(self):
    self._test_quantity_timestamps(self.quantity)
    return

  def _test_quantity_timestamps(self, quantity):
    for intervalid in quantity.iterIntervalIds():
      batch_start_time,\
      batch_end_time = self._get_batch_timestamps(intervalid)
      quantity_start_time,\
      quantity_end_time  = quantity.getTimeInterval(intervalid)
      self.assertAlmostEqual(batch_start_time, quantity_start_time)
      self.assertAlmostEqual(batch_end_time, quantity_end_time)
    return

  def _get_batch_timestamps(self, intervalid):
    return self.batch.query("""
                            SELECT start_time, end_time FROM entryintervals
                            WHERE entryid=? AND position=?""",
                            self.entryid, intervalid, fetchone=True)

  def test_update_quantity_set(self):
    waked = self.batch.wake_entry(self.entryid)
    for intervalid in waked.iterIntervalIds():
      waked.set(intervalid, 'pyon', 'atomsk', 3.2)
    self.batch.update_entry(waked, self.entryid)
    updated = self.batch.wake_entry(self.entryid)
    for intervalid in self.quantity.iterIntervalIds():
      self.assertDictEqual(updated.getQuantities(intervalid),
                           waked.getQuantities(intervalid))
    return

  def test_update_quantity_rm_interval_intervals(self):
    waked, updated = self._rm_quantity_interval()
    self.assertListEqual(waked.intervallist.Intervals, 
                         updated.intervallist.Intervals)
    return

  def _rm_quantity_interval(self):
    waked = self.batch.wake_entry(self.entryid)
    waked.rmInterval(0)
    self.batch.update_entry(waked, self.entryid)
    updated = self.batch.wake_entry(self.entryid)
    return waked, updated

  def test_update_quantity_rm_interval_quantities(self):
    waked, updated = self._rm_quantity_interval()
    self.assertDictEqual(waked.getQuantities(0), updated.getQuantities(0))
    return

  def test_update_quantity_rm_interval_removed_qauntity(self):
    waked, updated = self._rm_quantity_interval()
    self.assertEqual(len(updated._quantities), 1)
    return
    
  def test_update_quantity_rm_interval_timestamp(self):
    waked, updated = self._rm_quantity_interval()
    self._test_quantity_timestamps(updated)
    return

  def _add_quantity_interval(self):
    waked = self.batch.wake_entry(self.entryid)
    intervalindex = waked.addInterval((42, 56))
    waked.set(intervalindex, 'pyon', 'naota', 7.1)
    self.batch.update_entry(waked, self.entryid)
    updated = self.batch.wake_entry(self.entryid)
    return waked, updated, intervalindex

  def test_update_quantity_add_interval_quantities(self):
    waked, updated, intervalindex = self._add_quantity_interval()
    self.assertDictEqual(waked.getQuantities(intervalindex),
                         updated.getQuantities(intervalindex))
    return

  def test_update_quantity_add_interval_intervals(self):
    waked, updated, intervalindex = self._add_quantity_interval()
    self.assertListEqual(waked.intervallist.Intervals, 
                         updated.intervallist.Intervals)
    return

  def test_update_quantity_add_interval_timestamp(self):
    waked, updated, intervalindex = self._add_quantity_interval()
    self._test_quantity_timestamps(updated)
    return

  def _add_existed_quantity_interval(self):
    waked = self.batch.wake_entry(self.entryid)
    intervalindex = waked.addInterval((13, 78))
    waked.set(intervalindex, 'pyon', 'atomsk', 9.1)
    self.batch.update_entry(waked, self.entryid)
    updated = self.batch.wake_entry(self.entryid)
    return waked, updated, intervalindex

  def test_update_quantity_add_existed_interval_quantities(self):
    waked, updated, intervalindex = self._add_existed_quantity_interval()
    self.assertDictEqual(waked.getQuantities(intervalindex),
                         updated.getQuantities(intervalindex))
    return

  def test_update_quantity_add_existed_interval_intervals(self):
    waked, updated, intervalindex = self._add_existed_quantity_interval()
    self.assertListEqual(waked.intervallist.Intervals, 
                         updated.intervallist.Intervals)
    return

  def test_update_quantity_add_existed_interval_timestamps(self):
    waked, updated, intervalindex = self._add_existed_quantity_interval()
    self._test_quantity_timestamps(updated)
    return

  def _change_quantity(self):
    intervalindex = 0
    waked = self.batch.wake_entry(self.entryid)
    waked.set(intervalindex, 'pyon', 'atomsk', 8.65)
    self.batch.update_entry(waked, self.entryid)
    updated = self.batch.wake_entry(self.entryid)
    return waked, updated, intervalindex
    
  def test_update_quantity_change_interval_quantities(self):
    waked, updated, intervalindex = self._change_quantity()
    self.assertDictEqual(waked.getQuantities(intervalindex),
                         updated.getQuantities(intervalindex))
    return

if __name__ == '__main__':
  unittest.main()
