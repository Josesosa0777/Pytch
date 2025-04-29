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
--$comment
--!COMMENT
