ATTACH '%s' AS batch_1;

CREATE TABLE IF NOT EXISTS entries_filter AS
SELECT * from entries
WHERE entries.title='AEBS warnings';

CREATE TABLE IF NOT EXISTS entry_interval_filter AS
SELECT * FROM entryintervals AS ei
INNER JOIN entries_filter ON
ei.entryid = entries_filter.id;

DROP TABLE entries_filter;

CREATE TABLE IF NOT EXISTS entry_interval_batch AS
SELECT * FROM batch_1.entryintervals;

CREATE TABLE IF NOT EXISTS entry_interval_start_time_filter AS
SELECT * FROM entry_interval_filter AS ei
WHERE (SELECT bi.start_time FROM  entry_interval_batch AS  bi
        WHERE bi.start_time = ei.start_time);

DROP TABLE entry_interval_filter;

DROP TABLE entry_interval_batch;

CREATE TABLE IF NOT EXISTS interval2label_filter AS
SELECT * FROM batch_1.interval2label AS li
WHERE (SELECT ci.id FROM entry_interval_start_time_filter as ci
        WHERE ci.id = li.entry_intervalid);

DROP TABLE entry_interval_start_time_filter;

INSERT INTO interval2label(labelid, entry_intervalid)
              SELECT ei.labelid, ei.entry_intervalid FROM interval2label_filter AS ei
      WHERE NOT EXISTS (SELECT * FROM interval2label AS il
                        WHERE ei.labelid          = il.labelid
                          AND ei.entry_intervalid = il.entry_intervalid);

DROP TABLE interval2label_filter;

DETACH batch_1;