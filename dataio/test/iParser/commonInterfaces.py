import os
import time
import unittest

from measparser.iParser import iParser

class Test(unittest.TestCase):
  def setUp(self):
    self.parser = iParser()
    return

  def test_save(self):
    self.parser.save()
    return

  def test_add_signal(self):
    self.parser.addSignal('ECU', 'Vx', 5, [0, 1])
    return

  def test_add_time(self):
    self.parser.addTime(5, [0, 1])
    return

  def test_get_signal(self):
    with self.assertRaises(KeyError):
      self.parser.getSignal('ECU', 'Radar')
    return

  def test_get_signal(self):
    with self.assertRaises(KeyError):
      self.parser.getTime(5)
    return

if __name__ == '__main__':
  unittest.main()
