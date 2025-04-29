import os
import shutil
import unittest

import numpy as np

from measparser.BackupParser import BackupParser

class TestAddSignal(unittest.TestCase):
  def setUp(self):
    self.meas = 'foo'
    self.dir = 'bar'
    self.npydir = os.path.join(self.dir, self.meas)
    self.parser = BackupParser(self.npydir, self.meas, 'v0.0', 'v0.0', '')
    return

  def test_add_signal(self):
    signal = [0, 1]
    timekey = '5'
    self.parser.addSignal('Egg', 'Spam', timekey, signal)
    sig, tk = self.parser.getSignal('Egg', 'Spam')
    self.assertTrue(np.array_equal(sig, signal))
    self.assertEqual(timekey, tk)
    return

  def test_add_time(self):
    time = [0, 1]
    timekey = '5'
    self.parser.addTime(timekey, time)
    t = self.parser.getTime(timekey)
    self.assertTrue(np.array_equal(time, t))
    return


  def tearDown(self):
    shutil.rmtree(self.dir)
    return

if __name__ == '__main__':
  unittest.main()