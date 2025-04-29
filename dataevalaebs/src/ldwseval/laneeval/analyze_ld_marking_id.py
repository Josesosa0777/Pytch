# -*- dataeval: init -*-

"""
Queries the entries in the database according to the given parameter:
* default: query all entries
* last_entries: query the latest version of the entries
* last_start: query the entries registered by the latest search session run

The returned entries will be loaded into the Interval Table.
"""

from evaltools import analyze_all

init_params = analyze_all.init_params
print_init_params = analyze_all.print_init_params


class Analyze(analyze_all.Analyze):

  QUERY_PAT = """
    SELECT ei.id FROM entryintervals AS ei
    JOIN %(entries)s AS en ON en.id = ei.entryid
    JOIN modules AS mo ON mo.id = en.moduleid
    WHERE mo.class = "ldwseval.laneeval.search_ld_marking_id.Search"
  """
