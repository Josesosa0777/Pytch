import unittest
import shutil
import time
import os

import numpy

from measproc.batchsqlite import Batch, RESULTS
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList

db_name = 'batch.db'
dir_name = 'files'
labels = {'foo': (False, ['bar', 'baz'])}
tags = {'spam': ['egg', 'eggegg']}
quanames = {'pyon': ['atomsk', 'naota']}
measurement = 'D:/measurement/dataeval-test/CVR3_B1_2011-02-10_16-53_020.mdf'
start = time.strftime(Batch.TIME_FORMAT)

title = 'foo is never bar'

intervals = {(13,   78): 'bar', 
             (113, 182): 'baz'}

module = 'searchFoo.cSearch'
param = 'foo="bar"'
version = '0.1.0'
result = 'none'
entry_tags = 'egg',


def setUpModule():
  batch = Batch(db_name, dir_name, labels, tags, RESULTS, quanames)
  batch.save()
  return


class TestCase(unittest.TestCase):
  def setUp(self):
    self.batch = Batch(db_name, dir_name, labels, tags, RESULTS, quanames)
    self.batch.set_start(start)
    self.batch.set_measurement(measurement, True)
    self.batch.set_module(module, param, version)
    # init report
    time = numpy.arange(0, 600, 20e-3)
    exclusive, votes = labels.values()[0]

    intervallist = cIntervalList(time)
    report = Report(intervallist, title, labels)
    report.setEntryComment('spam')

    votegroup = 'foo'
    for interval, vote in intervals.iteritems():
      intervalid = report.addInterval(interval)
      report.vote(intervalid, votegroup, vote)
      report.setComment(intervalid, 'spamspam')

    self.entryid = self.batch.add_entry(report, result, entry_tags)
    self.report = report
    return

  def test_wake_report(self):
    waked = self.batch.wake_entry(self.entryid)
    
    # check interval votes
    for intervalid in self.report.iterIntervalIds():
      self.assertDictEqual(self.report.getVotes(intervalid), 
                           waked.getVotes(intervalid))
    return

  def test_report_timestamps(self):
    self._test_report_timestamps(self.report)
    return

  def _test_report_timestamps(self, report):
    for intervalid in report.iterIntervalIds():
      batch_time = numpy.array( self._get_batch_timestamps(intervalid) )
      report_time = numpy.array(report.getTimeInterval(intervalid))
      self.assertTrue(numpy.allclose(batch_time, report_time))
    return

  def _get_batch_timestamps(self, intervalid):
    return self.batch.query("""
                            SELECT start_time, end_time FROM entryintervals
                            WHERE entryid=? AND position=?""",
                            self.entryid, intervalid, fetchone=True)

  def test_update_report_add_vote(self):
    waked = self.batch.wake_entry(self.entryid)
    for intervalid in waked.iterIntervalIds():
      waked.vote(intervalid, 'foo', 'bar')
    self.batch.update_entry(waked, self.entryid)
    updated = self.batch.wake_entry(self.entryid)
    for intervalid in self.report.iterIntervalIds():
      self.assertDictEqual(updated.getVotes(intervalid), 
                           waked.getVotes(intervalid))
    return

  def _rm_report_interval(self):
    waked = self.batch.wake_entry(self.entryid)
    waked.rmInterval(0)
    self.batch.update_entry(waked, self.entryid)
    updated = self.batch.wake_entry(self.entryid)
    return waked, updated

  def test_update_report_rm_interval_intervals(self):
    waked, updated = self._rm_report_interval()
    self.assertListEqual(waked.intervallist.Intervals, 
                         updated.intervallist.Intervals)
    return

  def test_update_report_rm_interval_votes(self):
    waked, updated = self._rm_report_interval()
    self.assertDictEqual(waked.getVotes(0), updated.getVotes(0))
    return

  def test_update_report_rm_interval_removed_votes(self):
    waked, updated = self._rm_report_interval()
    self.assertEqual(len(updated.votes), 1)
    return

  def test_update_report_rm_interval_timestamps(self):
    waked, updated = self._rm_report_interval()
    self._test_report_timestamps(waked)
    return

  def _add_report_interval(self):
    waked = self.batch.wake_entry(self.entryid)
    intervalindex = waked.addInterval((42, 56))
    waked.vote(intervalindex, 'foo', 'bar')
    self.batch.update_entry(waked, self.entryid)
    updated = self.batch.wake_entry(self.entryid)
    return waked, updated, intervalindex

  def test_update_report_add_interval_votes(self):
    waked, updated, intervalindex = self._add_report_interval()
    self.assertDictEqual(waked.getVotes(intervalindex),
                         updated.getVotes(intervalindex))
    return

  def test_update_report_add_interva_intervals(self):
    waked, updated, intervalindex = self._add_report_interval()
    self.assertListEqual(waked.intervallist.Intervals,
                         updated.intervallist.Intervals)
    return

  def test_update_report_add_interva_timestamps(self):
    waked, updated, intervalindex = self._add_report_interval()
    self._test_report_timestamps(waked)
    return

  def _add_existed_report_interval(self):
    waked = self.batch.wake_entry(self.entryid)
    intervalindex = waked.addInterval( (13, 78) )
    waked.vote(intervalindex, 'foo', 'bar')
    self.batch.update_entry(waked, self.entryid)
    updated = self.batch.wake_entry(self.entryid)
    return waked, updated, intervalindex

  def test_update_report_add_existed_interval_votes(self):
    waked,\
    updated,\
    intervalindex = self._add_existed_report_interval()
    self.assertDictEqual(waked.getVotes(intervalindex),
                         updated.getVotes(intervalindex))
    return

  def test_update_report_add_existed_interva_intervals(self):
    waked,\
    updated,\
    intervalindex = self._add_existed_report_interval()
    self.assertListEqual(waked.intervallist.Intervals,
                         updated.intervallist.Intervals)
    return

  def test_update_report_add_existed_interval_timestamps(self):
    waked,\
    updated,\
    intervalindex = self._add_existed_report_interval()
    self._test_report_timestamps(waked)
    return

  def tearDown(self):
    self.batch.save()
  pass

def tearDownModule():
  os.remove(db_name)
  shutil.rmtree(dir_name)
  return

if __name__ == '__main__':
  unittest.main()
