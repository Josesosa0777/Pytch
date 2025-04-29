import os
import sys
import logging

import section
from measproc.Batch import findMeasurements
from interface.Interfaces import iSearch


class cSection(section.cSection):
  Interface = iSearch
  InnerBuild = True
  Measurements = set()
  Local = True

  def initConfig(self, Modules):
    self.Config.set('General', 'Measurements', '')
    self.Config.set('General', 'WildCard', '')
    self.Config.set('General', 'BatchFile', '')
    self.Config.set('General', 'RepDir', '')
    self._initModules(Modules)
    pass

  def build(self, Manager):
    Measurement = self.Config.get('Measurement', 'main')

    self.Config._uploadBatchParams(Manager)
    Batch = Manager.get_batch()
    Batch.set_start(self.Config.Start)
    Interface = self.Interface.__name__
    for Measurement in sorted(self.Measurements):
      self.Config.m(Measurement)
      Batch.set_measurement(Measurement, self.Local)
      try:
        self.Config.load(Manager, Interface)
        self.Config._build(Manager, Interface)
      except IOError, error:
        self.Config.log(error.message, Level=logging.ERROR)
        self.Config.log("(detailed info)", Level=logging.DEBUG)  # TODO: impl
      else:
        Manager.close(close_batch=False)
    Manager.close()
    self.Config.log('Search session ended.')

    self.Config.m(Measurement)
    return

  def save(self, Manager):
    self.Config.set('General', 'Measurements',
                    os.path.pathsep.join(self.Measurements))
    return

  def procArgs(self, Args):
    self.wildcard(Args.wild_card)

    if not Args.append and (Args.scan or Args.add):
      self.Measurements.clear()
    else:
      Measurements = self.Config.get('General', 'Measurements').strip(os.pathsep)
      if Measurements:
        self.Measurements.update( Measurements.split(os.path.pathsep) )

    self.Measurements.update(Args.add)

    for ScanDir in Args.scan:
      ScanDir = os.path.abspath(ScanDir)
      WildCard = self.Config.get('General', 'WildCard')
      Measurements = findMeasurements(ScanDir, WildCard, Args.r)
      self.Measurements.update(Measurements)

    self.Local = not Args.server

    for Measurement in set(Args.rm).difference(self.Measurements):
      sys.stderr.write('%s is not part of the measurements\n' %Measurement)
    self.Measurements.difference_update(Args.rm)
    return

  def wildcard(self, WildCard):
    "glob wild card for measurement file scan"
    if WildCard is None: return

    self.Config.set('General', 'WildCard', WildCard)
    return

  @classmethod
  def addArguments(cls, Parser):
    Group = Parser.add_argument_group(title='scan measurements for search')
    Group.add_argument('-r',
      help='recursive measurement file scan',
      action='store_true',
      default=False)
    Group.add_argument('-w', '--wild-card',
      help=cls.wildcard.__doc__)
    Group.add_argument('-a', '--append',
      help='append the new measurement files to the existing ones',
      action='store_true',
      default=False)
    Group.add_argument('--scan', metavar='SCAN_ROOT_DIR',
      help='scan measurements from SCAN_ROOT_DIR, WILD_CARD has to be set',
      action='append',
      default=[])
    Group.add_argument('--server',
      help='measurements are from server (temporary)',
      action='store_true',
      default=False)
    Group.add_argument('--add', metavar='MEASUREMENT',
      help='add MEASUREMENT to batch processing',
      action='append',
      default=[])
    Group.add_argument('--rm', metavar='MEASUREMENT',
      help='remove MEASUREMENT from batch processing',
      action='append',
      default=[])
    return Parser

