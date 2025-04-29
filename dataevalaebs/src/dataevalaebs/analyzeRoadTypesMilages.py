import collections
import sys

import interface
import measparser

Param = interface.NullParam

COLUMN_SEP = ':'
MILAGE_FORMAT = '%.2f'

class cAnalyze(interface.iAnalyze):
  def check(self):
    Group = interface.Batch.filter(type='measproc.cFileStatistic',
                                   title='AEBS-RoadType-Milages')
    if not Group:
      raise measparser.signalgroup.SignalGroupError('No required file statistic is available')
    return Group

  def fill(self, Group):
    Milages = collections.OrderedDict([('rural',   0.0), 
                                       ('city',    0.0),
                                       ('highway', 0.0)])
    for Entry in Group:
      Statistic = interface.Batch.wake_entry(Entry)
      for Tick in Milages:
        Milages[Tick] += Statistic.get([('RoadTypes', Tick)])
    return Milages

  def analyze(self, Param, Milages):
    print COLUMN_SEP.join(Milages.iterkeys())
    print COLUMN_SEP.join([MILAGE_FORMAT %Milage for Milage in Milages.itervalues()])
    sys.stdout.flush()
    pass

