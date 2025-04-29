from unittest import main

from create_view_from_last_start import BuildBatch as Build

class BuildBatch(Build):
  events = {}
  for interval, label, qua in [((0, 12), 'bar', 12.4), ((45, 50), 'baz', 2.3)]:
    events[interval] = {
      'labels': [('foo', label)],
      'quas': [('pyon', 'atomsk', qua)],
    }
  report = Build.report.copy()
  report['events'] = events
  reports = [report]

class TestGetTable(BuildBatch):
  def setUp(self):
    self.header = [
      (('measurement',),
       '''SELECT measurements.basename FROM entryintervals
            JOIN entries ON
                 entries.id = entryintervals.entryid
            JOIN measurements ON
                 measurements.id = entries.measurementid
          WHERE  entryintervals.id = ?'''),
      (('label',), 'LABEL foo'),
      (('atomsk',), 'QUANTITY pyon, atomsk'),
      (('naota',), 'QUANTITY pyon, naota'),
    ]
    return

  def test_get_table(self):
    table = [
      ['measurement',              'label' , 'atomsk', 'naota'],
      [u'2013.09.12_14.52.43.mdf', [u'baz'], 2.3,   None],
      [u'2013.09.12_14.52.43.mdf', [u'bar'], 12.4,  None],
    ]
    ids = [idx for idx, start, end in self.intervals]
    self.assertListEqual(self.batch.get_table(self.header, ids), table)
    return

  def test_str_table(self):
    ids = [idx for idx, start, end in self.intervals]
    col_sep = '|'
    row_sep = '\n'
    table =  '|measurement|label|atomsk|naota|\n'\
             '|2013.09.12_14.52.43.mdf|baz|2.30|n/a|\n'\
             '|2013.09.12_14.52.43.mdf|bar|12.40|n/a|\n'
    self.assertEqual(self.batch.str_table(self.header, ids,
                                          col_sep=col_sep,
                                          row_sep=row_sep),
                     table)
    return

class TestGetDoubleColumnTable(BuildBatch):
  def setUp(self):
    self.header = [
      (('i_id', 'measurement'),
       '''SELECT entryintervals.id, measurements.basename FROM entryintervals
            JOIN entries ON
                 entries.id = entryintervals.entryid
            JOIN measurements ON
                 measurements.id = entries.measurementid
          WHERE  entryintervals.id = ?'''),
      (('label',), 'LABEL foo'),
    ]
    return

  def test_get_table(self):
    table = [
      ['i_id', 'measurement',              'label'],
      [1,      u'2013.09.12_14.52.43.mdf', [u'baz']],
      [2,      u'2013.09.12_14.52.43.mdf', [u'bar']],
    ]
    ids = [idx for idx, start, end in self.intervals]
    self.assertListEqual(self.batch.get_table(self.header, ids), table)
    return

  def test_str_table(self):
    ids = [idx for idx, start, end in self.intervals]
    col_sep = '|'
    row_sep = '\n'
    table =  '|i_id|measurement|label|\n'\
             '|1|2013.09.12_14.52.43.mdf|baz|\n'\
             '|2|2013.09.12_14.52.43.mdf|bar|\n'
    self.assertEqual(self.batch.str_table(self.header, ids,
                                          col_sep=col_sep,
                                          row_sep=row_sep),
                     table)
    return


class TestStrTableSortBy(BuildBatch):
  def setUp(self):
    self.header = [
      (('measurement',),
       '''SELECT measurements.basename FROM entryintervals
            JOIN entries ON
                 entries.id = entryintervals.entryid
            JOIN measurements ON
                 measurements.id = entries.measurementid
          WHERE  entryintervals.id = ?'''),
      (('label',), 'LABEL foo'),
      (('qua',),
      '''SELECT qua.value FROM entryintervals ei
           JOIN quantities qua ON qua.entry_intervalid = ei.id
           JOIN quanames ON quanames.id = qua.nameid
           JOIN quanamegroups ON quanamegroups.id = quanames.groupid
         WHERE quanamegroups.name = "pyon"
           AND quanames.name = "atomsk"
           AND ei.id = ?''')
    ]
    return

  def test_str_table_sortby(self):
    ids = [idx for idx, start, end in self.intervals]
    col_sep = '|'
    row_sep = '\n'
    table =  '|measurement|label|qua|\n'\
             '|2013.09.12_14.52.43.mdf|baz|2.30|\n'\
             '|2013.09.12_14.52.43.mdf|bar|12.40|\n'
    self.assertEqual(self.batch.str_table(self.header, ids,
                                          col_sep=col_sep,
                                          row_sep=row_sep,
                                          sortby=[('qua', True)]),
                     table)
    return
