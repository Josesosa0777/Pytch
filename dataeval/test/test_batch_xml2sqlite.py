from datavis import pyglet_workaround  # necessary as early as possible (#164)

import unittest
import shutil
import time
import os

import numpy
import pylab

from measproc.Batch import CreateParams as XmlBatchCreateParams,\
                           UploadParams as XmlBatchUploadParams
from measproc.batchsqlite import Batch
from measproc.Report import CreateParams as ReportCreateParams,\
                            IntervalAddParams
from measproc.Statistic import CreateParams as StatCreateParams
from measproc.figentry import CreateParams as FigCreateParams
from measproc.textentry import CreateParams as TextCreateParams

from test_batchsqlite_merge import Params


class BatchConvertParams:
  def __init__(self, delete, rename, vote2label, labels):
    self.delete = delete
    self.rename = rename
    self.vote2label = vote2label
    self.labels = labels
    return

  def __call__(self, batchxml):
    batch = Batch.from_batchxml(batchxml, self.delete, self.rename,
                                self.vote2label, self.labels)
    return batch

class Params(Params):
  xmlbatches = []
  xmlbatch_create_params = []
  @classmethod
  def create_xmlbatch(cls, XmlFile, StartTime, ReplMeas, MeasPath):
    param = XmlBatchCreateParams(XmlFile, StartTime, ReplMeas, MeasPath)
    batch = param()
    cls.xmlbatches.append(batch)
    cls.xmlbatch_create_params.append(param)
    return batch

  reports = []
  reports_create_params = []
  @classmethod
  def create_report(cls, time, title, votes, repdir):
    param = ReportCreateParams(time, title, votes, repdir)
    report = param()
    cls.reports_create_params.append(param)
    cls.reports.append(report)
    return report

  interval_add_params = []
  @classmethod
  def add_interval_to_report(cls, report, interval, vote, comment):
    param = IntervalAddParams(interval, vote, comment)
    param(report)
    cls.interval_add_params.append(param)
    return

  batch_upload_params = []
  @classmethod
  def upload_entry_into_batch(cls, batch, entry, classname, signature, 
                              measurement, result, type):
    param = XmlBatchUploadParams(classname, signature, measurement, result, type)
    param(batch, entry)
    cls.batch_upload_params.append(param)
    return
  
  statistics = []
  statistic_create_params = []
  @classmethod
  def create_statistic(cls, title, axes, dirname):
    param = StatCreateParams(title, axes, dirname)
    statistic = param()
    cls.statistics.append(statistic)
    cls.statistic_create_params.append(param)
    return statistic

  figentries = []
  figentry_create_params = []
  @classmethod
  def create_figentry(cls, title, fig, dir_name):
    param = FigCreateParams(title, fig, dir_name)
    figentry = param()
    cls.figentries.append(figentry)
    cls.figentry_create_params.append(param)
    return figentry

  textentries = []
  textentry_create_params = []
  @classmethod
  def create_textentry(cls, title, text, dir_name):
    param = TextCreateParams(title, text, dir_name)
    textentry = param()
    cls.textentries.append(textentry)
    cls.textentry_create_params.append(param)
    return textentry

  batches = []
  batch_convert_params = []
  @classmethod
  def create_batch_from_batchxml(cls, batchxml, delete, rename, vote2label,
                                 labels):
    param = BatchConvertParams(delete, rename, vote2label, labels)
    batch = param(batchxml)
    cls.batches.append(batch)
    cls.batch_convert_params.append(param)
    return batch
  pass

measurement  = os.getenv('testmeas', 'CVR3_B1_2011-02-10_16-53_020.mdf')
module = 'searchDirk'
modulefile = os.path.join(os.path.dirname(__file__), 'search', module) + '.py'

