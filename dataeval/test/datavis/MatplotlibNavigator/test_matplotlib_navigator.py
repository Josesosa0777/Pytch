import os
import sys
import unittest
import cStringIO

import PIL
from PIL import ImageGrab
import numpy
import matplotlib
from PySide import QtGui, QtCore, QtTest

from datavis.Synchronizer import cSynchronizer
from datavis.MatplotlibNavigator import MatplotlibNavigator
import measproc

class Build(unittest.TestCase):
  def setUp(self):
    self.navigator = MatplotlibNavigator()
    self.init_navigator()
    return

  def init_navigator(self):
    fig = self.navigator.fig
    ax = fig.add_subplot(111)
    ax.plot((1,2,3), (4,5,6))
    self.navigator.start()
    self.ax = ax
    return
    
  def tearDown(self):
    self.navigator.close()
    return

class TestSetXLimOnline(Build):
  def test_set_axes_limitm(self):
    limits = [2.0, 5.0]
    self.navigator.setAxesLimits(limits)
    left, right = \
            self.ax.get_xlim()
    self.assertAlmostEqual(2.0, left)
    self.assertAlmostEqual(5.0, right)
    return
    
class TestFigureSave(Build):
  def test_copy_content_to_file(self):
    self.navigator.copyContentToFile('fig')
    pics = [ f for f in os.listdir(".") if f.endswith(".png") ]
    self.assertEqual(pics, ['fig.png'])
    file_syze = os.stat('fig.png').st_size
    self.assertGreater(file_syze, 0)
    return

  def test_copy_content_to_buffer(self):
    buff = self.navigator.copyContentToBuffer()
    buffer = cStringIO.StringIO()
    self.navigator.copyContentToFile(buffer, format='png')
    buff_value = buff.getvalue()
    buffer_value = buffer.getvalue()
    self.assertNotEqual(buff_value, '')
    self.assertNotEqual(buffer_value, '')
    self.assertEqual(buff_value, buffer_value)
    return

  @classmethod  
  def tearDownClass(cls):
    pics = [ f for f in os.listdir(".") if f.endswith(".png") ]
    for pic in pics:
      os.remove(pic)
    return


class TestKeyPressEvent(Build):
  def setUp(self):
    Build.setUp(self)
    renderer = self.navigator.fig.canvas.get_renderer()
    self.navigator.help.draw(renderer)
    return
  
  def test_f1_press(self):
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_F1)
    self.assertTrue(self.navigator.help.get_visible())
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_F1)
    self.assertFalse(self.navigator.help.get_visible())
    return
    
  def test_q_press(self):
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_Q)
    clip_board_data = ImageGrab.grabclipboard()
    clip_board_data.save('fig.png')
    pics = [ f for f in os.listdir(".") if f.endswith(".png") ]
    self.assertEqual(pics, ['fig.png'])
    file_syze = os.stat('fig.png').st_size
    self.assertGreater(file_syze, 0)
    return

  def test_k_press(self):
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_K)
    for ax in self.navigator.fig.axes:
      self.assertEqual(ax.get_xscale(), 'log')

    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_K)
    for ax in self.navigator.fig.axes:
      self.assertEqual(ax.get_xscale(), 'linear')
    return

  def test_l_press(self):
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_L)
    for ax in self.navigator.fig.axes:
      self.assertEqual(ax.get_yscale(), 'log')

    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_L)
    for ax in self.navigator.fig.axes:
      self.assertEqual(ax.get_yscale(), 'linear')
    return

  def test_p_press(self):
    for ax in self.navigator.fig.axes:
      ax.set_navigate_mode('ZOOM')
    QtTest.QTest.keyPress(self.navigator, QtCore.Qt.Key_P)
    for ax in self.navigator.fig.axes:
      self.assertEqual(ax.get_navigate_mode(), 'PAN')
    return

  def test_o_press(self):
    for ax in self.navigator.fig.axes:
      ax.set_navigate_mode('PAN')
    QtTest.QTest.keyPress(self.navigator, QtCore.Qt.Key_O)
    for ax in self.navigator.fig.axes:
      self.assertEqual(ax.get_navigate_mode(), 'ZOOM')
    return
    
  def test_home_press(self):
    self.navigator.set_xlim_online(4.5, 5.0)
    QtTest.QTest.keyPress(self.navigator, QtCore.Qt.Key_Home)
    left, right = self.ax.get_xlim()
    self.assertAlmostEqual(1.0, left)
    self.assertAlmostEqual(3.0, right, delta=.01)
    return
    
  def test_left_press(self):
    self.navigator.set_xlim_online(4.5, 5.0)
    left, right = self.ax.get_xlim()
    QtTest.QTest.keyPress(self.navigator, QtCore.Qt.Key_Left)
    left, right = self.ax.get_xlim()
    self.assertAlmostEqual(1.0, left)
    self.assertAlmostEqual(3.0, right, delta=.01)
    return

  @classmethod
  def tearDownClass(cls):
    pics = [ f for f in os.listdir(".") if f.endswith(".png") ]
    for pic in pics:
      os.remove(pic)
    return
 
if  __name__ == '__main__':
  app = QtGui.QApplication([])
  unittest.main()