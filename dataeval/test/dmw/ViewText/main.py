from datavis import pyglet_workaround  # necessary as early as possible (#164)

import os
import sys
import unittest

from PySide import QtGui, QtCore

from text.templates import viewTemplate
from text.ViewText import ViewText
from dmw.ViewControl import cViewControl
from config.modules import Modules
from config.Config import cScan, Config
from config.helper import writeConfig

prj_name = 'main'
cfg_name = 'view.cfg'
params_cfg = '%s.params.cfg' %prj_name

fills = {}
groups = {}
labels = {}
tags = {}
quanames = {}


def setUpModule():
  global modules

  dir_names = {'text.templates': os.path.dirname(viewTemplate.__file__)}

  modules = Modules()
  for prj_name_, dir_name in dir_names.iteritems():
    modules.scan(prj_name_, dir_name)

  writeConfig(params_cfg, {
    'Params': {
      'QuaNames': '__main__.quanames',
      'Labels': '__main__.labels',
      'Tags': '__main__.tags',
    },
    'General': {
      'cSource': 'measparser.SignalSource.cSignalSource',
    },
    'Fills': {
      prj_name: '__main__.fills',
    },
    'Groups': groups,
  })

  config = cScan(modules, dir_names, params_cfg, 'text.templates')
  config.save(cfg_name)
  return

def tearDownModule():
  for name in cfg_name, params_cfg:
    os.remove(name)
  return

class TestCase(unittest.TestCase):
  def setUp(self):
    setUpModule()
    config = Config(cfg_name, modules)
    control = cViewControl(None, config)

    self.name = viewTemplate.__file__.replace('.pyc', '.py')
    self.text = ViewText(self.name, config, control)
    return

  def test_parse(self):
    self.assertEqual(self.text.get_text(),
"""# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface

def_param = interface.NullParam

sgs  = [
{
},
]

class View(interface.iView):
  def check(self):
    group = self.source.selectSignalGroupOrEmpty(sgs)
    return group

  def fill(self, group):
    return group

  def view(self, param, group):
    return
""")
    return

  def test_add_signal(self):
    self.text.add_signal('foo', 'bar')
    self.text.add_signal('goo', 'car')
    self.text.add_signal('foo', 'bar')
    self.assertEqual(self.text.get_text(),
"""# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface

def_param = interface.NullParam

sgs  = [
{
  "car": ("goo", "car"),
  "bar": ("foo", "bar"),
},
]

class View(interface.iView):
  def check(self):
    group = self.source.selectSignalGroupOrEmpty(sgs)
    return group

  def fill(self, group):
    return group

  def view(self, param, group):
    return
""")
    return

  def test_add_lines(self):
    self.text.add_lines(['foo', 'bar'])
    self.assertEqual(self.text.get_text(),
"""# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface

def_param = interface.NullParam

sgs  = [
{
},
]

class View(interface.iView):
  def check(self):
    group = self.source.selectSignalGroupOrEmpty(sgs)
    return group

  def fill(self, group):
    return group

  def view(self, param, group):
    foo
    bar
    return
""")
    return

if __name__ == '__main__':
  app = QtGui.QApplication([])
  unittest.main()
