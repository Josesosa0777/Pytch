import unittest
import argparse

import numpy as np

from config.Config import init_dataeval
from measparser.signalgroup import SignalGroupError
from aebs.sdf import asso_flr20_fus_result
from asso.interface import pairs2occurence

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

class TestFlr20AssoResult(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    config, manager, modules = init_dataeval( ['-u', args.backupdir, '-m', args.measurement] )
    manager.set_measurement(args.measurement)
    manager.set_backup(args.backupdir)
    cls.manager = manager
    try:
      tracks = modules.calc('fill_flr20_raw_tracks@aebs.fill', manager)
    except (IOError, SignalGroupError), error:
      raise unittest.SkipTest(error.message)
    else:
      cls.a = asso_flr20_fus_result.Flr20AssoResult(tracks)
      cls.a.calc()
    return

  @classmethod
  def tearDownClass(cls):
    cls.manager.close()
    return

  def test_is_asso_done(self):
    self.assertTrue(self.a.isAssoDone)
    return

  def test_object_pairs_length(self):
    self.assertEqual( len(self.a.objectPairs), self.a.N )
    return

  def test_asso_data_length(self):
    for (i,j), indices in self.a.assoData.iteritems():
      size = len(indices)
      self.assertTrue( size<= self.a.N,
                       msg="%d,%d has more than %d pairings: %d" %(i,j,self.a.N,size))
    return

  def test_asso_data_equivalent_to_object_pairs(self):
    assoData = pairs2occurence(self.a.objectPairs)
    self.assertEqual(assoData, self.a.assoData)
    return

  def test_is_asso_successful_agrees_obj_pairs(self):
    objPairsLength = map(len, self.a.objectPairs)
    isAssoSuccessful = np.array(objPairsLength, dtype=np.bool)
    self.assertTrue( np.array_equal(isAssoSuccessful, self.a.isAssoSuccessful) )
    return

  def test_max_num_of_associations(self):
    if np.any(self.a.isAssoSuccessful):
      self.assertTrue(self.a.maxNumOfAssociations > 0)
    else:
      self.assertTrue(self.a.maxNumOfAssociations == 0)
    return

if __name__ == '__main__':
  import sys

  unittest.main(argv=[sys.argv[0]], verbosity=args.v)
