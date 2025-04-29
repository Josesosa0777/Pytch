PRAGMA user_version = 230;

CREATE TABLE entries
  (id            TEXT PRIMARY KEY,
   startid       INTEGER,
   measurementid INTEGER,
   moduleid      INTEGER,
   resultid      INTEGER,
   typeid        INTEGER,
   title         TEXT,
   comment       TEXT,

   FOREIGN KEY(startid)       REFERENCES starts(id),
   FOREIGN KEY(measurementid) REFERENCES measurements(id),
   FOREIGN KEY(moduleid)      REFERENCES modules(id),
   FOREIGN KEY(resultid)      REFERENCES results(id),
   FOREIGN KEY(typeid)        REFERENCES types(id),

   UNIQUE(id));

CREATE INDEX index_entries_moduleid ON entries(moduleid);

CREATE TABLE last_entries
  (id TEXT PRIMARY KEY,

  FOREIGN KEY(id) REFERENCES entries(id),

  UNIQUE(id));

CREATE TRIGGER insert_last_entries AFTER INSERT ON entries
WHEN (
      SELECT COUNT() FROM entries
      JOIN  modules AS all_modules ON
            all_modules.id = entries.moduleid
      JOIN  modules AS new_modules ON
            new_modules.id = new.moduleid
      JOIN  measurements AS all_measurements ON
            all_measurements.id = entries.measurementid
      JOIN  measurements AS new_measurements ON
            new_measurements.id = new.measurementid
      WHERE all_measurements.basename = new_measurements.basename
        AND all_modules.class = new_modules.class
        AND all_modules.param = new_modules.param
        AND entries.title = new.title
      ) = 1
BEGIN
  INSERT INTO last_entries(id) VALUES (new.id);
END;

CREATE TRIGGER update_last_entries AFTER INSERT ON entries
WHEN (
      SELECT COUNT() FROM entries
      JOIN  modules AS all_modules ON
            all_modules.id = entries.moduleid
      JOIN  modules AS new_modules ON
            new_modules.id = new.moduleid
      JOIN  measurements AS all_measurements ON
            all_measurements.id = entries.measurementid
      JOIN  measurements AS new_measurements ON
            new_measurements.id = new.measurementid
      JOIN  starts AS new_starts ON
            new_starts.id = new.startid
      JOIN  starts AS all_starts ON
            all_starts.id = entries.startid
      WHERE all_measurements.basename = new_measurements.basename
        AND all_modules.class = new_modules.class
        AND all_modules.param = new_modules.param
        AND entries.title = new.title
        AND new_starts.time > all_starts.time
      ) > 0
BEGIN
  UPDATE last_entries SET id = new.id
  WHERE id = (SELECT last_entries.id FROM last_entries
      JOIN  entries ON
            entries.id = last_entries.id
      JOIN  modules AS all_modules ON
            all_modules.id = entries.moduleid
      JOIN  modules AS new_modules ON
            new_modules.id = new.moduleid
      JOIN  measurements AS all_measurements ON
            all_measurements.id = entries.measurementid
      JOIN  measurements AS new_measurements ON
            new_measurements.id = new.measurementid
      WHERE all_measurements.basename = new_measurements.basename
        AND all_modules.class = new_modules.class
        AND all_modules.param = new_modules.param
        AND entries.title = new.title);
END;

CREATE TABLE files
  (id   INTEGER PRIMARY KEY AUTOINCREMENT,
   name TEXT,

   UNIQUE(name));

CREATE TABLE entry2domain
  (id      INTEGER PRIMARY KEY AUTOINCREMENT,
   entryid TEXT,
   fileid  INTEGER,

   FOREIGN KEY(entryid) REFERENCES entries(id),
   FOREIGN KEY(fileid) REFERENCES files(id),

   UNIQUE(entryid, fileid));

CREATE TABLE intervalcomments
  (id               INTEGER PRIMARY KEY AUTOINCREMENT,
   entry_intervalid INTEGER,
   comment          TEXT,

   UNIQUE(entry_intervalid),
   FOREIGN KEY(entry_intervalid) REFERENCES entryintervals(id));

