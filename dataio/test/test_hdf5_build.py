import unittest
import os

import h5py
import numpy


from measparser.Hdf5Parser import init,\
                                  setHeader,\
                                  addSignal,\
                                  getCompression,\
                                  VERSION

name = 'foo.h5'

class BuildHdf5(unittest.TestCase):
  def setUp(self):
    self.comp = getCompression('zlib', 1)
    self.h5, self.devs, self.times = init(name)
    return

  def test_setHeader(self):
    start  = 4242
    comment = 'foo is never bar'
    setHeader(self.h5, start, comment)

    h5 = h5py.File(name)
    self.assertEqual(h5.attrs['comment'], comment)
    self.assertEqual(h5.attrs['timens'], start)
    self.assertEqual(h5.attrs['version'], VERSION)
    h5.close()
    return

  def test_addSignal(self):
    time = numpy.arange(0, numpy.pi, 1e-3)
    value = numpy.sin(time)

    dev_name = 'foo'
    dev_ext  = 'bar'
    sig_name = 'pyon'
    timekey  = 'egg'
    unit     = 'spam'
    comment  = 'bla'

    addSignal(self.devs, self.times, dev_name, dev_ext, timekey, timekey, time,
              self.comp, 's', '')
    addSignal(self.devs, self.times, dev_name, dev_ext, sig_name, timekey,
              value, self.comp, unit, comment)

    h5 = h5py.File(name)
    signal_name = '/'.join(['', 'devices', dev_name, dev_ext, sig_name, 'value'])
    self.assertTrue(numpy.allclose(h5[signal_name].value, value))
    time_name = '/'.join(['', 'times', timekey])
    self.assertTrue(numpy.allclose(h5[signal_name].value, value))
    h5.close()
    return

  def tearDown(self):
    self.h5.close()
    os.remove(name)
    return

if __name__ == '__main__':
  unittest.main()
  if os.path.isfile(name):
    os.remove(name)
