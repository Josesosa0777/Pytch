SELECT road_type.label, COUNT(aebs_event.ei_id)
FROM (
  SELECT ei.id ei_id, ei.start_time, ei.end_time, en.measurementid me_id
  FROM entryintervals ei
  JOIN entries en ON en.id = ei.entryid
  JOIN modules mo ON mo.id = en.moduleid
  JOIN measurements me ON me.id = en.measurementid
  WHERE mo.class = "dataevalaebs.search_aebs_warning.Search"
--      AND mo.param = 'algo=''SIL KB AEBS'',phases=''calc_aebs_c_sil_phases-DEV_FORD_7.12_NON-BRAKING.DPV@aebs.fill'''
) aebs_event
JOIN (
  SELECT ei.id ei_id, ei.start_time, ei.end_time, en.measurementid me_id, la.name label
  FROM entryintervals ei
  JOIN entries en ON en.id = ei.entryid
  JOIN modules mo ON mo.id = en.moduleid
  JOIN measurements me ON me.id = en.measurementid
  JOIN interval2label il ON ei.id = il.entry_intervalid
  JOIN labels la         ON il.labelid = la.id
  JOIN labelgroups lg    ON la.groupid = lg.id

  WHERE mo.class = "egoeval.roadtypes.search_roadtypes.Search" AND
        lg.name = "road type"
) road_type ON aebs_event.me_id = road_type.me_id AND
               MAX(aebs_event.start_time, road_type.start_time) <= MIN(aebs_event.end_time, road_type.end_time)
GROUP BY road_type.label
;