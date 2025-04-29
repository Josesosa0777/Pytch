--$ @, measurement, start[s], duration [s], ego sp. avg [kph], ttc min [s], fused duty, radar obj
SELECT DISTINCT main_tb.ei_id, meas_tb.basename, main_tb.start_time,
                main_tb.end_time - main_tb.start_time AS duration,
                egospeed_tb.val, ttc_tb.val, fused_tb.val, main_tb.label
FROM (
  SELECT en.id en_id, ei.id ei_id, ei.position ei_pos, ei.start_time, ei.end_time, la.name label, en.measurementid me_id
  FROM entryintervals ei
  JOIN interval2label il ON ei.id = il.entry_intervalid
  JOIN labels la         ON il.labelid = la.id
  JOIN labelgroups lg    ON la.groupid = lg.id
  JOIN entries en        ON ei.entryid = en.id
  JOIN modules mo        ON en.moduleid = mo.id
  WHERE     lg.name = "AC100 track" 
        AND mo.class = "dataevalaebs.search_aebs_candidates.Search"
  ) main_tb
JOIN (
  SELECT ei.id ei_id, q.value as val
  FROM entryintervals ei
  JOIN quantities q      ON ei.id = q.entry_intervalid
  JOIN quanames qn       ON qn.id = q.nameid
  JOIN quanamegroups qng ON qn.groupid = qng.id
  WHERE     qng.name = "target"
        AND qn.name = "ttc min"
        AND q.value < 10
  ) ttc_tb ON main_tb.ei_id = ttc_tb.ei_id
JOIN (
  SELECT ei.id ei_id, q.value * 3.6 AS val
  FROM entryintervals ei
  JOIN quantities q      ON ei.id = q.entry_intervalid
  JOIN quanames qn       ON qn.id = q.nameid
  JOIN quanamegroups qng ON qn.groupid = qng.id
  WHERE     qng.name = "ego vehicle"
        AND qn.name = "speed"
        AND q.value * 3.6 > 10
  ) egospeed_tb ON main_tb.ei_id = egospeed_tb.ei_id
JOIN (
  SELECT ei.id ei_id
  FROM entryintervals ei
  JOIN interval2label il ON ei.id = il.entry_intervalid
  JOIN labels la         ON il.labelid = la.id
  JOIN labelgroups lg    ON la.groupid = lg.id
  WHERE      lg.name = "moving state"
        AND (la.name = "stopped" OR la.name = "stationary")
  ) mov_st_tb ON main_tb.ei_id = mov_st_tb.ei_id
JOIN (
  SELECT ei.id ei_id, q.value as val
  FROM entryintervals ei
  JOIN quantities q      ON ei.id = q.entry_intervalid
  JOIN quanames qn       ON qn.id = q.nameid
  JOIN quanamegroups qng ON qn.groupid = qng.id
  WHERE     qng.name = "target"
        AND qn.name = "fused duty"
        AND q.value > 0.
  ) fused_tb ON main_tb.ei_id = fused_tb.ei_id
JOIN (
  SELECT meas.id me_id, meas.basename
  FROM measurements meas
  ) meas_tb ON main_tb.me_id = meas_tb.me_id
WHERE duration > 0.5
;
--$ mov. st.
--! LABEL moving state
--$ relevance
--! LABEL relevance
--$ comment
--! COMMENT
