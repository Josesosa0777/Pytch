import os
import shutil
import unittest
from collections import OrderedDict

import numpy

from measparser.BackupParser import BackupParser
from measparser.signalgroup import SignalGroup
from measparser.SignalSource import cSignalSource


class SetUpConstructor(unittest.TestCase):
  backup = os.path.abspath('backup')
  measurement = os.path.abspath('foo.mdf')

  @classmethod
  def setUpClass(cls):
    source = BackupParser.fromFile(cls.measurement, cls.backup)
    cls.time = numpy.arange(0, 10, 1e-2)
    cls.value = numpy.sin(cls.time)

    source.addTime('t', cls.time)
    source.addSignal('d', 's', 't', cls.value)
    source.addSignal('d', 'z', 't', cls.value)
    source.addSignal('r', 's', 't', cls.value)
    source.save()

    cls.source = cSignalSource(os.path.join(cls.backup,
                                            os.path.basename(cls.measurement)))
    return

  @classmethod
  def tearDownClass(cls):
    shutil.rmtree(cls.backup)
    return

class TestConstructor(SetUpConstructor):
  def test_constructor(self):
    validated = {'s': ('d', 's')}
    winner = 0
    signalgroup = SignalGroup(winner, validated, self.source)
    self.assertDictEqual(signalgroup, validated)
    self.assertEqual(signalgroup.winner, 0)
    return

  def test_from_names_signalgroups(self): 
    signalgroups = OrderedDict([
     ('a', {'s': ('d', 's')}),
     ('b', {'s': ('e', 's')}),
    ])
    signalgroup = SignalGroup.from_named_signalgroups(signalgroups, self.source)
    self.assertDictEqual(signalgroup, {'s': ('d', 's')})
    self.assertEqual(signalgroup.winner, 'a')
    return

  def test_from_first_valid(self):
    signalgroups = [
     {'s': ('d', 's')},
     {'s': ('e', 's')},
    ]
    signalgroup = SignalGroup.from_first_valid(signalgroups, self.source)
    self.assertDictEqual(signalgroup, {'s': ('d', 's')})
    self.assertEqual(signalgroup.winner, 0)
    return

  def test_from_longest(self):
    signalgroups = [
     {'s': ('d', 's'), 'z': ('d', 'z')},
     {'s': ('r', 's'), 'z': ('r', 'z')},
    ]
    signalgroup = SignalGroup.from_longest(signalgroups, self.source)
    self.assertDictEqual(signalgroup, {'s': ('d', 's'), 'z': ('d', 'z')})
    self.assertEqual(signalgroup.winner, 0)
    return

  def test_from_longest_empty(self):
    signalgroups = [
     {'s': ('dd', 's'), 'z': ('dd', 'z')},
     {'s': ('rr', 's'), 'z': ('rr', 'z')},
    ]
    signalgroup = SignalGroup.from_longest(signalgroups, self.source)
    self.assertDictEqual(signalgroup, {})
    self.assertEqual(signalgroup.winner, 0)
    return

class TestMethods(SetUpConstructor):
  def setUp(self):
    self.signalgroup = SignalGroup(0, {'s': ('d', 's'), 'z': ('d', 'z')},
                                   self.source)
    return

  def test_get_signal(self):
    time, value = self.signalgroup.get_signal('s')
    self.assertTrue(numpy.allclose(time, self.time))
    self.assertTrue(numpy.allclose(value, self.value))
    return

  def test_get_signal_with_unit(self):
    time, value, unit = self.signalgroup.get_signal_with_unit('s')
    self.assertTrue(numpy.allclose(time, self.time))
    self.assertTrue(numpy.allclose(value, self.value))
    self.assertEqual(unit, '')
    return

  def test_get_value(self):
    value = self.signalgroup.get_value('s')
    self.assertTrue(numpy.allclose(value, self.value))
    return

  def test_get_time(self):
    time = self.signalgroup.get_time('z')
    self.assertTrue(numpy.allclose(time, self.time))
    return

  def test_get_signal_with_unit(self):
    unit = self.signalgroup.get_unit('s')
    self.assertEqual(unit, '')
    return

  def test_get_values(self):
    values = self.signalgroup.get_values(['s', 'z'])
    self.assertListEqual(values.keys(), ['s', 'z'])
    for value in values.itervalues():
      self.assertTrue(numpy.allclose(value, self.value))
    return

  def test_get_all_values(self):
    values = self.signalgroup.get_all_values()
    self.assertListEqual(values.keys(), ['s', 'z'])
    for value in values.itervalues():
      self.assertTrue(numpy.allclose(value, self.value))
    return

  def test_get_times(self):
    times = self.signalgroup.get_times(['s', 'z'])
    self.assertListEqual(times.keys(), ['s', 'z'])
    for time in times.itervalues():
      self.assertTrue(numpy.allclose(time, self.time))
    return

  def test_get_all_times(self):
    times = self.signalgroup.get_all_times()
    self.assertListEqual(times.keys(), ['s', 'z'])
    for time in times.itervalues():
      self.assertTrue(numpy.allclose(time, self.time))
    return

  def test_get_unit(self):
    unit = self.signalgroup.get_unit('z')
    self.assertEqual(unit, '')
    return

  def test_select_time_scale(self):
    time = self.signalgroup.select_time_scale()
    self.assertTrue(numpy.allclose(time, self.time))
    return

  

unittest.main()

