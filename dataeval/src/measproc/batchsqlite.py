import os
import re
import sys
import md5
import time
import uuid
import shutil
import sqlite3
import logging
import zipfile
import datetime
from collections import OrderedDict
from operator import itemgetter

import numpy
from xlrd import open_workbook

import measproc
from Report import cFileReport, iReport, iXmlNpy
from IntervalList import cIntervalList
from workspace import FileWorkSpace, WorkSpace
from textentry import FileTextEntry, TextEntry
from figentry import FileFigEntry, FigEntry
from Statistic import cFileStatistic, iStatistic
from report2 import Report
from measparser.filenameparser import FileNameParser
from measparser.SignalSource import findParser
from measparser.iParser import iParser


class Result:
    FAILED = 'failed'
    PASSED = 'passed'
    INCONS = 'incons'
    NONE = 'none'
    ERROR = 'error'

    @classmethod
    def to_tuple(cls):
        return cls.PASSED, cls.FAILED, cls.ERROR, cls.INCONS, cls.NONE


RESULTS = Result.to_tuple()


def str_cell(cell, none_value='n/a', float_fmt='%.2f', sep='; '):
    if cell is None:
        return none_value
    if isinstance(cell, basestring):
        return cell
    if isinstance(cell, int):
        return "%d" % cell
    if isinstance(cell, float):
        return float_fmt % cell
    if isinstance(cell, (list, tuple, set)):
        if len(cell) == 0:
            return none_value
        return sep.join(str_cell(subcell) for subcell in cell)  # recursion
    return str(cell)


def getType(entry):
    """
    Get the type string of the `entry` to register it into batch.

    :Parameter:
      entry : iReport|Report|iStatistic|Workspace|TextEntry|FigEntry
    :ReturnType: str
    """
    for type, methods in Batch.types.iteritems():
        if isinstance(entry, methods['type']):
            return type
    raise ValueError('unregistered entry type: %s' % entry.__class__.__name__)


def cursor(method):
    """Decorator to call method of batch with an extra cursor as second parameter.
    """

    def wrapper(self, *args, **kwargs):
        cur = self.con.cursor()
        res = method(self, cur, *args, **kwargs)
        cur.close()
        return res

    return wrapper


def commit(method):
    """
    Decorator to call method of batch with an extra cursor as second parameter and
    commit the changes.
    """

    def wrapper(self, *args, **kwargs):
        cur = self.con.cursor()
        res = method(self, cur, *args, **kwargs)
        cur.close()
        self.con.commit()
        return res

    return wrapper


def fetch(method):
    """
    Decorator to call method of batch with an extra cursor as second parameter,
    and call fetch/fetchone over the result.

    :Keywords:
      fetchone : bool
    """

    def wrapper(self, *args, **kwargs):
        cur = self.con.cursor()
        fetchone = kwargs.pop('fetchone', False)
        method(self, cur, *args, **kwargs)
        if fetchone:
            res = cur.fetchone()
        else:
            res = cur.fetchall()
        cur.close()
        return res

    return wrapper


def _init_db(cur, initscript):
    """
    Execute the `initscript` script.

    :Parameters:
      cur : sqlite3.Cursor
      initscript : str
        name of the init script
    """
    initscript = open(initscript).read()
    cur.executescript(initscript)
    return


def _merge_db(cur, mergescript, dbname):
    """
    Merge `dbname` with `mergescript` sql script into the connection of `cur`.

    :Parameters:
      cur : sqlite3.Cursor
      mergescript : str
        name of the merge script
      dbname : str
        name of the other db
    """
    mergescript = open(mergescript).read()
    mergescript = mergescript % dbname
    cur.executescript(mergescript)
    return


def _pack_batch(cur, batch, repdir, output, repdir_only=False):
    zf = zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED)
    try:
        batch_bn = os.path.basename(batch)
        res = cur.execute('SELECT name FROM files')
        for name, in res:
            if not repdir_only and name == batch_bn:
                raise AssertionError('Cannot store batch database as "{}" is part of the '
                                     'report directory'.format(name))
            fil = os.path.join(repdir, name)
            if os.path.isfile(fil):
                zf.write(fil, name)
            else:
                sys.stderr.write('[WARNING] File not found: {}\n'.format(name))
        if not repdir_only:
            zf.write(batch, batch_bn)
    finally:
        zf.close()
    return


def _dump_db(con, output):
    cur = con.cursor()
    db_version = _get_db_user_version(cur)
    with open(output, 'w') as f:
        f.write("PRAGMA user_version = {};\n\n".format(db_version))
        f.writelines('{}\n'.format(line) for line in con.iterdump())
    cur.close()
    return


def _table_is_exist(cur, name):
    cur.execute('''
    SELECT name FROM sqlite_master WHERE type=:type AND name=:name''',
                dict(type='table', name=name))
    return cur.fetchone()


def _table_is_exist_temp(cur, name):
    cur.execute('''
    SELECT name FROM sqlite_temp_master WHERE type=:type AND name=:name''',
                dict(type='table', name=name))
    return cur.fetchone()


def _clone_schema_to_temp_table(cur, master, name):
    master = 'entries'
    cur.execute('''
      SELECT sql FROM sqlite_master WHERE type=:type AND name=:name''',
                dict(type='table', name=master))
    schema, = cur.fetchone()
    schema = schema.replace('TABLE', 'TEMP TABLE').replace(master, name)
    cur.execute(schema)
    return


def _get_columns(cur):
    return [desc[0] for desc in cur.description]


def _add_label(cur, groupid, name):
    """
    Add label to the labels table.

    :Parameters:
      cur : sqlite3.Cursor
      groupid : int
        groupid to labels table
      name : str
        name to labels table
    """
    try:
        cur.execute('INSERT INTO labels(groupid, name) VALUES (?, ?);',
                    (groupid, name))
    except sqlite3.IntegrityError:
        pass
    return


def _add_labelgroup(cur, name, exclusive):
    """
    Add label group to the labelgroups table.

    :Parameters:
      cur : sqlite3.Cursor
      name : str
        name to labelgroups table
      exclusive : bool
        exclusive to labelgroups table
    :ReturnType: int
    :Return: id from labelgroups table
    """
    try:
        cur.execute('INSERT INTO labelgroups(name, exclusive) VALUES (?, ?);',
                    (name, exclusive))
    except sqlite3.IntegrityError:
        cur.execute('SELECT id FROM labelgroups WHERE name=?', (name,))
        groupid, = cur.fetchone()
    else:
        groupid = cur.lastrowid
    return groupid


def _add_labels(cur, group, exclusive, labels):
    """
    Add labels and their label group to batch.

    :Parameters:
      cur : sqlite3.Cursor
      group : str
        name to labelgroups table
      exclusive : bool
        exclusive to labelgroups table
      labels : list
        [name_to_labels_table<str>]
    """
    groupid = _add_labelgroup(cur, group, exclusive)
    for label in labels:
        _add_label(cur, groupid, label)
    return


def _add_quanames(cur, group, names):
    """
    :Parameters:
      cur : sqlite3.Cursor
      group : str
        name o the quantity name group
      names : list
        [value_name]
    """
    groupid = _add_quanamegroup(cur, group)
    for name in names:
        _add_quaname(cur, groupid, name)
    return


def _add_quanamegroup(cur, name):
    """
    :Parameters:
      cur : sqlite3.Cursor
      name : str
        name o the quantity name group
    :ReturnType: int
    :Return: id of the quanamegroup
    """
    try:
        cur.execute('INSERT INTO quanamegroups(name) VALUES(?);', (name,))
    except sqlite3.IntegrityError:
        cur.execute('SELECT id FROM quanamegroups WHERE name=?', (name,))
        groupid, = cur.fetchone()
    else:
        groupid = cur.lastrowid
    return groupid


def _add_quaname(cur, groupid, name):
    """
    :Parameters:
      cur : sqlite3.Cursor
      groupid : int
      name : str
        name o the quantity name group
    """
    try:
        cur.execute('INSERT INTO quanames(groupid, name) VALUES(?, ?);',
                    (groupid, name))
    except sqlite3.IntegrityError:
        pass
    return


def _add_tag(cur, groupid, name):
    """
    Add tag to the tags table.

    :Parameters:
      cur : sqlite3.Cursor
      groupid : str
        groupid to tags table
      name : str
        name to tags table
    """
    try:
        cur.execute('INSERT INTO tags(groupid, name) VALUES (?, ?);',
                    (groupid, name))
    except sqlite3.IntegrityError:
        pass
    return


def _add_taggroup(cur, name):
    """
    Add tag group to taggroups table.

    :Parameters:
      cur : sqlite3.Cursor
      name : str
        name to taggroups table
    :ReturnType: int
    :Return: id to taggroups table
    """
    try:
        cur.execute('INSERT INTO taggroups(name) VALUES (?);', (name,))
    except sqlite3.IntegrityError:
        cur.execute('SELECT id FROM taggroups WHERE name=?', (name,))
        groupid, = cur.fetchone()
    else:
        groupid = cur.lastrowid
    return groupid


def _add_tags(cur, group, tags):
    """
    Add tags and their tag group to batch.

    :Parameters:
      cur : sqlite3.Cursor
      group : str
        name to taggroups table
      tags : list
        [name_to_tags_table<str>]
    """
    groupid = _add_taggroup(cur, group)
    for tag in tags:
        _add_tag(cur, groupid, tag)
    return


def _add_result(cur, result):
    """
    Add result to results table.

    :Parameters:
      cur : sqlite3.Cursor
      name : str
        name to results table
    """
    try:
        cur.execute('INSERT INTO results(name) VALUES (?);', (result,))
    except sqlite3.IntegrityError:
        pass
    return


def _add_results(cur, results):
    """
    Add results to batch.

    :Parameters:
      cur : sqlite3.Cursor
      results : list
        [name_to_results_table<str>]
    """
    for result in results:
        _add_result(cur, result)
    return


def _add_type(cur, type):
    """
    Add type to the types table.

    :Parameters:
      cur : sqlite3.Cursor
      type : str
        name to type table
    """
    try:
        cur.execute('INSERT INTO types(name) VALUES(?)', (type,))
    except sqlite3.IntegrityError:
        pass
    return


def _add_types(cur, types):
    """
    Add types to batch.

    :Parameters:
      cur : sqlite3.Cursor
      types : list
        [name_to_types_table<str>]
    """
    for type in types:
        _add_type(cur, type)
    return


def _add_words(cur, labels, tags, results, types, quanames):
    """
    :Parameters:
      cur : sqlite3.Cursor
      labels : dict
        {name_to_labelgroups_table<str>: (exclusive_to_labelgroups_table<bool>,
                                          [name_to_labels_table<str>])}
      tags : dict
        {name_to_tags_table<str>: [name_to_tags_table<str>]}
      results : list
        [name_to_results_table<str>]
      types : list
        [name_to_types_table<str>]
      quanames : dict
        {group_name<str>: {value_name}}
    """
    for group_name, (exclusive, label_names) in labels.iteritems():
        _add_labels(cur, group_name, exclusive, label_names)
    for group_name, tag_names in tags.iteritems():
        _add_tags(cur, group_name, tag_names)
    _add_results(cur, results)
    _add_types(cur, types)
    for group_name, value_names in quanames.iteritems():
        _add_quanames(cur, group_name, value_names)
    return


def _add_start(cur, start):
    """
    :Parameters:
      cur : sqlite3.Cursor
      start : str
        time to starts table
    :ReturnType: int
    :Return: id from starts table
    """
    try:
        cur.execute('INSERT INTO starts(time) VALUES(?)', (start,))
    except sqlite3.IntegrityError:
        cur.execute('SELECT id FROM starts WHERE time=?', (start,))
        startid, = cur.fetchone()
    else:
        startid = cur.lastrowid
    return startid


def _add_measurement(cur, measurement, local, start):
    """
    :Parameters:
      cur : sqlite3.Cursor
      measurement : str
        source of basename, local or origin in measurements table
      local : bool
        set measurement as local or origin
      start : str
        start of the measurement
    :ReturnType: int
    :Return: id from measurements table
    """
    basename = os.path.basename(measurement)
    source = 'local' if local else 'origin'
    try:
        cur.execute('INSERT INTO measurements(basename, %s, start) VALUES(?, ?, ?);'
                    % source,
                    (basename, measurement, start))
    except sqlite3.IntegrityError:
        cur.execute('SELECT id FROM measurements WHERE basename=?', (basename,))
        measurementid, = cur.fetchone()
        cur.execute('UPDATE measurements SET %s=? WHERE id=?' % source,
                    (measurementid, measurement))
    else:
        measurementid = cur.lastrowid
    return measurementid


def _add_module(cur, class_name, param, version):
    """
    :Parameters:
      cur : sqlite3.Cursor
      class_name : str
        class to modules table
      param : str
        param to modules table
      version : str
        version to modules table
    :ReturnType:
    :Return: id from modules table
    """
    try:
        cur.execute('INSERT INTO modules(class, param, version) VALUES(?, ?, ?)',
                    (class_name, param, version))
    except sqlite3.IntegrityError:
        cur.execute('SELECT id FROM modules '
                    'WHERE class=? AND param=? AND version=?',
                    (class_name, param, version))
        moduleid, = cur.fetchone()
    else:
        moduleid = cur.lastrowid
    return moduleid


def _add_file(cur, name):
    """
    :Parameters:
      cur : sqlite3.Cursor
      name : str
        name to files table
    :ReturnType: int
    :Return: id from files table
    """
    try:
        cur.execute('INSERT INTO files(name) VALUES(?)', (name,))
    except sqlite3.IntegrityError:
        cur.execute('SELECT id FROM files WHERE name=?', (name,))
        fileid, = cur.fetchone()
    else:
        fileid = cur.lastrowid
    return fileid


def _add_entry(cur,
               startid,
               measurementid,
               moduleid,
               resultid,
               typeid,
               title,
               comment):
    """
    :Parameters:
      cur : sqlite3.Cursor
      startid : int
        id from starts table
      measurementid : int
        id from measurements table
      moduleid : int
        id from modules table
      resultid : int
        id from results table
      typeid : int
        id from results table
      title : str
        title to entries table
      comment : str
        comment to entries table
    :ReturnType: int
    :Return: id from entries table
    """
    entryid = uuid.uuid1()
    entryid = str(entryid)
    cur.execute("""
              INSERT INTO entries(id,
                                  startid,
                                  measurementid,
                                  moduleid,
                                  resultid,
                                  typeid,
                                  title,
                                  comment)
              VALUES(?, ?, ?, ?, ?, ?, ?, ?);
              """,
                (entryid,
                 startid,
                 measurementid,
                 moduleid,
                 resultid,
                 typeid,
                 title,
                 comment))
    return entryid


