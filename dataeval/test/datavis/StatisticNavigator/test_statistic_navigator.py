import os
import os.path
import shutil
import unittest

import numpy as np
import matplotlib
from PySide import QtGui, QtCore, QtTest

from datavis.StatisticNavigator import cStatisticNavigator
import measproc.Statistic

t = np.arange(0, 10, 0.01)
Qt_red = QtCore.Qt.red

class TestAddStatistic(unittest.TestCase):
  @classmethod
  def setUpClass(cls):

    curr_path = os.path.dirname(__file__)

    cls.save_path = os.path.join(curr_path, 'temp')
    os.mkdir(cls.save_path)
    cls.Statistic2D = measproc.Statistic.iStatistic(cls.save_path)
    cls.Statistic2D.Axes.append('bar')
    cls.Statistic2D.TickLabels['bar'] = ['foo', 'baz']
    cls.Statistic2D.Array = (2.0, 4.0)
    cls.Statistic3D =  measproc.Statistic.iStatistic(cls.save_path)
    cls.Statistic3D.Axes.append('foo')
    cls.Statistic3D.Axes.append('bar')
    cls.Statistic3D.TickLabels['foo'] = ['baz', 'test']
    cls.Statistic3D.TickLabels['bar'] = ['egg', 'spam']
    cls.Statistic3D.Array = ((4.0, 5.5),(3.0, 2.1), )
    return

  @classmethod
  def tearDownClass(cls):
    shutil.rmtree(cls.save_path)
    return

  def setUp(self):
    self.navigator = cStatisticNavigator()
    return

  def tearDown(self):
    self.navigator.close()
    return

  def test_add_2D_statitic(self):
    self.navigator.addStatistic(self.Statistic2D)
    self.navigator.start()

    self.assertEqual(len(self.Statistic2D.Axes), len(self.navigator.fig.axes))

    title = self.Statistic2D.getTitle()
    for ax, stat_ax in zip(self.navigator.fig.axes, self.Statistic2D.Axes):
      bars = [child for child in ax.get_children() 
                    if type(child) == matplotlib.patches.Rectangle]
      for bar in bars[:-1]:
        self.assertIn(bar.get_height(), self.Statistic2D.Array)
      self.assertEqual(ax.get_title(), title)
      tick_labels = ax.get_xticklabels()
      for tick_label in tick_labels:
        tick_label_text = tick_label.get_text()
        self.assertIn(tick_label_text, self.Statistic2D.TickLabels[stat_ax])
    return

  def test_add_3d_statistic(self):
    self.navigator.addStatistic(self.Statistic3D)
    self.navigator.start()

    title = self.Statistic3D.getTitle()
    for i, ax in enumerate(self.navigator.fig.axes):
      self.assertEqual(ax.get_title(), title)
      tick_labels = ax.get_xticklabels()
      stat_ax =  self.Statistic3D.Axes[i/2]
      for tick_label in tick_labels:
        tick_label_text = tick_label.get_text()
        self.assertIn(tick_label_text, self.Statistic3D.TickLabels[stat_ax])

      tick_labels = ax.get_yticklabels()
      stat_ax =  self.Statistic3D.Axes[i/2 + 1]
      for tick_label in tick_labels:
        tick_label_text = tick_label.get_text()
        self.assertIn(tick_label_text, self.Statistic3D.TickLabels[stat_ax])

      """TODO: 
      Implement a test for addStatistic3D, which checks the height of columns
      If we add 4 column, the axes will has 4 matplotlib.spines.Spine objects 
      and 2 mpl_toolkits.mplot3d.art3d.Poly3DCollections.

      If we call the set_color() function of Poly3DCollection object, the 
      displayed columns will changed their color (if we call one of 
      Poly3DCollection object set_color function, it will change color of two 
      object)

      It we call the set_color() function of Spine object, nothing will happens.

      So it seems the Poly3DCollection objects contains the data of columns, but 
      I can't figure out, yet how can I reach the heights of the columns.

      The clip_box of Poly3DCollection which we can reach with get_clip_box() 
      function has xmin, xmax, ymin, ymax, height and widht attributes. But it 
      seems they are in pixels, and there is only one height for each 
      Poly3DCollection object (but it responsible for two columns)"""
    return

if  __name__ == '__main__':
  app = QtGui.QApplication([])
  unittest.main()