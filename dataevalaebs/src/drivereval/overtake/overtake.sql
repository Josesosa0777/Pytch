--$measurement
SELECT measurements.basename FROM entryintervals
  JOIN entries ON
       entries.id = entryintervals.entryid
  JOIN measurements ON
       measurements.id = entries.measurementid
WHERE  entryintervals.id = ?
--$start [s]
SELECT start_time FROM entryintervals WHERE id = ?
--$duration [s]
SELECT end_time - start_time FROM entryintervals WHERE id = ?
--$max st. wh. speed [rad/s]
SELECT quantities.value FROM entryintervals
  JOIN quantities ON
       entryintervals.id = quantities.entry_intervalid
  JOIN quanames ON
       quantities.nameid = quanames.id
  JOIN quanamegroups ON
       quanames.groupid = quanamegroups.id
WHERE  quanamegroups.name = 'ego vehicle'
  AND  quanames.name = 'steering wheel speed'
  AND  entryintervals.id = ?
--$delta appos [%]
SELECT quantities.value FROM entryintervals
  JOIN quantities ON
       entryintervals.id = quantities.entry_intervalid
  JOIN quanames ON
       quantities.nameid = quanames.id
  JOIN quanamegroups ON
       quanames.groupid = quanamegroups.id
WHERE  quanamegroups.name = 'ego vehicle'
  AND  quanames.name = 'appos'
  AND  entryintervals.id = ?
--$max appos speed [%/s]
SELECT quantities.value FROM entryintervals
  JOIN quantities ON
       entryintervals.id = quantities.entry_intervalid
  JOIN quanames ON
       quantities.nameid = quanames.id
  JOIN quanamegroups ON
       quanames.groupid = quanamegroups.id
WHERE  quanamegroups.name = 'ego vehicle'
  AND  quanames.name = 'appos speed'
  AND  entryintervals.id = ?
--$overtaking type
--!LABEL "overtaking type"
--$overtake info
--!LABEL "overtake information"
--$comment
--!COMMENT