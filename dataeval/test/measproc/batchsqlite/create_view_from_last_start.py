import os
import time
import shutil
from unittest import TestCase, main

import numpy

from measproc.batchsqlite import Batch, _add_measurement, RESULTS
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList
from measparser.iParser import iParser

class BuildBatch(TestCase):
  labels = {'foo': (False, ['bar', 'baz'])}
  tags = {'spam': ['egg', 'eggegg']}
  quanames = {'pyon': ['atomsk', 'naota']}
  reports = []

  report = dict(start='2013-09-13 09:45:53', meas='2013.09.12_14.52.43.mdf',
                local=True, class_name='searchFoo.cSearch', param='foo="bar"',
                version='0.1.0', title='foo is never bar',
                time=numpy.arange(0, 1, 1e-2),
                events={(0, 12): {'labels': [('foo', 'bar')],
                                  'quas': [('pyon', 'atomsk', 42.0)]}})

  @classmethod
  def setUpClass(cls):
    cls.batch = Batch('foo.db', 'files', cls.labels, cls.tags, RESULTS,
                      cls.quanames)
    for report in cls.reports:
      cls.batch.set_start(report['start'])
      cls.batch.set_module(report['class_name'], report['param'],
                           report['version'])
      cls.batch.set_measurement(report['meas'], report['local'])

      label_groups = set()
      qua_groups = set()
      for interval, values in report['events'].iteritems():
        label_groups.update(lg for lg, l in values['labels'])
        qua_groups.update(qg for qg, q, v in values['quas'])
      label_groups = cls.batch.get_labelgroups(*label_groups)
      qua_groups = cls.batch.get_quanamegroups(*qua_groups)

      entry = Report(cIntervalList(report['time']), report['title'],
                     votes=label_groups, names=qua_groups)
      
      for interval, values in report['events'].iteritems():
        idx = entry.addInterval(interval)
        for label_group, label in values['labels']:
          entry.vote(idx, label_group, label)
        for qua_group, qua, value in values['quas']:
          entry.set(idx, qua_group, qua, value)

      cls.batch.add_entry(entry)
    cls.intervals = cls.batch.query('SELECT id, start, end FROM entryintervals')
    return

  @classmethod
  def tearDownClass(cls):
    cls.batch.save()
    os.remove(cls.batch.dbname)
    shutil.rmtree(cls.batch.dirname)
    return


class TestLastView(BuildBatch):
  reports = []
  for start in '2013-09-13 09:45:53', '2013-09-13 09:45:54':
    report = BuildBatch.report.copy()
    report['start'] = start
    reports.append(report)

  def test_last_view(self):
    view = self.batch.create_view_from_last_start()
    result = [start for start, in self.batch.query("""
      SELECT starts.time FROM %s en
        JOIN starts ON starts.id = en.startid
    """ % view)]
    self.assertListEqual(result, [self.reports[1]['start']])
    return
  
class TestDayLimit(BuildBatch):
  reports = []
  for meas in '2013.09.12_14.52.43.mdf',\
              '2013.09.13_14.52.43.mdf',\
              '2013.09.14_14.52.43.mdf',\
              '2013.09.15_14.52.43.mdf':
    report = BuildBatch.report.copy()
    report['meas'] = meas
    reports.append(report)

  def test_date(self):
    view = self.batch.create_view_from_last_start(date='2013-09-13')
    result = [meas for meas, in self.batch.query("""
      SELECT measurements.basename FROM %s en
        JOIN measurements ON measurements.id = en.measurementid
      """ % view)]
    self.assertListEqual(result, [self.reports[1]['meas']])
    return

  def test_start_date(self):
    view = self.batch.create_view_from_last_start(start_date='2013-09-14')
    result = [meas for meas, in self.batch.query("""
      SELECT measurements.basename FROM %s en
        JOIN measurements ON measurements.id = en.measurementid
      """ % view)]
    self.assertListEqual(result,
                         [report['meas'] for report in self.reports[2:]])
    return

  def test_end_date(self):
    view = self.batch.create_view_from_last_start(end_date='2013-09-14')
    result = [meas for meas, in self.batch.query("""
      SELECT measurements.basename FROM %s en
        JOIN measurements ON measurements.id = en.measurementid
      """ % view)]
    self.assertListEqual(result,
                         [report['meas'] for report in self.reports[:3]])
    return

  def test_between_dates(self):
    view = self.batch.create_view_from_last_start(start_date='2013-09-13',
                                                  end_date='2013-09-14')
    result = [meas for meas, in self.batch.query("""
      SELECT measurements.basename FROM %s en
        JOIN measurements ON measurements.id = en.measurementid
      """ % view)]
    self.assertListEqual(result,
                         [report['meas'] for report in self.reports[1:3]])
    return

if __name__ == '__main__':
  main()
