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
            JOIN measurements AS me ON me.id = en.measurementid
            WHERE     mo.class = "dataevalaebs.search_aebs_warning.Search"
            AND (    mo.param = 'algo=''SIL KB AEBS'',phases=''calc_aebs_c_sil_phases-DEV_DAF_80KPH_7.15_BRAKING.DPV@aebs.fill'''
                OR mo.param = 'algo=''SIL KB AEBS'',phases=''calc_aebs_c_sil_phases-DEV_FORD_7.12_NON-BRAKING.DPV@aebs.fill''')
            AND ei.id NOT IN (
                SELECT ford.ei_id
                FROM (
                    SELECT ei.id ei_id, ei.start_time, en.measurementid me_id
                    FROM entryintervals AS ei
                    JOIN entries AS en ON en.id = ei.entryid
                    JOIN modules AS mo ON mo.id = en.moduleid
                    JOIN measurements AS me ON me.id = en.measurementid
                    WHERE     mo.class = "dataevalaebs.search_aebs_warning.Search"
                        AND mo.param = 'algo=''SIL KB AEBS'',phases=''calc_aebs_c_sil_phases-DEV_FORD_7.12_NON-BRAKING.DPV@aebs.fill'''
                ) ford
                JOIN (
                    SELECT ei.id ei_id, ei.start_time, en.measurementid me_id
                    FROM entryintervals AS ei
                    JOIN entries AS en ON en.id = ei.entryid
                    JOIN modules AS mo ON mo.id = en.moduleid
                    JOIN measurements AS me ON me.id = en.measurementid
                    WHERE     mo.class = "dataevalaebs.search_aebs_warning.Search"
                        AND mo.param = 'algo=''SIL KB AEBS'',phases=''calc_aebs_c_sil_phases-DEV_DAF_80KPH_7.15_BRAKING.DPV@aebs.fill'''
                ) daf
                ON     ford.me_id = daf.me_id
                AND ABS(ford.start_time-daf.start_time) BETWEEN 0 AND 2
            )
    """
# TODO: hardcoded