def _select_filename_by_entryid(cur, entryid):
    """
    :Parameters:
      entryid : str
        id from entries table
    """
    cur.execute('SELECT files.name FROM files '
                'LEFT OUTER JOIN entry2file ON files.id=entry2file.fileid '
                'WHERE entry2file.entryid=?', (entryid,))
    return


def _get_typeid(cur, type):
    """
    :Parameters:
      cur : sqlite3.Cursor
      type : str
        name from types table
    :ReturnType: int
    :Return: id from types table
    """
    cur.execute('SELECT id FROM types WHERE name=?', (type,))
    typeid = cur.fetchone()
    assert typeid is not None, '%s is not registered type' % type
    typeid, = typeid
    return typeid


def _get_resultid(cur, result):
    """
    :Parameters:
      cur : sqlite3.Cursor
      result : str
        name from results table
    :ReturnType: int
    :Return: id from results table
    """
    cur.execute('SELECT id FROM results WHERE name=?', (result,))
    resultid = cur.fetchone()
    assert resultid is not None, '%s is not a registered result' % result
    resultid, = resultid
    return resultid


def _get_tagid(cur, tag):
    """
    :Parameters:
      cur : sqlite3.Cursor
      tag : str
        name from tags table
    :ReturnType: int
    :Return: id from tags table
    """
    cur.execute('SELECT id FROM tags WHERE name=?', (tag,))
    tagid = cur.fetchone()
    assert tagid is not None, '%s is not a registered tag' % tag
    tagid, = tagid
    return tagid


def _get_labelgroupname_by_id(cur, groupid):
    """
    :Parameters:
      cur : sqlite3.Cursor
      groupid : int
        id from labelgroups table
    :ReturnType: str
    :Return: name from labelgroups table
    """
    cur.execute('SELECT name FROM labelgroups WHERE id=?', (groupid,))
    name, = cur.fetchone()
    return name


def _get_labelgroupid(cur, group):
    """
    :Parameters:
      cur : sqlite3.Cursor
      group : str
        name from labelgroups table
    :ReturnType: int
    :Return: id from labelgroups table
    """
    cur.execute('SELECT id FROM labelgroups WHERE name=?', (group,))
    groupid = cur.fetchone()
    assert groupid is not None, 'invalid label group: %s' % group
    groupid, = groupid
    return groupid


def _get_labelgroup_by_id(cur, groupid):
    """
    :Parameters:
      cur : sqlite3.Cursor
      groupid : int
        id from labelgroups table
    :ReturnType: tuple
    :Return: (exclusive_from_labelgroups_table<bool>,
              [name_from_labels_table<str>])
    """
    cur.execute('SELECT exclusive FROM labelgroups WHERE id=?', (groupid,))
    exclusive, = cur.fetchone()
    cur.execute('SELECT name FROM labels WHERE groupid=?', (groupid,))
    labels = [label for label, in cur.fetchall()]
    return exclusive, labels


def _get_labelgroup(cur, groupname):
    """
    Get the label group of `groupname`

    :Parameters:
      cur : sqlite3.Cursor
      groupname : str
        name from labelgroups
    :ReturnType: tuple
    :Return:
      (exclusive_from_labelgroups_table<bool>,
       [name_from_labels_table<str>])
    """
    groupid = _get_labelgroupid(cur, groupname)
    return _get_labelgroup_by_id(cur, groupid)


def _get_labelid(cur, labelgroup, label):
    cur.execute("""
              SELECT labels.id FROM labels
                JOIN labelgroups ON
                     labelgroups.id = labels.groupid
              WHERE  labelgroups.name = ?
                AND  labels.name = ?
              """, (labelgroup, label))
    labelid, = cur.fetchone()
    return labelid


def _get_quagroupname_by_id(cur, groupid):
    """
    :Parameters:
      cur : sqlite3.Cursor
      groupid : int
    :ReturnType: str
    """
    cur.execute('SELECT name FROM quanamegroups WHERE id=?', (groupid,))
    name, = cur.fetchone()
    return name


def _get_quanames(cur, groupname):
    """
    :Parameters:
      cur : sqlite3.Cursor
      groupname : str
    :ReturnType: list
    :Return: [value_name<str>]
    """
    groupid = _get_quagroupid(cur, groupname)
    return _get_quanamegroup_by_id(cur, groupid)


def _get_quagroupid(cur, groupname):
    """
    :Parameters:
      cur : sqlite3.Cursor
      groupname : str
    :ReturnType: int
    """
    cur.execute('SELECT id FROM quanamegroups WHERE name=?', (groupname,))
    groupid = cur.fetchone()
    assert groupid is not None, 'invalid quanames name group: %s' % groupname
    groupid, = groupid
    return groupid


def _get_quanamegroup_by_id(cur, groupid):
    """
    :Parameters:
      cur : sqlite3.Cursor
      name : str
    :ReturnType: list
    :Return: [value_name<str>]
    """
    cur.execute('SELECT name FROM quanames WHERE groupid=?', (groupid,))
    return [name for name, in cur.fetchall()]


def _get_type(cur, entryid):
    """
    :Parameters:
      cur : sqlite3.Cursor
      entryid : str
        id from entries table
    :ReturnType: int
    :Return: name from types table
    """
    cur.execute("""SELECT types.name FROM types
                 LEFT OUTER JOIN entries ON
                                 entries.typeid=types.id
                 WHERE entries.id=?""", (entryid,))
    type, = cur.fetchone()
    return type


def _get_labelids(cur, entry_intervalid):
    """
    Get the registered labelids for the `entry_intervalid` from

    :Parameters:
      cur : sqlite3.Cursor
      entry_intervalid : int
        id from entryintervals table
    :ReturnType: set
    :Return: {id_from_labels_table<int>}
    """
    cur.execute('SELECT labelid FROM interval2label WHERE entry_intervalid=?',
                (entry_intervalid,))
    return set([labelid for labelid, in cur.fetchall()])


def _get_quanameids(cur, entry_intervalid):
    cur.execute('SELECT nameid, value from quantities WHERE entry_intervalid=?',
                (entry_intervalid,))
    return dict(cur.fetchall())


def _get_measurementid(cur, entryid):
    """
    :Parameters:
      cur : sqlite3.Cursor
      entryid : str
        id from entries table
    :ReturnType: int
    :Return: id from measurements table
    """
    cur.execute('SELECT measurementid FROM entries WHERE id=?', (entryid,))
    measurementid, = cur.fetchone()
    return measurementid


def _get_measurement(cur, measurementid):
    cur.execute(
        "SELECT IFNULL(local, origin), local FROM measurements WHERE id=?",
        (measurementid,))
    name, local = cur.fetchone()
    return name, local


def _get_measurement_by_intervalid(cur, entry_intervalid):
    cur.execute("""
    SELECT IFNULL(measurements.local, measurements.origin), measurements.local
      FROM entryintervals
      JOIN entries ON
           entries.id = entryintervals.entryid
      JOIN measurements ON
           measurements.id = entries.measurementid
     WHERE entryintervals.id = ?
    """, (entry_intervalid,))
    name, local = cur.fetchone()
    return name, local


def _get_measurement_basename_by_intervalid(cur, entry_intervalid):
    cur.execute("""
    SELECT measurements.basename FROM entryintervals
      JOIN entries ON
           entries.id = entryintervals.entryid
      JOIN measurements ON
           measurements.id = entries.measurementid
     WHERE entryintervals.id = ?
    """, (entry_intervalid,))
    name, = cur.fetchone()
    return name


def _get_title_comment(cur, entryid):
    """
    :Parameters:
      cur : sqlite3.Cursor
      entryid : str
        id from entries table
    :ReturnType: str, str
    :Return:
      title<str>
      comment<str>
    """
    cur.execute('SELECT title, comment FROM entries WHERE id=?', (entryid,))
    return cur.fetchone()


def _get_title_comment_result_by_intervalid(cur, entry_intervalid):
    """
    :Parameters:
      cur : sqlite3.Cursor
      entry_intervalid : str
        id from entry_intervals table
    :ReturnType: str, str, str
    :Return:
      title<str>
      comment<str>
      result<str>
    """
    cur.execute("""
    SELECT entries.title, entries.comment, results.name
      FROM entries
      JOIN results ON results.id = entries.resultid
      JOIN entryintervals ON entryintervals.entryid = entries.id
     WHERE entryintervals.id=?
     """, (entry_intervalid,))
    return cur.fetchone()


def _get_comment(cur, entryid):
    """
    Get the comment of `entryid` in entries table.

    :Parameters:
      cur : sqlite3.Cursor
      entryid : str
        id from entries table
    :ReturnType: comment
    """
    cur.execute('SELECT comment FROM entries WHERE id=?', (entryid,))
    comment, = cur.fetchone()
    return comment


def _get_interval_attr(cur, interval_id, attr_name):
    """
    :Parameters:
      interval_id : int
      attr_name : str
        Valid attribute names are: comment, start, end, start_time, end_time
    :Exceptions:
      ValueError : invalid attr_name
    """
    tables = {'comment': ('intervalcomments', 'entry_intervalid')}

    if attr_name in {'start', 'end', 'start_time', 'end_time'}:
        select = 'SELECT %s FROM entryintervals' % attr_name
    elif attr_name in tables:
        table, table_id = tables[attr_name]
        select = """
             SELECT %(table)s.%(attr_name)s FROM entryintervals
               JOIN %(table)s ON
                    %(table)s.%(table_id)s = entryintervals.id
             """ % locals()
    else:
        raise ValueError('Invalid interval attribute name: %s' % attr_name)
    cur.execute(select + ' WHERE entryintervals.id = ?', (interval_id,))
    attr = cur.fetchone()
    if attr is not None:
        attr, = attr
    return attr


def _get_interval_by_entryid(cur, entryid):
    """
    :Parameters:
      cur : sqlite3.Cursor
      entryid : str
        id from entries table
    :ReturnType: list
    :Return: [(entry_intervalid, start, end, comment)]
    """
    cur.execute("""
    SELECT entryintervals.id,
           entryintervals.start,
           entryintervals.end,
           intervalcomments.comment
    FROM entryintervals
    LEFT OUTER JOIN intervalcomments ON
                    intervalcomments.entry_intervalid=entryintervals.id
    WHERE entryintervals.entryid=?
    ORDER BY entryintervals.position""", (entryid,))
    return cur.fetchall()


def _get_domainname_by_entryid(cur, entryid):
    """
    :Parameters:
      cur : sqlite3.Cursor
      entryid : str
        id from entries table
    :ReturnType: str
    :Return: name from files table
    """
    cur.execute("""SELECT files.name FROM files
                 LEFT OUTER JOIN entry2domain ON
                                 entry2domain.fileid=files.id
                 WHERE entry2domain.entryid=?""", (entryid,))
    domainname, = cur.fetchone()
    return domainname


def _get_labels(cur, entry_intervalid):
    """
    :Parameters:
      cur : sqlite3.Cursor
      entry_intervalid : int
        id from entryintervals table
    :ReturnType: list
    :Return: [(groupid<int>, label<int>)]
    """
    cur.execute("""SELECT labels.groupid,
                        labels.name
                 FROM   labels
                 LEFT OUTER JOIN interval2label ON
                                 interval2label.labelid=labels.id
                 WHERE interval2label.entry_intervalid=?""", (entry_intervalid,))
    return cur.fetchall()


def _get_labels_by_labelgroup(cur, entry_intervalid, labelgroup):
    cur.execute("""
              SELECT labels.name FROM entryintervals
                JOIN interval2label ON
                     interval2label.entry_intervalid = entryintervals.id
                JOIN labels ON
                     labels.id = interval2label.labelid
                JOIN labelgroups ON
                     labelgroups.id = labels.groupid
              WHERE  entryintervals.id = ?
                AND  labelgroups.name = ?""", (entry_intervalid, labelgroup))
    labels = [label for label, in cur.fetchall()]
    return labels


def _get_qua_by_names(cur, entry_intervalid, quagroup, qua, factor=1.0, offset=0.0):
    cur.execute("""
              SELECT ? * quantities.value + ? FROM entryintervals
                JOIN quantities ON
                     quantities.entry_intervalid = entryintervals.id
                JOIN quanames ON
                     quanames.id = quantities.nameid
                JOIN quanamegroups ON
                     quanamegroups.id = quanames.groupid
              WHERE  entryintervals.id = ?
                AND  quanamegroups.name = ?
                AND  quanames.name = ?
              """, (factor, offset, entry_intervalid, quagroup, qua))
    value = cur.fetchone()
    if value is not None:
        value, = value
    return value


def _get_quantities(cur, entry_intervalid):
    cur.execute("""SELECT quanames.groupid,
                        quanames.name,
                        quantities.value
                 FROM quanames
                 LEFT OUTER JOIN quantities ON
                                 quantities.nameid = quanames.id
                 WHERE quantities.entry_intervalid = ?""", (entry_intervalid,))
    return cur.fetchall()


def _get_intervals(cur, entryid):
    """
    Iter over the interval of the `entryid`.

    :Parameters:
      cur : sqlite3.Cursor
      entryid : str
        id from entries table
    :ReturnType: list
    :Return: [(id<int>, index<int>, start<int>, end<int>)]
    """
    cur.execute('SELECT id, position, start, end FROM entryintervals '
                'WHERE entryid=?', (entryid,))
    return cur.fetchall()


def _get_intervalid_by_entryid(cur, entryid):
    """
    Iter over the interval of the `entryid`.

    :Parameters:
      cur : sqlite3.Cursor
      entryid : str
        id from entries table
    :ReturnType: list
    :Return: [(id<int>, index<int>, start<int>, end<int>)]
    """
    cur.execute('SELECT id FROM entryintervals WHERE entryid=?', (entryid,))
    return cur.fetchall()


def _get_filenames(cur):
    """
    :Parameters:
      cur : sqlite3.Cursor
    :ReturnType: list
    :Return: [(filename<str>,)]
    """
    cur.execute('SELECT name FROM files')
    return cur.fetchall()


def _get_measdate(cur):
    """
    :Parameters:
      cur : sqlite3.Cursor
    :ReturnType: list
    :Return: [(basename<str>,)]
    """
    cur.execute('SELECT basename from measurements order by basename')
    return cur.fetchall()


def _get_common_intervalids(cur, src_entryid, dst_entryid):
    cur.execute('''
    SELECT src_ei.id, dst_ei.id
      FROM entryintervals src_ei, entryintervals dst_ei
     WHERE src_ei.entryid = :src_entryid
       AND dst_ei.entryid = :dst_entryid
       AND src_ei.start = dst_ei.start
       AND src_ei.end = dst_ei.end
       AND src_ei.position = dst_ei.position
    ''', dict(src_entryid=src_entryid, dst_entryid=dst_entryid))
    intervalids = cur.fetchall()
    return intervalids


