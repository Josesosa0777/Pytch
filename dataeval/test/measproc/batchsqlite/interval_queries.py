import os
import time
import shutil
from unittest import TestCase, main

import numpy

from measproc.batchsqlite import Batch, RESULTS
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList

class BuildBatch(TestCase):
  labels = {'foo': (False, ['bar', 'baz'])}
  tags = {'spam': ['egg', 'eggegg']}
  quanames = {'pyon': ['atomsk', 'naota']}

  @classmethod
  def setUpClass(cls):
    cls.batch = Batch('foo.db', 'files', cls.labels, cls.tags, RESULTS,
                      cls.quanames)
    cls.start = time.strftime(Batch.TIME_FORMAT)
    cls.batch.set_start(cls.start)
    cls.batch.set_measurement('bar.mdf', True)
    cls.batch.set_module('searchFoo.cSearch', 'foo="bar"', '0.1.0')

    
    cls.title = 'foo is bar'
    cls.time = numpy.arange(0, 1, 1e-2)
    report = Report(cIntervalList(cls.time), cls.title,
                    votes=cls.batch.get_labelgroups('foo'),
                    names=cls.batch.get_quanamegroups('pyon'))
    
    cls.intervals = [(0, 3), (12, 15)]
    for interval in cls.intervals:
      idx = report.addInterval(interval)
      report.vote(idx, 'foo', 'bar')
      report.set(idx, 'pyon', 'atomsk', 3.2)
      report.setComment(idx, 'nyaff')

    cls.entryid = cls.batch.add_entry(report)
    return

  def iter_intervals(self):
    for start, end in self.intervals:
      idx = self.get_interval_id(start, end)
      yield idx, start, end
    return

  def get_interval_id(self, start, end):
    idx, = self.batch.query('''
                            SELECT id FROM entryintervals
                            WHERE start = ? AND end = ?''', start, end,
                            fetchone=True)
    return idx

  @classmethod
  def tearDownClass(cls):
    cls.batch.save()
    os.remove(cls.batch.dbname)
    shutil.rmtree(cls.batch.dirname)
    return

class TestQueries(BuildBatch):
  def test_get_interval_attrs(self):
    for idx, start, end in self.iter_intervals():

      start_time = self.batch.get_interval_attr(idx, 'start_time')
      self.assertAlmostEqual(start_time, self.time[start])

      end_time = self.batch.get_interval_attr(idx, 'end_time')
      self.assertAlmostEqual(end_time, self.time[end-1])

      self.assertEqual(self.batch.get_interval_attr(idx, 'comment'), 'nyaff')
    return

  def test_get_interval_labels(self):
    for idx, start, end in self.iter_intervals():
      self.assertListEqual(self.batch.get_interval_labels(idx, 'foo'), ['bar'])
    return

  def test_get_interval_attr_error(self):
    attr_name = 'eggegg'
    msg = 'Invalid interval attribute name: %s' % attr_name
    for idx, start, end in self.iter_intervals():
      with self.assertRaisesRegexp(ValueError, msg):
        self.batch.get_interval_attr(idx, attr_name)
    return

class TestGetEntryId(BuildBatch):
  def test_get_entryid_by_interval(self):
    for idx, start, end in self.iter_intervals():
      self.assertEqual(self.batch.get_entryid_by_interval(idx), self.entryid)
    return

class TestGetIntervalPos(BuildBatch):
  def test_get_interval_pos(self):
    for pos, (idx, start, end) in enumerate(self.iter_intervals()):
      self.assertEqual(self.batch.get_interval_pos(idx), pos)
    return

if __name__ == '__main__':
  main()
