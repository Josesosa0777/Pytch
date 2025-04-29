import sys
import unittest

import numpy as np
from PySide import QtGui, QtCore, QtTest

from datavis.Synchronizer import cSynchronizer
from datavis.PlotNavigator import cPlotNavigator

class NavigatorFunction(unittest.TestCase):
  @classmethod
  def setUp(cls): 
    cls.sync = cSynchronizer()
    
    t = np.arange(0,400,0.01)
    
    cls.pn1 = cPlotNavigator("First plot window")
    cls.pn1.addsignal('sine' ,  [t, np.sin(t)])
    cls.pn1.addsignal('cosine', [t, np.cos(t)])
    cls.sync.addClient(cls.pn1)
    
    cls.pn2 = cPlotNavigator("Second plot window")
    cls.pn2.addsignal('sine' ,  [t, np.sin(t)])
    cls.pn2.addsignal('cosine', [t, np.cos(t)])
    cls.sync.addClient(cls.pn2)
    cls.sync.start()
    cls.sync.show()
    return
    
  def test_play(self):
    self.pn1.onPlay(3.0)
    self.assertTrue(self.pn1.playing)
    self.assertTrue(self.pn2.playing)
    return
    
  def test_pause(self):
    self.pn1.onPlay(2.0)
    self.pn2.onPause(3.0)
    self.assertFalse(self.pn1.playing)
    self.assertFalse(self.pn2.playing)
    self.assertAlmostEqual(self.pn1.time, 3.0)
    self.assertAlmostEqual(self.pn2.time, 3.0)
    return
    
  def test_seek(self):
    self.pn1.onSeek(2.5)
    self.assertAlmostEqual(self.pn1.time, 2.5)
    self.assertAlmostEqual(self.pn2.time, 2.5)
    return
    
  def test_setROI(self):
    self.pn2.onSetROI(1.1, 2.2, 'r')
    ROIStart, ROIEnd = self.pn1.ROIstart, self.pn1.ROIend
    self.assertAlmostEqual(ROIStart, 1.1)
    self.assertAlmostEqual(ROIEnd, 2.2)
    return
    
if  __name__ == '__main__':
  app = QtGui.QApplication([])
  unittest.main()