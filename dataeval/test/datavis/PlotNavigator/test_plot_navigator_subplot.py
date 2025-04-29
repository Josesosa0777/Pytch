import unittest

from datavis.PlotNavigator import cPlotNavigator, FigureIndexError

class TestSubplotInit(unittest.TestCase):
  def test_init_zero_row_col(self):
    pn = cPlotNavigator(subplotGeom=(0,0))
    self.assertFalse(pn._isCustomSubplotMode)
    return

  def test_init_zero_row(self):
    with self.assertRaises(AssertionError):
      pn = cPlotNavigator(subplotGeom=(0,1))
    return

  def test_init_zero_col(self):
    with self.assertRaises(AssertionError):
      pn = cPlotNavigator(subplotGeom=(1,0))
    return

  def test_init_negative(self):
    with self.assertRaises(AssertionError):
      pn = cPlotNavigator(subplotGeom=(-1,-1))
    return

class TestSubplotAddAxis(unittest.TestCase):
  def setUp(self):
    self.pn = cPlotNavigator(subplotGeom=(2,2))

  def tearDown(self):
    self.pn.close()
    return

  def test_add_axis(self):
    ax = self.pn.addAxis(rowNr=1,colNr=1)
    self.assertIsNotNone(ax)
    return

  def test_add_axis_last(self):
    ax = self.pn.addAxis(rowNr=2,colNr=2)
    self.assertIsNotNone(ax)
    return

  def test_add_axis_zero_row_col(self):
    with self.assertRaises(FigureIndexError):
      ax = self.pn.addAxis(rowNr=0,colNr=0)
    return

  def test_add_axis_zero_row(self):
    with self.assertRaises(FigureIndexError):
      ax = self.pn.addAxis(rowNr=0,colNr=1)
    return

  def test_add_axis_zero_col(self):
    with self.assertRaises(FigureIndexError):
      ax = self.pn.addAxis(rowNr=1,colNr=0)
    return

  def test_add_axis_over_range_row_col(self):
    with self.assertRaises(FigureIndexError):
      ax = self.pn.addAxis(rowNr=3,colNr=3)
    return

  def test_add_axis_over_range_row(self):
    with self.assertRaises(FigureIndexError):
      ax = self.pn.addAxis(rowNr=3,colNr=2)
    return

  def test_add_axis_over_range_col(self):
    with self.assertRaises(FigureIndexError):
      ax = self.pn.addAxis(rowNr=2,colNr=3)
    return

if __name__ == '__main__':
  import sys

  from PySide import QtGui

  app = QtGui.QApplication([])
  unittest.main(argv=[sys.argv[0]])
