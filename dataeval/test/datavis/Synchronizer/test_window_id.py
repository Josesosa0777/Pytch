import os
import sys
import shutil
import os.path
import unittest

import numpy as np
from PySide import QtGui, QtCore, QtTest

from datavis.Synchronizer import cSynchronizer
from datavis.PlotNavigator  import cPlotNavigator

titles = ['foo', 'bar', 'baz']
meas = 'Egg_Meas'
navigator_name = cPlotNavigator.__module__.split('.')[-1]
module_names = ['viewFoo', 'viewBar']

class Build(unittest.TestCase):
  def setUp(self):
    self.sync = cSynchronizer()
    self.sync.setModule(module_names[0])
    #create cPlotNavigators with default names
    self.default_name_nav = []
    self.default_name_nav.append(cPlotNavigator())
    self.default_name_nav.append(cPlotNavigator())
    #create cPlotNavigator with same names
    self.nav_with_title = []
    self.nav_with_title.append(cPlotNavigator(title=titles[0]))
    self.nav_with_title.append(cPlotNavigator(title=titles[0]))
    #create cPlotNavigator with unique name
    self.nav_with_unique_title = cPlotNavigator(title=titles[1])
    #create cPlotNavigator with same name, but the names defined later 
    self.later_named_nav = []
    self.later_named_nav.append(cPlotNavigator())
    self.later_named_nav.append(cPlotNavigator())

    self.sync.addClient(self.default_name_nav[0])
    self.sync.addClient(self.default_name_nav[1])
    self.sync.addClient(self.nav_with_title[0])

    self.sync.setModule(module_names[1])

    self.sync.addClient(self.nav_with_title[1])
    self.sync.addClient(self.nav_with_unique_title)

    self.sync.addClient(self.later_named_nav[0], title=titles[2])
    self.sync.addClient(self.later_named_nav[1], title=titles[2])
    self.sync.setWindowTitles(meas)

class TestWindowId(Build):
  def test_different_id(self):
    self.assertNotEqual(self.default_name_nav[0].getWindowId(), 
                        self.default_name_nav[1].getWindowId())
    self.assertEqual(self.nav_with_title[0].getWindowId(), 
                        self.nav_with_title[1].getWindowId())
    self.assertNotEqual(self.later_named_nav[0].getWindowId(), 
                        self.later_named_nav[1].getWindowId())
    self.assertNotEqual(self.nav_with_unique_title.getWindowId(), 
                        self.later_named_nav[0].getWindowId())
    return

  def test_window_titles(self):
    self.assertEqual(self.default_name_nav[0].getWindowTitle(), 
                     '%s-%s' %(navigator_name, meas))
    self.assertEqual(self.default_name_nav[1].getWindowTitle(), 
                     '%s-0-%s' %(navigator_name, meas))
    self.assertEqual(self.nav_with_title[0].getWindowTitle(),
                    '%s-%s' %(titles[0], meas))
    self.assertEqual(self.nav_with_title[1].getWindowTitle(),
                    '%s-%s' %(titles[0], meas))
    self.assertEqual(self.nav_with_unique_title.getWindowTitle(),
                    '%s-%s' %(titles[1], meas))
    self.assertEqual(self.later_named_nav[0].getWindowTitle(),
                    '%s-%s' %(titles[2], meas))
    self.assertEqual(self.later_named_nav[1].getWindowTitle(),
                    '%s-0-%s' %(titles[2], meas))
    return

  def test_window_ids(self):
    self.assertEqual(self.default_name_nav[0].getWindowId(), 
                     '%s' %navigator_name)
    self.assertEqual(self.default_name_nav[1].getWindowId(), 
                     '%s-0' %navigator_name)
    self.assertEqual(self.nav_with_title[0].getWindowId(), '%s' %titles[0])
    self.assertEqual(self.nav_with_title[1].getWindowId(), '%s' %titles[0])
    self.assertEqual(self.nav_with_unique_title.getWindowId(), 
                     '%s' %titles[1])
    self.assertEqual(self.later_named_nav[0].getWindowId(), '%s' %titles[2])
    self.assertEqual(self.later_named_nav[1].getWindowId(), '%s-0' %titles[2])
    return

  def test_get_client(self):
    client = self.sync.getClient(module_names[0],
                                 self.default_name_nav[0].getWindowId())
    self.assertEqual(client, self.default_name_nav[0])

    client = self.sync.getClient(module_names[0],
                                 self.default_name_nav[1].getWindowId())
    self.assertEqual(client, self.default_name_nav[1])

    client = self.sync.getClient(module_names[0],
                                 self.nav_with_title[0].getWindowId())
    self.assertEqual(client, self.nav_with_title[0])

    client = self.sync.getClient(module_names[1],
                                 self.nav_with_title[1].getWindowId())
    self.assertEqual(client, self.nav_with_title[1])

    client = self.sync.getClient(module_names[1],
                                 self.later_named_nav[0].getWindowId())
    self.assertEqual(client, self.later_named_nav[0])

    client = self.sync.getClient(module_names[1],
                                 self.later_named_nav[1].getWindowId())
    self.assertEqual(client, self.later_named_nav[1])
    return

class BuildPictures(Build):
  temp_dir_name = 'Spam'
  def setUp(self):
    Build.setUp(self)
    self.path = './' + self.temp_dir_name
    for client in self.sync.clients:
      client.addAxis()

    self.sync.start()
    self.sync.show()
    return

class TestCapture(BuildPictures):
  def test_capture(self):
    client2picture = self.sync.capture(self.temp_dir_name)
    created_images = [f for f in os.listdir(self.path) if f.endswith(".png")]
    client_nr = len(self.sync.clients)
    self.assertEqual(len(created_images), client_nr)
    self.assertEqual(len(client2picture), client_nr)
    for client in self.sync.clients:
      window_id = client.getWindowId()
      picture_name = '%s-%s-%s.png' %(self.sync.clients2modulenames[client], 
                                      window_id, meas)
      self.assertTrue(picture_name in created_images)
    self.sync.remove_pictures(client2picture)
    return

class TestRemovePicture(BuildPictures):
  def test_remove_empty_dir(self):
    client2picture = self.sync.capture(self.temp_dir_name)
    self.sync.remove_pictures(client2picture)
    self.assertFalse(os.path.isdir(self.temp_dir_name))
    return

  def test_remove_not_empty_dir(self):
    os.mkdir(self.temp_dir_name)
    f = open(os.path.join(self.temp_dir_name, 'dummy.txt'), 'w')
    f.close()

    client2picture = self.sync.capture(self.temp_dir_name)
    self.sync.remove_pictures(client2picture)
    self.assertTrue(os.path.isdir(self.temp_dir_name))

    pictures = [f for f in os.listdir(self.path) if f.endswith(".png")]
    self.assertEqual(pictures, [])

    files = [f for f in os.listdir(self.path)
                  if os.path.isfile(os.path.join(self.path, f))]

    self.assertEqual(len(files), 1)
    self.assertEqual(os.path.basename(files[0]), 'dummy.txt')

    shutil.rmtree(self.path)
    return

if __name__ == '__main__':
  app = QtGui.QApplication([])
  unittest.main()