def _get_labelids_by_intervalid(cur, intervalid):
    labelids = [idx for idx, in cur.execute(
        'SELECT labelid FROM interval2label WHERE entry_intervalid = :intervalid',
        dict(intervalid=intervalid))]
    return labelids


def _get_comment_by_intervalid(cur, intervalid):
    cur.execute(
        'SELECT comment FROM intervalcomments WHERE entry_intervalid = :intervalid',
        dict(intervalid=intervalid))
    comment = cur.fetchone()
    if comment is not None:
        comment, = comment
    return comment


def _get_quantity_by_intervalid(cur, intervalid):
    cur.execute(
        'SELECT nameid, value FROM quantities WHERE entry_intervalid = :intervalid',
        dict(intervalid=intervalid))
    quantities = dict(cur.fetchall())
    return quantities


def _group_report_intervals(cur, report, entryid):
    """
    Group the intervals of the report into remained, removed and added.

    :Parameters:
      cur : sqlite3.Cursor
      report : Report
      entryid : str
        id from entries table
    :ReturnType: tuple
    :Return:
      remained, added, removed
      ([(interval_id<int>, report_index<t>)],
       [(report_index<>, start<int>, end<int>)],
       [(batch_index<int>)])
    """
    remained = []
    removed = []
    added = []

    iter_intervalids = iter(_get_intervals(cur, entryid))
    iter_intervalindices = enumerate(report.intervallist)

    for report_index, (report_start, report_end) in iter_intervalindices:
        try:
            entry_intervalid, \
            batch_index, \
            batch_start, \
            batch_end = iter_intervalids.next()
        except StopIteration:
            added.append((report_index, report_start, report_end))
        else:
            while report_start != batch_start or report_end != batch_end:
                removed.append(entry_intervalid)
                try:
                    entry_intervalid, \
                    batch_index, \
                    batch_start, \
                    batch_end = iter_intervalids.next()
                except StopIteration:
                    break
            remained.append((entry_intervalid, report_index))
    for entryinterval, batch_index, start, end in iter_intervalids:
        removed.append(entryinterval)

    return remained, added, removed


def _add_entrytag(cur, entryid, tag):
    """
    Store `tag` in entry2tag table with `entryid`.

    :Parameters:
      cur : sqlite3.Cursor
      entryid : str
        id from entries table
      tag : str
        name from tags table
    """
    tagid = _get_tagid(cur, tag)
    try:
        cur.execute('INSERT INTO entry2tag(entryid, tagid) VALUES(?, ?)',
                    (entryid, tagid))
    except sqlite3.IntegrityError:
        pass
    return


def _add_entrytags(cur, entryid, tags):
    """
    Store `tags` in entry2tag table with `entryid`.

    :Parameters:
      cur : sqlite3.Cursor
      entryid : str
        id from entries table
      tag : list
        [name_from_tags_table<str>]
    """
    for tag in tags:
        _add_entrytag(cur, entryid, tag)
    return


def _add_interval(cur, entryid, index, start, end, end_is_last, start_time,
                  end_time):
    """
    Store `interval` in intervals table.

    :Parameters:
      cur : sqlite3.Cursor
      entryid : str
        id from entries table
      index : int
      start : int
      end : int
      end_is_last : bool
      start_time : float
      end_time : float
    """
    try:
        cur.execute("""
     INSERT INTO entryintervals
     (entryid, position, start,   end,      end_is_last,       start_time,        end_time)
     VALUES
     (?,       ?,        ?,       ?,        ?,                 ?,                 ?)""",
                    (entryid, index, int(start), int(end), bool(end_is_last), float(start_time), float(end_time)))
    except sqlite3.IntegrityError:
        cur.execute('SELECT id FROM intervals WHERE entryid=? AND position=?',
                    (entryid, index))
        intervalid, = cur.fetchone()
    else:
        intervalid = cur.lastrowid
    return intervalid


def _add_intervalcomment(cur, entry_intervalid, comment):
    """
    Add `comment` into intervalcomments table with `entry_intervalid`.

    :Parameters:
      cur : sqlite3.Cursor
      entry_intervalid : int
        id from entryintervals table
      comment : str
        comment from intervalcomments table
    """
    if not comment:
        cur.execute('SELECT comment FROM intervalcomments WHERE entry_intervalid=?',
                    (entry_intervalid,))
        comm = cur.fetchone()
        if comm:
            cur.execute('UPDATE intervalcomments SET comment=NULL '
                        'WHERE entry_intervalid=?', (entry_intervalid,))
        return
    try:
        cur.execute('INSERT INTO intervalcomments'
                    '(entry_intervalid, comment) VALUES(?, ?);',
                    (entry_intervalid, comment))
    except sqlite3.IntegrityError:
        cur.execute('UPDATE intervalcomments SET comment=? '
                    'WHERE entry_intervalid=?', (comment, entry_intervalid))
    return


def _add_entry2domain(cur, entryid, domainid):
    """
    Add `domainid` with `entryid` to entry2domain table.

    :Parameters:
      cur : sqlite3.Cursor
      entryid : str
        id from entries table
      domainid : int
    """
    cur.execute('INSERT INTO entry2domain(entryid, fileid) VALUES(?, ?)',
                (entryid, domainid))
    return cur.lastrowid


def _add_interval2label(cur, entry_intervalid, labelid):
    """
    Add `labelid` with `entry_intervalid` to interval2label table.

    :Parameters:
      cur : sqlite3.Cursor
      entry_intervalid : int
        id from entryintervals table
      labelid : int
        id from labels table
    """
    try:
        cur.execute('INSERT INTO interval2label(labelid, entry_intervalid)'
                    'VALUES(?, ?);', (labelid, entry_intervalid))
    except sqlite3.IntegrityError:
        pass
    return


def _add_entry2file(cur, entryid, fileid):
    """
    Add `fileid` with `entryid` to entry2file table.

    :Parameters:
      cur : sqlite3.Cursor
      entryid : str
        id from entries table
      fileid : int
        id from files table
    """
    try:
        cur.execute('INSERT INTO entry2file(entryid, fileid) VALUES(?, ?)',
                    (entryid, fileid))
    except sqlite3.IntegrityError:
        pass
    return


def _add_quantities(cur, entry_intervalid, nameids, quantities):
    """
    :Parameters:
      entry_intervalid : int
      nameids : dict
        {group_name<str>: {value_name<str>: nameid<int>}}
      quantities : dict
        {group_name<str>: {value_name<str>: value<float>}}
    """
    for nameid, value in _get_quantities_nameids(nameids, quantities).iteritems():
        _add_quantity(cur, entry_intervalid, nameid, value)
    return


def _get_quantities_nameids(nameids, quantities):
    quantities_nameids = {}
    for group_name, values in quantities.iteritems():
        for value_name, value in values.iteritems():
            nameid = nameids[group_name][value_name]
            quantities_nameids[nameid] = value
    return quantities_nameids


def _add_quantity(cur, entry_intervalid, nameid, value):
    cur.execute("""INSERT INTO quantities(entry_intervalid, nameid, value)
                 VALUES(?, ?, ?)""", (entry_intervalid, nameid, value))
    return


def _build_label2labelid(cur, groupid):
    """
    Get the labels with their id of `groupid` from labels table.

    :Parameters:
      cur : sqlite3.Cursor
      groupid : int
        id from labelgroups table
    :ReturnType: dict
    :Return: {label_name<str>: labelid<int>}
    """
    cur.execute('SELECT name, id FROM labels WHERE groupid=?', (groupid,))
    label2labelid = cur.fetchall()
    return dict(label2labelid)


def _build_labelids(cur, votegroups):
    """
    Get the labels with their id of `votegroups` from labels table.

    :Parameters:
      cur : sqlite3.Cursor
      votegroups : dict
        [votegroup<str>: [vote<str>]]
    :ReturnType: dict
    :Return: {votegroup<str>: {label_name<str>: labelid<int>}}
    """
    labelids = {}
    for votegroup in votegroups:
        groupid = _get_labelgroupid(cur, votegroup)
        labelids[votegroup] = _build_label2labelid(cur, groupid)
    return labelids


def _build_nameids(cur, namegroups):
    """
    :Parameters:
      cur : sqlite3.Cursor
      namegroups : dict
        [group_name<str>: [value_name<str>]]
    :ReturnType: dict
    :Return: {group_name<str>: {value_name<str>: nameid<int>}}
    """
    nameids = {}
    for groupname in namegroups:
        groupid = _get_quagroupid(cur, groupname)
        nameids[groupname] = _build_name2nameid(cur, groupid)
    return nameids


def _build_name2nameid(cur, groupid):
    """
    :Parameters:
      cur : sqlite3.Cursor
      groupid : int
    :ReturnType: dict
    :Return: {value_name<str>: nameid<int>}
    """
    cur.execute('SELECT name, id FROM quanames WHERE groupid=?', (groupid,))
    label2labelid = cur.fetchall()
    return dict(label2labelid)


def _get_votegroups_labelids(labelids, votegroups):
    """
    Get the labelids of the votes of `votegroup`.

    :Parameters:
      cur : sqlite3.Cursor
      labelids : dict
        {votegroup<str>: {vote<str>: labelid<int>}}
      votegroups : dict
        {group<str>: [vote<str>]}
    :ReturnType: set
    :Return: {labelid<int>}
    """
    votegroup_labelids = set()
    for votegroup, votes in votegroups.iteritems():
        for vote in votes:
            labelid = labelids[votegroup][vote]
            votegroup_labelids.add(labelid)
    return votegroup_labelids


def _reg_interval(cur, labelids, votegroups, entryid, index, start, end,
                  end_is_last, start_time, end_time, comment):
    """
    Register interval into batch.

    :Parameters:
      cur : sqlite3.Cursor
      labelids : dict
        {votegroup<str>: {vote<str>: labelid<int>}}
      votegroups : dict
        {group<str>: [vote<str>]}
      entryid : str
      index ; int
      start : int
      end : int
      end_is_last : bool
      start_time : float
      end_time : float
      comment : str
    """
    entry_intervalid = _add_interval(cur, entryid, index, start, end, end_is_last,
                                     start_time, end_time)

    for labelid in _get_votegroups_labelids(labelids, votegroups):
        _add_interval2label(cur, entry_intervalid, labelid)

    # store interval comment
    _add_intervalcomment(cur, entry_intervalid, comment)
    return entry_intervalid


def _update_interval(cur,
                     labelids,
                     votegroups,
                     entryid,
                     entry_intervalid,
                     entry_index,
                     comment):
    """
    Update interval in batch.

    :Parameters:
      cur : sqlite3.Cursor
      labelids : dict
        {votegroup<str>: {vote<str>: labelid<int>}}
      votegroups : dict
        {group<str>: [vote<str>]}
      entryid : str
      entry_intervalid : int
      entry_index : int
      comment : str
    """
    stored_labelids = _get_labelids(cur, entry_intervalid)
    entry_labelids = _get_votegroups_labelids(labelids, votegroups)

    _update_intervalindex(cur, entry_intervalid, entry_index)

    for labelid in stored_labelids.difference(entry_labelids):
        _rm_interval2label(cur, entry_intervalid, labelid)

    for labelid in entry_labelids.difference(stored_labelids):
        _add_interval2label(cur, entry_intervalid, labelid)

    _add_intervalcomment(cur, entry_intervalid, comment)
    return


def _update_quantity(cur, nameids, quantities, entryid, entry_intervalid,
                     entry_index):
    """
    :Parameters:
      nameids : dict
        {groupname<str>: {valuename<str>: nameid<id>}}
      quantities : dict
        {groupname<str>: {valuename<str>: value<float>}}
      entryid : str
      entry_intervalid : int
      entry_index : int
    """
    stored_nameids = _get_quanameids(cur, entry_intervalid)
    entry_nameids = _get_quantities_nameids(nameids, quantities)

    stored_nameid_set = set(stored_nameids)
    entry_nameid_set = set(entry_nameids)

    for nameid in stored_nameid_set.difference(entry_nameid_set):
        _rm_quantities(cur, entry_intervalid, nameid)

    for nameid in entry_nameid_set.difference(stored_nameid_set):
        _add_quantity(cur, entry_intervalid, nameid, entry_nameids[nameid])

    for nameid in entry_nameid_set.intersection(stored_nameid_set):
        _update_quantity_value(cur, entry_intervalid, nameid, entry_nameids[nameid])
    return


def _update_comment(cur, entryid, comment):
    """
    :Parameters:
      cur : sqlite3.Cursor
      entryid : str
      comment : str
    """
    cur.execute('UPDATE entries SET comment=? WHERE id=?', (comment, entryid))
    return


def _update_measurement(cur, measpath):
    """
    Update stored measurement path with the proper local measurement path.

    :Parameters:
      cur : sqlite3.Cursor
      measpath : str
    """
    missing = set()
    cur.execute('SELECT basename, local FROM measurements WHERE local NOT NULL')
    for basename, local in cur.fetchall():
        if not os.path.exists(local):
            for root, dirs, files in os.walk(measpath):
                if basename in files:
                    name = os.path.join(root, basename)
                    cur.execute('UPDATE measurements SET local=? WHERE basename=?',
                                (name, basename))
                    break
            else:
                missing.add(local)
    return missing


def _update_intervalindex(cur, entry_intervalid, index):
    """
    :Parameters:
      cur : sqlite3.Cursor
      entry_intervalid : int
      index : int
    """
    cur.execute('UPDATE entryintervals SET position=? WHERE id=?',
                (index, entry_intervalid))
    return


def _update_quantity_value(cur, entry_intervalid, nameid, value):
    cur.execute('UPDATE quantities SET value=? '
                'WHERE entry_intervalid=? AND nameid=?',
                (value, entry_intervalid, nameid))
    return


# intervalcomment
def _rm_intervalcomment(cur, entry_intervalid):
    """
    Remove comment of `entry_intervalid` from intervalcomments table.

    :Parameters:
      cur : sqlite3.Cursor
      entry_intervalid : int
    """
    cur.execute('DELETE FROM intervalcomments WHERE entry_intervalid=?',
                (entry_intervalid,))
    return


# interval
def _rm_entry2interval(cur, entry_intervalid):
    """
    Remove the `entryid` with `intervalid` from entryintervals table.

    :Parameters:
      cur : sqlite3.Cursor
      entry_intervalid : int
    """
    cur.execute('DELETE FROM entryintervals WHERE id=?', (entry_intervalid,))
    return


# interval2label
def _rm_interval2label(cur, entry_intervalid, labelid):
    """
    Remove the `entry_intervalid` with `labelid` from interval2label table.

    :Parameters:
      cur : sqlite3.Cursor
      entry_intervalid : int
      labelid : int
    """
    cur.execute('DELETE FROM interval2label '
                'WHERE entry_intervalid=? AND labelid=?',
                (entry_intervalid, labelid))
    return


