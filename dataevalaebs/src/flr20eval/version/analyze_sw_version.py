# -*- dataeval: init -*-

"""
Queries the FLR21 SW version from the database.

The returned intervals will be loaded into the Interval Table.
"""

from evaltools import analyze_all

init_params = analyze_all.init_params
print_init_params = analyze_all.print_init_params


class Analyze(analyze_all.Analyze):
  QUERY_PAT = """
    SELECT ei.id FROM entryintervals AS ei
    JOIN %(entries)s AS en ON en.id = ei.entryid
    JOIN modules AS mo ON mo.id = en.moduleid
    WHERE mo.class = "flr20eval.version.search_sw_version.Search"
  """
