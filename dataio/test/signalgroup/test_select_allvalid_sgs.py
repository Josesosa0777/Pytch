import unittest

from measparser.signalgroup import select_allvalid_sgs, SignalGroupError

class Test(unittest.TestCase):
  def setUp(self):
    sg = dict( (signame, ('devname',signame)) for signame in ('foo', 'bar', 'baz') )
    self.size = len(sg)
    sg2 = sg.copy()
    sg2.pop('foo')
    self.sgs = [sg, sg2]
    return

  def test_basic(self):
    sgs = select_allvalid_sgs(self.sgs, self.size)
    self.assertTrue(sgs[0] is self.sgs[0])
    return

  def test_empty(self):
    with self.assertRaises(SignalGroupError):
      select_allvalid_sgs([], self.size)
    return

  def test_no_allvalid(self):
    with self.assertRaises(SignalGroupError):
      select_allvalid_sgs(self.sgs, self.size+1)
    return

  def test_no_allvalid_with_message(self):
    msg = 'my message'
    with self.assertRaises(SignalGroupError) as cm:
      select_allvalid_sgs( self.sgs, self.size+1, message=msg )
    self.assertTrue(cm.exception.message == msg)
    return

if __name__ == '__main__':
  unittest.main()
