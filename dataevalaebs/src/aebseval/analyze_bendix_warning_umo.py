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
    WHERE mo.class = "dataevalaebs.search_bendix_warning.Search"
      AND mo.param = 'algo=''9-UMO candidate qualified'',target=''fill_flr20_aeb_track@aebs.fill'',warning=''calc_bendix_umo@aebs.fill'''
      AND NOT EXISTS (
            SELECT * FROM entryintervals AS ei_2
            JOIN %(entries)s AS en_2 ON ei_2.entryid = en_2.id
            WHERE en_2.id = en.id AND
                  ei_2.id != ei.id AND
                  ei.start_time-ei_2.end_time BETWEEN 0 AND 2
          )
  """
