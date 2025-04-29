import unittest

import numpy as np

from nputils.array import recarray_to_dict, dict_to_recarray


class TestRecArray(unittest.TestCase):
  def setUp(self):
    # 2-level nested dtype
    dtype2 = np.dtype( [('field2_0', np.bool),
                        ('field2_1', np.int8),
                        ('field2_2', np.float32)] )
    # 1-level nested dtype
    dtype1 = np.dtype( [('field1_0', dtype2),
                        ('field1_1', dtype2)] )
    # main dtype
    dtype0 = np.dtype( [('field0_0', np.float32),
                        ('field0_1', dtype1),] )
    self.arr = np.empty(10, dtype=dtype0) # random data
    self.arr = self.arr.view(np.recarray)
    return

  def test_recarray_to_dict_to_recarray(self):
    d = recarray_to_dict(self.arr)
    arr = dict_to_recarray(d)
    self.assertTrue( np.all(self.arr == arr) )
    return

if __name__ == '__main__':
  unittest.main()
