import unittest
import argparse

import numpy as np

from interface.manager import Manager
from measparser.signalgroup import SignalGroupError
from measparser.signalproc import isSameTime
from measparser import cSignalSource
from aebs.fill import calc_flr20_egomotion
from config.Config import init_dataeval

parser = argparse.ArgumentParser()
parser.add_argument('-m', '--measurement',
                    help='measurement file',
                    default=r'\\file\Messdat\DAS\EnduranceRun\H566PP\2013-04-09\H566_2013-04-09_06-52-13.mf4')
parser.add_argument('--backupdir',
                    help='backup directory',
                    default=None)
parser.add_argument('-v',
                    help='verbosity level',
                    default=0)
args = parser.parse_args()

class TestEgoMotionFlr20(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    config, cls.manager, manager_modules = init_dataeval(
      ['-u', args.backupdir, '-m', args.measurement] )
    fill_ = calc_flr20_egomotion.Calc(cls.manager, 'aebs.fill')
    try:
      check_result = manager_modules.calc('calc_flr20_egomotion@aebs.fill', cls.manager)
    except (IOError, SignalGroupError), error:
      raise unittest.SkipTest(error.message)
    else:
      cls.result = manager_modules.fill('calc_flr20_egomotion@aebs.fill')
    return

  @classmethod
  def tearDownClass(cls):
    cls.manager.close()
    return

  def test_attribs_present(self):
    ATTRIBS = ('time', 'vx', 'yaw_rate', 'ax')
    ego_motion = self.result
    for attr in ATTRIBS:
      self.assertTrue(hasattr(ego_motion, attr),
                      'non-existing attribute: %s' % attr)
    return

  def test_shapes_equal(self):
    ego_motion = self.result
    for attr in ego_motion.__dict__:
      if attr == 'time':
        continue
      self.assertTrue(getattr(ego_motion, attr).shape == ego_motion.time.shape,
                      'shape mismatch: time and %s' % attr)
    return

class TestIsLeftPositiveFlr20(unittest.TestCase):
  def test_isleftpositive(self):
    MEAS_AND_RESULTS = {
      r'\\file\Messdat\DAS\EnduranceRun\H05_2604\2012-08-22\comparison_all_sensors_2012-08-22_17-05-15.MF4':
        True,
      r'\\file\Messdat\DAS\EnduranceRun\H05_2604\2012-12-05\comparison_all_sensors_2012-12-05_17-59-35.MF4':
        False,
      r'\\file\Messdat\DAS\EnduranceRun\H566PP\2013-05-16\H566_2013-05-16_13-30-54.mf4':
        False,
    }
    try:
      for meas, result in MEAS_AND_RESULTS.iteritems():
        source = cSignalSource(meas)
        left_positive = calc_flr20_egomotion.is_left_positive(source, exception=True)
        source.save()
        self.assertTrue(left_positive == result, 'incorrect y axis direction')
      source = cSignalSource(args.measurement)
      calc_flr20_egomotion.is_left_positive(source, exception=True)
      source.save()
    except IOError, error:
      raise unittest.SkipTest(error.message)
    return

if __name__ == '__main__':
  import sys

  unittest.main(argv=[sys.argv[0]], verbosity=args.v)

