ATTACH '%s' AS merge;

-- insert the new tag groups
INSERT INTO taggroups(name)
           SELECT mtg.name FROM merge.taggroups AS mtg
           WHERE  mtg.name NOT IN
          (SELECT  tg.name FROM taggroups AS tg);


-- insert the new starts
INSERT INTO starts(time)
         SELECT ms.time FROM merge.starts AS ms
         WHERE  ms.time NOT IN
        (SELECT  s.time FROM starts AS s);


-- insert the new measurements
INSERT INTO measurements(basename,    origin,    local,    start)
               SELECT mm.basename, mm.origin, mm.local, mm.start
               FROM merge.measurements AS mm
               WHERE  mm.basename NOT IN
              (SELECT  m.basename FROM measurements AS m);


-- insert the new modules
INSERT INTO modules(class,    param,    version)
          SELECT mm.class, mm.param, mm.version FROM merge.modules AS mm
          WHERE NOT EXISTS(SELECT * FROM modules AS m 
                           WHERE mm.class   = m.class 
                             AND mm.param   = m.param
                             AND mm.version = m.version);


-- insert the new results
INSERT INTO results(name)
          SELECT mr.name FROM merge.results AS mr
          WHERE  mr.name NOT IN
         (SELECT  r.name FROM results AS r);


-- insert the new types
INSERT INTO types(name)
        SELECT mt.name FROM merge.types AS mt
        WHERE  mt.name NOT IN
       (SELECT  t.name FROM types AS t);


-- insert the new label groups
INSERT INTO labelgroups(name,     exclusive)
             SELECT mlg.name, mlg.exclusive FROM merge.labelgroups AS mlg
             WHERE  mlg.name NOT IN
            (SELECT  lg.name FROM labelgroups AS lg);

-- insert the new quanames name groups
INSERT INTO quanamegroups(name)
             SELECT mqng.name FROM merge.quanamegroups AS mqng
             WHERE  mqng.name NOT IN
            (SELECT  qng.name FROM quanamegroups AS qng);

CREATE TABLE merge_tags AS SELECT * FROM merge.tags;
-- update the tag group id of the new tags
UPDATE merge_tags
SET groupid=(SELECT tg.id FROM taggroups AS tg
             JOIN  merge.taggroups ON
                   merge.taggroups.name = tg.name
             WHERE merge.taggroups.id = merge_tags.groupid);
-- insert the new tags
INSERT INTO tags(name, groupid)
          SELECT mt.name, mt.groupid FROM merge_tags AS mt
          WHERE NOT EXISTS (SELECT * FROM tags AS t 
                            WHERE mt.name    = t.name 
                              AND mt.groupid = t.groupid);
DROP TABLE merge_tags;


CREATE TABLE merge_entries AS SELECT * FROM merge.entries;
-- update the start id of the new entries
UPDATE merge_entries
SET startid=(SELECT s.id FROM starts s
             JOIN  merge.starts ON
                   merge.starts.time = s.time
             WHERE merge.starts.id = merge_entries.startid);
-- update the measurement id of the new entries
UPDATE merge_entries 
SET measurementid=(SELECT m.id FROM measurements AS m
                   JOIN  merge.measurements ON
                         merge.measurements.basename = m.basename
                   WHERE merge.measurements.id = merge_entries.measurementid);
-- update the module id of the new entries
UPDATE merge_entries 
SET moduleid=(SELECT m.id FROM modules AS m
                   JOIN  merge.modules ON
                         merge.modules.class   = m.class
                     AND merge.modules.param   = m.param 
                     AND merge.modules.version = m.version
                   WHERE merge.modules.id=merge_entries.moduleid);
-- update the result id of the new entries
UPDATE merge_entries 
SET resultid=(SELECT r.id FROM results AS r
                   JOIN  merge.results ON
                         merge.results.name = r.name
                   WHERE merge.results.id = merge_entries.resultid);
-- update the type id of the new entries
UPDATE merge_entries 
SET typeid=(SELECT t.id FROM types AS t
                   JOIN  merge.types ON
                         merge.types.name = t.name
                   WHERE merge.types.id = merge_entries.typeid);
