from datavis import pyglet_workaround  # necessary as early as possible (#164)
import unittest
import argparse

import numpy as np

from aebs.sdf.asso_cvr3_fus_result import AssoCvr3fusResult
from aebs.sdf.asso_cvr3_fus_recalc import AssoCvr3fusCore, AssoCvr3fusRecalc, norms
from aebs.sdf.asso_cvr3_fus_resolve import AssoCvr3fusResolve
import measparser

ABS_TOL = np.float32(2) / norms['N_prob1UW_uw'] # 2 times precision

parser = argparse.ArgumentParser()
parser.add_argument('-m', '--measurement',
                    help='measurement file [=%default]',
                    default='C:/data/meas/EnduranceRun/H05_2604/2012-09-03/comparison_all_sensors_2012-09-03_14-54-20.MF4')
parser.add_argument('--backupdir',
                    help='backup directory [=%default]',
                    default=None)
args = parser.parse_args()

class AssoCvr3FusModules(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    try:
      cls.source = measparser.cSignalSource(args.measurement, NpyHomeDir=args.backupdir)
      cls.result = AssoCvr3fusResult(cls.source)
      cls.recalc = AssoCvr3fusRecalc(cls.source)
      cls.core = AssoCvr3fusCore(cls.source)
      cls.resolve = AssoCvr3fusResolve(cls.source)
    except (IOError, measparser.signalgroup.SignalGroupError), error:
      raise unittest.SkipTest(error.message)
    else:
      cls.result.calc()
      cls.recalc.calc()
      cls.core.calc()
      cls.resolve.calc()
    return

  @classmethod
  def tearDownClass(cls):
    cls.source.save()
    return

  def test_asso_core_objectpairs(self):
    self.assertTrue( self.result.objectPairs == self.core.objectPairs )
    return

  def test_asso_recalc_objectpairs(self):
    self.assertTrue( self.result.objectPairs == self.recalc.objectPairs )
    return

  def test_asso_resolve_objectpairs(self):
    self.assertTrue( self.result.objectPairs == self.resolve.objectPairs )
    return

  def test_asso_recalc_matrix(self):
    self.assertTrue( np.allclose(self.resolve.filteredAssoProb, self.recalc.filteredAssoProb, rtol=0., atol=ABS_TOL) )
    return

  def test_asso_core_cost_matrix(self):
    self.assertTrue( np.array_equal(self.recalc.C, self.core.C) )
    return

if __name__ == '__main__':
  import sys

  unittest.main(argv=[sys.argv[0]], verbosity=0)
