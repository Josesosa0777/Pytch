import unittest
import os
import shutil
import time
import fnmatch

import numpy

import measproc
from measproc.batchsqlite import Batch
from measproc.Report import cIntervalListReport
from measproc.IntervalList import cIntervalList

db_name = 'batch.db'
dir_name = 'files'
labels = {'foo': (False, ['bar', 'baz'])}
tags = {'spam': ['egg', 'eggegg']}
results = 'passed', 'failed', 'error', 'inconc', 'none'
quanames = {'pyon': ['atomsk', 'naota']}
measurement = 'D:/measurement/dataeval-test/CVR3_B1_2011-02-10_16-53_020.mdf'
start = time.strftime('%Y-%m-%d %H:%M:%S')

title = 'foo is never bar'

intervals = {(13,   78): 'bar', 
             (113, 182): 'baz'}

class_name = 'searchFoo.cSearch'
param = 'foo="bar"'
version = '0.1.0'
result = 'none'
type = 'measproc.cFileReport'
entry_tags = 'egg',

entryid = -1

measproc.Report.RepDir = dir_name

def setUpModule():
  global entryid, report

  batch = Batch(db_name, dir_name, labels, tags, results, quanames)
  batch.set_start(start)
  batch.set_measurement(measurement, True)
  batch.set_module(class_name, param, version)

  # init report
  time = numpy.arange(0, 600, 20e-3)
  exclusive, votes = labels.values()[0]

  intervallist = cIntervalList(time)
  report = cIntervalListReport(intervallist, title, votes)
  report.ReportAttrs['Comment'] = 'spam'

  for interval, vote in intervals.iteritems():
    report.addInterval(interval)
    report.vote(interval, vote)
    report.setComment(interval, 'spamspam')

  entryid = batch.add_entry(report, 
                            result, 
                            entry_tags)
  batch.save()
  return

class BuildBatch(unittest.TestCase):
  def setUp(self):
    self.batch = Batch(db_name, dir_name, labels, tags, results, quanames)
    self.batch.set_measurement(measurement, True)
    self.basename = os.path.basename(measurement)
    return

  def test_get_labelgroup(self):
    groupname = 'foo'
    _exclusive, _labels = labels[groupname]
    __exclusive, __labels = self.batch.get_labelgroup(groupname)
    self.assertFalse(__exclusive)
    self.assertSetEqual(set(__labels), set(_labels))
    return

  def test_wake_report(self):
    waked = self.batch.wake_entry(entryid)
    
    # check interval votes
    for interval in intervals:
      self.assertSetEqual(report.getIntervalVotes(interval), 
                           waked.getIntervalVotes(interval))

  def test_filter_tag(self):
    entids = set([entryid])
    tag, = entry_tags
    self.assertSetEqual(set(self.batch.filter(tag=tag)), entids)
    return

  def test_filter_value(self):
    entids = set([entryid])
    self.assertSetEqual(set(self.batch.filter(param=param)), entids)
    return

  def test_filter_module(self):
    entids = set([entryid])
    self.assertSetEqual(set(self.batch.filter(class_name=class_name)), entids)
    self.assertSetEqual(set(self.batch.filter(param=param)), entids)
    self.assertSetEqual(set(self.batch.filter(class_name=class_name, param=param)), 
                        entids)
    return

  def test_filter_measurement(self):
    entids = set([entryid])
    self.assertSetEqual(set(self.batch.filter(measurement=self.basename)), entids)
    return

  def test_filter_start(self):
    entids = set([entryid])
    self.assertSetEqual(set(self.batch.filter(start=start)), entids)
    return

  def test_filter_start_measurement(self):
    entids = set([entryid])
    self.assertSetEqual(set(self.batch.filter(start=start, 
                                              measurement=self.basename)),
                        entids)
    return

  def test_filter_type(self):
    entids = set([entryid])
    self.assertSetEqual(set(self.batch.filter(type=type)), entids)
    return

  def test_filter_result(self):
    entids = set([entryid])
    self.assertSetEqual(set(self.batch.filter(result=result)), entids)
    return

  def test_filter_tag_measurement(self):
    entids = set([entryid])
    tag, = entry_tags
    self.assertSetEqual(set(self.batch.filter(measurement=self.basename, 
                                              tag=tag)),
                        entids)
    return

  def test_filter_module_measurement(self):
    entids = set([entryid])
    tag, = entry_tags
    self.assertSetEqual(set(self.batch.filter(measurement=self.basename,
                                              class_name=class_name)),
                        entids)
    return

  def test_filter_invalid_keyword(self):
    with self.assertRaises(AssertionError):
      self.batch.filter(foo=42)
    return

  def test_filter_extra_invalid_keyword(self):
    with self.assertRaises(AssertionError):
      self.batch.filter(type='none', foo=42)
    return

  def test_get_measurement(self):
    meas, local = self.batch.get_measurement()
    self.assertEqual(meas, measurement)
    self.assertTrue(local)
    return

  def test_get_last_entries(self):
    last_entryid, = self.batch.get_last_entries(class_name, param, type)
    self.assertEqual(entryid, last_entryid)
    return

  def test_query(self):
    q = self.batch.query("SELECT * FROM entries")
    self.assertTrue(isinstance(q, list) and len(q) > 0)
    return
  
  def test_query_fetchone(self):
    q = self.batch.query("SELECT * FROM entries", fetchone=True)
    self.assertTrue(isinstance(q, tuple) and len(q) > 0)
    return
  
  def test_query_param(self):
    q = self.batch.query("SELECT * FROM entries WHERE comment=?", "spam")
    self.assertTrue(isinstance(q, list) and len(q) > 0)
    return

  def test_query_param_fetchone(self):
    q = self.batch.query("SELECT * FROM entries WHERE comment=?", "spam",
                         fetchone=True)
    self.assertTrue(isinstance(q, tuple) and len(q) > 0)
    return

  def test_query_namedparam(self):
    q = self.batch.query("SELECT * FROM entries WHERE comment=:c", c="spam")
    self.assertTrue(isinstance(q, list) and len(q) > 0)
    return

  def test_query_namedparam_fetchone(self):
    q = self.batch.query("SELECT * FROM entries WHERE comment=:c", c="spam",
                         fetchone=True)
    self.assertTrue(isinstance(q, tuple) and len(q) > 0)
    return

  def test_query_namedparam_invalid(self):
    with self.assertRaises(AssertionError):
      q = self.batch.query("SELECT * FROM entries WHERE comment=:fetchone",
                           fetchone=True)
    return

  def test_query_mixedparam_invalid(self):
    with self.assertRaises(AssertionError):
      q = self.batch.query("SELECT * FROM entries "
                           "WHERE comment=:c AND measurementid>?", 0, c="spam")
    return

  def tearDown(self):
    self.batch.save()
    return

def tearDownModule():
  os.remove(db_name)
  shutil.rmtree(dir_name)
  for name in os.listdir('.'):
    if fnmatch.fnmatch(name, '%s*.xml' %title):
      os.remove(name)
  return

if __name__ == '__main__':
  unittest.main()
