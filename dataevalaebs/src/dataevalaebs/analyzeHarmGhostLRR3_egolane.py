import interface
import searchHarmGhostLRR3_egolane

class cParameter(interface.iParameter):
  def __init__(self, Last):
    self.Last = Last
    self.genKeys()
    pass
    
Last = cParameter(True)
All = cParameter(False)

class cHarmGhostLRR3_egolane(interface.iAnalyze):
  def analyze(self, Param=Last):
    ParSign   = searchHarmGhostLRR3_egolane.DefParam.getSign()
    ClassSign = searchHarmGhostLRR3_egolane.cHarmGhostLRR3_egolane.getSign()
    if Param.Last:
      self.addLastReports(ClassSign, ParSign)
    else:
      self.addAllReports(ClassSign, ParSign)
    pass
    
