#!C:\Python27\python.exe
from datavis import pyglet_workaround  # necessary as early as possible (#164)
from datavis import keyinterrupt_workaround

from argparse import ArgumentParser, RawTextHelpFormatter
import sys
import signal

from PySide import QtGui, QtCore

from config.Config import Config
from config.helper import procConfigFile, getConfigPath
from config.modules import Modules
from interface.manager import Manager

interface = 'iView'
config_status = -1
config = None
manger = None
app = None

def signal_handler(signal, frame):
  close()
  return

def close():
  config_status = config.exit(manager, interface)
  if app:
    app.quit()
  return

signal.signal(signal.SIGINT, signal_handler)

modules_name = getConfigPath('modules', '.csv')
modules = Modules()
modules.read(modules_name)

parser = ArgumentParser(formatter_class=RawTextHelpFormatter)
args = Config.addArguments( parser ).parse_args()
if not args.norun:
  app = QtGui.QApplication([])

if not args.nonav and not args.norun:
  app.setQuitOnLastWindowClosed(False)
  timer = QtCore.QTimer()
  timer.start(200)
  timer.timeout.connect(lambda: None)  # Let the interpreter run each 200 ms.

config = Config(procConfigFile('dataeval', args), modules)
manager = config.createManager(interface)
config.init(args)
config.run(manager, args, interface)

if not args.nonav and not args.norun:
  config.log( 'Please press ctrl + c to close the navigators' )
  sync = manager.get_sync()
  sync.allClosedSignal.signal.connect(close)
  app_status = app.exec_()
else:
  app_status = 0
  close()

#config.wait(args) TODO: wait app in config

modules.protected_write(modules_name)
sys.exit(app_status + config_status)


