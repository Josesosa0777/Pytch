from datavis import pyglet_workaround  # necessary as early as possible (#164)

import os
import glob
import sys
import shutil
import time
import argparse

import numpy
from reportlab.platypus import BaseDocTemplate

from text.templates import viewTemplate
from config.modules import Modules
from config.helper import writeConfig
from config.Config import cScan, Config
from config.parameter import GroupParams
from interface.Interfaces import iFill, iInterface
from interface.module import CreateModule
from interface.modules import TestCase, ModuleName
from measparser.BackupParser import BackupParser
from measparser.SignalSource import cSignalSource
from measproc.Batch import cBatch
from datavis.GroupParam import cGroupParam

grouptypes = {'foo', 'bar', 'baz'}
vidcalibs_path = os.path.join(os.getcwd(), "test", "vidcalibs.db") #"C:\\KBData\\Sandbox\\util_das\\dataeval\\test\\vidcalibs.db"# 

groups = GroupParams({
  'fillFoo-bar@fill': {
    'group-bar': cGroupParam({'foo'}, '1', True, False),
  },
  'fillFoo-baz@fill': {
    'group-baz': cGroupParam({'bar', 'baz'}, '2', True, False),
  },
})

view_angle_values = {
  'group-bar': 1,
  'group-baz': 2,
}
view_angles, missing = groups.build_groupname_params(view_angle_values)

legend_values = {
  'foo':  8,
  'bar':  9,
  'baz': 10,
}
legends, missing = groups.build_type_params(legend_values)

shape_values = {
  'foo': 11,
  'bar': 12,
  'baz': 14,
}
shape_legends, missing = groups.build_type_params(shape_values)

labels = {
  'foo': (False, ['bar', 'baz']),
}
tags = {
  'spam': ['egg', 'eggegg'],
}
quanames = {
  'tarack': ['sugar', 'hanyas'],
}

measurements = {}
backup = os.path.abspath('backup')
db = os.path.abspath('batch.xml')
repdir = os.path.abspath('reports')
mapdb = os.path.abspath('map.db')
start = time.strftime(cBatch.TIME_FORMAT)

open(mapdb, 'w')

_time = numpy.arange(0, 10, 20e-3)
_value = numpy.sin(_time)
version = BackupParser.getVersion()
for channel, name in [['main', 'foo.mdf'], ['can1', 'can1.blf']]:
  dir_name = os.path.join(backup, name)
  meas = BackupParser(dir_name, name, version, version, '')
  meas.addTime('foo', _time)
  meas.addSignal('spam', 'egg', 'foo', _value)
  meas.save()
  measurements[channel] = meas

def tearDownModule():
  for name in backup, repdir:
    if os.path.exists(name):
      shutil.rmtree(name)
  dirname, basename = os.path.split(db)
  name, ext = os.path.splitext(basename)
  name = os.path.join(dirname, name+'*'+ext)
  for name in glob.glob(name):
    os.remove(name)
  os.remove(mapdb)
  return

fill_prj_name = 'fill'

class BuildLoadNameSpace(TestCase):
  args = []
  def setUp(self):
    self.prj_name = 'main'
    self.name = 'view.cfg'
    self.params_cfg_name = '%s.params.cfg' %self.prj_name

    writeConfig(self.params_cfg_name, {
      'Params': {
        'QuaNames': '__main__.quanames',
        'Labels': '__main__.labels',
        'Tags': '__main__.tags',
      },
      'General': {
        'cSource': 'measparser.SignalSource.cSignalSource',
      },
      'GroupTypes': {
        'text.templates': '__main__.grouptypes',
      },
      'DocTemplates': {
        '%s.simple' %self.prj_name: 'datalab.doctemplate.SimpleDocTemplate',
      },
      'Groups': {
        'text.templates': '__main__.groups',
      },
      'ViewAngles': {
        'text.templates': '__main__.view_angles',
      },
      'Legends': {
        'text.templates': '__main__.legends',
      },
      'ShapeLegends': {
       'text.templates': '__main__.shape_legends',
      },
    })

    modules = Modules()
    fill_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'fill'))
    dir_names = {'text.templates': os.path.dirname(viewTemplate.__file__),
                 fill_prj_name: fill_dir}
    for prj_name, dir_name in dir_names.iteritems():
      modules.scan(prj_name, dir_name)

    config = cScan(modules, dir_names, self.params_cfg_name, self.prj_name)
    config.save(self.name)

    self.config = Config(self.name, modules)
    parser = argparse.ArgumentParser()
    parser = Config.addArguments(parser)
    args = parser.parse_args(self.args)
    self.config.init(args)
    self.manager = self.config.createManager('iView')
    self.manager.set_vidcalibs(vidcalibs_path)
    return

  def tearDown(self):
    self.manager.close()
    for name in self.name, self.params_cfg_name:
      os.remove(name)
    return

null_param = 'interface.Parameter.iParameter;'

class TestLoadNameSpace(BuildLoadNameSpace):
  def test_loadNameSpace(self):
    namespace = {
      'viewTemplate-def_param@text.templates':
        CreateModule('viewTemplate', 'View', 'method', null_param,
                      'text.templates'),
      'analyzeTemplate-def_param@text.templates':
        CreateModule('analyzeTemplate', 'Analyze', 'method', null_param,
                      'text.templates'),
      'compareTemplate-Parameter@text.templates':
        CreateModule('compareTemplate', 'cCompare', 'method', null_param,
                     'text.templates'),
      'fillFoo-bar@fill':
        CreateModule('fillFoo', 'Fill', 'init', 'spam=42', fill_prj_name),
      'fillFoo-baz@fill':
        CreateModule('fillFoo', 'Fill', 'init', 'spam=24', fill_prj_name),
    }
    self.config._loadNameSpace(self.manager)
    modules = self.manager.get_modules()
    self.assertNameSpaceEqual(modules, namespace)
    return

