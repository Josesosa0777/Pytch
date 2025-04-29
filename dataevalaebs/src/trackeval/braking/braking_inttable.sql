--Query attributes of braking forward vehicle

--$entry
SELECT entries.title
  FROM entryintervals
  JOIN entries ON entries.id = entryintervals.entryid
 WHERE entryintervals.id = ?
--$measurement
SELECT measurements.basename
  FROM entryintervals
  JOIN entries ON entries.id = entryintervals.entryid
  JOIN measurements ON measurements.id = entries.measurementid
 WHERE entryintervals.id = ?
--$start [s]
SELECT start_time FROM entryintervals WHERE id = ?
--$end [s]
SELECT end_time FROM entryintervals WHERE id = ?
--$duration [s]
SELECT end_time - start_time FROM entryintervals WHERE id = ?
--$ax avg [m/s2]
--!QUANTITY target, ax avg
--$ax std [m/s2]
--!QUANTITY target, ax std
--$ax min [m/s2]
--!QUANTITY target, ax min
--$ax max [m/s2]
--!QUANTITY target, ax max
--$ego speed [m/s]
--!QUANTITY ego vehicle, speed
--$comment
--!COMMENT