CREATE TABLE labelgroups
  (id        INTEGER PRIMARY KEY AUTOINCREMENT,
   name      TEXT,
   exclusive BOOL,

   UNIQUE(name));

CREATE TABLE labels
  (id      INTEGER PRIMARY KEY AUTOINCREMENT,
   name    TEXT,
   groupid INTEGER,

   UNIQUE(name, groupid)
   FOREIGN KEY(groupid) REFERENCES labelgroups(id));

CREATE TABLE interval2label
  (id               INTEGER PRIMARY KEY AUTOINCREMENT,
   labelid          INTEGER,
   entry_intervalid INTEGER,

   FOREIGN KEY(labelid)    REFERENCES labels(id),
   FOREIGN KEY(entry_intervalid) REFERENCES entryintervals(id),

   UNIQUE(entry_intervalid, labelid));

CREATE TABLE measurements
  (id       INTEGER PRIMARY KEY AUTOINCREMENT,
   basename TEXT,
   origin   TEXT,
   local    TEXT,
   start     DATETIME,

   UNIQUE(basename));

CREATE TABLE modules
  (id      INTEGER PRIMARY KEY AUTOINCREMENT,
   class  TEXT,
   param   TEXT,
   version TEXT,

   UNIQUE(class, param, version));

CREATE TABLE entryintervals
  (id          INTEGER PRIMARY KEY AUTOINCREMENT,
   entryid     TEXT,
   position    INTEGER,
   start       INTEGER,
   end         INTEGER,
   end_is_last BOOLEAN,
   start_time  REAL,
   end_time    REAL,

   FOREIGN KEY(entryid)   REFERENCES entries(id),

   UNIQUE(entryid, position));

CREATE TABLE starts
  (id   INTEGER PRIMARY KEY AUTOINCREMENT,
   time DATETIME,

   UNIQUE(time));

CREATE TABLE types
  (id   INTEGER PRIMARY KEY AUTOINCREMENT,
   name TEXT,

   UNIQUE(name));

CREATE TABLE taggroups
  (id   INTEGER PRIMARY KEY AUTOINCREMENT,
   name TEXT,

   UNIQUE(name));

CREATE TABLE tags
  (id      INTEGER PRIMARY KEY AUTOINCREMENT,
   name    TEXT,
   groupid INTEGER,

   UNIQUE(name, groupid),

   FOREIGN KEY(groupid) REFERENCES taggroups(id));

CREATE TABLE entry2tag
  (id      INTEGER PRIMARY KEY AUTOINCREMENT,
   entryid TEXT,
   tagid   INTEGER,

   FOREIGN KEY(entryid) REFERENCES entries(id),
   FOREIGN KEY(tagid)   REFERENCES tags(id),

   UNIQUE(entryid, tagid));

CREATE TABLE results
  (id   INTEGER PRIMARY KEY AUTOINCREMENT,
   name TEXT,

   UNIQUE(name));

CREATE TABLE entry2file
  (id      INTEGER PRIMARY KEY AUTOINCREMENT,
   entryid TEXT,
   fileid  INTEGER,

   FOREIGN KEY(entryid) REFERENCES entries(id),
   FOREIGN KEY(fileid)  REFERENCES files(id),

   UNIQUE(entryid, fileid));

CREATE TABLE quantities
  (id               INTEGER PRIMARY KEY AUTOINCREMENT,
   entry_intervalid INTEGER,
   nameid           INTEGER,
   value            REAL,


   FOREIGN KEY(entry_intervalid) REFERENCES entryintervals(id),
   FOREIGN KEY(nameid) REFERENCES quanames(id),

   UNIQUE(entry_intervalid, nameid));

CREATE TABLE quanames
  (id      INTEGER PRIMARY KEY AUTOINCREMENT,
   name    TEXT,
   groupid INTEGER,

   FOREIGN KEY(groupid) REFERENCES quanamegroups(id),

   UNIQUE(name, groupid));

CREATE TABLE quanamegroups
  (id   INTEGER PRIMARY KEY AUTOINCREMENT,
   name TEXT,

   UNIQUE(name));