class BuildWake(BuildLoadNameSpace):
  args = [
          '-n',     'iView',
          '-i',     'viewTemplate@main',
          '-p',     'viewTemplate@main.def_param',
          '--fill', 'fillFoo-bar@fill',
          '-m', 'main='+measurements['main'].NpyDir,
          '-m', 'can1='+measurements['can1'].NpyDir,
         ]
  def setUp(self):
    BuildLoadNameSpace.setUp(self)
    self.modulenames = self.config._loadNameSpace(self.manager)
    return

class BuildListChannels(BuildWake):
  def setUp(self):
    BuildLoadNameSpace.setUp(self)
    self.config.load(self.manager)
    return


class BuildSetChannels(BuildLoadNameSpace):
  args = [
          '-m', r'd:\measurment\foo.mdf',
          '-m', r'can1=d:\measurment\can1.blf',
         ]


class TestSetChannels(BuildSetChannels):
  def test_set_meas(self):
    self.assertEqual(self.config.get('Measurement', 'can1'),
                     r'd:\measurment\can1.blf')
    self.assertEqual(self.config.get('Measurement', 'main'),
                     r'd:\measurment\foo.mdf')
    return


class BuildLoad(BuildLoadNameSpace):
  args = [
          '-b', db,
          '--repdir', repdir,
          '--measpath', backup,
          '--start', start,
          '-m', 'main='+measurements['main'].NpyDir,
          '-m', 'can1='+measurements['can1'].NpyDir,
          '--solidtimecheck',
          '-u', '',
          '-s', 'measparser.SignalSource.cSignalSource',
          '-n', 'iView',
          '-i', 'viewTemplate@text.templates',
          '-p', 'viewTemplate@text.templates.def_param',
          '--fill', 'fillFoo-bar@fill',
          '--doc-name', 'foo.pdf',
          '--mapdb', mapdb,
         ]

  def setUp(self):
    BuildLoadNameSpace.setUp(self)
    self.config.load(self.manager, 'iView')
    return

  def tearDown(self):
    self.config.close(self.manager, 'iView')
    return

class TestLoad(BuildLoad):
  def test_config_upload(self):
    self.assertFalse(self.manager.strong_time_check)
    return

  def test_config_set(self):
    self.assertTrue(self.config.RunNav)
    return

  def test_search_upload(self):
    self.assertEqual(self.manager._batch_params.db_name, db)
    self.assertEqual(self.manager._batch_params.dir_name, repdir)
    self.assertDictEqual(self.manager._batch_params.labels, labels)
    self.assertDictEqual(self.manager._batch_params.tags, tags)
    self.assertDictEqual(self.manager._batch_params.quanames, quanames)
    return

  def test_verbose(self):
    self.assertFalse(self.config.Verbose)
    return

  def test_view_upload(self):
    self.assertEqual(self.manager._measurements['main'], measurements['main'].NpyDir)
    self.assertEqual(self.manager._measurements['can1'], measurements['can1'].NpyDir)
    self.assertIs(self.manager._Source, cSignalSource)
    return

  def test_uploadDocTemplates(self):
    template_names = self.manager._doctemplates.keys()
    self.assertListEqual(template_names, ['%s.simple' %self.prj_name])
    for name in template_names:
      self.assertTrue(issubclass(self.manager._doctemplates[name],
                                 BaseDocTemplate))
    return

  def test_get_doc(self):
    doc = self.manager.get_doc('%s.simple' %self.prj_name)
    self.assertIsInstance(doc, BaseDocTemplate)
    return

class BuilBuild(BuildLoad):
  def setUp(self):
    BuildLoad.setUp(self)
    self.config.m('')
    self.config.build(self.manager, 'iView')
    return

class TestBuild(BuilBuild):
  def test_fill(self):
    modules = self.manager.get_modules()
    self.assertDictEqual(modules._fills,
                        {'viewTemplate-def_param@text.templates': {}})
    return

  def test_check_modules(self):
    modules = self.manager.get_modules()
    self.assertSetEqual(modules.get_passed(),
                        {'viewTemplate-def_param@text.templates',
                         'fillFoo-bar@fill'})
    self.assertSetEqual(modules.get_failed(), set())
    return

  def test_view_angles(self):
    self.assertDictEqual(self.manager.view_angles,
                         view_angles['fillFoo-bar@fill'])
    return

  def test_groups(self):
    gtps = self.manager.grouptypes
    gps = {
    'group-bar': cGroupParam({gtps.get_type('text.templates', 'foo')}, '1',
                             True, False),
    }

    self._test_set_groups(gps)
    return

  def _test_set_groups(self, gps):
    for group_name, group in gps.iteritems():
      self.assertIn(group_name, self.manager.groups)
      mangroup = self.manager.groups[group_name]
      self.assertEqual(group, mangroup)
    return

  def test_legends(self):
    self._test_values(legend_values, self.manager.legends)
    return

  def test_mapdb(self):
    self.assertEqual(self.manager._mapdb, mapdb)
    return

  def test_shapes(self):
    self._test_values(shape_values, self.manager.shape_legends)
    return

  def _test_values(self, named_values, numbered_values):
    gtps = self.manager.grouptypes
    for group in groups['fillFoo-bar@fill'].itervalues():
      for type_name in group:
        type_number = gtps.get_type('text.templates', type_name)
        self.assertEqual(named_values[type_name],
                         numbered_values[type_number])
    return


if __name__ == '__main__':
  from unittest import main
  from PySide import QtGui
  app = QtGui.QApplication([])
  main()
