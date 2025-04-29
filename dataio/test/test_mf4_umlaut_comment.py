import os
import unittest

from measparser.Mf4Parser import cMf4Parser

default_meas = r'd:\measurement\430\ae\MAN_AEBS_ACC_2012-11-06_14-07-46.MF4'
meas = os.getenv('TEST_MEAS', default_meas)

class Test(unittest.TestCase):
  @unittest.skipUnless(os.path.isfile(meas), '%s is not present' %meas)
  def test(self):
    try:
      parser = cMf4Parser(meas)
    except UnicodeError:
      self.assertTrue(False)
    return
  pass

if __name__ == '__main__':
  unittest.main()
