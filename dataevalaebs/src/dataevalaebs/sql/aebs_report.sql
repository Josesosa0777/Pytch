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
--$duration [s]
SELECT end_time - start_time FROM entryintervals WHERE id = ?
--$moving state
--!LABEL "moving state"
--$asso state
--!LABEL "asso state"
--$cascade phase
--!LABEL "AEBS cascade phase"
--$ego speed [km/h]
SELECT quantities.value * 3.6 FROM entryintervals
  JOIN quantities ON
       quantities.entry_intervalid = entryintervals.id
  JOIN quanames ON
       quanames.id = quantities.nameid
  JOIN quanamegroups ON
       quanamegroups.id = quanames.groupid
WHERE  quanamegroups.name = "ego vehicle" 
  AND  quanames.name = "speed" 
  AND  entryintervals.id = ?
--$dx at start [m]
SELECT quantities.value FROM entryintervals
  JOIN quantities ON
       quantities.entry_intervalid = entryintervals.id
  JOIN quanames ON
       quanames.id = quantities.nameid
  JOIN quanamegroups ON
       quanamegroups.id = quanames.groupid
WHERE  quanamegroups.name = "target" 
  AND  quanames.name = "dx start" 
  AND  entryintervals.id = ?
--$vx at start [km/h]
SELECT quantities.value * 3.6 FROM entryintervals
  JOIN quantities ON
       quantities.entry_intervalid = entryintervals.id
  JOIN quanames ON
       quanames.id = quantities.nameid
  JOIN quanamegroups ON
       quanamegroups.id = quanames.groupid
WHERE  quanamegroups.name = "target" 
  AND  quanames.name = "vx start" 
  AND  entryintervals.id = ?
--$warning rating scale
--!LABEL "AEBS event rating scale"
--$false warning cause
--!LABEL "false warning cause"
--$comment
--!COMMENT
