import os
import sys
import time
import ctypes
import logging

import pip
from PySide import QtCore

def _create_file_path(file_pattern):
  """
  Substitute values into file name pattern.

  Possible string specifiers:
    'Y', 'm', 'd', 'H', 'M', 'S' --> see time.strftime() for explanation
  Possible integer specifiers:
    'cnt' --> counter, increases until non-existing file is found

  Example:
    >>> _create_file_path(
    ... "mass_%%(Y)s-%%(m)s-%%(d)s_%%(H)s-%%(M)s-%%(S)s_%%(cnt)03d.log")
    "mass_2014-03-10_09-35-53_001.log"
  """
  # prepare substitution
  now = time.localtime()
  tags = {'cnt': 0}
  time_tags = ('Y', 'm', 'd', 'H', 'M', 'S')
  for tt in time_tags:
    tags[tt] = time.strftime("%%%s" % tt, now)
  # do substitution
  file_name = file_pattern % tags
  # handle counter
  if 'cnt' in file_pattern and 'cnt' not in file_name: # substitution performed
    while os.path.exists(file_name):
      tags['cnt'] += 1
      file_name = file_pattern % tags
  return file_name

def _get_env_info(sep=";"):
  SINGLE_INFO_T = "%s:'%s'"
  info_dict = (
    ("platform", sys.platform),
    ("shell", os.environ.get('shell', "")),
    ("cwd", os.getcwd()),
    ("argv", " ".join(sys.argv)),
  )
  return sep.join(SINGLE_INFO_T % (name, value) for name, value in info_dict)

def _get_python_info(sep=";"):
  pkgs = pip.get_installed_distributions()
  info  = "python:'%s';" % sys.version
  info += sep.join(pkg.key + ":" + pkg.version for pkg in pkgs)
  return info

class ObjectEmittingSignal(QtCore.QObject):
  signal = QtCore.Signal(object)

class OutputColoring(object):
  def colorMessage(self, msg, color_name):
    color = getattr(self, color_name)
    message = self._colorMessage(msg, color)
    return message

  def _colorMessage(self, msg, color):
    return msg

  def restoreOutputColor(self):
    return

class WindowsCmdLineColoring(OutputColoring):
  STD_OUTPUT_HANDLE = -11
  DARK_BLUE    = 0x0001
  DARK_GREEN    = 0x0002
  BLUE    = 0x0003
  DARK_RED    = 0x0004
  MAGENTA    = 0x0005
  DARK_YELLOW   = 0x0006
  WHITE    = 0x0007
  GREY   = 0x0008
  INTENSIVE_BLUE    = 0x0009
  GREEN    = 0x000A
  LIGHT_BLUE    = 0x000B
  RED    = 0x000C
  PINK   = 0x000D
  YELLOW    = 0x000E
  VERY_WHITE    = 0x000F

  def _colorMessage(self, msg, color):
    handle = ctypes.windll.kernel32.GetStdHandle(self.STD_OUTPUT_HANDLE)

    ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
    return msg

  def restoreOutputColor(self):
    handle = ctypes.windll.kernel32.GetStdHandle(self.STD_OUTPUT_HANDLE)

    ctypes.windll.kernel32.SetConsoleTextAttribute(handle, self.WHITE)
    return


class CygwinTerminalColoring(OutputColoring):
  DARK_GREY = '\033[90m'
  RED = '\033[91m'
  GREEN = '\033[92m'
  YELLOW = '\033[93m'
  BLUE = '\033[94m'
  PINK = '\033[95m'
  LIGHT_BLUE = '\033[96m'
  WHITE = '\033[97m'
  ENDC = '\033[0m'

  def _colorMessage(self, msg, color):
    return '%s%s%s' %(color, msg, self.ENDC)



