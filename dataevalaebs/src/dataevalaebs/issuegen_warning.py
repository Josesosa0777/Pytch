# -*- dataeval: init -*-

from interface.Interfaces import iAnalyze

init_params = {
  'ldw': dict(dep='analyze_warning-ldw'),
  'aebs': dict(dep='analyze_warning-aebs'),
  'xls': dict(dep='analyze_warning-xls'),
}

class Analyze(iAnalyze):
  def init(self, dep):
    self.dep = dep,
    self.dep = self.extend_deps(self.dep)
    return

  def analyze(self):
    view_name, ids = self.get_modules().fill(self.dep[0])

    batch = self.get_batch()
    header = self.interval_table.getHeader()

    table = batch.get_table(header, ids)
    print batch.str_table(header[1:], ids)
    print
    meas_events = Events(table)

    for meas in sorted(meas_events):
      events = meas_events[meas]
      manager = self.clone_manager()
      manager.set_measurement(meas)
      module = 'viewVideoOverlay-DefParam'
      manager.build([module],
                    ['fillFLR20_ACC@aebs.fill', 'fillFLR20_AEB@aebs.fill',
                     'fillFLR20_FUS@aebs.fill',
                     'fillFLR20_AEBS_Warning-autobox@aebs.fill',],
                    ['FLR20_ACC', 'FLR20_AEB', 'FLR20_FUS', 'FLR20',
                     'FLR20_FUSED', 'FLC20', 'FLR20_RADAR_ONLY',
                     'FLR20_AEBS_Warning-AUTOBOX', 'moving', 'stationary'],
                    False)
      sync = manager.get_sync()
      client = sync.getClient(module, 'VideoNavigator')
      for start in sorted(events):
        sync.seek(start)
        event = events[start]
        client.copyContentToFile(event.get_picname())
        print event.get_section()
      manager.close()
    return

class Events(dict):
  def __init__(self, table):
    dict.__init__(self)

    head = table[0]
    for row in table[1:]:
      event = Event(zip(head, row))
      meas = event['fullmeas']
      start = event['start']
      self.setdefault(meas, {})[start] = event
    return

class Event(dict):
  PIC = 'vn_%(measurement)s_%(start).2f.png'
  def get_picname(self):
    return self.PIC % self

  TITLE = '%(measurement)s @ %(start).2f'
  def get_title(self):
    return self.TITLE % self

  SECTION = 'h3. %s\n\n!%s!\n' % (TITLE, PIC)
  def get_section(self):
    return self.SECTION % self
