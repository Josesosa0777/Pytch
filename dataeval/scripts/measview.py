from datavis import pyglet_workaround  # necessary as early as possible (#164)

import os
import sys
import argparse

from PySide import QtGui

from measparser import SignalSource
from dmw.MeasurementView import MeasurementView

parser = argparse.ArgumentParser(description="""
  Show basic information about measurements
""")
parser.add_argument('-m',
                    metavar='MEAS',
                    required=True,
                    help='Full name of the measurement to be loaded')
parser.add_argument('-u', '--backup',
                    metavar='BACKUP',
                    default=None,
                    help='Use BACKUP as measurement cache directory')
args = parser.parse_args()

try:
  SignalSource.cSignalSource(args.m)
except IOError as io_error:
  print >> sys.stderr, io_error.message
else:
  app = QtGui.QApplication(sys.argv)
  app.setStyle("cleanlooks")
  view = MeasurementView(args.m, backup_dir=args.backup)
  sys.exit(app.exec_())
