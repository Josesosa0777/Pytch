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
    WHERE mo.class = "mfc525eval.laneeval.search_flc25_lane_departure_warnings.Search" AND
          en.title = "FLC25 LDWS"
  """