# interval
def _rm_interval(cur, entry_intervalid):
    """
    Remove the `entryid` with `intervalid` from entire batch.

    :Parameters:
      cur : sqlite3.Cursor
      entry_intervalid : int
    """
    _rm_entry2interval(cur, entry_intervalid)
    for labelid in _get_labelids(cur, entry_intervalid):
        _rm_interval2label(cur, entry_intervalid, labelid)
    for nameid in _get_quanameids(cur, entry_intervalid):
        _rm_quantities(cur, entry_intervalid, nameid)
    _rm_intervalcomment(cur, entry_intervalid)
    return


def _rm_quantities(cur, entry_intervalid, nameid):
    cur.execute('DELETE FROM quantities WHERE entry_intervalid=? AND nameid=?',
                (entry_intervalid, nameid))
    return


# entry
def _rm_entry(cur, entryid):
    __rm_entry(cur, entryid)
    for entry_intervalid in _get_entry_intervalids(cur, entryid):
        _rm_interval(cur, entry_intervalid)
    for tagid in _get_tagids(cur, entryid):
        _rm_entry2tag(cur, entryid, tagid)
    for domainid in _get_domainids(cur, entryid):
        _rm_entry2domain(cur, entryid, domainid)
    for fileid in _get_fileids(cur, entryid):
        _rm_entry2file(cur, entryid, fileid)
    return


def __rm_entry(cur, entryid):
    cur.execute('DELETE FROM entries WHERE id=?', (entryid,))
    return


def _get_entry_intervalids(cur, entryid):
    cur.execute('SELECT id FROM entryintervals WHERE entryid=?', (entryid,))
    return set(id_ for id_, in cur.fetchall())


def _get_tagids(cur, entryid):
    cur.execute('SELECT tagid FROM entry2tag WHERE entryid=?', (entryid,))
    return set(id_ for id_, in cur.fetchall())


def _rm_entry2tag(cur, entryid, tagid):
    cur.execute('DELETE FROM entry2tag WHERE entryid=? AND tagid=?',
                (entryid, tagid))
    return


def _get_domainids(cur, entryid):
    cur.execute('SELECT fileid FROM entry2domain WHERE entryid=?', (entryid,))
    return set(id_ for id_, in cur.fetchall())


def _rm_entry2domain(cur, entryid, domainid):
    cur.execute('DELETE FROM entry2domain WHERE entryid=? AND fileid=?',
                (entryid, domainid))
    return


def _get_fileids(cur, entryid):
    cur.execute('SELECT fileid FROM entry2file WHERE entryid=?', (entryid,))
    return set(id_ for id_, in cur.fetchall())


def _rm_entry2file(cur, entryid, fileid):
    cur.execute('DELETE FROM entry2file WHERE entryid=? AND fileid=?',
                (entryid, fileid))
    return


# start
def _rm_start(cur, startid):
    __rm_start(cur, startid)
    for entryid in _get_entryid_4_startid(cur, startid):
        _rm_entry(cur, entryid)
    return


def __rm_start(cur, startid):
    cur.execute('DELETE FROM starts WHERE id=?', (startid,))
    return


def _get_entryid_4_startid(cur, startid):
    cur.execute('SELECT id FROM entries WHERE startid=?', (startid,))
    return set(ei_id for ei_id, in cur.fetchall())


# measurement
def _rm_measurement(cur, measurementid):
    __rm_measurement(cur, measurementid)
    for entryid in _get_entryid_4_measurementid(cur, measurementid):
        _rm_entry(cur, entryid)
    return


def __rm_measurement(cur, measurementid):
    cur.execute('DELETE FROM measurements WHERE id=?', (measurementid,))
    return


def _get_entryid_4_measurementid(cur, measurementid):
    cur.execute('SELECT id FROM entries WHERE measurementid=?', (measurementid,))
    return set(ei_id for ei_id, in cur.fetchall())


def _get_measurementid_4_basename(cur, basename):
    cur.execute('SELECT id FROM measurements WHERE basename=?', (basename,))
    res = cur.fetchone()
    if res is None:
        raise ValueError("'%s' basename is not in batch.")
    return res[0]


# module
def _rm_module(cur, moduleid):
    __rm_module(cur, moduleid)
    for entryid in _get_entryid_4_moduleid(cur, moduleid):
        _rm_entry(cur, entryid)
    return


def __rm_module(cur, moduleid):
    cur.execute('DELETE FROM modules WHERE id=?', (moduleid,))
    return


def _get_entryid_4_moduleid(cur, moduleid):
    cur.execute('SELECT id FROM entries WHERE moduleid=?', (moduleid,))
    return set(ei_id for ei_id, in cur.fetchall())


def _get_moduleid_4_classname(cur, classname):
    cur.execute('SELECT id FROM modules WHERE class=?', (classname,))
    return set(ei_id for ei_id, in cur.fetchall())


# result
def _rm_result(cur, resultid):
    __rm_result(cur, resultid)
    for entryid in _get_entryid_4_resultid(cur, resultid):
        _rm_entry(cur, entryid)
    return


def __rm_result(cur, resultid):
    cur.execute('DELETE FROM results WHERE id=?', (resultid,))
    return


def _get_entryid_4_resultid(cur, resultid):
    cur.execute('SELECT id FROM entries WHERE resultid=?', (resultid,))
    return set(ei_id for ei_id, in cur.fetchall())


# types
def _rm_type(cur, typeid):
    __rm_type(cur, typeid)
    for entryid in _get_entryid_4_typeid(cur, typeid):
        _rm_entry(cur, entryid)
    return


def __rm_type(cur, typeid):
    cur.execute('DELETE FROM types WHERE id=?', (typeid,))
    return


def _get_entryid_4_typeid(cur, typeid):
    cur.execute('SELECT id FROM entries WHERE typeid=?', (typeid,))
    return set(ei_id for ei_id, in cur.fetchall())


# files
def __rm_file(cur, fileid, repdir=None):
    if repdir is not None:
        cur.execute('SELECT name FROM files WHERE id=?', (fileid,))
        res = cur.fetchone()
        if res is not None:
            filename = os.path.join(repdir, res[0])
            if os.path.exists(filename):
                os.remove(filename)  # improvement possibility: delete only during commit
    cur.execute('DELETE FROM files WHERE id=?', (fileid,))
    return


def _is_measurement_local(cur, measurement):
    """
    :Parameters:
      cur : sqlite3.Cursor
      measurement : str
    :ReturnType: bool
    """
    cur.execute('SELECT id FROM measurements WHERE local=?', (measurement,))
    fetch = cur.fetchone()
    return fetch is not None


def _is_labelgroup_exclusive(cur, groupname):
    cur.execute('SELECT exclusive FROM labelgroups WHERE name = ?', (groupname,))
    exclusive, = cur.fetchone()
    return exclusive


def _get_init_scrpit_name():
    """
    :ReturnType: str
    :Return: name of the init sql script
    """
    return os.path.join(os.path.dirname(__file__), 'batchsqlite', 'init.sql')


version_pattern = re.compile(r'PRAGMA\s+user_version\s*=\s*(\d+)\s*;')


def _get_user_version(init):
    """
    :Parameters:
      init : str
        name of the sql init script
    :ReturnType: int
    :Return: user_verion of the sql schema
    """
    f = open(init)
    for line in f:
        match = version_pattern.search(line)
        if match:
            version = match.group(1)
            version = int(version)
            break
    else:
        raise ValueError('%s does not contain user_version pragma' % init)
    f.close()
    return version


def _get_db_user_version(cur):
    """
    :Parameters:
      cur : sqlite3.Cursor
    :ReturnType: int
    :Return: user_verion of the database
    """
    cur.execute('PRAGMA user_version;')
    version, = cur.fetchone()
    return version


def _check_version(parser_version, db_version):
    """
    :Parameters:
      parser_version : int
      db_version : int
    :Raises:
      ValueError: in case of user_version conflict
    """
    if parser_version != db_version:
        raise ValueError('Invalid user_version: parser (%d) does not handle %d. '
                         'Please use --batch-update to bring database up-to-date.'
                         % (parser_version, db_version))
    return


def update(dbname, dirname):
    con = sqlite3.connect(dbname)
    cur = con.cursor()

    init = _get_init_scrpit_name()
    parser_version = _get_user_version(init)
    db_version = _get_db_user_version(cur)
    assert db_version in updates, 'No update for %d' % db_version

    for version, updater in updates.iteritems():
        if db_version != version: continue

        db_version = updater(cur, dirname)
        con.commit()
    return db_version


def add_meas_start(cur, dirname):
    version = 211
    cur.execute('ALTER TABLE measurements ADD COLUMN start DATETIME')
    cur.execute('SELECT basename, IFNULL(origin, local) FROM measurements')
    for basename, fullname in cur.fetchall():
        start = get_meas_startdate(fullname).strftime(Batch.TIME_FORMAT)
        cur.execute('UPDATE measurements SET start = ? WHERE basename = ?',
                    (start, basename))
    _update_user_version(cur, version)
    return version


def _update_user_version(cur, version):
    cur.execute('PRAGMA user_version = %d' % version)
    return


def add_end_is_last(cur, dirname):
    version = 220
    cur.execute('ALTER TABLE entryintervals ADD COLUMN end_is_last BOOLEAN')
    cur.execute('''
    SELECT ei.entryid, ei.position, ei.end, files.name FROM entries
      JOIN entryintervals ei ON ei.entryid = entries.id
      JOIN entry2domain ON entry2domain.entryid = entries.id
      JOIN files ON files.id = entry2domain.fileid
  ''')
    for entryid, position, end, domain_name in cur.fetchall():
        domain = numpy.load(os.path.join(dirname, domain_name))
        cur.execute('''
      UPDATE entryintervals
         SET end_is_last = ?
      WHERE entryid = ? AND position = ?
    ''', (end == domain.size, entryid, position))
    _update_user_version(cur, version)
    return version


def add_last_entries(cur, dirname):
    version = 230
    cur.execute('''
              CREATE TABLE last_entries AS
              SELECT id FROM (
              SELECT en.*, mo.class mo_class, mo.param mo_param, st.time st_time
                FROM entries en
                JOIN modules mo ON en.moduleid = mo.id
                JOIN measurements me ON en.measurementid = me.id
                JOIN starts st ON en.startid = st.id
            ) q1 JOIN (
              SELECT DISTINCT en.id en_id, mo.class mo_class, mo.param mo_param,
                              me.id me_id, MAX(st.time) last_time
              FROM entries en
              JOIN modules mo        ON en.moduleid = mo.id
              JOIN measurements me   ON en.measurementid = me.id
              JOIN starts st         ON en.startid = st.id
              GROUP BY mo.class, mo.param, me.id
            ) q2 ON q1.measurementid = q2.me_id
                AND q1.mo_class = q2.mo_class
                AND q1.mo_param = q2.mo_param
            WHERE q1.st_time = q2.last_time
              ''')

    cur.execute('''
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
                  END
                  ''')

    cur.execute('''
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
                WHERE id = (SELECT enid FROM (
                      SELECT en.id enid, mo.class mo_class,
                             mo.param mo_param, st.time st_time,
                             me.id me_id, en.title
                        FROM last_entries laen
                        JOIN entries en ON laen.id = en.id
                        JOIN modules mo ON en.moduleid = mo.id
                        JOIN measurements me ON en.measurementid = me.id
                        JOIN starts st ON en.startid = st.id
                    ) q1
                      JOIN (
                      SELECT DISTINCT en.id en_id, en.title,
                                      mo.class mo_class, mo.param mo_param,
                                      me.id me_id, MAX(st.time) last_time
                      FROM last_entries laen
                      JOIN entries en ON laen.id = en.id
                      JOIN modules mo        ON en.moduleid = mo.id
                      JOIN measurements me   ON en.measurementid = me.id
                      JOIN starts st         ON en.startid = st.id
                      GROUP BY mo.class, mo.param, me.id
                    ) q2 ON q1.me_id = q2.me_id
                        AND q1.mo_class = q2.mo_class
                        AND q1.mo_param = q2.mo_param
                        AND q1.title = q2.title
                    JOIN (
                      SELECT mo.class mo_class, mo.param mo_param
                        FROM entries en
                        JOIN modules mo ON mo.id = en.moduleid
                       WHERE en.id = new.id
                    ) q3
                    ON  q2.mo_class = q3.mo_class
                    AND q2.mo_param = q3.mo_param
                    AND q2.title = new.title
                    AND q2.me_id = new.measurementid

                    WHERE q1.st_time = q2.last_time);
              END
              ''')

    _update_user_version(cur, version)
    return version


updates = OrderedDict([
    (210, add_meas_start),
    (211, add_end_is_last),
    (220, add_last_entries),
])


class Filter:
    JOIN = ''

    def get_join(self):
        row = self.JOIN % self.columns
        return row

    WHERE = ''
    _WHERE_ROW = '%s = ?'

    def get_where(self):
        where = self.WHERE % self.columns
        row = self._WHERE_ROW % where
        return row

    _ORDER_ROW = 'ORDER BY %s %s'

    def get_order(self, asc):
        asc = 'ASC' if asc else 'DESC'
        order = self.WHERE % self.columns
        row = self._ORDER_ROW % (order, asc)
        return row

    QUERY = ''

    def get_query(self):
        row = self.QUERY % self.columns
        return row

    OCCASION = ''

    def get_occasion(self):
        row = self.OCCASION % self.columns
        return row


class TableFilter(Filter):
    def __init__(self, entryid, table, value):
        self.columns = dict(entryid=entryid, table=table, value=value)
        return

    JOIN = 'JOIN %(table)s ON %(table)s.id = entries.%(entryid)s'
    WHERE = '%(table)s.%(value)s'
    QUERY = """SELECT %(table)s.%(value)s FROM %(table)s
               JOIN entries ON entries.%(entryid)s = %(table)s.id
             WHERE entries.id = ?"""
    OCCASION = 'SELECT %(value)s FROM %(table)s'


class TableWithNullFilter(TableFilter):
    def __init__(self, entryid, table, value, nullvalue):
        self.columns = dict(entryid=entryid, table=table, value=value,
                            nullvalue=nullvalue)
        return

    WHERE = 'IFNULL(%(table)s.%(value), %(table)s.%(nullvalue)s)'
    QUERY = """SELECT IFNULL(%(table)s.%(value)s, %(table)s.%(nullvalue)s)
             FROM %(table)s JOIN  entries ON %(table)s.id = entries.%(entryid)s
             WHERE entries.id = ?"""
    OCCASION = 'SELECT IFNULL(%(value)s, %(nullvalue)s) FROM %(table)s'


