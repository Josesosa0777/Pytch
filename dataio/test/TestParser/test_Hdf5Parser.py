import unittest
import os
import sys

from measparser.Hdf5Parser import cHdf5Parser


h5_name = r"C:\KBData\Measurement\all_format_meas\h5\2021.02.09_at_20.33.41_radar-mi_5031.h5"

if not os.path.isfile(h5_name):
    sys.stderr.write('Measurement file does not exist\n')
    sys.exit(-1)


class Hdf5Parser(unittest.TestCase):
    def setUp(self):
        self.h5 = cHdf5Parser(h5_name)
        return

    def test_getSignal(self):
        time = u't_ACC1_2A_s2A_ACC1_2A_CAN21'
        dev_name = u'ACC1_2A_s2A_ACC1_2A_CAN21'
        sig_name = u'AdaptiveCruiseCtrlMode'

        h5_value, timekey = self.h5.getSignal(dev_name, sig_name)
        self.assertTrue(h5_value.size != 0 and timekey == time)
        return


if __name__ == '__main__':
    unittest.main()
    pass
