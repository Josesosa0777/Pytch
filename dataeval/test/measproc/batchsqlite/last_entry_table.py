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
start = '2013-01-01 00:00:01'

title = 'foo is never bar'

intervals = {(13,   78): 'bar',
             (113, 182): 'baz'}

class_name = 'searchFoo.cSearch'
param = 'foo="bar"'
version = '0.1.0'
result = 'none'
type = 'measproc.cFileReport'
entry_tags = 'egg',

measproc.Report.RepDir = dir_name

class TestAddNewEntries(unittest.TestCase):
  def setUp(self):
    self.batch = Batch(db_name, dir_name, labels, tags, results, quanames)
    self.batch.set_start(start)
    self.batch.set_measurement(measurement, True)
    self.batch.set_module(class_name, param, version)
    self.basename = os.path.basename(measurement)

    # init report
    time = numpy.arange(0, 600, 20e-3)
    exclusive, votes = labels.values()[0]

    intervallist = cIntervalList(time)
    self.report = cIntervalListReport(intervallist, title, votes)
    self.report.ReportAttrs['Comment'] = 'spam'

    for interval, vote in intervals.iteritems():
      self.report.addInterval(interval)
      self.report.vote(interval, vote)
      self.report.setComment(interval, 'spamspam')

    self.entryids = [ self.batch.add_entry(self.report, result, entry_tags), ]
    return

  def test_add_entry_diff_meas_basename(self):
    measurement = 'C:/CVR3_B1_2011-02-10_16-53_020_temp.mdf'
    self.batch.set_measurement(measurement, False)
    self.entryids.append(self.batch.add_entry(self.report, result, entry_tags))
    ids = self._get_last_entries(self.entryids[-1])
    self.assertEqual(ids, [(self.entryids[-1], )])
    return

  def _get_last_entries(self, entryid):
    return self.batch.query('''SELECT last_entries.id from last_entries
                            WHERE  last_entries.id = ?''', entryid)

  def tearDown(self):
    self.batch.save()
    os.remove(db_name)
    shutil.rmtree(dir_name)
    return

  def test_add_entry_diff_entry_title(self):
    time = numpy.arange(0, 600, 20e-3)
    intervallist = cIntervalList(time)
    exclusive, votes = labels.values()[0]
    report = cIntervalListReport(intervallist, 'New_title', votes)
    report.ReportAttrs['Comment'] = 'spam'

    for interval, vote in intervals.iteritems():
      report.addInterval(interval)
      report.vote(interval, vote)
      report.setComment(interval, 'spamspam')

    self.entryids.append(self.batch.add_entry(report, result, entry_tags))
    ids = self._get_last_entries(self.entryids[-1])
    self.assertEqual(ids, [(self.entryids[-1], )])
    return

  def test_add_entry_diff_module_class(self):
    classname = 'searchEgg.cSearch'
    self.batch.set_module(classname, param, version)
    self.entryids.append(self.batch.add_entry(self.report, result, entry_tags))
    ids = self._get_last_entries(self.entryids[-1])
    self.assertEqual(ids, [(self.entryids[-1], )])
    return

  def test_add_entry_diff_module_param(self):
    new_param = 'foo="baz"'
    self.batch.set_module(class_name, new_param, version)
    self.entryids.append(self.batch.add_entry(self.report, result, entry_tags))
    ids = self._get_last_entries(self.entryids[-1])
    self.assertEqual(ids, [(self.entryids[-1], )])
    return

  def test_add_entry_diff_result_older_start(self):
    self.batch.set_start('2000-01-01 00:00:01')
    self.entryids.append(self.batch.add_entry(self.report, result, entry_tags))
    time = numpy.arange(0, 600, 20e-3)
    intervallist = cIntervalList(time)
    exclusive, votes = labels.values()[0]
    report = cIntervalListReport(intervallist, title, votes)
    report.ReportAttrs['Comment'] = 'spam'

    for interval, vote in intervals.iteritems():
      report.addInterval(interval)
      report.vote(interval, vote)
      report.setComment(interval, 'spamspam')
    self.entryids.append(self.batch.add_entry(report, 'passed', entry_tags))
    ids = self._get_last_entries(self.entryids[-1])
    self.assertEqual(ids, [])
    ids = self._get_last_entries(self.entryids[0])
    self.assertEqual(ids, [(self.entryids[0], )])
    return

  def test_add_entry_diff_result_newer_start(self):
    self.batch.set_start('2100-01-01 00:00:01')
    time = numpy.arange(0, 600, 20e-3)
    intervallist = cIntervalList(time)
    exclusive, votes = labels.values()[0]
    report = cIntervalListReport(intervallist, title, votes)
    report.ReportAttrs['Comment'] = 'spam'

    for interval, vote in intervals.iteritems():
      report.addInterval(interval)
      report.vote(interval, vote)
      report.setComment(interval, 'spamspam')
    self.entryids.append(self.batch.add_entry(report, 'passed', entry_tags))
    ids = self._get_last_entries(self.entryids[-1])
    self.assertEqual(ids, [(self.entryids[-1], )])
    ids = self._get_last_entries(self.entryids[0])
    self.assertEqual(ids, [])
    return

if __name__ == '__main__':
  unittest.main()
