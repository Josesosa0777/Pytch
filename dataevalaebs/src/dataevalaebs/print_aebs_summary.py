# -*- dataeval: init -*-
import sys

from interface.Interfaces import iAnalyze

from issuegen_aebs_warning import Events as AebsEvents, Event as AebsEvent

init_params = {
  'online': dict(algo='FLR20 Warning', suppression=False),
  'offline': dict(algo='SIL KB AEBS', suppression=True),
}

class Analyze(iAnalyze):
  def init(self, algo, suppression, date=None):
    self.algo = algo
    self.suppression = suppression
    self.date = date
    return

  def analyze(self):
    batch = self.get_batch()
    view_name = batch.create_table_from_last_entries(date=self.date)

    table = Table( ['date', 'tot dist', 'warnings', 'stationary',
                    'warning cause (all/stat)'] )
    date_warnings = Summary(batch, view_name, self.algo, self.suppression)
    date_events = DateEvents(batch, view_name, self.algo, self.suppression)
    tot_dists = TotDist(batch, view_name)
    for date in sorted(tot_dists):
      tot_dist = tot_dists[date]
      warnings = date_warnings.get(date, Table.Record.Warnings())
      table.add(date, tot_dist, warnings)
      #events = date_events.get(date, Events([]))
      #events(self._manager)
    sys.stdout.write(table)
    sys.stdout.flush()
    return

class Table(list):
  def __init__(self, header):
    self.header = header
    return

  def add(self, date, tot_dist, warnings):
    self.append( self.Record(date, tot_dist, warnings) )
    return

  def __repr__(self):
    table = [self.header]
    record = self.Record.from_table(self)
    table.extend( self.Record.from_table(self).create_rows() )
    for record in self:
      table.extend( record.create_rows() )
    table = '\n'.join('|%s|' % '|'.join(row) for row in table)
    return table

  class Record:
    def __init__(self, date, tot_dist, warnings):
      self.date = date
      self.tot_dist = tot_dist
      self.warnings = self.Warnings(warnings)
      return

    @classmethod
    def from_table(cls, table):
      date = '%s\n%s' % (table[0].date, table[-1].date)
      tot_dist = 0.0
      warnings = cls.Warnings()
      for record in table:
        tot_dist += record.tot_dist
        warnings.update(record.warnings)
      self = cls(date, tot_dist, warnings)
      return self

    def create_rows(self):
      rows = []
      row = []
      rows.append(row)
      span = self.warnings.extend_row(rows, row)
      row.insert(0, '/%d.%s' % (span, self.date) )
      row.insert(1, '/%d.%.2f km' % (span, self.tot_dist) )
      return rows

    class Warnings(dict):
      def update(self, other):
        for algo, warning_causes in other.iteritems():
          if algo in self:
            self_causes = self[algo]
            for cause, warnings in warning_causes.iteritems():
              if cause in self_causes:
                self_causes[cause] += warnings
              else:
                self_causes[cause] = warnings
          else:
            self[algo] = warning_causes.copy()
        return

      def extend_row(self, rows, row):
        span = 1
        all_warnings = all_stat_warnings = 0
        if self:
          for cause in sorted(self):
            if row:
              span += 1
              cause_row = []
              rows.append(cause_row)
            else:
              cause_row = row
            warnings = self[cause]
            no_warnings = sum(warnings.values())
            moving = warnings.get('moving', 0)
            stationary = no_warnings - moving
            cause_row.append('%s (%d/%d)' %(cause, no_warnings, stationary))
            all_warnings += no_warnings
            all_stat_warnings += stationary
        else:
          row.append('-')
        row.insert(0, '/%d.%d' % (span, all_warnings))
        row.insert(1, '/%d.%d' % (span, all_stat_warnings))
        return span

