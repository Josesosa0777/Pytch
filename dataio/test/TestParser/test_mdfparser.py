import unittest
import os
import sys

from measparser.MdfParser import cMdfParser


file_name = r"C:\KBData\Measurement\all_format_meas\mdf\1240134.MDF"

if not os.path.isfile(file_name):
    sys.stderr.write('Measurement file does not exist\n')
    sys.exit(-1)


class MatParser(unittest.TestCase):
    def setUp(self):
        self.mdf_object = cMdfParser(file_name)
        return

    def test_getSignal(self):
        time = u'00056'
        dev_name = u'ACC_S22-9CFFEC2A-2-ACC'
        sig_name = u'debug_cancel_global_cond'

        value, timekey = self.mdf_object.getSignal(dev_name, sig_name)
        self.assertTrue(value.size != 0 and timekey == time)
        return


if __name__ == '__main__':
    unittest.main()
    pass
