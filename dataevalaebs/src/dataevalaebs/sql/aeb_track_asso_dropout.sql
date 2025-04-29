--$ @, measurement, start[s], duration [s], dx min [m], ego sp. avg [kph], ttc min [s], radar obj, video obj
SELECT DISTINCT asso_dropout.ei_id, meas_tb.basename, asso_dropout.start_time,
                asso_dropout.end_time - asso_dropout.start_time AS duration,
                dx_tb.val, egospeed_tb.val, ttc_tb.val, asso_dropout.label,
                cam_tb.label
FROM (
  SELECT en.id en_id, ei.id ei_id, ei.position ei_pos, ei.start_time, ei.end_time, la.name label, en.measurementid me_id
  FROM entryintervals ei
  JOIN interval2label il ON ei.id = il.entry_intervalid
  JOIN labels la         ON il.labelid = la.id
  JOIN labelgroups lg    ON la.groupid = lg.id
  JOIN entries en        ON ei.entryid = en.id
  JOIN last_entries laen ON en.id = laen.id
  JOIN modules mo        ON en.moduleid = mo.id
  WHERE     lg.name = "AC100 track" 
        AND mo.class = "dataevalaebs.search_flr20_aeb_track_asso_dropout.SearchFlr20AssoDropout"
  ) asso_dropout
JOIN (
  SELECT ei.id ei_id, q.value as val
  FROM entryintervals ei
  JOIN quantities q      ON ei.id = q.entry_intervalid
  JOIN quanames qn       ON qn.id = q.nameid
  JOIN quanamegroups qng ON qn.groupid = qng.id
  WHERE     qng.name = "target"
        AND qn.name = "dx min"
        AND q.value < 60
  ) dx_tb ON asso_dropout.ei_id = dx_tb.ei_id
JOIN (
  SELECT ei.id ei_id, q.value as val
  FROM entryintervals ei
  JOIN quantities q      ON ei.id = q.entry_intervalid
  JOIN quanames qn       ON qn.id = q.nameid
  JOIN quanamegroups qng ON qn.groupid = qng.id
  WHERE     qng.name = "target"
        AND qn.name = "ttc min"
        AND q.value < 10
  ) ttc_tb ON asso_dropout.ei_id = ttc_tb.ei_id
JOIN (
  SELECT ei.id ei_id, q.value AS val
  FROM entryintervals ei
  JOIN quantities q      ON ei.id = q.entry_intervalid
  JOIN quanames qn       ON qn.id = q.nameid
  JOIN quanamegroups qng ON qn.groupid = qng.id
  WHERE     qng.name = "ego vehicle"
        AND qn.name = "speed"
        AND q.value > 10
  ) egospeed_tb ON asso_dropout.ei_id = egospeed_tb.ei_id
LEFT JOIN (
  SELECT ei.id ei_id, la.name label
  FROM entryintervals ei
  JOIN interval2label il ON ei.id = il.entry_intervalid
  JOIN labels la         ON il.labelid = la.id
  JOIN labelgroups lg    ON la.groupid = lg.id
  WHERE     lg.name = 'S-Cam object'
  ) cam_tb ON asso_dropout.ei_id = cam_tb.ei_id
JOIN (
  SELECT meas.id me_id, meas.basename
  FROM measurements meas
  ) meas_tb ON asso_dropout.me_id = meas_tb.me_id
--WHERE duration < 5
;
--$ mov. st.
--! LABEL moving state
--$ camera status
--! LABEL camera status
--$ relevance
--! LABEL relevance
--$ dropout cause
--! LABEL fusion dropout cause
--$ improvable
--! LABEL improvable
--$ comment
--! COMMENT