class TestGetDropColumnTable(BuildBatch):
  def setUp(self):
    self.header = [
      (('_', 'measurement'),
       '''SELECT entryintervals.id, measurements.basename FROM entryintervals
            JOIN entries ON
                 entries.id = entryintervals.entryid
            JOIN measurements ON
                 measurements.id = entries.measurementid
          WHERE  entryintervals.id = ?'''),
      (('label',), 'LABEL foo'),
    ]
    return

  def test_get_table(self):
    table = [
      ['measurement',              'label'],
      [u'2013.09.12_14.52.43.mdf', [u'baz']],
      [u'2013.09.12_14.52.43.mdf', [u'bar']],
    ]
    ids = [idx for idx, start, end in self.intervals]
    self.assertListEqual(self.batch.get_table(self.header, ids), table)
    return

  def test_str_table(self):
    ids = [idx for idx, start, end in self.intervals]
    col_sep = '|'
    row_sep = '\n'
    table =  '|measurement|label|\n'\
             '|2013.09.12_14.52.43.mdf|baz|\n'\
             '|2013.09.12_14.52.43.mdf|bar|\n'
    self.assertEqual(self.batch.str_table(self.header, ids,
                                          col_sep=col_sep,
                                          row_sep=row_sep),
                     table)
    return

class TestNotAvailableData(BuildBatch):
  def setUp(self):
    self.header = [
      (('measurement',),
       '''SELECT measurements.basename FROM entryintervals
            JOIN entries ON
                 entries.id = entryintervals.entryid
            JOIN measurements ON
                 measurements.id = entries.measurementid
          WHERE  entryintervals.id = ?
            AND  measurements.start = "never"'''),
      (('label',), 'LABEL foo'),
    ]
    return

  def test_get_table(self):
    table = [
      ['measurement', 'label'],
      [None, ['baz']],
      [None, ['bar']],
    ]
    ids = [idx for idx, start, end in self.intervals]
    self.assertListEqual(self.batch.get_table(self.header, ids), table)
    return

  def test_str_table(self):
    ids = [idx for idx, start, end in self.intervals]
    col_sep = '|'
    row_sep = '\n'
    table = "|measurement|label|\n"\
            "|n/a|baz|\n"\
            "|n/a|bar|\n"
    self.assertEqual(self.batch.str_table(self.header, ids,
                                          col_sep=col_sep,
                                          row_sep=row_sep),
                     table)
    return

class TestStaticTable(BuildBatch):
  def setUp(self):
    self.header = [
      (('@', 'measurement'),
       '''SELECT entryintervals.id, measurements.basename FROM entryintervals
            JOIN entries ON
                 entries.id = entryintervals.entryid
            JOIN measurements ON
                 measurements.id = entries.measurementid'''),
      (('label',), 'LABEL foo'),
    ]
    return

  def test_get_table(self):
    table = [
      ['measurement',              'label'],
      [u'2013.09.12_14.52.43.mdf', [u'baz']],
      [u'2013.09.12_14.52.43.mdf', [u'bar']],
    ]
    self.assertListEqual(self.batch.get_table(self.header, []), table)
    return

  def test_str_table(self):
    col_sep = '|'
    row_sep = '\n'
    table =  '|measurement|label|\n'\
             '|2013.09.12_14.52.43.mdf|baz|\n'\
             '|2013.09.12_14.52.43.mdf|bar|\n'
    self.assertEqual(self.batch.str_table(self.header, [],
                                          col_sep=col_sep,
                                          row_sep=row_sep),
                     table)
    return
if __name__ == '__main__':
  main()
