import Search
from interface.Interfaces import iCompare

class cSection(Search.cSection):
  Interface = iCompare

  def initConfig(self, Modules):
    Search.cSection.initConfig(self, Modules)
    self.Config.set('Measurement', 'compare', '')    
    return
 
  def comp(self, Compare):
    "set COMP as compare measurement channel"
    if Compare is None: return

    self.m('compare='+Compare)
    return
  
  def build(self, Manager):
    Measurement = self.get('Measurement', 'compare')
    if Measurement in self.Measurements:
      self.Measurements.remove(Measurement)

    Search.cSection.build(self, Manager)
    
    self.Config.log('Compare session started.')
    return

  def procArgs(self, Args):
    self.comp(Args.comp)
    return

  @classmethod
  def addArguments(cls, Parser):
    Group = Parser.add_argument_group(title='compare')
    Group.add_argument('--comp',  help=cls.comp.__doc__)
    return Parser

