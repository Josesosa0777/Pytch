from unittest import main

from measproc.batchsqlite import TableQuery, LabelTableQuery, CommentTableQuery,\
                                 SelectTableQuery, StaticSelectTableQuery

from interval_queries import BuildBatch

class TestLabelTableQuery(BuildBatch):
  def setUp(self):
    names = 'foo',
    query = 'LABEL foo'
    cur = self.batch.con.cursor()
    self.query = TableQuery.factory(names, query, cur)
    return

  def test_type(self):
    self.assertIsInstance(self.query, LabelTableQuery)
    return

  def test_update_row(self):
    cur = self.batch.con.cursor()
    for idx, start, end in self.iter_intervals():
      row = self.query.update_row(cur, {}, idx)
      self.assertDictEqual(row, {'foo': ['bar']})
    return

  def test_str_update_row(self):
    cur = self.batch.con.cursor()
    for idx, start, end in self.iter_intervals():
      row = self.query.str_update_row(cur, {}, idx)
      self.assertDictEqual(row, {'foo': 'bar'})
    return

class TestCommentTableQuery(BuildBatch):
  def setUp(self):
    names = 'foo',
    query = 'comment'
    cur = self.batch.con.cursor()
    self.query = TableQuery.factory(names, query, cur)
    return

  def test_type(self):
    self.assertIsInstance(self.query, CommentTableQuery)
    return

  def test_update_row(self):
    cur = self.batch.con.cursor()
    for idx, start, end in self.iter_intervals():
      row = self.query.update_row(cur, {}, idx)
      self.assertDictEqual(row, {'foo': 'nyaff'})
    return

  def test_str_update_row(self):
    cur = self.batch.con.cursor()
    for idx, start, end in self.iter_intervals():
      row = self.query.str_update_row(cur, {}, idx)
      self.assertDictEqual(row, {'foo': 'nyaff'})
    return

class TestSelectTableQuery(BuildBatch):
  def setUp(self):
    names = 'foo',
    query = '''SELECT measurements.basename FROM entryintervals
                 JOIN entries ON
                      entries.id = entryintervals.entryid
                 JOIN measurements ON
                      measurements.id = entries.measurementid
               WHERE  entryintervals.id = ?'''
    cur = self.batch.con.cursor()
    self.query = TableQuery.factory(names, query, cur)
    return

  def test_type(self):
    self.assertIsInstance(self.query, SelectTableQuery)
    return

  def test_update_row(self):
    cur = self.batch.con.cursor()
    for idx, start, end in self.iter_intervals():
      row = self.query.update_row(cur, {}, idx)
      self.assertDictEqual(row, {'foo': 'bar.mdf'})
    return

  def test_str_update_row(self):
    cur = self.batch.con.cursor()
    for idx, start, end in self.iter_intervals():
      row = self.query.str_update_row(cur, {}, idx)
      self.assertDictEqual(row, {'foo': 'bar.mdf'})
    return

class TestDoubleSelectTableQuery(BuildBatch):
  def setUp(self):
    names = 'foo', 'bar'
    query = '''SELECT measurements.basename, entryintervals.id
               FROM entryintervals
                 JOIN entries ON
                      entries.id = entryintervals.entryid
                 JOIN measurements ON
                      measurements.id = entries.measurementid
               WHERE  entryintervals.id = ?'''
    cur = self.batch.con.cursor()
    self.query = TableQuery.factory(names, query, cur)
    return
  
  def test_update_row(self):
    cur = self.batch.con.cursor()
    for idx, start, end in self.iter_intervals():
      row = self.query.update_row(cur, {}, idx)
      self.assertDictEqual(row, {'foo': 'bar.mdf', 'bar': idx})
    return

  def test_str_update_row(self):
    cur = self.batch.con.cursor()
    for idx, start, end in self.iter_intervals():
      row = self.query.str_update_row(cur, {}, idx)
      self.assertDictEqual(row, {'foo': 'bar.mdf', 'bar': '%d' % idx})
    return

class TestDropSelectTableQuery(BuildBatch):
  def setUp(self):
    names = 'foo', '_'
    query = '''SELECT measurements.basename, entryintervals.id
               FROM entryintervals
                 JOIN entries ON
                      entries.id = entryintervals.entryid
                 JOIN measurements ON
                      measurements.id = entries.measurementid
               WHERE  entryintervals.id = ?'''
    cur = self.batch.con.cursor()
    self.query = TableQuery.factory(names, query, cur)
    return
  
  def test_update_row(self):
    cur = self.batch.con.cursor()
    for idx, start, end in self.iter_intervals():
      row = self.query.update_row(cur, {}, idx)
      self.assertDictEqual(row, {'foo': 'bar.mdf'})
    return

  def test_str_update_row(self):
    cur = self.batch.con.cursor()
    for idx, start, end in self.iter_intervals():
      row = self.query.str_update_row(cur, {}, idx)
      self.assertDictEqual(row, {'foo': 'bar.mdf'})
    return

class TestNotAvailableTableQuery(BuildBatch):
  def setUp(self):
    names = 'foo',
    query = '''SELECT measurements.basename FROM entryintervals
                 JOIN entries ON
                      entries.id = entryintervals.entryid
                 JOIN measurements ON
                      measurements.id = entries.measurementid
               WHERE  entryintervals.id = ?
                 AND  measurements.start = "never"'''
    cur = self.batch.con.cursor()
    self.query = TableQuery.factory(names, query, cur)
    return

  def test_update_row(self):
    cur = self.batch.con.cursor()
    for idx, start, end in self.iter_intervals():
      row = self.query.update_row(cur, {}, idx)
      self.assertDictEqual(row, {'foo': None})
    return

  def test_str_update_row(self):
    cur = self.batch.con.cursor()
    for idx, start, end in self.iter_intervals():
      row = self.query.str_update_row(cur, {}, idx)
      self.assertDictEqual(row, {'foo': 'n/a'})
    return

class TestStaticSelectTableQuery(BuildBatch):
  def setUp(self):
    names = '@', 'foo'
    query = '''SELECT entryintervals.id, measurements.basename
               FROM entryintervals
                 JOIN entries ON
                      entries.id = entryintervals.entryid
                 JOIN measurements ON
                      measurements.id = entries.measurementid'''
    cur = self.batch.con.cursor()
    self.query = TableQuery.factory(names, query, cur)
    return

  def test_type(self):
    self.assertIsInstance(self.query, StaticSelectTableQuery)
    return

  def test_create_rows(self):
    rows = self.query._create_rows(self.batch.con.cursor())
    self.assertDictEqual(rows, {1: {'foo': 'bar.mdf'}, 2: {'foo': 'bar.mdf'}})
    return

  def test_update_row(self):
    row = self.query.update_row(self.batch.con.cursor(), {}, 1)
    self.assertDictEqual(row, {'foo': 'bar.mdf'})
    return

  def test_update_row_with_missing_id(self):
    row = self.query.update_row(self.batch.con.cursor(), {}, 3)
    self.assertDictEqual(row, {'foo': None})
    return

if __name__ == '__main__':
  main()
