import sys
import unittest

import numpy as np
from PySide import QtGui, QtCore, QtTest

from datavis.Synchronizer import cSynchronizer
from datavis.PlotNavigator import cPlotNavigator

class Build:
 def setUp(self): 
    self.sync = cSynchronizer()
    
    t = np.arange(0,400,0.01)
    
    self.pn1 = cPlotNavigator("First plot window")
    self.pn1.addsignal('sine' ,  [t, np.sin(t)])
    self.pn1.addsignal('cosine', [t, np.cos(t)])
    self.sync.addClient(self.pn1)
    
    self.pn2 = cPlotNavigator("Second plot window")
    self.pn2.addsignal('sine' ,  [t, np.sin(t)])
    self.pn2.addsignal('cosine', [t, np.cos(t)])
    self.sync.addClient(self.pn2)
    self.sync.start()
    self.sync.show()
    return

class TestClick(Build, unittest.TestCase): 
  def test_seek(self):    
    clicked_point = QtCore.QPoint(self.pn1.width()/2, self.pn1.height()/3)
    QtTest.QTest.mouseClick(self.pn1.canvas,
                                        QtCore.Qt.LeftButton, pos=clicked_point)
    self.assertNotEqual(0.0, self.pn1.time)
    self.assertAlmostEqual(self.pn1.time, self.pn2.time)
    self.sync.close()
    return
    
  def test_play(self):
    QtTest.QTest.keyClick(self.pn1, QtCore.Qt.Key_Space)
    self.assertTrue(self.pn1.playing)
    self.assertTrue(self.pn2.playing)
    self.sync.close()
    return
    
  def test_pause(self):
    QtTest.QTest.keyClick(self.pn2, QtCore.Qt.Key_Space)
    QtTest.QTest.keyClick(self.pn2, QtCore.Qt.Key_Space)
    self.assertFalse(self.pn1.playing)
    self.assertFalse(self.pn2.playing)
    self.assertAlmostEqual(self.pn1.time, self.pn2.time)
    self.sync.close()
    return
    
  

class TestRoi(Build, unittest.TestCase): 
  def test_setROI(self):
    pressed_point = QtCore.QPoint(self.pn1.width()/3, self.pn1.height()/3)
    released_point = QtCore.QPoint(self.pn1.width()/2, self.pn1.height()/3)
    QtTest.QTest.keyPress(self.pn1, QtCore.Qt.Key_Shift)
    QtTest.QTest.mousePress(self.pn1.canvas,
                                        QtCore.Qt.LeftButton, pos=pressed_point)
    QtTest.QTest.mouseMove(self.pn1.canvas, pos=released_point)
    QtTest.QTest.mouseRelease(self.pn1.canvas, QtCore.Qt.LeftButton,
                              pos=released_point)
    QtTest.QTest.keyRelease(self.pn1, QtCore.Qt.Key_Shift)
    ROIStart, ROIEnd = self.pn2.ROIstart, self.pn2.ROIend
    self.assertNotEqual(ROIStart, ROIEnd)
    self.sync.close()
    return
    
if  __name__ == '__main__':
  app = QtGui.QApplication([])
  unittest.main()