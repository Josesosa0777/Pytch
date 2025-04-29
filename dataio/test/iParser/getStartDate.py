import os
import time
import unittest

from measparser.iParser import iParser

class Test(unittest.TestCase):
  def test_start_by_pattern(self):
    date = iParser.getStartDate('foo_1970-01-01_07-44-56.mdf')
    self.assertEqual(date.strftime('%Y-%m-%d %H:%M:%S'), '1970-01-01 07:44:56')
    return

  def test_missing_file(self):
    name = 'foo.txt'
    with self.assertRaisesRegexp(AssertionError, '%s does not exists' % name):
      iParser.getStartDate(name)
    return

  def test_start_by_creation_time(self):
    name = 'bar.txt'
    open(name, 'w')
    date = iParser.getStartDate(name)
    self.assertEqual(time.mktime(date.timetuple()), int(os.path.getctime(name)))
    os.remove(name)
    return

if __name__ == '__main__':
  unittest.main()