class Summary(dict):
  join = ''

  def __init__(self, batch, view_name, algo, suppression):
    dict.__init__(self)

    supp_join = '''
      JOIN interval2label suppression_i2l ON
                          suppression_i2l.entry_intervalid = entryintervals.id
      JOIN labels suppression ON
                  suppression.id = suppression_i2l.labelid
      JOIN labelgroups suppression_lg ON
                       suppression_lg.id = suppression.groupid
      ''' if suppression else ''
    suppression = '''
      AND suppression.name != :suppression
      AND suppression_lg.name = :suppression_group
      ''' if suppression else ''

    self.init( batch.query("""
      SELECT DATE(measurements.start) meas_date, %s FROM %s en
        JOIN modules ON
             modules.id = en.moduleid

        JOIN measurements ON
             measurements.id = en.measurementid

        JOIN entryintervals ON
             entryintervals.entryid = en.id

        JOIN interval2label algo_i2l ON
                            algo_i2l.entry_intervalid = entryintervals.id
        JOIN labels algo ON
                    algo.id = algo_i2l.labelid
        JOIN labelgroups algo_lg ON
                         algo_lg.id = algo.groupid

        JOIN interval2label warning_cause_i2l ON
                            warning_cause_i2l.entry_intervalid = entryintervals.id
        JOIN labels warning_cause ON
                    warning_cause.id = warning_cause_i2l.labelid
        JOIN labelgroups warning_cause_lg ON
                         warning_cause_lg.id = warning_cause.groupid

        JOIN interval2label moving_i2l ON
                            moving_i2l.entry_intervalid = entryintervals.id
        JOIN labels moving ON
                    moving.id = moving_i2l.labelid
        JOIN labelgroups moving_lg ON
                         moving_lg.id = moving.groupid

        %s

      WHERE modules.class = :class_name
        AND en.title = :title
        AND algo_lg.name = :algo_group
        AND algo.name = :algo
        AND warning_cause_lg.name = :warning_group
        AND moving_lg.name = :moving_group
        %s

      GROUP BY meas_date, warning_cause.name, moving.name
      """ % (self.select, view_name, supp_join, suppression),
      class_name='dataevalaebs.search_aebs_warning.Search',
      title='AEBS-warnings',
      algo_group='AEBS algo',
      warning_group='false warning cause',
      moving_group='moving state',
      suppression_group='KB AEBS suppression phase',
      suppression='cancelled',
      algo=algo
    ) )
    return

  select = 'warning_cause.name, moving.name, COUNT(*)'
  def init(self, data):
    for date, warning_cause, moving, count in data:
      self.setdefault(date, {}).setdefault(warning_cause, {})[moving] = count
    return


class DateEvents(Summary):
  select = '''
    IFNULL(measurements.local, measurements.origin), measurements.basename,
    warning_cause.name, moving.name, entryintervals.start_time
    '''
  def init(self, data):
    for date, fullmeas, meas, warning_cause, moving, start in data:
      if date in self:
        events = self[date]
      else:
        events = Events([])
        self[date] = events
      event = Event(measurement=meas, warning_cause=warning_cause,
                    moving=moving, start=start)
      events.setdefault(fullmeas, {})[start] = event
    return

class Events(AebsEvents):
  def init(self, data):
    return

class Event(AebsEvent):
  TITLE = '%(measurement)s @ %(start).2f'
  def get_title(self):
    return self.TITLE % self

  SECTION = 'h3. %s\n\n!%s!\n' % (TITLE, AebsEvent.PIC)

class TotDist(dict):
  def __init__(self, batch, view_name):
    data = batch.query("""
      SELECT DATE(measurements.start) meas_date, TOTAL(tot_dist.value)
        FROM %s en
        JOIN modules ON
             modules.id = en.moduleid
        JOIN measurements ON
             measurements.id = en.measurementid

        JOIN entryintervals ON
             entryintervals.entryid = en.id

        JOIN quantities tot_dist ON
                        tot_dist.entry_intervalid = entryintervals.id
        JOIN quanames tot_dist_names ON
                      tot_dist_names.id = tot_dist.nameid
        JOIN quanamegroups tot_dist_namegroups ON
                           tot_dist_namegroups.id = tot_dist_names.groupid

      WHERE modules.class = :class_name
        AND en.title = :title
        AND tot_dist_namegroups.name = :tot_dist_group
        AND tot_dist_names.name = :tot_dist
      GROUP BY meas_date
      """ % view_name,
    class_name='dataevalaebs.searchAEBSWarnEval_RoadTypes.cSearch',
    title='AEBS-RoadType-Intervals',
    tot_dist_group='ego vehicle',
    tot_dist='driven distance',
    )
    self.update(data)
    return

