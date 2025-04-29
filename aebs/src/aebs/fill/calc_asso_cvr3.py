# -*- dataeval: init -*-

import interface
from aebs.sdf.asso_cvr3_fus_recalc import AssoCvr3fusRecalc

class Calc(interface.iCalc):
  def fill(self):
    a = AssoCvr3fusRecalc( self.get_source() )
    a.calc()
    return a
