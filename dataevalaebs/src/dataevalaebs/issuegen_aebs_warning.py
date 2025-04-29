# -*- dataeval: init -*-
import os
import sys
from collections import OrderedDict

from config.Analyze import cIntervalHeader

from interface.Interfaces import iAnalyze

from docgen_aebs_warning import ActiveFlag

init_params = {
  'ldw': dict(dep='analyze_warning-ldw', dist_time='analyze_driven_distance_time-all'),
  'aebs': dict(dep='analyze_warning-aebs', dist_time='analyze_driven_distance_time-all'),
  'xls': dict(dep='analyze_warning-xls', dist_time='analyze_driven_distance_time-all'),
}

class Analyze(iAnalyze):
  def init(self, dep, dist_time):
    self.dep = dep,
    self.optdep = dist_time,
    self._dist_time = dist_time
    return

  def analyze(self):
    view_name, ids = self.modules.fill(self.dep[0])

    print 'h2. Driving info\n'
    if self._dist_time in self.passed_optdep:
      dist, time = self.modules.fill(self._dist_time)
      print 'Driven distance: %.1f km' % dist
      print 'Driven time: %.1f h' % time
      print
    else:
      msg = 'Driven distance and time not available.'
      self.logger.warning(msg)
      print msg
      print

    print 'h2. TRW active faults\n'
    active_flag = ActiveFlag(self.batch, view_name, 'trw-active-faults')
    print active_flag.str_table()
    print

    print 'h2. A087 active faults\n'
    active_flag = ActiveFlag(self.batch, view_name, 'a087-active-faults')
    print active_flag.str_table()
    print

    print 'h2. Warnings\n'
    header = os.path.join(os.path.dirname(__file__), 'sql', 'aebs_report.sql')
    header = cIntervalHeader.fromFile(open(header))
    table = self.batch.get_table(header, ids)
    print self.batch.str_table(header[1:], ids,
      sortby=[('measurement', True), ('start [s]', True)])
    print
    meas_events = Events(table)
    meas_events(self._manager)
    return

class Events(dict):
  modules = OrderedDict([
    ('viewVideoOverlay-DefParam@dataevalaebs', ['VideoNavigator']),
  ])
  statuses = ['fillFLR20_ACC@aebs.fill', 'fillFLR20_AEB@aebs.fill',
              'fillFLR20_FUS@aebs.fill', 'fillFLR20_AEBS_Warning-autobox@aebs.fill',]
  visibles = ['FLR20_ACC', 'FLR20_AEB', 'FLR20_FUS', 'FLR20', 'FLR20_FUSED',
              'FLC20', 'FLR20_RADAR_ONLY', 'FLR20_AEBS_Warning-AUTOBOX', 'moving',
              'stationary']
  show_nav = False
  def __init__(self, table):
    dict.__init__(self)
    self.init(table)
    return

  def init(self, table):
    head = table[0]
    for row in table[1:]:
      event = Event(zip(head, row))
      event['start'] = event['start [s]']  # hack for later access of 'start'
      meas = event['fullmeas']
      start = event['start']
      self.setdefault(meas, {})[start] = event
    return

  def __call__(self, master_manager):
    for meas in sorted(self):
      events = self[meas]
      manager = master_manager.clone()
      manager.set_measurement(meas)
      manager.build(self.modules, self.statuses, self.visibles, self.show_nav)
      sync = manager.get_sync()
      for start in sorted(events):
        sync.seek(start)
        for module, clients in self.modules.iteritems():
          for client_name in clients:
            try:
              client = sync.getClient(module, client_name)
            except ValueError:
              pass
            else:
              event = events[start]
              client.copyContentToFile(event.get_picname(module, client_name))
              print event.get_section(module, client_name)
              sys.stdout.flush()
      manager.close()
    return

class Event(dict):
  PIC = '%(module)s_%(client)s_%(measurement)s_%(start).2f.png'
  def get_picname(self, module, client):
    self['module'] = module
    self['client'] = client
    return self.PIC % self

  TITLE = '%(measurement)s @ %(start).2f'
  def get_title(self):
    return self.TITLE % self

  SECTION = 'h3. %s\n\n!%s!\n' % (TITLE, PIC)
  def get_section(self, module, client):
    self['module'] = module
    self['client'] = client
    return self.SECTION % self
