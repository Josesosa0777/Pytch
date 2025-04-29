# -*- dataeval: init -*-

"""
Queries the simulated AEBS events from the database.

The returned intervals will be loaded into the Interval Table.
"""

from evaltools import analyze_all

init_params = analyze_all.init_params
print_init_params = analyze_all.print_init_params


class Analyze(analyze_all.Analyze):
    QUERY_PAT = """
        SELECT ei.id FROM entryintervals AS ei
            JOIN entries AS en ON en.id = ei.entryid
            JOIN modules AS mo ON mo.id = en.moduleid
            WHERE     mo.class = "dataevalaebs.search_aebs_warning.Search"
                  AND mo.param = 'algo=''SIL KB AEBS'',phases=''calc_aebs_c_sil_phases-DEV_DAF_89KPH_7_15_BRAKING_MBT_tuned_after_Boxberg@aebs.fill'''
    """
# TODO: hardcoded