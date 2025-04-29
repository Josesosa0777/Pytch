--$fullmeas
SELECT IFNULL(measurements.origin, measurements.local) FROM entryintervals
  JOIN entries ON
       entries.id = entryintervals.entryid
  JOIN measurements ON
       measurements.id = entries.measurementid
WHERE  entryintervals.id = ?
--$measurement
SELECT measurements.basename FROM entryintervals
  JOIN entries ON
       entries.id = entryintervals.entryid
  JOIN measurements ON
       measurements.id = entries.measurementid
WHERE  entryintervals.id = ?
--$start [s]
SELECT start_time FROM entryintervals WHERE id = ?
--$end [s]
SELECT end_time FROM entryintervals WHERE id = ?
--$max proc load [%]
SELECT quantities.value FROM entryintervals
  JOIN quantities ON
       entryintervals.id = quantities.entry_intervalid
  JOIN quanames ON
       quantities.nameid = quanames.id
  JOIN quanamegroups ON
       quanames.groupid = quanamegroups.id
WHERE  quanamegroups.name = 'ecu performance'
  AND  quanames.name = 'processor load max'
  AND  entryintervals.id = ?
--$comment
--!COMMENT