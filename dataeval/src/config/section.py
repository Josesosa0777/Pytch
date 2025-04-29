from interface.manager import Manager
from interface.modules import ModuleName

class cSection:
  Interface = None
  InnerBuild = False
  NeedStatuses = False
  def __init__(self, Config):
    self.Config = Config
    return

  def initConfig(self, Modules):
    'Init sections and options before config read'
    raise NotImplementedError()

  def _initModules(self, Modules):
    InterfaceName = self.Interface.__name__
    self.Config.add_section(InterfaceName)
    for ModName, ParamName, PrjName in Modules.iter_by_interface(InterfaceName):
      self.Config.initModuleByName(InterfaceName, ModName, ParamName, PrjName)
      Channels_ = Modules.get_channel(ModName, ParamName, PrjName)
      Channels = ','.join(Channels_)
      ExtendedModName = ModuleName.create(ModName, ParamName, PrjName)
      self.Config.set('Channels', ExtendedModName, Channels)
    for ModName in self.Config.options(InterfaceName):
      self.Config.likeAlone(ModName)
    return

  @classmethod
  def addArguments(cls, Parser):
    return

  def procArgs(self, Args):
    return

  def uploadParams(self, Manager):
    return

  def build(self, Manager):
    raise NotImplementedError()

  def save(self, Manager):
    return

  def update(self):
    return

  def clearSectionConfig(self):
    return

  def getSessionSections(self):
    return []

  def removeModule(self):
    return

  def createManager(self):
    _Manager = Manager()
    return _Manager
