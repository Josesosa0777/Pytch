import unittest

import numpy

from measproc.report2 import Report, Quantity
from measproc.IntervalList import cIntervalList

class Test(unittest.TestCase):
  def setUp(self):
    time = numpy.arange(0, 2*numpy.pi, 20e-3)
    intervallist = cIntervalList(time)
    self.report = Report(intervallist, 'foo', {'spam': (True, ['egg'])})
    self.quantity = Quantity(intervallist, 'bar', {'spam': ['egg']})
    return
    
  def test_report_intervallist_separated(self):
    self.quantity.addInterval((24, 78))
    self.assertEqual(len(self.report.intervallist), 0)
    return

  def test_quantity_intervallist_separated(self):
    self.report.addInterval((24, 78))
    self.assertEqual(len(self.quantity.intervallist), 0)
    return


if __name__ == '__main__':
  unittest.main()
