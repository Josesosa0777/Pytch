#!C:\Python27\python.exe
from datavis import pyglet_workaround  # necessary as early as possible (#164)

from argparse import ArgumentParser, RawTextHelpFormatter
import sys

from config.Config import Config
from config.helper import procConfigFile, getConfigPath
from config.modules import Modules
from interface.manager import Manager

modules_name = getConfigPath('modules', '.csv')
modules = Modules()
modules.read(modules_name)

interface = 'iCompare'
parser = ArgumentParser(formatter_class=RawTextHelpFormatter)
args = Config.addArguments( parser ).parse_args()
name = procConfigFile('dataeval', args)
config = Config(name, modules)
manager = config.createManager(interface)

config.init(args)
config.run(manager, args, interface)
#config.wait(args) TODO: wait app in config
config_status = config.exit(manager, interface)
modules.protected_write(modules_name)
sys.exit(config_status)  

