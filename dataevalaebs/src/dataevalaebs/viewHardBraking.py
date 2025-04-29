import interface

class cParam(interface.iParameter):
    def __init__(self, status):
      self.status = status
      self.genKeys()
      pass

DefParam = cParam(status = ["LRR3_FUS", "LRR3_ATS"])

class cHardBraking(interface.iView):
  @classmethod
  def view(cls, Param=DefParam):
    pass
