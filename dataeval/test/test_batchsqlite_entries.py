import unittest
import os
import shutil
import time
import fnmatch

import pylab

import measproc
from measproc.batchsqlite import Batch
from measproc.Statistic   import cDinStatistic
from measproc.workspace   import DinWorkSpace
from measproc.textentry   import DinTextEntry
from measproc.figentry    import DinFigEntry

db_name = 'batch.db'
dir_name = 'files'
labels = {'foo' : (False, ['bar', 'baz'])}
tags = {'spam': ['egg', 'eggegg']}
results = 'passed', 'failed', 'error', 'inconc', 'none'
quanames = {'pyon': ['atomsk', 'naota']}
measurement = 'D:/measurement/dataeval-test/CVR3_B1_2011-02-10_16-53_020.mdf'
start = time.strftime('%Y-%m-%d %H:%M:%S')

title = 'foo is never bar'
module = 'searchFoo.cSearch'
param = 'foo="bar"'
version = '42'
result = 'none'
entry_tags = 'egg',

measproc.Statistic.StatDir      = dir_name
measproc.workspace.WorkSpaceDir = dir_name
measproc.textentry.TextEntryDir = dir_name
measproc.figentry.FigEntryDir   = dir_name

class Build(unittest.TestCase):
  def setUp(self):
    self.batch = Batch(db_name, dir_name, labels, tags, results, quanames)
    self.batch.set_start(start)
    self.batch.set_measurement(measurement, True)
    self.batch.set_module(module, param, version)
    return
  
  def add_statistic(self):
    entry = cDinStatistic(title, [['spam', ['egg', 'eggegg']]])
    return self.batch.add_entry(entry, result, entry_tags)


  def test_add_statistic(self):
    self.add_statistic()
    return

  def test_wake_statistic(self):
    entryid = self.add_statistic()
    self.batch.wake_entry(entryid)
    return

  def add_workspace(self):
    entry = DinWorkSpace(title)
    return self.batch.add_entry(entry, result, entry_tags)

  def test_add_workspace(self):
    self.add_workspace()
    return

  def test_wake_workspace(self):
    entryid = self.add_workspace()
    self.batch.wake_entry(entryid)
    return

  def add_text(self, text):
    entry = DinTextEntry(title, text)
    return self.batch.add_entry(entry, result, entry_tags)

  def test_add_text(self):
    self.add_text('spamspam')
    return

  def test_wake_text(self):
    entryid = self.add_text('spamspam')
    self.batch.wake_entry(entryid)
    return

  def add_fig(self):
    fig = pylab.figure()
    entry = DinFigEntry(title, fig)
    return self.batch.add_entry(entry, result, entry_tags)
  
  def test_add_fig(self):
    self.add_fig()
    return
  
  def test_wake_fig(self):
    entryid = self.add_fig()
    self.batch.wake_entry(entryid)
    return

  def tearDown(self):
    self.batch.save()
    return

def tearDownModule():
  os.remove(db_name)
  shutil.rmtree(dir_name)
  return

if __name__ == '__main__':
  unittest.main()
