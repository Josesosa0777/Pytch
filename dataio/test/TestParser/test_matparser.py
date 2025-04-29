import unittest
import os
import sys

from measparser.MatParser import cMatParser


file_name = r"C:\KBData\Measurement\all_format_meas\mat\2021.02.09_at_20.33.41_radar-mi_5031.mat"

if not os.path.isfile(file_name):
    sys.stderr.write('Measurement file does not exist\n')
    sys.exit(-1)


class MatParser(unittest.TestCase):
    def setUp(self):
        self.mat_object = cMatParser(file_name)
        return

    def test_getSignal(self):
        time = u't_ACC1_2A_s2A_ACC1_2A_CAN21'
        dev_name = u'ACC1_2A_s2A_ACC1_2A_CAN21'
        sig_name = u'AdaptiveCruiseCtrlMode'

        value, timekey = self.mat_object.getSignal(dev_name, sig_name)
        self.assertTrue(value.size != 0 and timekey == time)
        return


if __name__ == '__main__':
    unittest.main()
    pass
