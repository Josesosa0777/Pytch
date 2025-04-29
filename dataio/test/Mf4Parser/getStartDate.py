import os
import sys
import time
import unittest
import argparse

from measparser.Mf4Parser import cMf4Parser

parser = argparse.ArgumentParser()
parser.add_argument('-v', action='count')
parser.add_argument('-m', default=r'C:\KBData\measurement\874\H566_2013-03-28_10-29-02.mf4')
args = parser.parse_args()

class Test(unittest.TestCase):
  @unittest.skipUnless(os.path.isfile(args.m), '%s does not exists' % args.m)
  def test_start_by_content(self):
    date = cMf4Parser.readStartDate(args.m)
    self.assertEqual(date.strftime('%Y-%m-%d %H:%M:%S'), '2013-03-28 11:29:05')
    return

  @unittest.skipUnless(os.path.isfile(args.m), '%s does not exists' % args.m)
  def test_start_by_name(self):
    date = cMf4Parser.getStartDate(args.m)
    self.assertEqual(date.strftime('%Y-%m-%d %H:%M:%S'), '2013-03-28 10:29:02')
    return

  def test_missing_file(self):
    name = 'foo.mdf'
    with self.assertRaisesRegexp(AssertionError, '%s does not exists' % name):
      cMf4Parser.getStartDate(name)
    return

if __name__ == '__main__':
  unittest.main(argv=sys.argv[:1], verbosity=args.v)
