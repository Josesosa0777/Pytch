import unittest
import os
import sys

from measparser.DatParser import cDatParser


file_name = r"C:\KBData\__PythonToolchain\Meas\TrailerTeam\Dauerlauf_itebsx_2022_03_23-09-04-10.DAT"

if not os.path.isfile(file_name):
    sys.stderr.write('Measurement file does not exist\n')
    sys.exit(-1)


class MatParser(unittest.TestCase):
    def setUp(self):
        self.dat_object = cDatParser(file_name)
        return

    def test_getSignal(self):
        time = u'Dauerlauf_itebsx_2022_03_23-09-04-10.DAT'
        dev_name = u'DAUERLAUF_ITEBSX_2022_03_23-09-04-10.D02'
        sig_name = u'PkgZStat2' #'PkgZStat2''Odometer''VehWhlSpeed''V_A1R''TrlWeight'

        value, timekey = self.dat_object.getSignal(dev_name, sig_name)
        print(value)
        time = self.dat_object.getTime(timekey)
        self.assertTrue(value.size != 0 and timekey == time)
        return


if __name__ == '__main__':
    unittest.main()
    pass
