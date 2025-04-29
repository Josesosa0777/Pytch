# -*- dataeval: init -*-

from interface.Interfaces import Interface

__version__ = '0.5.6' # test get_sign

class View(Interface):
  dep = 'fill-bar@prj',
  channels = 'main', 'can2'
  def check(self):
    return 33, 66

  def fill(self, bar, baz):
    return baz - bar

  def run(self, spam):
    self.spam = spam - 9
    return