class EntryFilter(Filter):
    def __init__(self, entryid):
        self.columns = dict(entryid=entryid)
        return

    WHERE = 'entries.%(entryid)s'
    QUERY = "SELECT %(entryid)s FROM entries WHERE id = ?"
    OCCASION = 'SELECT %(entryid)s FROM entries'


class CrossTableFilter(TableFilter):
    def __init__(self, crosstable, crossid, table, value):
        self.columns = dict(crosstable=crosstable, crossid=crossid, table=table,
                            value=value)
        return

    JOIN = 'JOIN %(crosstable)s ON %(crosstable)s.entryid = entries.id ' \
           'JOIN %(table)s ON %(table)s.id = %(crosstable)s.%(crossid)s'
    QUERY = """SELECT %(table)s.%(value)s FROM %(table)s
               JOIN %(crosstable)s ON %(crosstable)s.%(crossid)s = %(table).id
             WHERE %(crosstable)s.entryid = ?"""
    OCCASION = 'SELECT %(value)s FROM %(table)s'


class CountFilter(Filter):
    def __init__(self, table):
        self.columns = dict(table=table)
        return

    QUERY = 'SELECT COUNT(*) FROM %(table)s WHERE %(table)s.entryid = ?'


class Joins(set):
    def add(self, filter_):
        row = filter_.get_join()
        set.add(self, row)
        return


class Wheres(list):
    def add(self, filter_):
        row = filter_.get_where()
        self.append(row)
        return

    SEP = ' AND '

    def __call__(self):
        row = self.SEP.join(self)
        return row


class Query:
    def __init__(self):
        self.wheres = Wheres()
        self.joins = Joins()
        self.order = ''
        return

    SEP = ' '

    def __call__(self):
        query = ['SELECT entries.id FROM entries']
        query.extend(self.joins)
        query.append('WHERE')
        query.append(self.wheres())
        query.append(self.order)
        row = self.SEP.join(query)
        return row

    def set_order(self, filter_, asc):
        self.order = filter_.get_order(asc)
        return


filters = {
    'start': TableFilter('startid', 'starts', 'time'),
    'measurement': TableFilter('measurementid', 'measurements', 'basename'),
    'meas_start': TableFilter('measurementid', 'measurements', 'start'),
    'fullmeas': TableWithNullFilter('measurementid', 'measurements', 'local',
                                    'origin'),
    'type': TableFilter('typeid', 'types', 'name'),
    'result': TableFilter('resultid', 'results', 'name'),
    'class_name': TableFilter('moduleid', 'modules', 'class'),
    'param': TableFilter('moduleid', 'modules', 'param'),
    'tag': CrossTableFilter('entry2tag', 'tagid', 'tags', 'name'),
    'title': EntryFilter('title'),
    'intervals': CountFilter('entryintervals'),
}


def _get_entry_attr(cur, entryid, name):
    assert name in filters, 'invalid attribute name: %s' % name
    filter_ = filters[name]
    query = filter_.get_query()
    cur.execute(query, (entryid,))
    attr = cur.fetchone()
    assert attr is not None, 'invalid entryid %s' % entryid
    attr, = attr
    return attr


def _filter(cur, order, asc, **kwargs):
    query = Query()
    values = []
    for key, value in kwargs.iteritems():
        assert key in filters, 'invalid filter: %s' % key
        filter_ = filters[key]
        assert not isinstance(filter_, CountFilter), 'invalid filter type: %s' % key
        query.joins.add(filter_)
        query.wheres.add(filter_)
        values.append(value)
    if order:
        assert order in filters, 'invalid order'
        filter_ = filters[order]
        assert not isinstance(filter_, CountFilter), 'invalid order type: %s' % order
        query.joins.add(filter_)
        query.set_order(filter_, asc)
    query = query()
    cur.execute(query, values)
    entryids = [entryid for entryid, in cur.fetchall()]
    return entryids


def _get_occasions(cur, name):
    assert name in filters, 'invalid filter %s' % name
    filter_ = filters[name]
    assert not isinstance(filter_, CountFilter), \
        'invalid filtertype: %s' % filter_.__class__.__name__
    query = filter_.get_occasion()
    cur.execute(query)
    occasions = [o for o, in cur.fetchall()]
    return occasions


