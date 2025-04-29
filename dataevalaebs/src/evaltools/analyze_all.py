# -*- dataeval: init -*-

"""
Queries the entries in the database according to the given parameter:
* default: query all entries
* last_entries: query the latest version of the entries
* last_start: query the entries registered by the latest search session run

The returned entries will be loaded into the Interval Table.
"""

import sys
import copy
from collections import OrderedDict

from interface.Interfaces import iAnalyze

init_params = {
  'default':      dict(entries_creator=None,
                       output='interval_table'),
  'last_entries': dict(entries_creator='create_table_from_last_entries',
                       output='interval_table'),
  'last_start':   dict(entries_creator='create_table_from_last_start',
                       output='interval_table'),
}

print_init_params = copy.deepcopy(init_params)
for paramset_name in print_init_params.iterkeys():
  print_init_params[paramset_name]['output'] = 'stdout'

class Analyze(iAnalyze):
  QUERY_PAT = """
    SELECT ei.id FROM entryintervals AS ei
    JOIN %(entries)s AS en ON en.id = ei.entryid
  """
  
  def init(self, entries_creator, output):
    self.entries_creator = entries_creator
    self.output = output
    return
  
  def fill(self):
    all_ei_ids = EntriesViewsResultCollector()
    for view_name in self.iter_entries_views(self.entries_creator):
      ei_ids = self.batch.query(self.QUERY_PAT % dict(entries=view_name))
      all_ei_ids[view_name] = [ei_id for ei_id, in ei_ids]
    return all_ei_ids
  
  def iter_entries_views(self, entries_creator='create_table_from_last_entries'):
    """
    Iterates through the dates pairwise in
    "self.start_date --> self.global_params['datelist'] --> self.end_date"
    and yields a corresponding temporary 'entries' table name that contains
    the entry ids of the specified intervals.
    """
    # attention: code currently duplicated in view_quantity_vs_status_stats
    if entries_creator is None:
      yield 'entries'
      return
    middatelist = self.global_params.get('datelist', "").split()
    dates = [self.start_date] + middatelist + [self.end_date]
    create = getattr(self.batch, entries_creator)  # returns a method
    i = 0
    while i < len(dates):
      start_date = dates[i]; i += 1
      end_date = dates[i]; i += 1
      view_name = create(start_date=start_date, end_date=end_date)
      yield view_name
    return
  
  def analyze(self, all_ei_ids):
    if self.output == 'interval_table':
      self.interval_table.addIntervals(all_ei_ids.all)
    elif self.output == 'stdout':
      header = self.interval_table.getHeader()
      for view_name, ei_ids in all_ei_ids.iteritems():
        sys.stdout.write("Using subset: %s\n" % view_name)
        sys.stdout.write(self.batch.str_table(header, ei_ids))
      sys.stdout.flush()
    else:
      self.logger.error("Unknown output specified: '%s'" % self.output)
    return


class EntriesViewsResultCollector(OrderedDict):
  # attention: code currently duplicated in view_quantity_vs_status_stats
  def get_all(self):
    res = None
    for val in self.itervalues():
      if res is None:
        res = val
        continue
      res += val
    return res
  all = property(get_all)
