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
    JOIN interval2label AS il ON ei.id = il.entry_intervalid
    JOIN labels AS la         ON il.labelid = la.id
    JOIN labelgroups AS lg    ON la.groupid = lg.id
    WHERE mo.class = "mfc525eval.sensorstatus.search_sensorstatus.Search" AND
          lg.name = "camera status" AND
          la.name != "Fully Operational"
  """
