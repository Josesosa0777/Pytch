#!C:\Python27\python.exe
from datavis import pyglet_workaround  # necessary as early as possible (#164)
from datavis import keyinterrupt_workaround

import sys
import os
import signal
from argparse import ArgumentParser, RawTextHelpFormatter

from PySide import QtGui, QtCore

from config.Config import Config
from config.helper import procConfigFile, getConfigPath
from config.modules import Modules
from dmw.sessionframes import MassFrame

config_frame = None


def signal_handler(signal, frame):
		config_frame.close()
		return


signal.signal(signal.SIGINT, signal_handler)

modules_name = getConfigPath('modules', '.csv')
modules = Modules()
modules.read(modules_name)

sys.argv.append('-r')
sys.argv.append('--forced-save')

parser = ArgumentParser(formatter_class=RawTextHelpFormatter)
args = Config.addArguments(parser).parse_args()
name = procConfigFile('dataeval', args)
config = Config(name, modules)
config.init(args)

app = QtGui.QApplication([])
timer = QtCore.QTimer()
timer.start(200)
timer.timeout.connect(lambda: None)  # Let the interpreter run each 200 ms.

config_frame = MassFrame(config, args)
cfg_path = os.path.basename(config.CfgPath)
pytch_version_file_path = os.path.join(os.path.dirname(__file__), "pytch_version.txt")
pytch_version_fp = open(pytch_version_file_path, "r")
pytch_version = pytch_version_fp.readline()
pytch_version_fp.close()

title = 'Python Toolchain ' + pytch_version + config_frame.FILE_SEP + cfg_path
config_frame.setWindowTitle(title)
config_frame.start()

print >> sys.stderr, 'Please press ctrl + c in command prompt to close MASS'
sys.stderr.flush()

app_status = app.exec_()
modules.protected_write(modules_name)

sys.exit(app_status)
