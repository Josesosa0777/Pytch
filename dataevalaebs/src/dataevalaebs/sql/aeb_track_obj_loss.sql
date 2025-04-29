--$ @, measurement, start[s], duration [s], reason, radar obj, dx start [m], ego speed [kph], mov. st., afterlife
SELECT DISTINCT object_loss.ei_id, meas_tb.basename, object_loss.start_time, object_loss.end_time - object_loss.start_time AS duration, reason_tb.label, object_loss.label, dx_tb.val, egospeed_tb.val, movst_tb.label, afterlife_tb.label
FROM (
  SELECT en.id en_id, ei.id ei_id, ei.position ei_pos, ei.start_time, ei.end_time, la.name label, en.measurementid me_id
  FROM entryintervals ei
  JOIN interval2label il ON ei.id = il.entry_intervalid
  JOIN labels la         ON il.labelid = la.id
  JOIN labelgroups lg    ON la.groupid = lg.id
  JOIN entries en        ON ei.entryid = en.id
  JOIN modules mo        ON en.moduleid = mo.id
  WHERE     lg.name = "AC100 track"
        AND mo.class = "dataevalaebs.search_flr20_object_loss.SearchFlr20ObjectLoss"
  ) object_loss
--JOIN (
--  SELECT en.measurementid me_id, la.name label, ei.start_time, ei.end_time
--  FROM entryintervals ei
--  JOIN interval2label il ON ei.id = il.entry_intervalid
--  JOIN labels la         ON il.labelid = la.id
--  JOIN labelgroups lg    ON la.groupid = lg.id
--  JOIN entries en        ON ei.entryid = en.id
--  JOIN modules mo        ON en.moduleid = mo.id
--  WHERE lg.name = "AC100 track" AND
--        mo.class = "search_flr20_aeb_track.SearchFlr20aebTrack"
--  ) aeb_tb ON     object_loss.me_id = aeb_tb.me_id
--                    AND object_loss.label = aeb_tb.label
--                    AND MAX(object_loss.start_time, aeb_tb.start_time) <= MIN(object_loss.end_time, aeb_tb.end_time)
JOIN (
  SELECT ei.id ei_id, q.value as val
  FROM entryintervals ei
  JOIN quantities q      ON ei.id = q.entry_intervalid
  JOIN quanames qn       ON qn.id = q.nameid
  JOIN quanamegroups qng ON qn.groupid = qng.id
  WHERE     qng.name = "target"
        AND qn.name = "dx start"
        AND q.value > 6
        AND q.value < 60
  ) dx_tb ON object_loss.ei_id = dx_tb.ei_id
--JOIN (
--  SELECT ei.id ei_id, q.value as val
--  FROM entryintervals ei
--  JOIN quantities q      ON ei.id = q.entry_intervalid
--  JOIN quanames qn       ON qn.id = q.nameid
--  JOIN quanamegroups qng ON qn.groupid = qng.id
--  WHERE     qng.name = "target"
--        AND qn.name = "ttc min"
--        AND q.value < 10
--  ) ttc_tb ON object_loss.ei_id = ttc_tb.ei_id
JOIN (
  SELECT ei.id ei_id, la.name label
  FROM entryintervals ei
  JOIN interval2label il ON ei.id = il.entry_intervalid
  JOIN labels la         ON il.labelid = la.id
  JOIN labelgroups lg    ON la.groupid = lg.id
  WHERE     lg.name = "asso breakup reason"
        AND la.name = "radar loss"
  ) reason_tb ON object_loss.ei_id = reason_tb.ei_id
JOIN (
  SELECT ei.id ei_id, la.name label
  FROM entryintervals ei
  JOIN interval2label il ON ei.id = il.entry_intervalid
  JOIN labels la         ON il.labelid = la.id
  JOIN labelgroups lg    ON la.groupid = lg.id
  WHERE     lg.name = "asso afterlife"
        --AND la.name = "lonely"
  ) afterlife_tb ON object_loss.ei_id = afterlife_tb.ei_id
JOIN (
  SELECT ei.id ei_id, la.name label
  FROM entryintervals ei
  JOIN interval2label il ON ei.id = il.entry_intervalid
  JOIN labels la         ON il.labelid = la.id
  JOIN labelgroups lg    ON la.groupid = lg.id
  WHERE     lg.name = "track selection"
        AND la.name = "AEB"
  ) trsel_tb ON object_loss.ei_id = trsel_tb.ei_id
JOIN (
  SELECT ei.id ei_id, la.name label
  FROM entryintervals ei
  JOIN interval2label il ON ei.id = il.entry_intervalid
  JOIN labels la         ON il.labelid = la.id
  JOIN labelgroups lg    ON la.groupid = lg.id
  WHERE     lg.name = "moving state"
        --AND (la.name = "stopped" OR la.name = "stationary")
  ) movst_tb ON object_loss.ei_id = movst_tb.ei_id
JOIN (
  SELECT ei.id ei_id, q.value AS val
  FROM entryintervals ei
  JOIN quantities q      ON ei.id = q.entry_intervalid
  JOIN quanames qn       ON qn.id = q.nameid
  JOIN quanamegroups qng ON qn.groupid = qng.id
  WHERE     qng.name = "ego vehicle"
        AND qn.name = "speed"
        AND q.value > 40
  ) egospeed_tb ON object_loss.ei_id = egospeed_tb.ei_id
JOIN (
  SELECT meas.id me_id, meas.basename
  FROM measurements meas
  ) meas_tb ON object_loss.me_id = meas_tb.me_id
;
--$ validity
--! LABEL standard
