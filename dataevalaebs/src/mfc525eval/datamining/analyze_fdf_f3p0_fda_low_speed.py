# -*- dataeval: init -*-

"""
TBD
"""

from evaltools import analyze_all

init_params = analyze_all.init_params
print_init_params = analyze_all.print_init_params


class Analyze(analyze_all.Analyze):
  QUERY_PAT = """
    SELECT ei.id FROM entryintervals AS ei
    JOIN %(entries)s AS en ON en.id = ei.entryid
    JOIN modules AS mo ON mo.id = en.moduleid
    WHERE mo.class = "mfc525eval.datamining.search_fdf_f3p0_fda_low_speed.Search" AND
          en.title = "Fusion3 Data Mining"
  """
