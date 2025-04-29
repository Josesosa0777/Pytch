import os
import sys
import time
import unittest
import argparse

from measparser.MdfParser import cMdfParser

parser = argparse.ArgumentParser()
parser.add_argument('-v', action='count')
parser.add_argument('-m', default='VTC6200_022_2013-07-22_09-40-08.MDF')
args = parser.parse_args()

class Test(unittest.TestCase):
  @unittest.skipUnless(os.path.isfile(args.m), '%s does not exists' % args.m)
  def test_start_by_name(self):
    date = cMdfParser.getStartDate(args.m)
    self.assertEqual(date.strftime('%Y-%m-%d %H:%M:%S'), '2013-07-22 09:40:08')
    return

  @unittest.skipUnless(os.path.isfile(args.m), '%s does not exists' % args.m)
  def test_start_by_content(self):
    date = cMdfParser.readStartDate(args.m)
    self.assertEqual(date.strftime('%Y-%m-%d %H:%M:%S'), '2013-07-22 10:40:09')
    return

  def test_missing_file(self):
    name = 'foo.mdf'
    with self.assertRaisesRegexp(AssertionError, '%s does not exists' % name):
      cMdfParser.getStartDate(name)
    return

if __name__ == '__main__':
  unittest.main(argv=sys.argv[:1], verbosity=args.v)