class Batch:
    TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, dbname, dirname, labels, tags, results, quanames):
        """
        :Parameters:
          dbname : str
          dirname : str
          labels : dict
            {group_name<str>: (exclusive<bool>, [label_names<str>])}
          tags : dict
            {group_name<str>: [tag_names<str>]}
          results : list
            [tag_name<str>]
          quanames : dict
            {group_name<str>: {value_name}}
        :Raises:
          ValueError: in case of user_version conflict
        """
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        exist = os.path.exists(dbname)
        self.con = sqlite3.connect(dbname)
        self.dirname = os.path.abspath(dirname)
        self.dbname = dbname
        self.startid = None
        self.measurementid = None

        cur = self.con.cursor()
        init = _get_init_scrpit_name()
        if not exist:
            _init_db(cur, init)

        parser_version = _get_user_version(init)
        db_version = _get_db_user_version(cur)
        try:
            _check_version(parser_version, db_version)
        except ValueError, error:
            cur.close()
            self.con.close()
            raise error
        else:
            _add_words(cur, labels, tags, results, self.types, quanames)
            # register custom functions
            self.con.create_function('meastag', 2, FileNameParser.get_meastag)
            cur.close()
            self.con.commit()
        return

    @classmethod
    def from_batchxml(cls, batchxml, delete, rename, vote2label, labels,
                      dbname=None):
        """
        :Parameters:
          batchxml : `measproc.Batch.cBatch`
          dbname : str
        :ReturnType: `Batch`
        """
        if dbname is None:
            dbname, ext = os.path.splitext(batchxml.XmlFile)
            dbname += '.db'

        basedir = os.path.dirname(batchxml.XmlFile)
        names = batchxml.getReportAttrs('ReportPath')
        if not names:
            dirname = os.curdir
        else:
            dirname = os.path.join(basedir, names[0])
            dirname = os.path.abspath(dirname)
            dirname = os.path.dirname(dirname)
        tags = {}
        quanames = {}
        results = set(batchxml.getReportAttrs('Result'))
        self = cls(dbname, dirname, labels, tags, results, quanames)

        cur = self.con.cursor()
        start_pack = batchxml.pack_itself(batchxml.Reports, 'StartTime')
        for start, start_entries in start_pack.iteritems():
            start_time = time.strptime(start, batchxml.TIME_FORMAT)
            start = time.strftime(cls.TIME_FORMAT, start_time)
            self.set_start(start)

            meas_pack = batchxml.pack_itself(start_entries, 'MeasPath')
            for meas, meas_entries in meas_pack.iteritems():
                local = not meas.startswith('//') and not meas.startswith(r'\\')
                self.set_measurement(meas, local)

                class_name_pack = batchxml.pack_itself(meas_entries, 'SearchClass')
                for class_name, class_name_entries in class_name_pack.iteritems():
                    param_pack = batchxml.pack_itself(class_name_entries, 'SearchSign')
                    for param, param_entries in param_pack.iteritems():
                        version_pack = batchxml.pack_itself(param_entries, 'ModuleHash')
                        for version, version_entries in version_pack.iteritems():
                            self.set_module(class_name, param, version)
                            for entry in version_entries:
                                _, _, _, name, _, _, title, result, type, _ = entry
                                if type == 'measproc.cFileReport':
                                    report = batchxml.wakeEntry(entry)
                                    report = Report.from_reportxml(report, delete, rename,
                                                                   vote2label, labels)
                                    self.add_entry(report)
                                else:
                                    store = self.types[type]['store']
                                    # copy the file of the entry
                                    oldname = os.path.join(basedir, name)
                                    oldname = os.path.abspath(oldname)
                                    basename = os.path.basename(name)
                                    newname = os.path.join(dirname, basename)
                                    if oldname != newname: shutil.copy(oldname, newname)
                                    entry = iXmlNpy(newname)
                                    # copy the time file of the entry if it has one
                                    if store.__name__ == '_store_npyxml_entry':
                                        newname = entry.getTimeFile()
                                        basename = os.path.basename(newname)
                                        oldname = os.path.dirname(oldname)
                                        oldname = os.path.join(oldname, basename)
                                        if oldname != newname: shutil.copy(oldname, newname)

                                    entryid = self._add_entry(cur, result, type, title, '', ())
                                    store(self, cur, entry, entryid)
        cur.close()
        self.con.commit()
        return self

    @classmethod
    def from_xls(cls, xls_name, dbname, dbdir, labels, tags, results, quanames,
                 start, local, meas_name, t_start, t_dura, col2label, col2qua,
                 converter, verbose=False):
        """
        Create batch from kbtools xls result

        :Parameters:
          xls_name : str
          dbname : str
          dbdir : str
          labels : dict
            {group_name<str>: (exclusive<bool>, [label_names<str>])}
          tags : dict
            {group_name<str>: [tag_names<str>]}
          results : list
            [tag_name<str>]
          quanames : dict
            {group_name<str>: {value_name}}
          start : str
            start timestamp of the report creation
          local : bool
            measurements are local or from the server
          meas_name : str
            measurement column name
          t_start : str
            start time column name
          t_dura : str
            suration column name
          col2label : dict
            {(column_name<str>, loabel_group<str>): {value<int>: label<str>}}
          col2qua : dict
            {column_name<str>: (qua_group<str>, qua<str>, factor<float>)}
          converter : `batchconv.BaseConv`
          verbose : bool, optional
        """
        xls = open_workbook(xls_name)
        logger = logging.getLogger()
        meas_events = {}
        for sheet_name in xls.sheet_names():
            sheet = xls.sheet_by_name(sheet_name)
            # build sheet header
            header = [sheet.cell(0, col).value for col in xrange(sheet.ncols)]
            assert meas_name in header, 'Invalid sheet header %s' % header
            meas_col = header.index(meas_name)
            # read sheet
            for row in xrange(1, sheet.nrows):
                meas = sheet.cell(row, meas_col).value
                sheet_events = meas_events.setdefault(meas, {})
                events = sheet_events.setdefault(sheet_name, [])
                event = {}
                for col in xrange(sheet.ncols):
                    event[header[col]] = sheet.cell(row, col).value
                events.append(event)

        self = cls(dbname, dbdir, labels, tags, results, quanames)
        self.set_start(start)

        votes = [name for _, name in col2label]
        votes = self.get_labelgroups(*votes)

        quas = set(name for name, _, _ in col2qua.itervalues())
        quas = self.get_quanamegroups(*quas)

        reports = {}
        for measbase, sheet_events in meas_events.iteritems():
            names = os.path.abspath(xls_name).split(os.path.sep)
            self.set_module(names[-1], '' if len(names) < 2 else names[-2], '')
            for sheet_name, events in sheet_events.iteritems():
                for event in events:
                    intervals = converter.get_intervals(measbase, event[t_start],
                                                        event[t_dura])
                    if verbose and not intervals:
                        logger.warning('event cannot be converted: "%s",%s,%s \n'
                                       % (measbase, event[t_start], event[t_dura]))
                    for meas, time, start, end in intervals:
                        self.set_measurement(meas, local)
                        if meas not in reports:
                            intervals = cIntervalList(time)
                            report = Report(intervals, sheet_name, votes=votes, names=quas)
                            reports[meas] = report
                        else:
                            report = reports[meas]

                        idx = report.addInterval((start, end))
                        for (colname, labelgroup), rule in col2label.iteritems():
                            # if colname not in event: continue
                            label = event[colname]
                            vote = rule[label] if label in rule else label
                            if vote:
                                report.vote(idx, labelgroup, vote)
                        for colname, (quagroup, qua, factor) in col2qua.iteritems():
                            report.set(idx, quagroup, qua, event[colname] * factor)

        for report in reports.itervalues():
            self.add_entry(report)
        return self

    def clone(self):
        other = Batch(self.dbname, self.dirname, {}, {}, [], {})
        other.startid = self.startid
        other.measurementid = self.measurementid
        return other

    @commit
    def set_start(self, cur, start):
        """
        Add `start` into starts table and set `startid` to its id.

        :Parameters:
          cur : sqlite3.Cursor
          start : str
        """
        self.startid = _add_start(cur, start)
        return

    @commit
    def set_measurement(self, cur, measurement, local):
        """
        Add `name` with local into measurements table and set `measurementid` to its
        id.

        :Parameters:
          measurement : str
          local : bool
        """
        start = get_meas_startdate(measurement).strftime(self.TIME_FORMAT)
        self.measurementid = _add_measurement(cur, measurement, local, start)
        return

    @cursor
    def get_measurement(self, cur):
        return _get_measurement(cur, self.measurementid)

    @commit
    def set_module(self, cur, class_name, param, version):
        """
        Add `class`, `param` with `version` into modules table and set `moduleid` to
        its id.

        :Parameters:
          class_name : str
          param : str
          version : str
        """
        self.moduleid = _add_module(cur, class_name, param, version)
        return

    @commit
    def repl_meas(self, cur, measpath):
        """
        :Parameters:
          measpath : str
        """
        _update_measurement(cur, measpath)
        return

    def _add_entry(self, cur, result, type, title, comment, tags):
        """
        Register entry into batch.

        :Parameters:
          cur : sqlite3.Cursor
          result : str
            name from results table
          type : str
            name from types table
          title : str
          comment : str
          tags : list
            [tags_name<str>]

        :ReturnType: int
        :Return: id of the new entry in entries table.
        """
        resultid = _get_resultid(cur, result)
        typeid = _get_typeid(cur, type)
        entryid = _add_entry(cur,
                             self.startid,
                             self.measurementid,
                             self.moduleid,
                             resultid,
                             typeid,
                             title,
                             comment)
        _add_entrytags(cur, entryid, tags)
        return entryid

    def _add_ndarray(self, cur, array):
        """
        :Parameters:
          cur : sqlite3.Cursor
          array : numpy.ndarray
        :ReturnType: int
        :Return: id of `array` in files table
        """
        name = get_ndarray_hash(array) + '.npy'
        fullname = os.path.join(self.dirname, name)
        if not os.path.exists(fullname):
            numpy.save(fullname, array)
        return _add_file(cur, name)

    def _add_file(self, cur, name):
        """
        :Parameters:
          cur : sqlite3.Cursor
          name : str
        :ReturnType: int
        :Return: id of the `name` in files table
        """
        dirname, basename = os.path.split(name)
        assert dirname == self.dirname, \
            'entry is stored in a wrong directory: %s <> %s' % (dirname, self.dirname)
        return _add_file(cur, basename)

    @cursor
    def get_labelgroup(self, cur, groupname):
        """
        :Parameters:
          groupname : str
        :ReturnType: bool, list
        :Return:
          exclusive
          [lable_name<str>]
        """
        return _get_labelgroup(cur, groupname)

    @cursor
    def get_labelgroups(self, cur, *groupnames):
        """
        :Arguments:
          groupname : str
        :ReturnType: dict
        :Return: {groupname: (exclusive<bool>, [label_name<str>])}
        """
        labelgroups = {}
        for groupname in groupnames:
            labelgroups[groupname] = _get_labelgroup(cur, groupname)
        return labelgroups

    @cursor
    def get_quanamegroup(self, cur, name):
        """
        :Parameters:
          name : str
        :ReturnType: list
        :Return: quanames names of the selected quaname group
        """
        return _get_quanames(cur, name)

    @cursor
    def get_quanamegroups(self, cur, *names):
        """
        :Arguments:
          name : str
        :ReturnType: dict
        :Return: {group_name<str>: [value_name<str>]}
        """
        groups = {}
        for name in names:
            groups[name] = _get_quanames(cur, name)
        return groups

    @cursor
    def get_last_entries(self, cur, classname, param, type='measproc.Report'):
        cur.execute("""SELECT starts.id FROM starts
                     JOIN entries ON entries.startid = starts.id
                     JOIN modules ON modules.id = entries.moduleid
                     JOIN types ON types.id = entries.typeid
                   WHERE modules.class=? AND modules.param=? AND types.name=?
                   ORDER BY starts.time DESC LIMIT 1""",
                    (classname, param, type))
        startid = cur.fetchone()
        if startid is None:
            entryids = []
        else:
            startid, = startid
            cur.execute("""SELECT entries.id FROM entries
                       JOIN modules ON modules.id = entries.moduleid
                       JOIN types ON types.id = entries.typeid
                     WHERE modules.class=? AND modules.param=? AND types.name=?
                       AND entries.startid=?""",
                        (classname, param, type, startid))
            entryids = [entryid for entryid, in cur.fetchall()]
        return entryids

    @cursor
    def get_last_entry_start(self, cur):
        cur.execute("""SELECT starts.time FROM starts
                     JOIN entries ON entries.startid = starts.id
                   ORDER BY starts.time DESC LIMIT 1""")
        start = cur.fetchone()
        assert start is not None, 'batch does not contain entries'
        start, = start
        return start

    def _store_report(self, cur, report, entryid):
        """
        :Parameters:
          cur : sqlite3.Cursor
          report : Report2
          entryid : str
        """
        # store domain
        domain = report.intervallist.Time
        domainid = self._add_ndarray(cur, domain)
        _add_entry2domain(cur, entryid, domainid)

        # find vote labels
        votegroups = report.getVoteGroups()
        labelids = _build_labelids(cur, votegroups)

        names = report.getNames()
        nameids = _build_nameids(cur, names)

        # fill intervals
        for index, (start, end) in report.iterIntervalsWithId():
            votegroup = report.getVotes(index)
            comment = report.getComment(index)
            start_time, end_time = report.getTimeInterval(index)
            entry_intervalid = _reg_interval(cur, labelids, votegroup, entryid, index,
                                             start, end, end == domain.size,
                                             start_time, end_time, comment)

            quantities = report.getQuantities(index)
            _add_quantities(cur, entry_intervalid, nameids, quantities)
        return

    @cursor
    def get_filenames(self, cur):
        """
        :Parameters:
          cur : sqlite3.Cursor
        :ReturnType: list
        :Return: [absfilename<str>]
        """
        return [os.path.join(self.dirname, filename)
                for filename, in _get_filenames(cur)]

    @cursor
    def get_measdate(self, cur):
        """
        :Parameters:
          cur : sqlite3.Cursor
        :ReturnType: list
        :Return: [start_date and end_date<str>]
        """
        try:
            start_date = str(re.compile(r"\d{4}-\d{2}-\d{2}").findall(_get_measdate(cur)[0][0])[0])
            end_date = str(re.compile(r"\d{4}-\d{2}-\d{2}").findall(_get_measdate(cur)[-1][0])[0])
        except:
            start_date = str(re.compile(r"\d{4}-\d{2}-\d{2}").findall(_get_measdate(cur)[1][0])[0])
            end_date = str(re.compile(r"\d{4}-\d{2}-\d{2}").findall(_get_measdate(cur)[-1][0])[0])

        return start_date, end_date

    @commit
    def merge(self, cur, batch):
        """
        :Parameters:
          cur : sqlite3.Cursor
          batch : `Batch`
        """
        # merge database
        self.merge_db(batch)
        # copy files from repdir
        files = [os.path.join(self.dirname, name)
                 for name in os.listdir(self.dirname)]
        for name in batch.get_filenames():
            if name in files:
                continue
            shutil.copy(name, self.dirname)
        return

    @commit
    def merge_db(self, cur, batch):
        """
        :Parameters:
          cur : sqlite3.Cursor
          batch : `Batch`
        """
        mergescript = os.path.join(os.path.dirname(__file__),
                                   'batchsqlite',
                                   'merge.sql')
        _merge_db(cur, mergescript, batch.dbname)
        return

    def dump_db(self, output=None):
        """
        :Parameters:
          output : str
        """
        if output is None:
            output = os.path.extsep.join((os.path.splitext(self.dbname)[0], 'sql'))

        _dump_db(self.con, output)
        return

    @cursor
    def pack_batch(self, cur, output=None, repdir_only=False):
        """
        :Parameters:
          output : str
        """
        if output is None:
            output = os.path.extsep.join((os.path.splitext(self.dbname)[0], 'zip'))

        _pack_batch(cur, self.dbname, self.dirname, output, repdir_only=repdir_only)
        return

    def _store_filelike_entry(self, cur, entry, entryid):
        """
        :Parameters:
          cur : sqlite3.Cursor
          entry : iReport|Report|iStatistic|Workspace|TextEntry|FigEntry
          entryid : str
        """
        fileid = self._add_file(cur, entry.PathToSave)
        entry.save()
        _add_entry2file(cur, entryid, fileid)
        return

    def _store_npyxml_entry(self, cur, entry, entryid):
        """
        :Parameters:
          cur : sqlite3.Cursor
          entry : iReport|Report|iStatistic|Workspace|TextEntry|FigEntry
          entryid : str
        """
        for name in entry.PathToSave, entry.getTimeFile():
            fileid = self._add_file(cur, name)
            _add_entry2file(cur, entryid, fileid)
        entry.save()
        return

    def _wake_report(self, cur, entryid):
        """
        :Parameters:
          cur : sqlite3.Cursor
          entryid : str
        """
        intervallist = self._init_intervallist(cur, entryid)

        # initialize report
        ## get title and comment
        title, comment = _get_title_comment(cur, entryid)
        report = Report(intervallist, title)
        report.setEntryComment(comment)

        labelgroups = set()
        names = set()
        intervals = _get_interval_by_entryid(cur, entryid)
        for entry_intervalid, start, end, comment in intervals:
            intervalindex = report.addInterval((start, end))
            ### select label
            for groupid, label, in _get_labels(cur, entry_intervalid):
                groupname = _get_labelgroupname_by_id(cur, groupid)
                if groupname not in labelgroups:
                    exclusive, labels = _get_labelgroup_by_id(cur, groupid)
                    report.addVoteGroup(groupname, exclusive, labels)
                    labelgroups.add(groupname)
                report.vote(intervalindex, groupname, label)
            if comment:
                report.setComment(intervalindex, comment)

            ### select quantity
            for groupid, valuename, value in _get_quantities(cur, entry_intervalid):
                groupname = _get_quagroupname_by_id(cur, groupid)
                if groupname not in names:
                    names.add(groupname)
                    valuenames = _get_quanamegroup_by_id(cur, groupid)
                    report.setNames(groupname, valuenames)
                report.set(intervalindex, groupname, valuename, value)
        return report

    def _init_intervallist(self, cur, entryid):
        """
        :Parameters:
          cur : sqlite3.Cursor
          entryid : str
        :ReturnType: `measproc.cIntervalList`
        """
        time = _get_domainname_by_entryid(cur, entryid)
        time = numpy.load(os.path.join(self.dirname, time))
        intervallist = cIntervalList(time)
        return intervallist

    def _get_filename_by_entryid(self, cur, entryid):
        """
        :Parameters:
          cur : sqlite3.Cursor
          entryid : str
        """
        _select_filename_by_entryid(cur, entryid)
        name, = cur.fetchone()
        return os.path.join(self.dirname, name)

    def _get_npyxml_filename(self, cur, entryid):
        """
        :Parameters:
          cur : sqlite3.Cursor
          entryid : str
        """
        _select_filename_by_entryid(cur, entryid)
        for name, in cur.fetchall():
            if name.endswith('.xml'):
                break
        else:
            raise ValueError('No xml file have been found for %d' % entryid)
        return os.path.join(self.dirname, name)

    def _wake_workspace(self, cur, entryid):
        """
        :Parameters:
          cur : sqlite3.Cursor
          entryid : str
        """
        name = self._get_filename_by_entryid(cur, entryid)
        entry = FileWorkSpace(name)
        return entry

    def _wake_text(self, cur, entryid):
        """
        :Parameters:
          cur : sqlite3.Cursor
          entryid : str
        """
        name = self._get_filename_by_entryid(cur, entryid)
        entry = FileTextEntry(name)
        return entry

    def _wake_fig(self, cur, entryid):
        """
        :Parameters:
          cur : sqlite3.Cursor
          entryid : str
        """
        name = self._get_filename_by_entryid(cur, entryid)
        entry = FileFigEntry(name)
        return entry

    def _wake_statistic(self, cur, entryid):
        """
        :Parameters:
          cur : sqlite3.Cursor
          entryid : str
        """
        name = self._get_npyxml_filename(cur, entryid)
        entry = cFileStatistic(name)
        return entry

    def _wake_filereport(self, cur, entryid):
        """
        :Parameters:
          cur : sqlite3.Cursor
          entryid : str
        """
        name = self._get_npyxml_filename(cur, entryid)
        entry = cFileReport(name)
        return entry

    def _update_filelike_entry(self, cur, entry, entryid):
        """
        :Parameters:
          cur : sqlite3.Cursor
          entry : iReport|iStatistic|Workspace|TextEntry|FigEntry
          entryid : str
        """
        entry.save()
        return

    def _update_report(self, cur, report, entryid):
        """
        :Parameters:
          cur : sqlite3.Cursor
          report : Report
          entryid : str
        """
        remained, added, removed = _group_report_intervals(cur, report, entryid)

        added_ids = set()

        for entry_intervalid in removed:
            _rm_interval(cur, entry_intervalid)

        # find vote labels
        votegroups = report.getVoteGroups()
        labelids = _build_labelids(cur, votegroups)

        names = report.getNames()
        nameids = _build_nameids(cur, names)

        for entry_intervalid, report_index in remained:
            votegroup = report.getVotes(report_index)
            comment = report.getComment(report_index)
            _update_interval(cur,
                             labelids,
                             votegroup,
                             entryid,
                             entry_intervalid,
                             report_index,
                             comment)

            quantities = report.getQuantities(report_index)
            _update_quantity(cur, nameids, quantities, entryid, entry_intervalid,
                             report_index)

        domain = report.intervallist.Time
        for index, start, end in added:
            votegroup = report.getVotes(index)
            comment = report.getComment(index)
            start_time, end_time = report.getTimeInterval(index)
            entry_intervalid = _reg_interval(cur, labelids, votegroup, entryid, index,
                                             start, end, end == domain.size,
                                             start_time, end_time, comment)

            added_ids.add(entry_intervalid)
            quantities = report.getQuantities(index)
            _add_quantities(cur, entry_intervalid, nameids, quantities)
        return added_ids, removed

    types = {
        'measproc.cFileReport': {
            'wake': _wake_filereport,
            'store': _store_npyxml_entry,
            'update': _update_filelike_entry,
            'type': iReport,
        },
        'measproc.Report': {
            'wake': _wake_report,
            'store': _store_report,
            'update': _update_report,
            'type': Report,
        },
        'measproc.cFileStatistic': {
            'wake': _wake_statistic,
            'store': _store_npyxml_entry,
            'update': _update_filelike_entry,
            'type': iStatistic,
        },
        'measproc.FileWorkSpace': {
            'wake': _wake_workspace,
            'store': _store_filelike_entry,
            'update': _update_filelike_entry,
            'type': WorkSpace,
        },
        'measproc.FileTextEntry': {
            'wake': _wake_text,
            'store': _store_filelike_entry,
            'update': _update_filelike_entry,
            'type': TextEntry,
        },
        'measproc.FileFigEntry': {
            'wake': _wake_fig,
            'store': _store_filelike_entry,
            'update': _update_filelike_entry,
            'type': FigEntry,
        },
    }

    @cursor
    def wake_entry(self, cur, entryid):
        """
        :Parameters:
          entryid : str
        :ReturnType: iReport|Report|iStatistic|Workspace|TextEntry|FigEntry
        """
        type = _get_type(cur, entryid)
        wake = self.types[type]['wake']
        return wake(self, cur, entryid)

    @commit
    def update_entry(self, cur, entry, entryid):
        """
        :Parameters:
          entry: iReport|Report|iStatistic|Workspace|TextEntry|FigEntry
          entryid : str
        """
        type = _get_type(cur, entryid)
        update = self.types[type]['update']
        return update(self, cur, entry, entryid)

    @commit
    def add_entry(self, cur, entry, result=Result.NONE, tags=()):
        """
        :Parameters:
          entry: iReport|Report|iStatistic|Workspace|TextEntry|FigEntry
          result : str
            name from results table
            tags : list
              [tags_name<str>]
        :ReturnType: int
        """
        comment = entry.getEntryComment()
        type = getType(entry)
        title = entry.getTitle()
        entryid = self._add_entry(cur, result, type, title, comment, tags)
        store = self.types[type]['store']
        store(self, cur, entry, entryid)
        return entryid

    @cursor
    def is_measurement_local(self, cur, measurement):
        """
        :Parameters:
          cur : sqlite3.Cursor
          measurement : str
        :ReturnType: bool
        """
        return _is_measurement_local(cur, measurement)

    @cursor
    def get_entry_comment(self, cur, entryid):
        """
        :Parameters:
          entryid : str
        :ReturnType: str
        """
        return _get_comment(cur, entryid)

    def set_entry_comment(self, entryid, comment):
        """
        :Parameters:
          entryid : str
          comment : str
        """
        cur = self.con.cursor()
        _update_comment(cur, entryid, comment)
        cur.close()
        self.con.commit()
        return

    @fetch
    def query(self, cur, query, *args, **kwargs):
        """
        Run a query on batch

        :Parameters:
          query : str
        :Arguments:
          parameters of the query
        :Keywords:
          fetchone : bool
            return only one result row
          * : *
            named parameters of the query
        """
        assert re.search('[:$%]fetchone', query) is None, \
            'reserved keyword: \'fetchone\''
        assert not (bool(args) and bool(kwargs)), \
            'named and non-named parameters cannot be used simultaneously'
        cur.execute(query, args or kwargs)
        return

    @cursor
    def filter(self, cur, order='', asc=True, **kwargs):
        """
        Get the entryids which are equal to the keywords.

        :Keywords: are from `filters`
        """
        entryids = _filter(cur, order, asc, **kwargs)
        return entryids

    @cursor
    def get_entry_attr(self, cur, entryid, name):
        attr = _get_entry_attr(cur, entryid, name)
        return attr

    @cursor
    def select_npyxml_file(self, cur, entryid):
        npyxml_filename = self._get_npyxml_filename(cur, entryid)
        return npyxml_filename

    @cursor
    def pack(self, cur, entryids, name):
        pack = {}
        for entryid in entryids:
            attr = _get_entry_attr(cur, entryid, name)
            group = pack.setdefault(attr, [])
            group.append(entryid)
        return pack

    @cursor
    def get_occasions(self, cur, name):
        occasions = _get_occasions(cur, name)
        return occasions

    @commit
    def create_view_from_last_start(self, cur, date=None, start_date=None,
                                    end_date=None, offset='-4 hours'):
        """
        Create a temporary view from the last run of the entries.
        Repeated runs of the modules can be eliminated, when the module was run over
        the same measurement and with the same parameter.

        :Optionals:
          date : str
            date of the measurement of the entries
          start_date : str
            lower date limit of the measurement's date of the entries
          end_date : str
            upper date limit of the measurement's date of the entries
          offset : str
            date offset to count the early hours to the previous day
            default is '-4 hours'

        :Return: name of the created view
        :ReturnType: str
        """
        date_filter = self.create_measdate_where('me', date, start_date, end_date,
                                                 offset)
        name = self.create_measdate_name('last', date, start_date, end_date)

        cur.execute("""
      CREATE TEMP VIEW IF NOT EXISTS %s AS
      SELECT * FROM (
        SELECT en.*, mo.class mo_class, mo.param mo_param, st.time st_time
          FROM entries en
          JOIN modules mo ON en.moduleid = mo.id
          JOIN measurements me ON en.measurementid = me.id
          JOIN starts st ON en.startid = st.id
        %s
      ) q1 JOIN (
        SELECT DISTINCT en.id en_id, mo.class mo_class, mo.param mo_param,
                        me.id me_id, MAX(st.time) last_time
        FROM entries en
        JOIN modules mo        ON en.moduleid = mo.id
        JOIN measurements me   ON en.measurementid = me.id
        JOIN starts st         ON en.startid = st.id
        GROUP BY mo.class, mo.param, me.id
      ) q2 ON q1.measurementid = q2.me_id
          AND q1.mo_class = q2.mo_class
          AND q1.mo_param = q2.mo_param
      WHERE q1.st_time = q2.last_time
      """ % (name, date_filter))
        return name

    # 06/07/2020 sawantdp : setting offset to 0 as default behaviour
    @commit
    def create_table_from_last_entries(self, cur, date=None, start_date=None,
                                       end_date=None, offset='0 hours'):
        """
        Create a temporary table from the last run of the entries.
        Repeated runs of the modules can be eliminated, when the module was run over
        the same measurement and with the same parameter.

        :Optionals:
          date : str
            date of the measurement of the entries
          start_date : str
            lower date limit of the measurement's date of the entries
          end_date : str
            upper date limit of the measurement's date of the entries
          offset : str
            date offset to count the early hours to the previous day
            default is '-4 hours'

        :Return: name of the created view
        :ReturnType: str
        """

        date_filter = self.create_measdate_where('me', date, start_date, end_date,
                                                 offset)
        name = self.create_measdate_name('last', date, start_date, end_date)

        check = _table_is_exist(cur, name)
        check_temp = _table_is_exist_temp(cur, name)
        if check is not None or check_temp is not None:
            return name

        _clone_schema_to_temp_table(cur, 'entries', name)
        cur.execute('SELECT * FROM %s' % name)
        columns = _get_columns(cur)

        cur.execute("""
      INSERT INTO %(name)s (%(cols)s)
      SELECT %(en_cols)s FROM last_entries
        JOIN entries en      ON last_entries.id = en.id
        JOIN measurements me ON en.measurementid = me.id
        %(date_filter)s

      """ % dict(name=name, date_filter=date_filter,
                 cols=', '.join(columns),
                 en_cols=', '.join('en.%s' % n for n in columns))
                    )
        return name

    @commit
    def create_table_from_last_start(self, cur, date=None, start_date=None,
                                     end_date=None, offset='-4 hours'):
        """
        Create a temporary table from the last run of the entries.
        Repeated runs of the modules can be eliminated, when the module was run over
        the same measurement and with the same parameter.

        :Optionals:
          date : str
            date of the measurement of the entries
          start_date : str
            lower date limit of the measurement's date of the entries
          end_date : str
            upper date limit of the measurement's date of the entries
          offset : str
            date offset to count the early hours to the previous day
            default is '-4 hours'

        :Return: name of the created view
        :ReturnType: str
        """
        date_filter = self.create_measdate_where('me', date, start_date, end_date,
                                                 offset)
        name = self.create_measdate_name('last', date, start_date, end_date)

        check = _table_is_exist(cur, name)
        if check is not None:
            return name

        _clone_schema_to_temp_table(cur, 'entries', name)
        cur.execute('SELECT * FROM %s' % name)
        columns = _get_columns(cur)

        cur.execute("""
      INSERT INTO %(name)s (%(cols)s)
      SELECT %(q1_cols)s FROM (
        SELECT en.*, mo.class mo_class, mo.param mo_param, st.time st_time
          FROM entries en
          JOIN modules mo ON en.moduleid = mo.id
          JOIN measurements me ON en.measurementid = me.id
          JOIN starts st ON en.startid = st.id
        %(date_filter)s
      ) q1 JOIN (
        SELECT DISTINCT en.id en_id, mo.class mo_class, mo.param mo_param,
                        me.id me_id, MAX(st.time) last_time
        FROM entries en
        JOIN modules mo        ON en.moduleid = mo.id
        JOIN measurements me   ON en.measurementid = me.id
        JOIN starts st         ON en.startid = st.id
        GROUP BY mo.class, mo.param, me.id
      ) q2 ON q1.measurementid = q2.me_id
          AND q1.mo_class = q2.mo_class
          AND q1.mo_param = q2.mo_param
      WHERE q1.st_time = q2.last_time
      """ % dict(name=name, date_filter=date_filter,
                 cols=', '.join(columns),
                 q1_cols=', '.join('q1.%s' % n for n in columns))
                    )
        return name

    @staticmethod
    def create_measdate_where(measurements, date=None, start_date=None,
                              end_date=None, offset='-4 hour'):
        if date is not None:
            date_filter = "WHERE DATE(%s.start, '%s') = '%s'" \
                          % (measurements, offset, date)
        elif start_date is not None and end_date is not None:
            date_filter = "WHERE DATE(%s.start, '%s') BETWEEN '%s' AND '%s'" \
                          % (measurements, offset, start_date, end_date)
        elif start_date is not None:
            date_filter = "WHERE DATE(%s.start, '%s') >= '%s'" \
                          % (measurements, offset, start_date)
        elif end_date is not None:
            date_filter = "WHERE DATE(%s.start, '%s') <= '%s'" \
                          % (measurements, offset, end_date)
        else:
            date_filter = ""
        return date_filter

    @staticmethod
    def create_measdate_name(name, date=None, start_date=None, end_date=None):
        if date is not None:
            name += 'e' + date.replace('-', '')
        elif start_date is not None and end_date is not None:
            name += 'ge' + start_date.replace('-', '') + 'le' + end_date.replace('-', '')
        elif start_date is not None:
            name += 'ge' + start_date.replace('-', '')
        elif end_date is not None:
            name += 'le' + end_date.replace('-', '')
        return name

    @cursor
    def get_interval_attr(self, cur, interval_id, attr_name):
        """
        :Parameters:
          interval_id : int
          attr_name : str
            Valid attribute names are: comment, start, end, start_time, end_time
        :Exceptions:
          ValueError : invalid attr_name
        """
        attr = _get_interval_attr(cur, interval_id, attr_name)
        return attr

    @cursor
    def get_interval_labels(self, cur, interval_id, labelgroup):
        labels = _get_labels_by_labelgroup(cur, interval_id, labelgroup)
        return labels

    @commit
    def label_interval(self, cur, interval_id, labelgroup, label):
        if _is_labelgroup_exclusive(cur, labelgroup):
            cur.execute("""
                  SELECT interval2label.labelid FROM interval2label
                    JOIN labels ON
                         labels.id = interval2label.labelid
                    JOIN labelgroups ON
                         labelgroups.id = labels.groupid
                  WHERE  interval2label.entry_intervalid = ?
                    AND  labelgroups.name = ?
                  """, (interval_id, labelgroup))
            for labelid, in cur.fetchall():
                _rm_interval2label(cur, interval_id, labelid)
        labelid = _get_labelid(cur, labelgroup, label)
        _add_interval2label(cur, interval_id, labelid)
        return

    @commit
    def unlabel_interval(self, cur, interval_id, labelgroup, label):
        labelid = _get_labelid(cur, labelgroup, label)
        _rm_interval2label(cur, interval_id, labelid)
        return

    @commit
    def rm_interval(self, cur, intervalid):
        _rm_interval(cur, intervalid)
        return

    @cursor
    def get_interval_qua(self, cur, interval_id, quagroup, qua):
        value = _get_qua_by_names(cur, interval_id, quagroup, qua)
        return value

    @commit
    def set_interval_qua(self, cur, interval_id, quagroup, qua, value):
        cur.execute("""
                SELECT quanames.id FROM quanames
                  JOIN quanamegroups ON
                       quanamegroups.id = quanames.groupid
                WHERE  quanamegroups.name = ?
                  AND  quanames.name = ?
               """, (quagroup, qua))
        nameid = cur.fetchone()
        assert nameid is not None, \
            "Invalid quantity group (%s) or quantity name (%s)" % (quagroup, qua)

        nameid, = nameid
        cur.execute("""
                SELECT  id FROM quantities
                WHERE  entry_intervalid = ?
                  AND  nameid = ?
                """, (interval_id, nameid))
        quaid = cur.fetchone()
        if quaid is None:
            _add_quantity(cur, interval_id, nameid, value)
        else:
            _update_quantity_value(cur, interval_id, nameid, value)
        return

    @cursor
    def get_intervalid_by_entryid(self, cur, entryid):
        ids = _get_intervalid_by_entryid(cur, entryid)
        return [id[0] for id in ids]

    @commit
    def add_intervalcomment(self, cur, interval_id, comment):
        _add_intervalcomment(cur, interval_id, comment)
        return

    @cursor
    def get_entryid_by_interval(self, cur, interval_id):
        cur.execute("SELECT entryid FROM entryintervals WHERE  id = ?",
                    (interval_id,))
        entryid, = cur.fetchone()
        return entryid

    @cursor
    def get_interval_pos(self, cur, interval_id):
        cur.execute("SELECT position FROM entryintervals WHERE id = ?",
                    (interval_id,))
        pos, = cur.fetchone()
        return pos

    @cursor
    def str_table(self, cur, header, ids,
                  col_sep='|', row_sep='\n', row_init='|', row_term='|',
                  show_header=True, sortby=None, cell_formatter=str_cell):
        """
        :Parameters:
          header : list
            [query<TableQuery>]
          ids : list
            [interval_id<int>]
        :Kwargs:
          colsep : str
          rowsep : str
          rowinit : str
          rowterm : str
          show_header : bool
          sortby : list
            [(query_name<str>, ascending<bool>)]
        """
        data = self.get_table(header, ids,
                              show_header=show_header, sortby=sortby, cell_formatter=cell_formatter)
        table = []
        for row in data:
            table.append(row_init + col_sep.join(row) + row_term)
        table = row_sep.join(table) + row_sep
        return table

    @cursor
    def csv_table(self, cur, header, ids, col_sep=';',
                  show_header=True, sortby=None, cell_formatter=str_cell):
        return self.str_table(header, ids,
                              col_sep=col_sep, row_sep='\n', row_init='', row_term='',
                              show_header=show_header, sortby=sortby, cell_formatter=cell_formatter)

    @cursor
    def get_table(self, cur, header, ids,
                  show_header=True, sortby=None, cell_formatter=None):
        """
        Return data table as list of lists.
        """
        if cell_formatter is not None:
            format_cell = cell_formatter
        else:
            format_cell = lambda cell: cell  # identical transformation (no change)

        queries = [TableQuery.factory(names, query, cur) for names, query in header]

        _header = []
        for query in queries:
            _header.extend(query.get_names())

        table = []
        ids = set(ids)
        ids.update(get_static_table_ids(queries))
        for idx in sorted(ids):
            row = {}
            for query in queries:
                query.update_row(cur, row, idx)
            table.append([row[name] for name in _header])

        sortby = sortby or []
        for name, asc in sortby[::-1]:
            try:
                sort_col_idx = _header.index(name)
            except ValueError:
                raise ValueError("Cannot sort by '%s': no such column" % name)
            table.sort(key=itemgetter(sort_col_idx), reverse=not asc)

        table = [[format_cell(cell) for cell in row] for row in table]

        if show_header:
            table = [_header] + table
        return table

    @cursor
    def get_table_dict(self, cur, header, ids,
                       sortby=None, cell_formatter=None):
        """
        Return data table as list of OrderedDicts.

        Usage example:
        >>> table_dict = batch.get_table_dict(header, ids)
        >>> print table_dict[0]['column1'], table_dict[0]['column2']
        >>> print len(table_dict)
        """
        return [row for row in self.get_table_xdict(
            header, ids, sortby=sortby, cell_formatter=cell_formatter)]

    @cursor
    def get_table_xdict(self, cur, header, ids,
                        sortby=None, cell_formatter=None):
        """
        Generator for data table as list of OrderedDicts.

        Usage example:
        >>> table_dict = batch.get_table_xdict(header, ids)
        >>> for row in table_dict:
        >>>     print row['column1'], row['column2']
        """
        table = self.get_table(header, ids,
                               show_header=True, sortby=sortby, cell_formatter=cell_formatter)
        header, data = table[0], table[1:]
        for row in data:
            yield OrderedDict(zip(header, row))
        return

    @commit
    def update_interval_labels(self, cur, src_entryid, dst_entryid):
        for src_ei_id, dst_ei_id in _get_common_intervalids(cur, src_entryid, dst_entryid):
            labelids = set(_get_labelids_by_intervalid(cur, src_ei_id)) \
                       - set(_get_labelids_by_intervalid(cur, dst_ei_id))
            for labelid in labelids:
                _add_interval2label(cur, dst_ei_id, labelid)
        return

    @commit
    def update_interval_comment(self, cur, src_entryid, dst_entryid):
        for src_ei_id, dst_ei_id in _get_common_intervalids(cur, src_entryid, dst_entryid):
            if _get_comment_by_intervalid(cur, dst_ei_id) is not None: continue
            comment = _get_comment_by_intervalid(cur, src_ei_id)
            if comment is None: continue
            _add_intervalcomment(cur, dst_ei_id, comment)
        return

    @commit
    def update_interval_quantities(self, cur, src_entryid, dst_entryid):
        for src_ei_id, dst_ei_id in _get_common_intervalids(cur, src_entryid, dst_entryid):
            src_quas = _get_quantity_by_intervalid(cur, src_ei_id)
            dst_quas = _get_quantity_by_intervalid(cur, dst_ei_id)
            for nameid, value in src_quas.iteritems():
                if nameid in dst_quas: continue
                _add_quantity(cur, dst_ei_id, nameid, value)
        return

    def save(self):
        self.con.close()
        return