-- insert the new entries
INSERT INTO entries SELECT * FROM merge_entries
                    WHERE merge_entries.id NOT IN
                   (SELECT e.id FROM entries AS e);

DROP TABLE merge_entries;


INSERT INTO files(name)
           SELECT mf.name FROM merge.files AS mf
           WHERE  mf.name NOT IN
          (SELECT f.name FROM files AS f);


CREATE TABLE merge_labels AS SELECT * FROM merge.labels;
-- update the label group id of the new labels
UPDATE merge_labels 
SET groupid=(SELECT lg.id FROM labelgroups AS lg
                   JOIN  merge.labelgroups ON
                         merge.labelgroups.name = lg.name
                   WHERE merge.labelgroups.id = merge_labels.groupid);
-- insert the new labels
INSERT INTO labels(name, groupid)
         SELECT ml.name, ml.groupid FROM merge_labels AS ml
         WHERE NOT EXISTS (SELECT * FROM labels AS l 
                           WHERE ml.name    = l.name
                             AND ml.groupid = l.groupid);
DROP TABLE merge_labels;

CREATE TABLE merge_quanames AS SELECT * FROM merge.quanames;
-- update the quantity name groupid of the new names
UPDATE merge_quanames
SET groupid=(SELECT qng.id FROM quanamegroups AS qng
                   JOIN  merge.quanamegroups ON
                         merge.quanamegroups.name = qng.name
                   WHERE merge.quanamegroups.id = merge_quanames.groupid);
-- insert new names
INSERT INTO quanames(name, groupid)
         SELECT  mqn.name, mqn.groupid FROM merge_quanames AS mqn
         WHERE NOT EXISTS (SELECT * FROM quanames as qn
                           WHERE mqn.name = qn.name
                             AND mqn.groupid = qn.groupid);
DROP TABLE merge_quanames;

CREATE TABLE merge_entry2tag AS SELECT * FROM merge.entry2tag;
-- update the tag id of the new entry2tag connections
UPDATE merge_entry2tag
SET tagid=(SELECT t.id FROM tags AS t
                JOIN  merge.tags ON
                      merge.tags.name = t.name
                JOIN  merge.taggroups ON
                      merge.taggroups.id = merge.tags.groupid
                JOIN  taggroups AS tg ON
                                   tg.id = t.groupid
                WHERE merge.tags.id = merge_entry2tag.tagid
                  AND merge.taggroups.name = tg.name);
-- insert the new entry2tag connections
INSERT INTO entry2tag(    entryid,     tagid)
               SELECT met.entryid, met.tagid FROM merge_entry2tag AS met
               WHERE NOT EXISTS (SELECT * FROM entry2tag AS et
                                 WHERE met.entryid = et.entryid
                                   AND met.tagid   = et.tagid);
DROP TABLE merge_entry2tag;


-- insert the new enry intervals
INSERT INTO 
entryintervals(    entryid,     position,     start,     end,     end_is_last,     start_time,     end_time)
        SELECT mei.entryid, mei.position, mei.start, mei.end, mei.end_is_last, mei.start_time, mei.end_time
          FROM merge.entryintervals AS mei
        WHERE NOT EXISTS (SELECT * FROM entryintervals AS ei
                          WHERE mei.entryid  = ei.entryid
                            AND mei.position = ei.position);


CREATE TABLE merge_entry2domain AS SELECT * FROM merge.entry2domain;
-- update the new entry domain connections
UPDATE merge_entry2domain
SET fileid=(SELECT f.id FROM files AS f
                 JOIN  merge.files ON
                       merge.files.name=f.name
                 WHERE merge.files.id=merge_entry2domain.fileid);
-- insert te new entry domain connections
INSERT INTO entry2domain(    entryid,     fileid) 
                  SELECT med.entryid, med.fileid FROM merge_entry2domain AS med
                  WHERE NOT EXISTS (SELECT * FROM entry2domain AS ed
                                    WHERE med.entryid = ed.entryid
                                      AND med.fileid  = ed.fileid);
DROP TABLE merge_entry2domain;


CREATE TABLE merge_entry2file AS SELECT * FROM merge.entry2file;
-- update the new entry domain connections
UPDATE merge_entry2file
SET fileid=(SELECT f.id FROM files AS f
                 JOIN  merge.files ON
                       merge.files.name = f.name
                 WHERE merge.files.id = merge_entry2file.fileid);
