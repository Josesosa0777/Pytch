import interface
import searchLRR3_Warnings

class cParameter(interface.iParameter):
  def __init__(self, Last):
    self.Last = Last
    self.genKeys()
    pass
    
Last = cParameter(True)
All = cParameter(False)

class cLRR3_Warnings(interface.iAnalyze):
  def analyze(self, Param=Last):
    ParSign   = searchLRR3_Warnings.DefParam.getSign()
    ClassSign = searchLRR3_Warnings.cLRR3_Warnings.getSign()
    if Param.Last:
      self.addLastReports(ClassSign, ParSign)
    else:
      self.addAllReports(ClassSign, ParSign)
    pass