class Build(Params):
  @classmethod
  @unittest.skipUnless(os.path.isfile(measurement), '%s missing' %measurement)
  #@unittest.skipUnless(os.path.isfile(modulefile), '%s missing' %modulefile)
  def build(cls):
    batchxml = cls.create_xmlbatch(
      os.path.abspath('batchxml.xml'), time.localtime(0), False, '')
    report = cls.create_report(
      numpy.arange(0, 42, 20e-3), 'pyon', ('foo', 'bar', 'baz'), 'files')
    cls.add_interval_to_report(report, (45, 78), 'bar', 'egg')
    cls.add_interval_to_report(report, (46, 48), 'baz', 'eggegg')
    cls.add_interval_to_report(report, (96, 98), 'foo', 'spam')
    classname = '%s.cSearch' %module 
    cls.upload_entry_into_batch(batchxml, report, 
                                classname, 
                                'foo="bar"', 
                                measurement, 
                                'passed', 
                                'measproc.cFileReport')
    workspace = cls.create_workspace('foo is the king', 'files')
    cls.upload_entry_into_batch(batchxml, workspace,
                                classname,
                                'foo="bar"',
                                measurement,
                                'none',
                                'measproc.FileWorkSpace')
    statistic = cls.create_statistic(
      'egg is good', [['foo', ['bar', 'baz']]], 'files')
    cls.upload_entry_into_batch(batchxml, statistic,
                                classname,
                                'foo="bar"',
                                measurement,
                                'none',
                                'measproc.cFileStatistic')
    fig = pylab.figure()
    figentry = cls.create_figentry('egg spam egg', fig, 'files')
    cls.upload_entry_into_batch(batchxml, figentry,
                                classname,
                                'foo="bar"',
                                measurement,
                                'none',
                                'measproc.FileFigEntry')
    textentry = cls.create_textentry('bar', 'baz', 'files')
    cls.upload_entry_into_batch(batchxml, textentry,
                                classname,
                                'foo="bar"',
                                measurement,
                                'none',
                                'measproc.FileTextEntry')
    return

  @classmethod
  def destroy(cls):
    for trashdir in cls.reports_create_params,\
                    cls.workspace_create_params,\
                    cls.statistic_create_params,\
                    cls.figentry_create_params,\
                    cls.textentry_create_params:
      while trashdir:
        params = trashdir.pop()
        if hasattr(params, 'DirName'):
          dirname = params.DirName
        elif hasattr(params, 'dir_name'):
          dirname = params.dir_name
        if os.path.exists(dirname): shutil.rmtree(dirname)

    for trash in cls.xmlbatches,\
                 cls.xmlbatch_create_params,\
                 cls.reports,\
                 cls.report_create_params,\
                 cls.interval_add_params,\
                 cls.batch_upload_params,\
                 cls.workspaces,\
                 cls.statistics,\
                 cls.figentries,\
                 cls.textentries:
      while trash: trash.pop()
    while cls.batches:
      batch = cls.batches.pop()
      batch.save()
      if os.path.isfile(batch.dbname): os.remove(batch.dbname)
    return
  pass


