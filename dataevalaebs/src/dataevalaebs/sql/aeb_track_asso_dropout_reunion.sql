--$ @, measurement, start[s], end[s], duration [s], ego speed [kph], ttc min [s], radar obj, dx min [m], mov. st.
SELECT DISTINCT asso_dropout.ei_id, meas_tb.basename,
                MAX(asso_dropout.start_time, aeb_tb.start_time) AS common_start_time,
                MIN(asso_dropout.end_time, aeb_tb.end_time) AS common_end_time,
                MIN(asso_dropout.end_time, aeb_tb.end_time) - MAX(asso_dropout.start_time, aeb_tb.start_time) AS duration,
                egospeed_tb.val, ttc_tb.val, asso_dropout.label,
                dx_tb.val, movst_tb.label
FROM (
  SELECT en.id en_id, ei.id ei_id, ei.position ei_pos, ei.start_time, ei.end_time, la.name label, en.measurementid me_id
  FROM entryintervals ei
  JOIN interval2label il ON ei.id = il.entry_intervalid
  JOIN labels la         ON il.labelid = la.id
  JOIN labelgroups lg    ON la.groupid = lg.id
  JOIN entries en        ON ei.entryid = en.id
  JOIN modules mo        ON en.moduleid = mo.id
  WHERE     lg.name = "AC100 track"
        AND mo.class = "dataevalaebs.search_asso_dropout_reunion_flr20.SearchFlr20AssoReunion"
  ) asso_dropout
JOIN (
  SELECT en.measurementid me_id, la.name label, ei.start_time, ei.end_time
  FROM entryintervals ei
  JOIN interval2label il ON ei.id = il.entry_intervalid
  JOIN labels la         ON il.labelid = la.id
  JOIN labelgroups lg    ON la.groupid = lg.id
  JOIN entries en        ON ei.entryid = en.id
  JOIN modules mo        ON en.moduleid = mo.id
  WHERE lg.name = "AC100 track" AND
        mo.class = "dataevalaebs.search_flr20_aeb_track.SearchFlr20aebTrack"
  ) aeb_tb ON     asso_dropout.me_id = aeb_tb.me_id
              AND asso_dropout.label = aeb_tb.label
JOIN (
  SELECT ei.id ei_id, q.value as val
  FROM entryintervals ei
  JOIN quantities q      ON ei.id = q.entry_intervalid
  JOIN quanames qn       ON qn.id = q.nameid
  JOIN quanamegroups qng ON qn.groupid = qng.id
  WHERE     qng.name = "target"
        AND qn.name = "dx min"
--      AND q.value > 6
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
        AND q.value < 50
  ) ttc_tb ON asso_dropout.ei_id = ttc_tb.ei_id
JOIN (
  SELECT ei.id ei_id, la.name label
  FROM entryintervals ei
  JOIN interval2label il ON ei.id = il.entry_intervalid
  JOIN labels la         ON il.labelid = la.id
  JOIN labelgroups lg    ON la.groupid = lg.id
  WHERE     lg.name = "moving state"
        AND (la.name = "stopped" OR la.name = "stationary")
  ) movst_tb ON asso_dropout.ei_id = movst_tb.ei_id
JOIN (
  SELECT ei.id ei_id, q.value AS val
  FROM entryintervals ei
  JOIN quantities q      ON ei.id = q.entry_intervalid
  JOIN quanames qn       ON qn.id = q.nameid
  JOIN quanamegroups qng ON qn.groupid = qng.id
  WHERE     qng.name = "ego vehicle"
        AND qn.name = "speed"
        AND q.value > 20
  ) egospeed_tb ON asso_dropout.ei_id = egospeed_tb.ei_id
JOIN (
  SELECT meas.id me_id, meas.basename
  FROM measurements meas
  ) meas_tb ON asso_dropout.me_id = meas_tb.me_id
WHERE common_start_time <= common_end_time
;
--$ validity
--! LABEL standard
--$ improvable
--! LABEL improvable
--$ comment
--! COMMENT