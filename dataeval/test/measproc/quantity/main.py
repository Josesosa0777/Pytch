import unittest

import numpy

from measproc.IntervalList import cIntervalList
from measproc.report2 import Quantity

class Test(unittest.TestCase):
  def setUp(self):
    self.names = {'foo': ['bar', 'baz'], 'spam': ['egg', 'eggegg']}
    time = numpy.arange(0, 2*numpy.pi, 1e-2)
    intervallist = cIntervalList(time)
    self.quantity = Quantity(intervallist, 'foo', self.names)
    return

  def test_addInterval(self):
    id = self.quantity.addInterval((42, 56))
    self.assertEqual(len(self.quantity._quantities), 1)
    return

  def test_rmInterval(self):
    id = self.quantity.addInterval((26, 86))
    self.assertEqual(len(self.quantity._quantities), 1)
    self.quantity.rmInterval(id)
    self.assertEqual(len(self.quantity._quantities), 0)
    return

  def test_set(self):
    groupname = 'spam'
    valuename = 'egg'
    value = 5.6
    id = self.quantity.addInterval((26, 86))    
    self.quantity.set(id, groupname, valuename, value)
    self.assertEqual(self.quantity._quantities[id][groupname][valuename], value)
    return

  def test_checkName(self):
    self.assertRaises(AssertionError, self.quantity.checkName,
                      'spamspam', 'eggeggegg')
    return

  def test_checkIntervalId(self):
    self.assertRaises(AssertionError, self.quantity.checkIntervalId, 42)
    return

  def test_get(self):
    groupname = 'spam'
    valuename = 'egg'
    value = 6.6
    id = self.quantity.addInterval((27, 91))    
    self.quantity.set(id, groupname, valuename, value)
    self.assertEqual(self.quantity.get(id, groupname, valuename), value)
    return

  def test_get_deafult(self):
    value = 5.3
    self.assertEqual(self.quantity.get(42, 'spam', 'egg', value), value)
    return

  def test_pop(self):
    groupname = 'spam'
    valuename = 'egg'
    value = 6.6
    id = self.quantity.addInterval((27, 91))    
    self.quantity.set(id, groupname, valuename, value)
    self.assertEqual(self.quantity.pop(id, groupname, valuename), value)
    self.assertRaises(KeyError, self.quantity.pop, id, groupname, valuename)
    return

  def test_pop_default(self):
    value = 5.3
    self.assertEqual(self.quantity.pop(42, 'spam', 'egg', value), value)
    return

  def test_sort(self):
    ids = []
    ids.append( self.quantity.addInterval( (27, 91) ) )
    self.quantity.set(ids[0], 'spam', 'egg', 56)
    ids.append( self.quantity.addInterval( (14, 22) ) )
    self.quantity.set(ids[1], 'spam', 'egg', 42)
    self.quantity.sort()
    self.assertEqual(self.quantity.get(ids[0], 'spam', 'egg'), 42)
    self.assertEqual(self.quantity.get(ids[1], 'spam', 'egg'), 56)
    return

  def test_setNames(self):
    groupname = 'nyavaja'
    valuenames = ['one', 'two', 'three']
    self.quantity.setNames(groupname, valuenames)
    self.assertListEqual(self.quantity._names[groupname], valuenames)
    return

  def test_getNames(self):
    self.assertDictEqual(self.quantity.getNames(), self.names)
    return

  def test_getQuantities(self):
    id = self.quantity.addInterval( (27, 91) )
    quantities = {'foo': {'bar': 9.0}}
    for groupname, quantity in quantities.iteritems():
      for valuename, value in quantity.iteritems():
        self.quantity.set(id, groupname, valuename, value)
    self.assertDictEqual(self.quantity.getQuantities(id), quantities)
    return

if __name__ == '__main__':
  unittest.main()
