# -*- dataeval: init -*-

from evaltools import analyze_all

__doc__ = analyze_all.__doc__

init_params = analyze_all.init_params
print_init_params = analyze_all.print_init_params


class Analyze(analyze_all.Analyze):
  QUERY_PAT = """
    SELECT ei.id FROM entryintervals AS ei
    JOIN %(entries)s AS en ON en.id = ei.entryid
    JOIN modules AS mo ON mo.id = en.moduleid
    WHERE mo.class = "flr20eval.covi.search_covi_error.Search" OR
    mo.class = "flr20eval.covi.search_covi.Search"
  """