import os
import sys
import unittest
import argparse

import numpy

from measparser.Mf4Parser import cMf4Parser

# parser = argparse.ArgumentParser()
# parser.add_argument('-m', default=r"C:\KBData\Measurement\fast_searching_test\mf4\DAF__2017-07-14_17-45-50.mf4")
# args = parser.parse_args()
file_name = r"C:\KBData\Measurement\all_format_meas\mf4\DAF__2017-07-14_17-45-50.mf4"

if not os.path.isfile(file_name):
		sys.stderr.write('Measurement file does not exist\n')
		sys.exit(-1)


class Mf4Parser(unittest.TestCase):
		def setUp(self):
				self.mf4_parser = cMf4Parser(file_name)
				self.device_mf4 = r'XBR_A0_0B-AEBS_A0-Message-AEBS_A0-J1939_DAS_CAN2_vehicle'
				self.signal_mf4 = 'XBR_ExtAccelDem_A0_0B_C2'
				self.originals, _ = self.mf4_parser.getSignal(self.device_mf4,
						self.signal_mf4)
				return

		def test_value_read(self):
				value, tk = self.mf4_parser.getSignal(self.device_mf4, self.signal_mf4)
				self.assertTrue(value.size != 0)
				return


if __name__ == '__main__':
		unittest.main()
