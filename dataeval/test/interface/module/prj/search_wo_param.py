# -*- dataeval: method -*-

from interface.Interfaces import iSearch

class Search(iSearch):
  def check(self):
    return 56

  def fill(self, egg):
    return egg + 4, egg - 4

  def search(self, spam, spamspam):
    self.egg = spam - spamspam
    return

  def error(self):
    self.egg = 11
    return
  pass


