import sys
import copy
import logging
import argparse

import section

from interface.Interfaces import iAnalyze
from interface.manager import AnalyzeManager
from interval_header import cIntervalHeader

class cIntervalHeaderSortbys(list):
  @classmethod
  def fromConfig(cls, Config, Section):
    Header = [None for Option in Config.options(Section)]
    for NrName in Config.options(Section):
      try:
        Nr, Name = NrName.split('.', 1)
        ASC = True if Config.get(Section, NrName).lower() == 'asc' else False
        Header[int(Nr)] = [Name, ASC]
      except:
        pass
    self = cls(Header)
    return self

  def toConfig(self, Config, Section):
    if Config.has_section(Section):
      Config.remove_section(Section)
    Config.add_section(Section)
    for i, (Name, Asc) in enumerate(self):
      Asc = 'asc' if Asc else 'desc'
      Config.set(Section, '%d.%s' % (i, Name), Asc)
    return

class cSection(section.cSection):
  Interface = iAnalyze
  HEADER_SEP = ','
  _Header = []
  _IntervalHeader = cIntervalHeader([])
  _IntervalSortBys = []

  def initConfig(self, Modules):
    self.Config.set('General', 'Header', 'measurement,title,type,intervals,query')
    self.Config.set('General', 'SortBy', 'measurement')
    self.Config.set('General', 'Query', '')
    self.Config.set('General', 'IntervalHeaderFile', '')

    self._initModules(Modules)

    cIntervalHeaderSortbys([['measurement', True]]).toConfig(self.Config,
                                                             'IntervalSortBys')
    return

  def header(self, Header):
    "set comma separated HEADER as batch frame header"
    if Header:
      self._Header = Header
    else:
      self._Header = self.Config.get('General', 'Header').split(self.HEADER_SEP)
    return

  def sortby(self, SortBy):
    "set SORTBY as sort column of the batch frame"
    if SortBy is None: return

    if SortBy in self._Header:
      self.Config.set('General', 'SortBy', SortBy)
    else:
      self.Config.log('Invalid header sort %s replaced to %s\n'
                       %(SortBy, self.Config.get('General', 'SortBy')),
                       Level=logging.WARNING)
    return

  def interval_header(self):
    "Add column to the interval header with COLUMN_NAME as the result of QUERY.\n"\
    "LABEL label_group_name is a special query which creates a label button."
    IntervalHeaderFileName = self.Config.get('General', 'IntervalHeaderFile')
    try:
      File = open(IntervalHeaderFileName, 'r')
    except IOError:
      self._IntervalHeader = cIntervalHeader([])
      self.Config.log("%s isn't a valid file path to intervalheader file"
                      %IntervalHeaderFileName, logging.WARNING)
    else:
      self._IntervalHeader = cIntervalHeader.fromFile(File)
    return

  def interval_sortbys(self, SortBys):
    "set COLUMN_NAMEs as sort column of the batch frame. Set sorting order with" \
    " ASC or DESC keywords"
    Valids = []
    Invalids = set()
    for SortBy in SortBys:
      Name, Order = SortBy
      if Order.lower() == 'asc':
        Valids.append([Name, True])
        Invalids.add(Name)
      elif Order.lower() == 'desc':
        Valids.append([Name, False])
        Invalids.add(Name)
      else:
        self.Config.log('%s is an invalid sorting order for %s. Please use ASC'
                        'or DESC' %(Order, Name), Level=logging.WARNING)
        continue

    Names = []
    for QNames, Query in self._IntervalHeader:
      Names.extend(QNames)
    Invalids.difference_update(Names)

    _SortBys = cIntervalHeaderSortbys.fromConfig(self.Config, 'IntervalSortBys')
    if not Valids:
      self._IntervalSortBys = _SortBys
    elif Invalids:
      self.Config.log('Invalid interval header sort: %s\n' % ', '.join(Invalids),
                      Level=logging.WARNING)
      self._IntervalSortBys = _SortBys
    else:
      self._IntervalSortBys = cIntervalHeaderSortbys(Valids)
    return

  def query(self, Query):
    "set QUERY as query for query column in batch frame"
    if Query is None: return

    self.Config.set('General', 'Query', Query)
    return

  def queryfile(self, QueryFile):
    "Set query from file for query column in batch frame"
    if QueryFile is None: return

    Query = QueryFile.read().replace('\n', ' ')
    self.query(Query)
    return

  def uploadParams(self, Manager):
    SortBy = self.Config.get('General', 'SortBy')
    Query = self.Config.get('General', 'Query')
    Config = copy.copy(self.Config)

    self.uploadIntervalTable(Manager)
    Manager.set_batchnav_params(Config, self._Header, SortBy, Query,
                                self._IntervalHeader, self._IntervalSortBys)
    return

  def uploadIntervalTable(self, Manager):
    self.interval_header()
    Manager.set_int_table_params(self._IntervalHeader, self._IntervalSortBys)
    return

  def build(self, Manager):
    if Manager.is_batch_loaded():
      Batch = Manager.get_batch()
      Batch.set_start(self.Config.Start)
      Batch.set_measurement('dummy', True)

    if self.batchnav:
      BatchNav = Manager.get_batchnav()
      if self.Config.RunNav:
        BatchNav.start()
    
    self.Config.log('Analyze session started.')
    pass

  def setIntervalHeaderSortbys(self, IntervalSortBys):
    self._IntervalSortBys = cIntervalHeaderSortbys(IntervalSortBys)
    return

  def createManager(self):
    manager = AnalyzeManager()
    return manager

  def procArgs(self, Args):
    self.header(Args.header)
    self.sortby(Args.sortby)
    self.query(Args.query)
    self.queryfile(Args.queryfile)
    if Args.interval_header_file:
      self.Config.set('General', 'IntervalHeaderFile',
                       Args.interval_header_file)
    self.interval_sortbys(Args.interval_sortbys)
    self.batchnav = Args.batchnav
    self.save(None)
    return

  @classmethod
  def addArguments(cls, Parser):
    Group = Parser.add_argument_group(title='batch navigator')
    Group.add_argument('--batchnav', help='Run batch navigator',
                       action='store_true',
                       default=False)
    Group.add_argument('--header', help=cls.header.__doc__, nargs='*',
                       default=[])
    Group.add_argument('--sortby', help=cls.sortby.__doc__)
    Group.add_argument('--query', help=cls.query.__doc__)
    Group.add_argument('--queryfile',
                       help=cls.queryfile.__doc__, type=argparse.FileType('r'))
    Group.add_argument('--interval-header-file',
                       help=cIntervalHeader.fromFile.__doc__, default=[])
    Group.add_argument('--interval-sortbys', help=cls.interval_sortbys.__doc__,
                       nargs=2, action='append',
                       default=[], metavar=('COMUMN_NAME', 'ASC'))
    return Parser

  def save(self, Manager):
    self.Config.set('General', 'Header', self.HEADER_SEP.join(self._Header))
    self._IntervalSortBys.toConfig(self.Config, 'IntervalSortBys')
    return

  def update(self):
    self._IntervalSortBys = cIntervalHeaderSortbys.fromConfig(self.Config,
                                                              'IntervalSortBys')
    return

  def clearSectionConfig(self):
    for section in self.getSessionSections():
      if self.Config.has_section(section):
        self.Config.remove_section(section)
        self.Config.add_section(section)
    return

  def getSessionSections(self):
    return ['IntervalSortBys',]
