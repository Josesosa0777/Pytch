import os
import sys
import unittest

import numpy
from PySide import QtGui, QtCore, QtTest

import matplotlib as mpl


from datavis.SituationNavigator import cSituationNavigator
from datavis.SituationNavigator import cSituationModule
import measproc

t = numpy.arange(0, 20, 0.01)
y = numpy.sin(t)
z = numpy.cos(t)

names = ['Egg', 'Spam']

values = {'Egg': y, 'Spam': z}

i1 = measproc.cEventFinder.compExtSigScal(t, y, measproc.greater, 0.5)
i2 = measproc.cEventFinder.compExtSigScal(t, z, measproc.greater, 0.5)
intervals1 = {'i1' : i1, }
intervals2 = {'i2' : i2, }

name_2_interval = {
                    'Egg' : 'i1',
                    'Spam' : 'i2',
                  }

class TestSituationNavigator(unittest.TestCase):
  def setUp(self):
    self.sms = []
    self.sms.append(cSituationModule('Foo', 'Egg', intervallists=intervals1))
    self.sms.append(cSituationModule('Bar', 'Spam', intervallists=intervals2))
    self.navigator = cSituationNavigator(self.sms)

    self.init_navigator()
    return

  def init_navigator(self):
    self.navigator.start()
    self.navigator.seek(12.5)
    return

  def tearDown(self):
    self.navigator.close()
    return
    
  def test_plot_signals(self):
    signals = self.navigator.getplotsignals()
    for signal_name in names:
      time, signal = signals[signal_name][1]
      self.assertTrue(numpy.array_equal(time, t))
      for i in range(len(signal)):
        if values[signal_name][i] > 0.5:
          self.assertTrue(signal[i])
        else:
          self.assertFalse(signal[i])
    return
    
  def test_seek(self):
    in_radian_45_degree = 45 / 180.0 * numpy.pi
    self.navigator.seek(in_radian_45_degree)
    self.assertEqual(len(self.navigator.text), len(self.sms))
    signals = self.navigator.getplotsignals()
    text = ''
    expected_text =  ''
    for child in self.navigator.fig.get_children():
      if type(child) == mpl.text.Text:
        text = child.get_text()
        
        for name in names:
          time, signal = signals[name][1]
          min = signal.min()
          max = signal.max()
          expected_text += '\n.:|%s|:.\n%s\n(%.1f-%.1f)\n' %(name, name_2_interval[name], min, max)
    self.assertNotEqual(text, '')
    self.assertEqual(text, expected_text)
    self.navigator.seek(numpy.pi)
    self.assertEqual(len(self.navigator.text), len(self.sms))
    for child in self.navigator.fig.get_children():
      if type(child) == mpl.text.Text:
        self.assertEqual(child.get_text(), '')
    return

if  __name__ == '__main__':
  app = QtGui.QApplication([])
  unittest.main()