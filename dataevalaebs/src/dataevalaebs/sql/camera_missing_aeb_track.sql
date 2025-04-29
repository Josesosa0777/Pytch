--$ @, measurement, frame_start, frame_end, start [s], duration [s], camera status, ego speed avg [kph], radar track, dx start [m], moving state, ttc min [s]
SELECT DISTINCT main_tb.ei_id, meas_tb.basename, CAST(frame_st_tb.val AS INTEGER), CAST(frame_end_tb.val AS INTEGER), main_tb.start_time, main_tb.end_time - main_tb.start_time AS duration, camst_tb.label, egospeed_tb.val, main_tb.label, dx_start_tb.val, movst_tb.label, ttc_tb.val
FROM (
  SELECT en.id en_id, ei.id ei_id, ei.position ei_pos, ei.start_time, ei.end_time, la.name label, en.measurementid me_id
  FROM entryintervals ei
  JOIN interval2label il ON ei.id = il.entry_intervalid
  JOIN labels la         ON il.labelid = la.id
  JOIN labelgroups lg    ON la.groupid = lg.id
  JOIN entries en        ON ei.entryid = en.id
  JOIN modules mo        ON en.moduleid = mo.id
  WHERE     lg.name = "AC100 track"
        AND mo.class = "dataevalaebs.search_flc20_missing_aeb_track.Search"
        AND end_time-start_time > 1.
  ) main_tb
JOIN (
  SELECT ei.id ei_id, la.name label
  FROM entryintervals ei
  JOIN interval2label il ON ei.id = il.entry_intervalid
  JOIN labels la         ON il.labelid = la.id
  JOIN labelgroups lg    ON la.groupid = lg.id
  WHERE     lg.name = "sensor check"
  ) camst_tb ON main_tb.ei_id = camst_tb.ei_id
JOIN (
  SELECT ei.id ei_id, q.value as val
  FROM entryintervals ei
  JOIN quantities q      ON ei.id = q.entry_intervalid
  JOIN quanames qn       ON qn.id = q.nameid
  JOIN quanamegroups qng ON qn.groupid = qng.id
  WHERE     qng.name = "target"
        AND qn.name = "dx min"
--      AND q.value > 6
        AND q.value < 80
  ) dx_tb ON main_tb.ei_id = dx_tb.ei_id
JOIN (
  SELECT ei.id ei_id, q.value as val
  FROM entryintervals ei
  JOIN quantities q      ON ei.id = q.entry_intervalid
  JOIN quanames qn       ON qn.id = q.nameid
  JOIN quanamegroups qng ON qn.groupid = qng.id
  WHERE     qng.name = "target"
        AND qn.name = "dx start"
  ) dx_start_tb ON main_tb.ei_id = dx_start_tb.ei_id
JOIN (
  SELECT ei.id ei_id, q.value as val
  FROM entryintervals ei
  JOIN quantities q      ON ei.id = q.entry_intervalid
  JOIN quanames qn       ON qn.id = q.nameid
  JOIN quanamegroups qng ON qn.groupid = qng.id
  WHERE     qng.name = "target"
        AND qn.name = "ttc min"
--      AND q.value < 50
  ) ttc_tb ON main_tb.ei_id = ttc_tb.ei_id
JOIN (
  SELECT ei.id ei_id, la.name label
  FROM entryintervals ei
  JOIN interval2label il ON ei.id = il.entry_intervalid
  JOIN labels la         ON il.labelid = la.id
  JOIN labelgroups lg    ON la.groupid = lg.id
  WHERE     lg.name = "moving state"
--      AND (la.name = "stopped" OR la.name = "stationary")
  ) movst_tb ON main_tb.ei_id = movst_tb.ei_id
JOIN (
  SELECT ei.id ei_id, q.value * 3.6 AS val
  FROM entryintervals ei
  JOIN quantities q      ON ei.id = q.entry_intervalid
  JOIN quanames qn       ON qn.id = q.nameid
  JOIN quanamegroups qng ON qn.groupid = qng.id
  WHERE     qng.name = "ego vehicle"
        AND qn.name = "speed"
        AND val > 20.
  ) egospeed_tb ON main_tb.ei_id = egospeed_tb.ei_id
JOIN (
  SELECT ei.id ei_id, q.value as val
  FROM entryintervals ei
  JOIN quantities q      ON ei.id = q.entry_intervalid
  JOIN quanames qn       ON qn.id = q.nameid
  JOIN quanamegroups qng ON qn.groupid = qng.id
  WHERE     qng.name = "mobileye"
        AND qn.name = "frame start"
  ) frame_st_tb ON main_tb.ei_id = frame_st_tb.ei_id
JOIN (
  SELECT ei.id ei_id, q.value as val
  FROM entryintervals ei
  JOIN quantities q      ON ei.id = q.entry_intervalid
  JOIN quanames qn       ON qn.id = q.nameid
  JOIN quanamegroups qng ON qn.groupid = qng.id
  WHERE     qng.name = "mobileye"
        AND qn.name = "frame end"
  ) frame_end_tb ON main_tb.ei_id = frame_end_tb.ei_id
JOIN (
  SELECT meas.id me_id, meas.basename
  FROM measurements meas
  ) meas_tb ON main_tb.me_id = meas_tb.me_id
;
--$ evaluation
--! LABEL standard
--$ comment
--! COMMENT
