# -*- dataeval: init -*-
from interface.Interfaces import iCalc

class Calc(iCalc):
  QUALIFIED = 1

  group = [
    ('umoCandidateQualified', ('ACC_S11', 'umoCandidateQualified')),
  ]
  def check(self):
    group = self.get_source().selectSignalGroup([dict(self.group)])
    return group

  def fill(self, group):
    t, umo = group.get_signal('umoCandidateQualified')
    warning = umo == self.QUALIFIED
    return t, warning