class Test(unittest.TestCase, Build):
  @classmethod
  def setUpClass(cls):
    cls.build()
    cls.create_batch_from_batchxml(cls.xmlbatches[0], ['baz'], {'foo': 'goo'},
                                   {'goo': 'spam', 'bar': 'egg'},
                                   {'spam': (True,  ['goo', 'hoo']),
                                    'egg':  (False, ['bar', 'car'])})
    return

  @classmethod
  def tearDownClass(cls):
    cls.destroy()
    return

  def _get_entry_all_files(self, entry):
    xml = entry.getTitle(WithoutExt=False)
    npy = entry.getTimeFile()
    npy = os.path.basename(npy)
    return {xml, npy}
    
  def _get_registered_files(self, batch, entryid):
    names = batch.query("""SELECT files.name FROM files 
                           JOIN entry2file ON 
                                entry2file.fileid = files.id
                           WHERE entry2file.entryid = ?""", entryid)
    return set([name for name, in names])

  def _test_entry_with_multiple_files_reg(self, batch, entry, type):
    entryid, = batch.filter(type=type)
    names = self._get_registered_files(batch, entryid)
    _names = self._get_entry_all_files(entry)
    self.assertSetEqual(names, _names)
    return

  def gen_entry_with_multiple_files_reg(self, entries, type):
    batch = self.batches[0]
    entry = entries[0]
    self._test_entry_with_multiple_files_reg(batch, entry, type)
    return

  def _test_entry_with_multiple_files_exists(self, batch, entry):
    for name in self._get_entry_all_files(entry):
      fullname = os.path.join(batch.dirname, name)
      self.assertTrue(os.path.isfile(fullname))
    return
    
  def gen_entry_with_multiple_files_exists(self, entries):
    batch = self.batches[0]
    entry = entries[0]
    self._test_entry_with_multiple_files_exists(batch, entry)
    return

  def _get_entry_main_file(self, entry):
    name = entry.getTitle(WithoutExt=False)
    return {name}

  def _test_entry_with_single_file_reg(self, batch, entry, type):
    entryid, = batch.filter(type=type)
    names = self._get_registered_files(batch, entryid)
    _names = self._get_entry_main_file(entry)
    self.assertSetEqual(names, _names)
    return

  def gen_entry_with_single_file_reg(self, entries, type):
    batch = self.batches[0]
    entry = entries[0]
    self._test_entry_with_single_file_reg(batch, entry, type)
    return
  
  def _test_entry_with_single_file_exitsts(self, batch, entry):
    for name in self._get_entry_main_file(entry):
      fullname = os.path.join(batch.dirname, name)
      self.assertTrue(os.path.isfile(fullname))
    return

  def gen_entry_with_single_file_exitsts(self, entries):
    batch = self.batches[0]
    entry = entries[0]
    self._test_entry_with_single_file_exitsts(batch, entry)
    return

  def test_report(self):
    batch = self.batches[0]
    entryid, = batch.filter(type='measproc.Report')
    report = batch.wake_entry(entryid)
    reportxml = self.reports[0]
    convert = self.batch_convert_params[0]

    self.assertEqual(reportxml.ReportAttrs['Comment'], report.getEntryComment())

    for i, interval in enumerate(reportxml.IntervalList):
      self.assertEqual(reportxml.getComment(interval), report.getComment(i))
      votes = report.getVotes(i)
      for vote in reportxml.getIntervalVotes(interval):
        if vote in convert.delete:
          for _votes in votes.itervalues():
            self.assertNotIn(vote, votes_)
        else:
          vote = convert.rename.get(vote, vote)
          groupname = convert.vote2label[vote]
          self.assertIn(groupname, votes)
          self.assertIn(vote, votes[groupname])
    return

  def test_no_file_report(self):
    batch = self.batches[0]
    self.assertListEqual(batch.filter(type='measproc.cFileReport'), [])
    return

  pass

for name,         entries in [
   ['report',     Test.reports],
   ['statistics', Test.statistics],
  ]:
  method = lambda s, e=entries: Test.gen_entry_with_multiple_files_exists(s, e)
  setattr(Test, 'test_%s_files_exists' %name, method)

for name,         entries,         type in [
   ['report',     Test.reports,    'measproc.cFileReports'],
   ['statistics', Test.statistics, 'measproc.cFileStatistic'],
  ]:
  method = lambda s, e=entries, t=type: Test.gen_entry_with_multiple_files_reg(s, e, t)
  setattr(Test, 'test_%s_files_reg', method)

for name,        entries in [
   ['workspace', Test.workspaces],
   ['figentry',  Test.figentries],
   ['textentry', Test.textentries],
  ]:
  method = lambda s, e=entries: Test.gen_entry_with_single_file_exitsts(s, e)
  setattr(Test, 'test_%s_file_exists' %name, method)

for name,        entries,          type in [
   ['workspace', Test.workspaces,  'measproc.FileWorkSpace'],
   ['figentry',  Test.figentries,  'measproc.FileFigEntry'],
   ['textentry', Test.textentries, 'measproc.FileTextEntry'],
  ]:
  method = lambda s, e=entries, t=type: Test.gen_entry_with_single_file_reg(s, e, t)
  setattr(Test, 'test_%s_file_reg' %name, method)

if __name__ == '__main__':
  unittest.main()
