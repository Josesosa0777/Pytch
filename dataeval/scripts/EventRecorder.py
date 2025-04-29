#!C:\Python27\python.exe
from datavis import pyglet_workaround  # necessary as early as possible (#164)

import sys
import signal
from argparse import ArgumentParser, RawTextHelpFormatter

from PySide import QtGui, QtCore

from config.Config import Config
from config.helper import procConfigFile, getConfigPath
from config.modules import Modules
from dmw.EventRecorderViewConfigFrame import cEventRecorderViewConfigFrame

config_frame = None

def signal_handler(signal, frame):
  config_frame.close()
  return

signal.signal(signal.SIGINT, signal_handler)

modules_name = getConfigPath('modules', '.csv')
modules = Modules()
modules.read(modules_name)

parser = ArgumentParser(formatter_class=RawTextHelpFormatter)
args = Config.addArguments( parser ).parse_args()
name = procConfigFile('dataeval', args)
config = Config(name, modules)
config.init(args)

app = QtGui.QApplication([])
timer = QtCore.QTimer()
timer.start(200)
timer.timeout.connect(lambda: None)  # Let the interpreter run each 200 ms.

config_frame = cEventRecorderViewConfigFrame(app, config)
config_frame.setWindowTitle('Event Recorder')
config_frame.start()

config.log( 'Event Recorder' )

app_status = app.exec_()
modules.protected_write(modules_name)

sys.exit(app_status)

