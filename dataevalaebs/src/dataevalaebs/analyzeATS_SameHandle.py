import interface
import searchATS_SameHandle

class cParameter(interface.iParameter):
  def __init__(self, Last):
    self.Last = Last
    self.genKeys()
    pass
    
Last = cParameter(True)
All = cParameter(False)

class cATS_SameHandle(interface.iAnalyze):
  def analyze(self, Param=Last):
    ParSign   = searchATS_SameHandle.DefParam.getSign()
    ClassSign = searchATS_SameHandle.cSearch.getSign()
    if Param.Last:
      self.addLastReports(ClassSign, ParSign)
    else:
      self.addAllReports(ClassSign, ParSign)
    pass
