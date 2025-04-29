--$ @, measurement, frame_start, frame_end, start [s], duration [s], camera status, whole time, ego speed min [kph]
SELECT DISTINCT main_tb.ei_id, meas_tb.basename, CAST(frame_st_tb.val AS INTEGER), CAST(frame_end_tb.val AS INTEGER), main_tb.start_time, main_tb.end_time - main_tb.start_time AS duration, main_tb.label, main_tb.whole_time, ego_speed_tb.val
FROM (
  SELECT en.id en_id, ei.id ei_id, ei.position ei_pos, ei.start_time, ei.end_time, la.name label, en.measurementid me_id, ei.start=0 AND ei.end_is_last AS whole_time
  FROM entryintervals ei
  JOIN interval2label il ON ei.id = il.entry_intervalid
  JOIN labels la         ON il.labelid = la.id
  JOIN labelgroups lg    ON la.groupid = lg.id
  JOIN entries en        ON ei.entryid = en.id
  JOIN modules mo        ON en.moduleid = mo.id
  WHERE     lg.name = "camera status"
        AND label != "Fully Operational"
        AND mo.class = "flc20eval.sensorstatus.search_sensorstatus.Search"
  ) main_tb
JOIN (
  SELECT meas.id me_id, meas.basename
  FROM measurements meas
  ) meas_tb ON main_tb.me_id = meas_tb.me_id
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
  SELECT ei.id ei_id, q.value * 3.6 as val
  FROM entryintervals ei
  JOIN quantities q      ON ei.id = q.entry_intervalid
  JOIN quanames qn       ON qn.id = q.nameid
  JOIN quanamegroups qng ON qn.groupid = qng.id
  WHERE     qng.name = "ego vehicle"
        AND qn.name = "speed min"
        AND val > 5
  ) ego_speed_tb ON main_tb.ei_id = ego_speed_tb.ei_id
;
--$ comment
--! COMMENT