def get_static_table_ids(queries):
    ids = {}
    for query in queries:
        if not isinstance(query, StaticSelectTableQuery): continue
        ids.update(query.rows)
    return ids


class TableQuery(object):
    QUERY_TYPE = ''
    NOT_AVAILABLE = 'n/a'
    SEP = ', '
    FLOAT_FMT = '%.2f'
    DROP = '_'
    ID = '@'

    def __init__(self, names, query, cur):
        self.names = names
        self.query = query
        return

    @classmethod
    def factory(cls, names, query, cur):
        sub_cls = cls.get_type(names, query)
        self = sub_cls(names, query, cur)
        return self

    @classmethod
    def get_type(cls, names, query):
        for sub_cls in cls.__subclasses__():
            if sub_cls.check(names, query): return sub_cls
            for subsub_cls in sub_cls.__subclasses__():
                if subsub_cls.check(names, query): return subsub_cls
        raise ValueError('Invalid query %s' % query)

    @classmethod
    def check(cls, names, query):
        return cls.get_query_head(query) == cls.QUERY_TYPE

    @classmethod
    def get_query_head(cls, query):
        head = cls._split_query(query)[0]
        return head.upper()

    @staticmethod
    def _split_query(query):
        split = query.split(' ', 1)
        return split

    @classmethod
    def str_result(cls, result):
        if isinstance(result, (list, tuple)):
            result = cls.str_list(result)
        else:
            result = cls.str_value(result)
        return result

    @classmethod
    def str_list(cls, result):
        if result:
            result = cls.SEP.join(cls.str_value(value) for value in result)
        else:
            result = cls.NOT_AVAILABLE
        return result

    @classmethod
    def str_value(cls, value):
        if value is None:
            value = cls.NOT_AVAILABLE
        elif isinstance(value, float):
            value = cls.FLOAT_FMT % value
        else:
            value = str(value)
        return value

    def update_row(self, cur, row, idx):
        raise NotImplementedError

    def str_update_row(self, cur, row, idx):
        row = self.update_row(cur, row, idx)
        row = self.str_row(row)
        return row

    def str_row(self, row):
        for name in self.names:
            if name == self.DROP or name == self.ID: continue
            row[name] = self.str_result(row[name])
        return row

    def get_names(self):
        names = self.filter_names(self.names)
        return names

    @classmethod
    def filter_names(cls, names):
        names = [name for name in names if name != cls.DROP and name != cls.ID]
        return names


