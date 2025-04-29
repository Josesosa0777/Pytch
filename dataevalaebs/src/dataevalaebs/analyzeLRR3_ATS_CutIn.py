import interface
import searchLRR3_ATS_CutIn

class cParameter(interface.iParameter):
  def __init__(self, Last):
    self.Last = Last
    self.genKeys()
    pass
    
Last = cParameter(True)
All = cParameter(False)

class cLRR3_ATS_CutIn(interface.iAnalyze):
  def analyze(self, Param=Last):
    ParSign   = searchLRR3_ATS_CutIn.DefParam.getSign()
    ClassSign = searchLRR3_ATS_CutIn.cLRR3_ATS_CutIn.getSign()
    if Param.Last:
      self.addLastReports(ClassSign, ParSign)
    else:
      self.addAllReports(ClassSign, ParSign)
    pass
    
