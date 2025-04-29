# -*- coding: utf-8 -*-
from datavis import pyglet_workaround  # necessary as early as possible (#164)

import os
import sys
import glob
import time
import shutil
import unittest
from argparse import ArgumentParser, RawTextHelpFormatter

import numpy
from PySide import QtGui, QtCore, QtTest

import interface
import measproc
from interface.Interfaces import iInterface, iView
from interface.modules import Modules
from interface.manager import AnalyzeManager
from measparser.BackupParser import BackupParser
from measparser.SignalSource import cSignalSource
from datavis.Synchronizer import cSynchronizer
from datavis.BatchNavigator import cBatchNavigator
from config.modules import Modules as ModuleScan
from config.Config import cScan, Config
from config.helper import writeConfig
from measproc.batchsqlite import Batch, RESULTS
from config.parameter import GroupParams
from datavis.GroupParam import cGroupParam

parser = ArgumentParser()
parser.add_argument('-v', '--verbose', action='count', default=0)
parser.add_argument('--meas-path', default=r'C:\KBData\measurement\535\H566_2013-03-21_16-38-04.mf4')
args = parser.parse_args()

args.meas_measpath = r'C:\KBData\measurement\535\H566_2013-03-21_16-38-04.mf4'

if not os.path.isfile(args.meas_measpath):
  sys.stderr.write('Test skipped,\n%s is not present\n' %(args.meas_measpath))
  sys.exit(1)
  
class View(iView):
  channels = 'main', 'can1'
  pass

db = os.path.abspath('batch.db')
repdir = os.path.abspath('reports')
measpath = os.path.abspath('replace')
replmeas = False

prj_name = 'main'
cfg_name = os.path.abspath('batchnav.cfg')
params_cfg_name = os.path.abspath('%s.params.cfg' %prj_name)
module_dir = os.path.abspath('modules')
modules_csv = os.path.abspath('modules.csv')

fills = {}
groups = GroupParams({
  'fillFoo-bar': {
    'group-bar': cGroupParam({'foo'}, '1', False, False),
  },
  'fillFoo-baz': {
    'group-baz': cGroupParam({'bar', 'baz'}, '2', False, False),
  },
})
labels = {}
tags = {}
quanames = {}
results = ()
quanames = {}
header = ['measurement', 'title', 'type', 'intervals', 'query']
sortby = 'measurement'
query = ''
grouptypes = {'foo', 'bar', 'baz'}
interval_header = [(('measurement',),
        '''SELECT measurements.basename FROM entryintervals
          JOIN entries ON
               entries.id = entryintervals.entryid
          JOIN measurements ON
               measurements.id = entries.measurementid
        WHERE  entryintervals.id = ?''')]


def setUpModule():
  global measurement
  meas_backup = os.path.abspath('backup')
  measurement = BackupParser.fromFile(args.meas_measpath, meas_backup)
  measurement.save()
  os.makedirs(module_dir)
  os.makedirs(repdir)

  writeConfig(params_cfg_name, {
    'Params': {
      'QuaNames': '__main__.quanames',
      'Labels': '__main__.labels',
      'Tags': '__main__.tags',
    },
    'General': {
      'cSource': 'measparser.SignalSource.cSignalSource',
    },
    'GroupTypes': {
        prj_name: '__main__.grouptypes',
      },
    'Fills': {
      prj_name: '__main__.fills',
    },
    'Groups': {
      prj_name: '__main__.groups',
    },
  })

  dirs = {prj_name: module_dir}
  modules = ModuleScan()
  # dummy module to setup Measurement section in the config
  modules.add('dummy', '', 'iView', 'View', 'init', '', prj_name,
              *View.channels)
  config = cScan(modules, dirs, params_cfg_name, prj_name)
  config.save(cfg_name)
  modules.write(modules_csv)
  return

def tearDownModule():
  for name in os.path.dirname(measurement.NpyDir), repdir, module_dir:
    shutil.rmtree(name)
  
  rm_names = [cfg_name, params_cfg_name, modules_csv]
  dirname, basename = os.path.split(db)
  name, ext = os.path.splitext(basename)
  name = os.path.join(dirname, name+'*'+ext)
  rm_names.extend( glob.glob(name) )
  for name in rm_names:
    os.remove(name)
  return

