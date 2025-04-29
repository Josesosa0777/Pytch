import os
import sys
import unittest
import argparse

import numpy

from measparser.Mf4Parser import cMf4Parser

parser = argparse.ArgumentParser()
parser.add_argument('-v', action='count', default=0,
                    help='incrementable verbosity level')
parser.add_argument('-m', default='2013-07-08-07-28-20.MF4',
                    help='measurement file name')
args = parser.parse_args()


@unittest.skipUnless(os.path.isfile(args.m), '%s is not present' % args.m)
class Test(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.dev_name = 'General_radar_status--Message--A087MB_V3_2_MH8_truck'
    cls.sig_name = 'cm_system_status'
    cls.parser = cMf4Parser(args.m)
    return
  
  def test_no_rule_print(self):
    stderr = sys.stderr
    sys.stderr = open('stderr', 'w')
    value, tk = self.parser.getSignal(self.dev_name, self.sig_name)
    self.assertEqual(sys.stderr.tell(), 0)
    sys.stderr.close()
    sys.stderr = stderr
    os.remove('stderr')
    return

  def test_getConversionRule(self):
    rule = self.parser.getConversionRule(self.dev_name, self.sig_name)
    self.assertDictEqual(rule, 
      {0: u'NOT_ALLOWED',
       1: u'ALLOWED',
       2: u'WARNING',
       3: u'BRAKING',
       4: u'WAITING',
       'default': 'unknown'})
    return

  def test_value_read(self):
    value, tk = self.parser.getSignal(self.dev_name, self.sig_name)
    self.assertTrue(numpy.array_equal(value,
                                      numpy.zeros(600, dtype=numpy.uint8)))
    return

  def test_missing_rule(self):
    dev_name = 'Tracks--Message--A087MB_V3_2_MH8_truck'
    sig_name = 'tr9_relative_velocitiy'
    rule = self.parser.getConversionRule(dev_name, sig_name)
    self.assertDictEqual(rule, {})
    return

if __name__ == '__main__':
  unittest.main(argv=sys.argv[:1], verbosity=args.v)