class StreamFormatter(logging.Formatter):
  DEF_FMT =  "%(message)s"
  DBG_FMT =  "[DEBUG] %(module)s, L%(lineno)d: %(message)s"
  INFO_FMT = "[INFO] %(message)s"
  WARN_FMT = "[WARNING] %(message)s"
  ERR_FMT =  "[ERROR] %(message)s"
  CRIT_FMT = "[FATAL] %(message)s"
  LOGLEVEL_2_COLOR = {
                        logging.DEBUG : 'LIGHT_BLUE',
                        logging.INFO : 'WHITE',
                        logging.WARNING : 'YELLOW',
                        logging.ERROR : 'RED',
                        logging.CRITICAL : 'PINK',
                      }
  LOGLEVEL_2_FORMAT = {
                        logging.DEBUG : DBG_FMT,
                        logging.INFO : INFO_FMT,
                        logging.WARNING : WARN_FMT,
                        logging.ERROR : ERR_FMT,
                        logging.CRITICAL : CRIT_FMT,
                      }
  def __init__(self, colorful_stderr):
    logging.Formatter.__init__(self)
    self.colorful_stderr = colorful_stderr
    if os.environ.get("shell") == r"/bin/bash":
      self.colorer = CygwinTerminalColoring()
    elif sys.platform.startswith("win"):
      self.colorer = WindowsCmdLineColoring()
    else:
      self.colorer = OutputColoring()  # no coloring
      self.colorful_stderr = False  # optimization (avoid unnecessary calls)
    self.log_signal = ObjectEmittingSignal()
    return

  def format(self, record):
    format_orig = self._fmt

    color = self.LOGLEVEL_2_COLOR.get(record.levelno, 'WHITE')
    self._fmt = self.LOGLEVEL_2_FORMAT.get(record.levelno, self.DEF_FMT)

    result = logging.Formatter.format(self, record)
    self.log_signal.signal.emit((result, record.levelno))
    if self.colorful_stderr:
      result = self.colorer.colorMessage(result, color)

    self._fmt = format_orig

    return result

class Logger(object):
  DEFAULT_STREAM_LOG_LEVEL = logging.INFO
  DEFAULT_FILE_LOG_LEVEL = logging.DEBUG

  def __init__(self, log_file_pattern, stderr_logger_level,
              file_logger_level=logging.DEBUG, colorful_stderr=True):
    self.logger = logging.getLogger()
    #set the level of rootlogger to the minimum, to let through the information
    #to subloggers
    self.logger.setLevel(0)
    self.stderr_handler = logging.StreamHandler(sys.stderr)
    self.stderr_form = StreamFormatter(colorful_stderr)
    self.stderr_handler.setFormatter(self.stderr_form)
    self.stderr_handler.setLevel(stderr_logger_level)
    self.logger.addHandler(self.stderr_handler)
    self.file_handler = None
    if log_file_pattern:
      log_file_path = _create_file_path(log_file_pattern)
      log_file_dir = os.path.dirname(log_file_path)
      if not os.path.exists(log_file_dir):
        log_file_dir = os.path.expanduser(os.path.join('~', '.' + os.getenv('DATAEVAL_NAME', 'dataeval')))
        log_file_path = os.path.join(log_file_dir, log_file_path.split('\\')[-1])
      self.file_handler = logging.FileHandler(log_file_path, mode='w')
      self.file_handler.setLevel(file_logger_level)
      file_form = logging.Formatter(
        '%(asctime)s [%(levelname)s]\t%(module)s, L%(lineno)d:\t%(message)s')
      self.file_handler.setFormatter(file_form)
      self.logger.addHandler(self.file_handler)
    logging.captureWarnings(True)
    self.logger.debug('Logger successfully created')
    self.logger.debug('Environment info: %s' % _get_env_info())
    self.logger.debug('Python info: %s' % _get_python_info())
    return

  def close(self):
    if self.stderr_form.colorful_stderr:
      self.stderr_form.colorer.restoreOutputColor()
    if self.file_handler:
      self.file_handler.close()
    logging.shutdown()
    return

  def log(self, msg, level):
    self.logger.log(level, msg)
    return

  def change_stderr_level(self, level):
    self.stderr_handler.setLevel(level)
    return
