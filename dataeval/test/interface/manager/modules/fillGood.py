# -*- dataeval: init -*-
from interface.Interfaces import iFill

class Fill(iFill):
  def check(self):
    return 4

  def fill(self, a):
    return a + 8