-- insert te new entry domain connections
INSERT INTO entry2file(    entryid,    fileid) 
                SELECT mef.entryid, mef.fileid FROM merge_entry2file AS mef
                WHERE NOT EXISTS (SELECT * FROM entry2file AS ef
                                  WHERE mef.entryid = ef.entryid
                                    AND mef.fileid  = ef.fileid);
DROP TABLE merge_entry2file;


CREATE TABLE merge_interval2label AS SELECT * FROM merge.interval2label;
-- update new interval labelid
UPDATE merge_interval2label
SET labelid=(SELECT l.id FROM labels AS l
                  JOIN  merge.labels ON
                        merge.labels.name = l.name
                  JOIN  merge.labelgroups ON
                        merge.labelgroups.id = merge.labels.groupid
                  JOIN  labelgroups lg ON
                                    lg.id = l.groupid
                  WHERE merge.labels.id = merge_interval2label.labelid
                    AND merge.labelgroups.name = lg.name);
-- update new interval label connection
UPDATE merge_interval2label
SET entry_intervalid=(
SELECT ei.id FROM entryintervals AS ei
      JOIN  merge.entryintervals ON
            merge.entryintervals.entryid  = ei.entryid
       AND  merge.entryintervals.position = ei.position
      WHERE merge.entryintervals.id = merge_interval2label.entry_intervalid);
--insert new interval label conections
INSERT INTO interval2label(    labelid,     entry_intervalid)
                    SELECT mil.labelid, mil.entry_intervalid 
                      FROM merge_interval2label AS mil
                    WHERE NOT EXISTS (SELECT * FROM interval2label AS il
                                      WHERE mil.labelid          = il.labelid
                                        AND mil.entry_intervalid = il.entry_intervalid); 
DROP TABLE merge_interval2label;

CREATE TABLE merge_quantities AS SELECT * FROM merge.quantities;
-- update new quantity ids
UPDATE merge_quantities
SET nameid=(SELECT qn.id FROM quanames AS qn
                  JOIN  merge.quanames ON
                        merge.quanames.name = qn.name
                  JOIN  merge.quanamegroups ON
                        merge.quanamegroups.id = merge.quanames.groupid
                  JOIN  quanamegroups AS qng ON
                                         qng.id = qn.groupid
                  WHERE merge.quanames.id = merge_quantities.nameid
                    AND merge.quanamegroups.name = qng.name);
-- update new quantity name connection
UPDATE merge_quantities
SET entry_intervalid=(
SELECT ei.id FROM entryintervals AS ei
      JOIN  merge.entryintervals ON
            merge.entryintervals.entryid = ei.entryid
       AND  merge.entryintervals.position = ei.position
      WHERE merge.entryintervals.id = merge_quantities.entry_intervalid);
-- insert new quantity connections
INSERT INTO quantities(nameid,    entry_intervalid,    value)
             SELECT mq.nameid, mq.entry_intervalid, mq.value
               FROM merge_quantities AS mq
             WHERE NOT EXISTS (SELECT * FROM quantities AS q
                               WHERE mq.nameid = q.nameid
                                 AND mq.entry_intervalid = q.entry_intervalid);
DROP TABLE merge_quantities;


CREATE TABLE merge_intervalcomments AS SELECT * FROM merge.intervalcomments;
--update entry intervalids
UPDATE merge_intervalcomments
SET entry_intervalid=(
SELECT ei.id FROM entryintervals AS ei
      JOIN  merge.entryintervals ON
            merge.entryintervals.entryid  = ei.entryid
       AND  merge.entryintervals.position = ei.position
      WHERE merge.entryintervals.id = merge_intervalcomments.entry_intervalid);
--insert new interval comments
INSERT INTO 
intervalcomments(entry_intervalid, comment)
          SELECT mic.entry_intervalid, mic.comment 
            FROM merge_intervalcomments AS mic
          WHERE mic.entry_intervalid NOT IN
         (SELECT ic.entry_intervalid FROM intervalcomments AS ic);
DROP TABLE merge_intervalcomments;


DETACH merge;
