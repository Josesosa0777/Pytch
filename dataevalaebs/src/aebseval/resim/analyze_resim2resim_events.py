# -*- dataeval: init -*-

"""
Queries the AEBS events from the database.

The returned intervals will be loaded into the Interval Table.
Intervals that are following a previous interval within 2 seconds are skipped.
"""

from evaltools import analyze_all

init_params = analyze_all.init_params
print_init_params = analyze_all.print_init_params


class Analyze(analyze_all.Analyze):
  QUERY_PAT = """
    SELECT ei.id FROM entryintervals AS ei
    JOIN %(entries)s AS en ON en.id = ei.entryid
    JOIN modules AS mo ON mo.id = en.moduleid
    WHERE mo.class = "aebseval.resim.search_resim2resim_event.Search"
  """