def createBatch(dbname, dirname, measurement, origmeas, labels, tags, quanames):
  """
  Setup function for module test.

  :Parameters:
    dbname : str
    dirname : str
    measurement : str
    origmeas : bool
    labels : dict
      {group_name<str>: (exclusive<bool>, [label_names<str>])}
    tags : dict
      {group_name<str>: [tag_names<str>]}
  """
  # batch and report parameters
  start = time.strftime(Batch.TIME_FORMAT)
  time_array = numpy.arange(0, 600, 20e-3)
  titles = 'foo is never bar', 'bar should be', 'pyon get the bottom'
  intervalgroup = [{(13,   78): 'bar', 
                    (113, 182): 'baz'},
                   {(56, 77): 'bar'}]
  # init batch
  batch = Batch(dbname, dirname, labels, tags, RESULTS, quanames)
  batch.set_start(start)
  batch.set_measurement(measurement, origmeas)
  measproc.Report.RepDir = dirname

  # init report
  entids = []
  for group_name, (exclusive, votes) in labels.iteritems():
    for title in titles:
      for intervals in intervalgroup:
        intervallist = measproc.cIntervalList(time_array)
        report = measproc.report2.Report(intervallist, title, labels)
        report.setEntryComment('spam')
        filereport = measproc.cIntervalListReport(intervallist, title)
        for interval, vote in intervals.iteritems():
          intervalid = report.addInterval(interval)
          report.vote(intervalid, group_name, vote)
          report.setComment(intervalid, 'spamspam')

        # add report to batch
        class_name = 'searchFoo.cSearch'
        param = 'foo="bar"'
        version = '0.1.0'
        result = 'none'
        entry_tags = 'egg',
        batch.set_module(class_name, param, version)
        entid = batch.add_entry(report, 
                                result, 
                                entry_tags)
        entids.append(entid)
        entid = batch.add_entry(filereport, 
                                result, 
                                entry_tags)
        entids.append(entid)
  return batch, entids

class Build(unittest.TestCase):    
  def setUp(self):
    labels = {'foo': (False, ['bar', 'baz'])}
    tags = {'spam': ['egg', 'eggegg']}
    self.batch, self.entids = createBatch('batch.db', 
                                   repdir,
                                   args.meas_measpath,
                                   True, 
                                   labels, 
                                   tags, 
                                   dict(one=[1, 1], two=[2, 2], three=[3, 3]))
    
    channel = 'can1'
    self.manager = AnalyzeManager() 
    self.manager.set_measurement(measurement.NpyDir, channel=channel)
    self.manager.set_backup(measurement.NpyDir)
    self.manager.set_batch_params(db, repdir, labels, tags, results, quanames,
                                  False)
    modules = ModuleScan()
    modules.read(modules_csv)
    self.manager.set_int_table_params(interval_header, [('measurement', True)])
    self.manager.set_batchnav_params(Config(cfg_name, modules), header, sortby,
                                     query, interval_header, [('measurement', True)])

    self.navigator = self.manager.get_batchnav()

    self.init_batchframe()
    return

  def init_batchframe(self):
    self.navigator.BatchFrame.addEntries(self.entids)
    
    self.navigator.start()
    return
    
  def select_entries(self, selectable_ndxs):

    model = self.navigator.BatchFrame.batchTable.model()
    rows = set()
    selected_entries = set()

    for i in selectable_ndxs:
      row, column = i
      ndx = model.index(row, column)
      self.navigator.BatchFrame.batchTable.clicked.emit(ndx)
      self.navigator.BatchFrame.batchTable.setCurrentIndex(ndx)
      rows.add(row)
      id = model.entries[row]['entryid']
      selected_entries.add(id)
    selecteds = self.navigator.BatchFrame.batchTable.selectedIndexes()
    self.assertEqual(len(selecteds) % len(model.header), 0)
    for selected in selecteds:
      self.assertIn(selected.row(), rows)
    return selected_entries

  def tearDown(self):
    self.navigator.close()
    self.batch.save()
    self.navigator.Batch.save()
    return

    
class TestStart(Build):
  def test_start(self):
    self.navigator.BatchFrame.batchTable.selectAll()
    self.navigator.StartBtn.click()
    basename = os.path.basename(args.meas_measpath)
    manager = self.navigator.Control.Managers[basename]
    all_report = manager.reports.viewkeys() or \
                 manager.report2s.viewkeys() or \
                 manager.statistics.viewkeys()
    
    self.assertNotEqual(manager.reports, {})
    self.assertNotEqual(manager.report2s, {})
    self.assertEqual(manager.statistics, {})
    for report in manager.reports.keys():
      self.assertIsInstance(report, measproc.cFileReport)
    for report2 in manager.report2s:
      self.assertIsInstance(report2, measproc.report2.Report)
    for statistic in manager.statistics:
      self.assertIsInstance(statistic, measproc.cFileStatistic)
    return
    
class TestSelect(Build):
  def test_select(self):
    self.assertIsNone(self.navigator.ReportId)
    i = 0
    type = ''
    while type != 'measproc.cFileReport':
      self.navigator.BatchFrame.batchTable.clearSelection()
      selectable_indexes = (i, 4), 
      entries = self.select_entries(selectable_indexes)
      entryid= entries.pop()
      type = self.batch.get_entry_attr(entryid, 'type')
      i += 1
    
    self.navigator.SelectReportBtn.click()
    self.assertEqual(self.navigator.ReportId, entryid)
    xml = self.navigator.Config.get('General', 'Report')
    self.assertTrue(xml.endswith('.xml'))
    return
      

if __name__ == '__main__':
  app = QtGui.QApplication([])
  unittest.main(argv=[sys.argv[0]], verbosity=args.verbose)
