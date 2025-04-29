import sys
import unittest

from measparser.mf4 import checkBlock, iterDT

if '-m' in sys.argv:
  index = sys.argv.index('-m')
  sys.argv.pop(index)
  measurement = sys.argv.pop(index)
else:
  measurement = 'D:/measurement/jochen/comparison_all_sensors_2012-10-10_13-47-25.MF4'


class TestExtractDT(unittest.TestCase):
  def setUp(self):
    self.f  = open(measurement, 'rb')
    self.link = 1302689736L
    return

  def test_checkBlock(self):
    self.assertTrue(checkBlock(self.f, self.link, '##DL'))
    return

  def test_iterDT(self):
    sizes = [size for dt, size in iterDT(self.f, self.link)]
    self.assertEqual(len(sizes), 19)
    self.assertListEqual(sizes[:-1], [10688 for i in xrange(18)])
    self.assertEqual(sizes[-1], 7328)
    return

  def tearDown(self):
    self.f.close()
    return
  pass


if __name__ == '__main__':
  unittest.main()
