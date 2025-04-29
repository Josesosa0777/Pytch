import unittest
import optparse
import os

import numpy

from measparser.Hdf5Parser import init,\
                                  setHeader,\
                                  cHdf5Parser,\
                                  splitDeviceName,\
                                  getCompression


h5_name = 'foo.h5'

class Hdf5Parser(unittest.TestCase):
  def setUp(self):
    comp = getCompression('zlib', 1)
    h5, devs, times = init(h5_name)
    setHeader(h5, 4242, 'foo is sometimes could be bar')
    h5.close()
    self.h5 = cHdf5Parser(h5_name)
    return

  def test_add_rm_Time(self):
    time = numpy.arange(0, numpy.pi, 1e-3)
    timekey = 'egg'

    self.h5.addTime(timekey, time)
    h5_time = self.h5.getTime(timekey)
    self.assertTrue(numpy.allclose(h5_time, time))

    self.h5.rmTime(timekey)
    self.assertTrue(timekey not in self.h5.Hdf5['times'])
    return

  def test_add_rm_Signal(self):
    time = numpy.arange(0, numpy.pi, 1e-3)
    value = numpy.cos(time)
    timekey = 'egg'
    sig_name = 'spam'
    dev_name = 'foo-bar' # - has to be in the device name

    self.h5.addTime(timekey, time)
    self.h5.addSignal(dev_name, sig_name, timekey, value)
    h5_value, timekey = self.h5.getSignal(dev_name, sig_name)
    self.assertTrue(numpy.allclose(h5_value, value))

    self.h5.rmTime(timekey)
    self.h5.rmSignal(dev_name, sig_name)
    dev_name, dev_ext = splitDeviceName(dev_name)
    dev_name = '/'.join(['', 'devices', dev_name, dev_ext])
    self.assertTrue(sig_name not in self.h5.Hdf5[dev_name])
    return

  def tearDown(self):
    self.h5.close()
    os.remove(h5_name)
    return


if __name__ == '__main__':
  unittest.main()
  pass
