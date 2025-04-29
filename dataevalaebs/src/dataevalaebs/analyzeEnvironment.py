import interface
import searchEnvironment

class cParameter(interface.iParameter):
  def __init__(self, Last):
    self.Last = Last
    self.genKeys()
    pass
    
Last = cParameter(True)
All = cParameter(False)

class cEnvironment(interface.iAnalyze):
  def analyze(self, Param=Last):
    ParSign   = searchEnvironment.DefParam.getSign()
    ClassSign = searchEnvironment.cEnvironment.getSign()
    if Param.Last:
      self.addLastReports(ClassSign, ParSign)
    else:
      self.addAllReports(ClassSign, ParSign)
    pass


      
