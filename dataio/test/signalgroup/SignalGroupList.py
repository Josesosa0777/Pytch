import os
import shutil
import unittest
from collections import OrderedDict

import numpy

from measparser.BackupParser import BackupParser
from measparser.signalgroup import SignalGroupList
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
    source.addSignal('d', 's0', 't', cls.value)
    source.addSignal('d', 's1', 't', cls.value)
    source.addSignal('r', 's0', 't', cls.value)
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
    validated = [
      {'s': ('d', 's0')},
      {'s': ('d', 's1')},
    ]
    winner = 0
    signalgroups = SignalGroupList(winner, validated, self.source)
    self.assertListEqual(signalgroups, validated)
    self.assertEqual(signalgroups.winner, 0)
    return
    
  def test_from_first_allvalid(self):
    super_signalgroups = [
      [{'s': ('d', 's0')}, {'s': ('d', 's1')}],
      [{'s': ('r', 's0')}, {'s': ('r', 's1')}],
    ]
    signalgroups = SignalGroupList.from_first_allvalid(super_signalgroups,
                                                       self.source)
    self.assertListEqual(signalgroups, [{'s': ('d', 's0')}, {'s': ('d', 's1')}])
    self.assertEqual(signalgroups.winner, 0)
    return

  def test_from_arbitrary(self):
    arbitrary = [
      {'s': ('r', 's0')},
      {'s': ('r', 's1')},
    ]
    signalgroups = SignalGroupList.from_arbitrary(arbitrary, self.source)
    self.assertListEqual(signalgroups, [{'s': ('r', 's0')}])
    self.assertIsNone(signalgroups.winner)
    return

class TestMethods(SetUpConstructor):
  def setUp(self):
    self.signalgroups = SignalGroupList(0,
                                        [{'s': ('d', 's0')}, {'s': ('d', 's1')}],
                                        self.source)
    return

  def test_get_value(self):
    values = self.signalgroups.get_value('s')
    self.assertEqual(len(values), 2)
    for value in values:
      self.assertTrue(numpy.allclose(value, self.value))
    return

  def test_get_value(self):
    super_values = self.signalgroups.get_values(['s'])
    self.assertEqual(len(super_values), 2)
    for values in super_values:
      self.assertListEqual(values.keys(), ['s'])
      for value in values.itervalues():
        self.assertTrue(numpy.allclose(value, self.value))
    return

  def test_select_time_scale(self):
    time = self.signalgroups.select_time_scale()
    self.assertTrue(numpy.allclose(time, self.time))
    return


unittest.main()
