# -*- dataeval: init -*-

from interface.Interfaces import iFill

__version__ = '0.5.6' # test get_sign

class Fill(iFill):
  channels = 'main', 'can1'
  def init(self, spam):
    self.spam = spam
    return

  def check(self):
    return self.spam + 1

  def fill(self, egg):
    return egg + 4
  
  def run(self, param):
    self.egg = param - 6
    return
  pass