class SelectTableQuery(TableQuery):
    QUERY_TYPE = 'SELECT'

    @classmethod
    def check(cls, names, query):
        return cls.get_query_head(query) == cls.QUERY_TYPE and '?' in query

    def update_row(self, cur, row, idx):
        cur.execute(self.query, (idx,))
        results = cur.fetchall() or [[None for name in self.names]]
        single = len(results) == 1
        for result in results:
            for name, value in zip(self.names, result):
                if name == self.DROP: continue
                if single:
                    row[name] = value
                else:
                    row.setdefault(name, []).append(value)
        return row


class StaticSelectTableQuery(TableQuery):
    QUERY_TYPE = 'STATIC SELECT'

    def __init__(self, names, query, cur):
        TableQuery.__init__(self, names, query, cur)
        self.rows = self._create_rows(cur)
        return

    @classmethod
    def check(cls, names, query):
        return cls.ID in names \
               and cls.get_query_head(query) == 'SELECT' \
               and '?' not in query

    def _create_rows(self, cur):
        cur.execute(self.query)
        rows = {}
        for row in cur.fetchall():
            data = {}
            for name, value in zip(self.names, row):
                if name == self.DROP:
                    continue
                elif name == self.ID:
                    idx = value
                else:
                    data[name] = value
            rows[idx] = data
        return rows

    def update_row(self, cur, row, idx):
        if idx in self.rows:
            row.update(self.rows[idx])
        else:
            row.update((name, None) for name in self.get_names())
        return row


class SingleNameTableQuery(TableQuery):
    def __init__(self, names, query, cur):
        no_names = len(names)
        assert no_names == 1, \
            'Too many names (%d) for %s' % (no_names, self.__class__.__name__)
        TableQuery.__init__(self, names, query, cur)
        self.name, = names
        return


class LabelTableQuery(SingleNameTableQuery):
    QUERY_TYPE = 'LABEL'

    def __init__(self, names, query, cur):
        SingleNameTableQuery.__init__(self, names, query, cur)
        self.labelgroup = self.get_lg_from_query(query)
        return

    def update_row(self, cur, row, idx):
        row[self.name] = _get_labels_by_labelgroup(cur, idx, self.labelgroup)
        return row

    @classmethod
    def get_lg_from_query(cls, query):
        head, labelgroup = cls._split_query(query)
        labelgroup = labelgroup.strip('"\'')
        return labelgroup

    pass


class QuaTableQuery(SingleNameTableQuery):
    QUERY_TYPE = 'QUANTITY'

    def __init__(self, names, query, cur):
        SingleNameTableQuery.__init__(self, names, query, cur)
        self.quagroup, self.qua, self.factor, self.offset = \
            self.get_quanames_from_query(query)
        return

    def update_row(self, cur, row, idx):
        row[self.name] = _get_qua_by_names(cur, idx,
                                           self.quagroup, self.qua, self.factor, self.offset)
        return row

    @classmethod
    def get_quanames_from_query(cls, query):
        head, query = cls._split_query(query)
        parts = query.split(',')
        assert len(parts) > 1 and len(parts) < 5, \
            "Invalid number of arguments for QUANTITY query"
        quagroup = parts[0].strip().strip('"\'')
        qua = parts[1].strip().strip('"\'')
        factor = float(parts[2].strip()) if len(parts) > 2 else 1.0
        offset = float(parts[3].strip()) if len(parts) > 3 else 0.0
        return quagroup, qua, factor, offset


class CommentTableQuery(SingleNameTableQuery):
    QUERY_TYPE = 'COMMENT'

    def update_row(self, cur, row, idx):
        row[self.name] = _get_interval_attr(cur, idx, 'comment')
        return row


class EntryCommentTableQuery(SingleNameTableQuery):
    QUERY_TYPE = 'ENTRYCOMMENT'

    def update_row(self, cur, row, idx):
        row[self.name] = _get_title_comment_result_by_intervalid(cur, idx)[1]
        return row


class StartTimeTableQuery(SingleNameTableQuery):
    QUERY_TYPE = 'STARTTIME'

    def update_row(self, cur, row, idx):
        row[self.name] = _get_interval_attr(cur, idx, 'start_time')
        return row


class EndTimeTableQuery(SingleNameTableQuery):
    QUERY_TYPE = 'ENDTIME'

    def update_row(self, cur, row, idx):
        row[self.name] = _get_interval_attr(cur, idx, 'end_time')
        return row


class DurationTableQuery(SingleNameTableQuery):
    QUERY_TYPE = 'DURATION'

    def update_row(self, cur, row, idx):
        row[self.name] = (_get_interval_attr(cur, idx, 'end_time') -
                          _get_interval_attr(cur, idx, 'start_time'))
        return row


class MeasTableQuery(SingleNameTableQuery):
    QUERY_TYPE = 'MEAS'

    def update_row(self, cur, row, idx):
        row[self.name] = _get_measurement_basename_by_intervalid(cur, idx)
        return row


class FullMeasTableQuery(SingleNameTableQuery):
    QUERY_TYPE = 'FULLMEAS'

    def update_row(self, cur, row, idx):
        row[self.name] = _get_measurement_by_intervalid(cur, idx)[0]
        return row


class TitleTableQuery(SingleNameTableQuery):
    QUERY_TYPE = 'TITLE'

    def update_row(self, cur, row, idx):
        row[self.name] = _get_title_comment_result_by_intervalid(cur, idx)[0]
        return row


class ResultTableQuery(SingleNameTableQuery):
    QUERY_TYPE = 'RESULT'

    def update_row(self, cur, row, idx):
        row[self.name] = _get_title_comment_result_by_intervalid(cur, idx)[2]
        return row


def get_ndarray_hash(a):
    """
    Get md5 hash of `a` npy header

    :Parameters:
      a : numpy.ndarray
    :ReturnType: str
    """
    m = md5.new()
    m.update(a.dtype.str)
    m.update('F' if a.flags['F_CONTIGUOUS'] else 'C')
    m.update(','.join([str(e) for e in a.shape]))
    m.update(a.tostring())
    return m.hexdigest()


def get_meas_startdate(measurement):
    try:
        Parser = findParser(measurement)
    except IOError:
        try:
            date = iParser.getStartDateFromFileName(measurement)
        except ValueError:
            date = datetime.datetime.now()
    else:
        date = Parser.getStartDate(measurement)
    return date


class CreateParams:
    def __init__(self, db_name, dir_name, labels, tags, results, quanames,
                 enable_update):
        self.db_name = db_name
        self.dir_name = dir_name
        self.labels = labels
        self.tags = tags
        self.results = results
        self.quanames = quanames
        self.enable_update = enable_update
        return

    def __call__(self):
        try:
            batch = Batch(self.db_name, self.dir_name, self.labels, self.tags,
                          self.results, self.quanames)
        except ValueError, error:
            if not self.enable_update: raise error

            update(self.db_name, self.dir_name)
            batch = Batch(self.db_name, self.dir_name, self.labels, self.tags,
                          self.results, self.quanames)
        return batch


class InitParams:
    def __init__(self, start, measurement, local, class_name, param, version):
        self.start = time.strftime(Batch.TIME_FORMAT, start)
        self.measurement = measurement
        self.local = local
        self.class_name = class_name
        self.param = param
        self.version = version
        return

    def __call__(self, batch):
        batch.set_start(self.start)
        batch.set_measurement(self.measurement, self.local)
        batch.set_module(self.class_name, self.param, self.version)
        return


class UploadParams:
    def __init__(self, result, tags):
        self.result = result
        self.tags = tags
        return

    def __call__(self, batch, entry):
        return batch.add_entry(entry, self.result, self.tags)


def main(dbname, dirname, measurement, origmeas, labels, tags, quanames):
    """
    Setup function for module test.

    :Parameters:
      dbname : str
      dirname : str
      measurement : str
      origmeas : bool
      labels : dict
        {group_name<str>: (exclusive<bool>, [label_names<str>])}
      tags : dict
        {group_name<str>: [tag_names<str>]}
    """
    # batch and report parameters
    start = time.strftime(Batch.TIME_FORMAT)
    time_array = numpy.arange(0, 600, 20e-3)
    titles = 'foo is never bar', 'bar should be', 'pyon get the bottom'
    intervalgroup = [{(13, 78): 'bar',
                      (113, 182): 'baz'},
                     {(56, 77): 'bar'}]
    # init batch
    batch = Batch(dbname, dirname, labels, tags, RESULTS, quanames)
    batch.set_start(start)
    batch.set_measurement(measurement, origmeas)
    measproc.Report.RepDir = dirname

    # init report
    entids = []
    for group_name, (exclusive, votes) in labels.iteritems():
        for title in titles:
            for intervals in intervalgroup:
                intervallist = cIntervalList(time_array)
                report = Report(intervallist, title, labels)
                report.setEntryComment('spam')
                for interval, vote in intervals.iteritems():
                    intervalid = report.addInterval(interval)
                    report.vote(intervalid, group_name, vote)
                    report.setComment(intervalid, 'spamspam')

                # add report to batch
                class_name = 'searchFoo.cSearch'
                param = 'foo="bar"'
                version = '0.1.0'
                result = 'none'
                entry_tags = 'egg',
                batch.set_module(class_name, param, version)
                entid = batch.add_entry(report,
                                        result,
                                        entry_tags)
                entids.append(entid)
    return batch, entids


def clear(dbname, dirname):
    """
    Teardown function for module test.

    :Parameters:
      dbname : str
      dirname : str
    """
    os.remove(dbname)
    shutil.rmtree(dirname)
    return


def configParser(parser):
    """
    Command line parser config function for module test.

    :Parameters:
      parser : optparser.OptionParser
    :ReturnType: optparser.OptionParser
    """
    parser.add_option('-m', '--measurement',
                      help='measurement file [=%default]',
                      default='D:/measurement/dataeval-test/'
                              'CVR3_B1_2011-02-10_16-53_020.mdf')
    parser.add_option('--dbname',
                      help='Name of the database file [=%default]',
                      default='batch.db')
    parser.add_option('--dirname',
                      help='Name of the directory where the files will be stored'
                           ' [=%default]',
                      default='files')
    parser.add_option('--origmeas',
                      help='The measurement presents on the measurement server',
                      default=True,
                      action='store_false')
    return parser


if __name__ == '__main__':
    import optparse

    labels = {'foo': (False, ['bar', 'baz'])}
    tags = {'spam': ['egg', 'eggegg']}
    quanames = {'egg': ['spam', 'spamspam']}

    # command line options
    parser = optparse.OptionParser()
    parser = configParser(parser)
    opts, args = parser.parse_args()

    batch, entids = main(opts.dbname, opts.dirname, opts.measurement,
                         opts.origmeas, labels, tags, quanames)
    batch.save()

    batch = Batch(opts.dbname, opts.dirname, labels, tags, RESULTS, quanames)
    waked = batch.wake_entry(entids[0])

    measid, = batch.query('SELECT id FROM measurements WHERE local=?',
                          opts.measurement, fetchone=True)
    measids = batch.query('SELECT id FROM measurements WHERE local=?',
                          opts.measurement)
    batch.save()

    clear(opts.dbname, opts.dirname)
