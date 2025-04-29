import unittest

import numpy as np
from PySide import QtGui, QtCore, QtTest

from datavis.ListNavigator import cListNavigator

start_time = 1e13  # to check that no OverflowError occurs
duration = 600.0
resolution = 0.001
t = np.arange(start_time, start_time+duration, resolution)
Qt_red = QtCore.Qt.red

class Build(unittest.TestCase):
  def setUp(self):
    self.navigator = cListNavigator()
    self.init_navigator()
    return

  def init_navigator(self):
    self.navigator.addsignal('sine' ,(t , np.sin(t)), "bla")
    self.navigator.addsignal('sine2' ,(t , np.sin(t)), "bla")
    self.navigator.addsignal('sine3' ,(t , np.sin(t)), "bla")
    self.navigator.addsignal('sine' ,(t , np.sin(t)), "egg")
    self.navigator.addsignal('sine5' ,(t , np.sin(t)), "egg")
    self.navigator.addsignal('sine6' ,(t , np.sin(t)), "egg")
    self.navigator.start()
    return

  def tearDown(self):
    self.navigator.close()
    return

  def set_current_tab(self, tab_name):
    for i in range(self.navigator.pw.count()):
      if self.navigator.pw.tabText(i) == tab_name:
        self.navigator.pw.setCurrentIndex(i)
    return

  def get_signal_label_values(self, groupname, signal_name):
    signals = self.navigator.groups[groupname]['signals']
    for signal in signals:
      if signal['name'] == signal_name:
        label_value = float(signal['qtLabel'].text())
        yield label_value
    return

  def check_signal_label(self, groupname, signalname, correct_value):
    signal_label_values = self.get_signal_label_values(groupname, signalname)

    for signal_label_value in signal_label_values:
      self.assertAlmostEqual(correct_value, signal_label_value)
    return

class TestAddSignal(Build):
  def init_navigator(self):
    return

  def test_add_signal(self):
    self.navigator.addsignal('sine' ,(t , np.sin(t)), "bla")
    self.navigator.addsignal('sine' ,(t , np.sin(t)))
    self.navigator.addsignal('cos' ,(t , np.cos(t)))

    self.check_signals()
    return

  def test_add_signals(self):
    self.navigator.addsignals([{'name' : 'sine', 'time' : t, 
                               'signal' : np.sin(t)}], groupname="bla")
    self.navigator.addsignals([
                           {'name' : 'sine', 'time' : t, 'signal' : np.sin(t)},
                           {'name' : 'cos', 'time' : t, 'signal' : np.cos(t)}
                             ])

    self.check_signals()
    return

  def test_plus_operator(self):
    self.navigator += [
                           {'name' : 'sine', 'time' : t, 'signal' : np.sin(t)},
                           {'name' : 'cos', 'time' : t, 'signal' : np.cos(t)}
                      ]

    self.navigator.start()

    self.navigator.seek(start_time + 5.5)
    correct_value_sin = np.sin(start_time + 5.5)
    correct_value_cos = np.cos(start_time + 5.5)

    self.assertIn('Default', self.navigator.groups)

    self.check_signal_label('Default', 'sine', correct_value_sin)
    self.check_signal_label('Default', 'cos', correct_value_cos)
    return

  def test_add_nested_list_as_signal(self):
    array = [ (25, 25) for i in range(len(t))]
    signal = np.array(array, dtype=object)
    self.navigator.addsignal('nested_array' ,(t , signal))

    self.navigator.start()
    self.navigator.seek(start_time + 5.5)

    signals = self.navigator.groups['Default']['signals']
    for signal in signals:
      if signal['name'] == 'nested_array':
        label_value = signal['qtLabel'].text()
        self.assertEqual(label_value, '[25 25]')
    return

  def check_signals(self):
    self.navigator.start()

    self.navigator.seek(start_time + 5.5)
    correct_value_sin = np.sin(start_time + 5.5)
    correct_value_cos = np.cos(start_time + 5.5)

    self.assertIn('bla', self.navigator.groups)
    self.assertIn('Default', self.navigator.groups)

    self.check_signal_label('Default', 'sine', correct_value_sin)
    self.check_signal_label('Default', 'cos', correct_value_cos)

    self.set_current_tab('bla')

    self.check_signal_label('bla', 'sine', correct_value_sin)
    signal_label_values = self.get_signal_label_values('bla', 'cos')
    self.assertEqual(len(list(signal_label_values)), 0)
    return

  def test_color(self):
    self.navigator.addsignal('sine' ,(t , np.sin(t)), "bla", bg='red')
    self.navigator.start()

    colors = [signal['bg'] for signal in self.navigator.groups['bla']['signals']
                    if signal['name'] == 'sine']

    self.assertEqual(colors, [Qt_red])

    scroll_frame = self.navigator.groups['bla']['frame']

    frame = scroll_frame.widget()

    labels = [child for child in frame.children()
                 if type(child) == QtGui.QLabel]
    sine_labels = [label for label in labels if label.text() == 'sine']
    for sine_label in sine_labels:
      palette = sine_label.palette()
      color = palette.color(sine_label.backgroundRole())
      self.assertEqual(color, QtGui.QColor(Qt_red))
    return

class TestGui(Build):    
  def setUp(self):
    Build.setUp(self)
    self.args = None
    self.navigator.seekSignal.signal.connect(self.save_args)
    return

  def save_args(self, *args):
    self.args = args
    return

  def test_tab_change(self):
    self.navigator.seek(start_time + 5.5)

    value = np.sin(start_time)
    self.check_signal_label('bla', 'sine', value)

    self.set_current_tab('bla')

    value = np.sin(start_time + 5.5)
    self.check_signal_label('bla', 'sine', value)
    return

  def test_slider_change(self):
    self.navigator.seek(start_time + 5.5)
    slider_value = self.navigator.timeScale.value()
    self.assertAlmostEqual(slider_value, start_time + 5.5)

    new_time = start_time + 7.5
    self.navigator.timeScale.setValue(new_time)
    time, = self.args
    self.assertAlmostEqual(time, new_time)
    return

if  __name__ == '__main__':
  app = QtGui.QApplication([])
  unittest.main()
