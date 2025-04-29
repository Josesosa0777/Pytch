import unittest

import numpy as np

from nputils.min_dtype import min_typecode

ranges = {
  np.bool   : ( (0,1), ),
  np.uint8  : ( (0,2), (0,255) ),
  np.int8   : ( (0,-1), (-128, 127) ),
  np.uint16 : ( (0,256), (0, 65535) ),
  np.int16  : ( (-1,128), (-129,0), (-32768, 32767) ),
  np.uint32 : ( (0,65536), (0, 4294967295) ),
  np.int32  : ( (-1,32768), (-32769,0), (-2147483648, 2147483647) ),
  np.uint64 : ( (0,4294967296), ), #(0, 18446744073709551615) ), # np.asarray results float array for some reason (?)
  np.int64  : ( (-1,2147483648), (-9223372036854775808, 9223372036854775807) ),
}

class TestMinDtype(unittest.TestCase):
  def _test_min_dtype(self, arr, req_dtype):
    out_dtype = min_typecode(arr)
    self.assertTrue(out_dtype == req_dtype,
                    msg="output %s does not fit required dtype %s for input %s"
                        %(out_dtype, req_dtype, arr))
    return

  def test_basic(self):
    for t, values in ranges.iteritems():
      for arr in values:
        self._test_min_dtype(arr, t)
    return

  def test_float(self):
    with self.assertRaises(ValueError):
      out_dtype = min_typecode((0.1, 1.2))
    return

if __name__ == '__main__':
  unittest.main()
