import os
import glob
import shutil
import ConfigParser

def correctCfgFileExt(CfgPath):
  if not CfgPath.endswith('.cfg'):
    CfgPath = '%s.cfg' %CfgPath
  return CfgPath

def getConfigPath(InterfaceName, Ext='.cfg'):
  CfgDir = '.'+os.getenv('DATAEVAL_NAME', 'dataeval')
  CfgDir = os.path.join('~', CfgDir)
  CfgDir = os.path.expanduser(CfgDir)
  CfgDir = os.getenv('DATAEVAL_CONFIG_DIR', CfgDir)
  if not os.path.exists(CfgDir):
    os.mkdir(CfgDir)
  CfgPath = os.path.join(CfgDir, InterfaceName+Ext)
  return CfgPath

def getModuleAttrDir(FullName):
  ModuleName, AttrName = FullName.rsplit('.', 1)
  Module = __import__(ModuleName, fromlist=[AttrName])
  return os.path.dirname(Module.__file__)

def procConfigFile(Name, Args):
  ConfigFileName = getConfigPath(Name)
  if Args.push:
    shutil.copyfile( correctCfgFileExt(Args.push), ConfigFileName )
  if Args.export:
    shutil.copyfile( ConfigFileName, correctCfgFileExt(Args.export) )
    exit()
  if Args.config:
    ConfigFileName = Args.config
  return ConfigFileName

def getScanDirs():
  ScanDirs = {}
  for Name in glob.glob(getConfigPath('*', '.pth')):
    Pth = open(Name).read().strip()
    _, Name = os.path.split(Name)
    Name, _ = os.path.splitext(Name)
    ScanDirs[Name] = Pth
  return ScanDirs

def writeConfig(Name, Sections):
  Config = ConfigParser.RawConfigParser()
  Config.optionxform = str

  for Section, Options in Sections.iteritems():
    Config.add_section(Section)
    for Option, Value in Options.iteritems():
      Config.set(Section, Option, Value)

  Fp = open(Name, 'wb')
  Config.write(Fp)
  Fp.close()
  return