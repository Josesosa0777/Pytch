import unittest

from pyutils.cycle import BiCycle

class TestBasic(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.c = BiCycle( xrange(10) )
    return

  def test_01_current(self):
    self.assertEqual( self.c.current(), 0 )
    return

  def test_02_next(self):
    self.assertEqual( self.c.next(), 1 )
    return

  def test_03_prev(self):
    self.assertEqual( self.c.prev(), 0 )
    return

  def test_04_prev_underflow(self):
    self.assertEqual( self.c.prev(), 9 )
    return

  def test_05_next_overflow(self):
    self.assertEqual( self.c.next(), 0 )
    return


class TestCustomStart(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.c = BiCycle( xrange(10), start=5 )
    return

  def test_01_current(self):
    self.assertEqual( self.c.current(), 5 )
    return

  def test_02_next(self):
    self.assertEqual( self.c.next(), 6 )
    return

  def test_03_prev(self):
    self.assertEqual( self.c.prev(), 5 )
    return

  def test_04_prev(self):
    self.assertEqual( self.c.prev(), 4 )
    return

  def test_05_next_step_4(self):
    self.assertEqual( self.c.next(steps=4), 8 )
    return

  def test_06_prev_step_7(self):
    self.assertEqual( self.c.prev(steps=7), 1 )
    return

  def test_07_prev_step_3_underflow(self):
    self.assertEqual( self.c.prev(steps=3), 8 )
    return

  def test_08_next_step_3_overflow(self):
    self.assertEqual( self.c.next(steps=3), 1 )
    return

if  __name__ == '__main__':
  unittest.main()
