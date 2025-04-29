import interface
import viewHardBraking
import searchHardBraking

SearchModules = [searchHardBraking.cHardBraking.getSign()]

class cParameter(interface.iParameter):
  def __init__(self, Last):
    self.Last = Last
    self.genKeys()
    pass
      
Last = cParameter(True)
All = cParameter(False)

class cHardBraking(interface.iAnalyze):
  def analyze(self, Param = Last):
    ParSign   = searchHardBraking.DefParam.getSign()
    ClassSign = searchHardBraking.cHardBraking.getSign()
    if Param.Last:
     self.addLastReports(ClassSign, ParSign)
    else:
      self.addAllReports(ClassSign, ParSign)
    pass
