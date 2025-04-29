import unittest
import shutil
import time
import os

import numpy

from measproc.batchsqlite import get_ndarray_hash,\
                                 CreateParams as BatchCreateParams,\
                                 InitParams as BatchInitParams,\
                                 UploadParams as BatchUploadParams
from measproc.report2 import CreateParams as ReportCreateParams,\
                             IntervalAddParams, CreateQuantity, AddQuantity
from measproc.workspace import CreateParams as WorkspaceCreateParams


class Params:
  batches = []
  batch_create_params = []
  @classmethod
  def create_batch(cls, db_name, dir_name, labels, tags, results, quanames,
                   enable_update):
    params = BatchCreateParams(db_name, dir_name, labels, tags, results, 
                               quanames, enable_update)
    cls.batch_create_params.append(params)
    batch = params()
    cls.batches.append(batch)
    return batch

  batch_init_params = []
  @classmethod
  def init_batch(cls, batch, start, measurement, local, class_name, param, version):
    param = BatchInitParams(start, measurement, local, class_name, param, version)
    cls.batch_init_params.append(param)
    return param(batch)

  batch_upload_params = []
  entry_ids = []
  @classmethod
  def upload_entry_into_batch(cls, batch, entry, result, tags):
    param = BatchUploadParams(result, tags)
    cls.batch_upload_params.append(param)
    entryid =  param(batch, entry)
    cls.entry_ids.append(entryid)
    return entryid

  reports = []
  report_create_params = []
  @classmethod
  def create_report(cls, time, title, labels, comment):
    param = ReportCreateParams(time, title, labels, comment)
    cls.report_create_params.append(param)
    report = param()
    cls.reports.append(report)
    return report

  interval_add_params = []
  interval_indices = []
  @classmethod
  def add_interval_to_report(cls, report, interval, votegroup, vote, comment):
    param = IntervalAddParams(interval, votegroup, vote, comment)
    cls.interval_add_params.append(param)
    interval_id =  param(report)
    cls.interval_indices.append(interval_id)
    return interval_id

  workspaces = []
  workspace_create_params = []
  @classmethod
  def create_workspace(cls, title, dir_name):
    param = WorkspaceCreateParams(title, dir_name)
    cls.workspace_create_params.append(param)
    workspace = param()
    cls.workspaces.append(workspace)
    return workspace

  quantities = []
  quantity_create_params = []
  @classmethod
  def create_quantity(cls, time, title, names):
    param = CreateQuantity(time, title, names)
    cls.quantity_create_params.append(param)
    quantity = param()
    cls.quantities.append(quantity)
    return quantity

  quantity_add_params = []
  quantity_indices = []
  @classmethod
  def add_interval_to_quantity(cls, quantity, interval, groupname, valuename,
                               value):
    param = AddQuantity(interval, groupname, valuename, value)
    cls.quantity_add_params.append(param)
    intervalid = param(quantity)
    cls.quantity_indices.append(intervalid)
    return intervalid

class Build(Params):
  @classmethod
  def build(cls):
    # create the first batch
    batch = cls.create_batch('batch.db', 
                             'files',
                             {'foo': (False, ['bar', 'baz'])},
                             {'spam': ['egg', 'eggegg']},
                             ('good', 'bad'),
                             {'atomsk': ['pyon', 'tutu']},
                             False)
    cls.init_batch(batch,
                   time.localtime(),
                   'd:/measurement/2011-02-10_16-50-33_020.mdf', True,
                   'searchFoo.cSearch', 'foo="bar"', '0.1')
    
    # create the second batch
    batch = cls.create_batch('catch.db', 
                             'giles',
                             {'foo':  (False, ['bar', 'baz']),
                              'pyon': (True,  ['atomsk'])},
                             {'spam': ['egg',  'eggegg'],
                              'egg':  ['spam', 'spamspam'],
                              'nyam': ['nyamnyam']},
                             ('good', 'bad', 'ugly', 'nyam'),
                             {'atomsk': ['pyon', 'tutu'],
                              'naota': ['vespa', 'medical']},
                             False)
    cls.init_batch(batch,
                   time.localtime(1),
                   'd:/measurement/2011-02-10_16-50-22_021.mdf', False,
                   'searchGoo.cSearch', 'foo="car"', '0.1')

    # create report
    report = cls.create_report(numpy.arange(0, 600, 20e-3),
                               'foo is never bar',
                               cls.batch_create_params[0].labels,
                               'spam')
    cls.add_interval_to_report(report, 
                               (45, 889), 'foo', 'bar', 'spamspam')
    cls.add_interval_to_report(report, 
                               (54, 89), 'foo', 'baz', 'spamspam')
    
    # upload report into both batches
    cls.upload_entry_into_batch(cls.batches[0], report, 'good', ['egg'])
    cls.upload_entry_into_batch(cls.batches[1], report, 'bad',  ['eggegg'])

    # create report
    report = cls.create_report(numpy.arange(0, 500, 20e-3),
                               'goo is bar',
                               cls.batch_create_params[1].labels,
                               'egg')
    cls.add_interval_to_report(report, 
                               (55, 589), 'foo', 'baz', 'eggegg')
    cls.add_interval_to_report(report, 
                               (64, 89), 'pyon', 'atomsk', 'spamspam')
    
    # create workspace
    workspace = cls.create_workspace('nyam nyam', 
                                     cls.batch_create_params[1].dir_name)

    # create quantity
    quantity = cls.create_quantity(numpy.arange(0, 400, 15e-3), 'egg spam',
                                   cls.batch_create_params[0].quanames)
    cls.add_interval_to_quantity(quantity, ( 34,  89), 'atomsk', 'pyon', 17.6)
    cls.add_interval_to_quantity(quantity, (113, 234), 'atomsk', 'tutu', 43.2)

    # upload quantity into both batches
    cls.upload_entry_into_batch(cls.batches[0], quantity, 'good', ['eggegg'])
    cls.upload_entry_into_batch(cls.batches[1], quantity, 'good', ['egg'])

    # reinit second batch
    cls.init_batch(cls.batches[1],
                   time.localtime(2),
                   'd:/measurement/2011-02-9_16-53_022.mdf', False,
                   'searchHoo.cSearch', 'foo="dar"', '0.2')
    # upload report into the second batch
    cls.upload_entry_into_batch(cls.batches[1], report, 'ugly', ['spamspam'])

    # reinit second batch
    cls.init_batch(cls.batches[1],
                   time.localtime(3),
                   'd:/measurement/2011-02-9_16-53_023.mdf', False,
                   'searchJoo.cSearch', 'foo="far"', '0.2')
    # upload workspace into second batch
    cls.upload_entry_into_batch(cls.batches[1], workspace, 'nyam', ['nyamnyam'])

    # reinit second batch
    cls.init_batch(cls.batches[0],
                   time.localtime(4),
                   'd:/measurement/2011-02-9_16-53_024.mdf', False,
                   'searchKoo.cSearch', 'foo="gar"', '0.2')
    cls.upload_entry_into_batch(cls.batches[0], quantity, 'bad', ['eggegg'])
    return

  @classmethod
  def destroy(cls):
    while cls.batches:
      batch = cls.batches.pop()
      batch.save()
    while cls.batch_create_params:
      batch_create_params = cls.batch_create_params.pop()
      if os.path.exists(batch_create_params.db_name):
        os.remove(batch_create_params.db_name)
      if os.path.exists(batch_create_params.dir_name):
        shutil.rmtree(batch_create_params.dir_name)
    for trash in cls.batch_init_params,\
                 cls.batch_upload_params,\
                 cls.entry_ids,\
                 cls.reports,\
                 cls.report_create_params,\
                 cls.interval_add_params,\
                 cls.interval_indices,\
                 cls.quantities,\
                 cls.quantity_create_params,\
                 cls.quantity_add_params,\
                 cls.quantity_indices,\
                 cls.workspaces,\
                 cls.workspace_create_params:
      while trash: trash.pop()
    return 


class TestMerge(unittest.TestCase, Build):
  @classmethod
  def setUpClass(cls):
    cls.build()
    # merge the second batch into the first
    cls.batches[0].merge(cls.batches[1])
    return

  @classmethod
  def tearDownClass(cls):
    cls.destroy()
    return

  def _test_by_measurement(self, batch, measurement, entryids):
    basename = os.path.basename(measurement)
    _entryids = set(batch.filter(measurement=basename))
    self.assertSetEqual(entryids, _entryids)
    return

  def test_by_measurement(self):
    for batch_idx, init_idx, entry_ids in [
       [0,         0,        [0, 2]],
       [0,         1,        [1, 3]],
       [0,         2,        [4]],
       [0,         3,        [5]],
       [0,         4,        [6]],
       [1,         1,        [1, 3]],
       [1,         2,        [4]],
       [1,         3,        [5]],
      ]:
      batch = self.batches[batch_idx]
      measurement = self.batch_init_params[init_idx].measurement
      entryids =set([self.entry_ids[entry_idx] for entry_idx in entry_ids])
      self._test_by_measurement(batch, measurement, entryids)
    return

  def _test_by_start(self, batch, start, entryids):
    _entryids = set(batch.filter(start=start))
    self.assertSetEqual(entryids, _entryids)
    return
  
  def test_batch_by_start(self):
    for batch_idx, init_idx, entry_ids in [
       [0,         0,        [0, 2]],
       [0,         1,        [1, 3]],
       [0,         2,        [4]],
       [0,         3,        [5]],
       [0,         4,        [6]],
       [1,         1,        [1, 3]],
       [1,         2,        [4]],
       [1,         3,        [5]],
      ]:
      batch = self.batches[batch_idx]
      start = self.batch_init_params[init_idx].start
      entryids = set([self.entry_ids[entryid] for entryid in entry_ids])
      self._test_by_start(batch, start, entryids)
    return

  def _test_by_type(self, batch, type, entryids):
    _entryids = set(batch.filter(type=type))
    self.assertSetEqual(entryids, _entryids)
    return

  def test_by_type(self):
    for batch_idx, type,                     entryids in [
       [0,         'measproc.Report',        [0, 1, 2, 3, 4, 6]],
       [1,         'measproc.Report',        [1, 3, 4]],
       [1,         'measproc.FileWorkSpace', [5]],
      ]:
      batch = self.batches[batch_idx]
      entryids = set([self.entry_ids[entryid] for entryid in entryids])
      self._test_by_type(batch, type, entryids)
    return

  def _test_by_result(self, batch, result, entryids): 
    _entryids = set(batch.filter(result=result))
    self.assertSetEqual(entryids, _entryids)
    return

  def test_batch_by_result(self):
    for batch_idx, upload_idx, entry_ids in [
       [0,         0,          [0, 2, 3]],
       [0,         1,          [1, 6]],
       [0,         2,          [0, 2, 3]],
       [0,         3,          [0, 2, 3]],
       [0,         4,          [4]],
       [0,         5,          [5]],
       [1,         0,          [3]],
       [1,         1,          [1]],
       [1,         2,          [3]],
       [1,         3,          [3]],
       [1,         4,          [4]],
       [1,         5,          [5]],
      ]:
      batch = self.batches[batch_idx]
      result = self.batch_upload_params[upload_idx].result
      entryids = set([self.entry_ids[entryid] for entryid in entry_ids])
      self._test_by_result(batch, result, entryids)
    return

  def _test_by_class_name(self, batch, class_name, entryids):
    _entryids = set(batch.filter(class_name=class_name))
    self.assertSetEqual(entryids, _entryids)
    return

  def test_batch_by_class_name(self):
    for batch_idx, init_idx, entry_ids in [
       [0,         0,        [0, 2]],
       [0,         1,        [1, 3]],
       [0,         2,        [4]],
       [0,         3,        [5]],
       [0,         4,        [6]],
       [1,         0,        []],
       [1,         1,        [1, 3]],
       [1,         2,        [4]],
       [1,         3,        [5]],
       [1,         4,        []],
      ]:
      batch = self.batches[batch_idx]
      class_name = self.batch_init_params[init_idx].class_name
      entryids = set([self.entry_ids[entryid] for entryid in entry_ids])
      self._test_by_class_name(batch, class_name, entryids)
    return

  def _test_by_param(self, batch, param, entryids):
    _entryids = set(batch.filter(param=param))
    self.assertSetEqual(entryids, _entryids)
    return

  def test_batch_by_param(self):
    for batch_idx, init_idx, entry_ids in [
       [0,         0,        [0, 2]],
       [0,         1,        [1, 3]],
       [0,         2,        [4]],
       [0,         3,        [5]],
       [0,         4,        [6]],
       [1,         0,        []],
       [1,         1,        [1, 3]],
       [1,         2,        [4]],
       [1,         3,        [5]],
       [1,         4,        []],
      ]:
      batch = self.batches[batch_idx]
      param = self.batch_init_params[init_idx].param
      entryids = set([self.entry_ids[entryid] for entryid in entry_ids])
      self._test_by_param(batch, param, entryids)
    return

  def _test_by_tag(self, batch, tag, entryids):
    _entryids = set(batch.filter(tag=tag))
    self.assertSetEqual(entryids, _entryids)
    return

  def test_batch_by_tag(self):
    for batch_idx, upload_idx, entry_ids in [
       [0,         0,          [0, 3]],
       [0,         1,          [1, 2, 6]],
       [0,         2,          [1, 2, 6]],
       [0,         3,          [0, 3]],
       [0,         4,          [4]],
       [0,         5,          [5]],
       [0,         6,          [1, 2, 6]],
       [1,         0,          [3]],
       [1,         1,          [1]],
       [1,         2,          [1]],
       [1,         3,          [3]],
       [1,         4,          [4]],
       [1,         5,          [5]],
       [1,         6,          [1]],
      ]:
      batch = self.batches[batch_idx]
      tag = self.batch_upload_params[upload_idx].tags[0]
      entryids = set([self.entry_ids[entry_idx] for entry_idx in entry_ids])
      self._test_by_tag(batch, tag, entryids)
    return

  def _test_labels(self, batch, entryid, position, labels):
    _labels = batch.query("""
      SELECT labels.name FROM labels
       JOIN  interval2label ON
             interval2label.labelid=labels.id
       JOIN  entryintervals ON
             entryintervals.id=interval2label.entry_intervalid
       WHERE entryintervals.entryid=?
         AND entryintervals.position=?""", entryid, position)
    _labels = set([label for label, in _labels])
    self.assertSetEqual(labels, _labels)
    return

  def test_labels(self):
    for batch_idx, entry_idx, interval_idx, interval_add_idx in [
       [0,         0,         0,            0],
       [0,         0,         1,            1],
       [0,         1,         0,            0],
       [0,         1,         1,            1],
       [0,         4,         2,            2],
       [0,         4,         3,            3],
       [1,         1,         0,            0],
       [1,         1,         1,            1],
       [1,         4,         2,            2],
       [1,         4,         3,            3],
      ]:
      batch = self.batches[batch_idx]
      entryid = self.entry_ids[entry_idx]
      position = self.interval_indices[interval_idx]
      labels = {self.interval_add_params[interval_add_idx].vote}
      self._test_labels(batch, entryid, position, labels)
    return

  def test_quantity(self):
    for batch_idx, entry_idx, qua_idx, qua_add_idx in [
       [0,         2,         0,       0],
       [0,         2,         1,       1],
       [0,         3,         0,       0],
       [0,         3,         1,       1],
       [0,         6,         0,       0],
       [0,         6,         1,       1],
       [1,         3,         0,       0],
       [1,         3,         1,       1],
      ]:
      batch = self.batches[batch_idx]
      entryid = self.entry_ids[entry_idx]
      position = self.quantity_indices[qua_idx]
      qua_add_param = self.quantity_add_params[qua_add_idx]
      quantities = {qua_add_param.valuename: qua_add_param.value}
      self._test_quantity(batch, entryid, position, quantities)
    return

  def _test_quantity(self, batch, entryid, position, quantities):
    _quantities = batch.query("""
      SELECT quanames.name, quantities.value FROM quanames
       JOIN  quantities ON
             quantities.nameid = quanames.id
       JOIN  entryintervals ON
             entryintervals.id = quantities.entry_intervalid
       WHERE entryintervals.entryid = ?
         AND entryintervals.position = ?""", entryid, position)
    _quantities = dict(_quantities)
    self.assertDictEqual(quantities, _quantities)
    return

  def _test_entry_domain(self, batch, entryid, files):
    _files = batch.query("""SELECT files.name FROM files 
                              JOIN entry2domain ON
                                   entry2domain.fileid = files.id
                            WHERE  entry2domain.entryid = ?""", entryid)
    _files = set([name for name, in _files])
    self.assertSetEqual(files, _files)
    return

  def test_entry_domain(self):
    for batch_idx, entry_idx, report_idx in [
       [0,         0,         0],
       [0,         1,         0],
       [0,         4,         1],
       [1,         1,         0],
       [1,         4,         1],
      ]:
      batch = self.batches[batch_idx]
      entryid = self.entry_ids[entry_idx]
      name = get_ndarray_hash(self.report_create_params[report_idx].time)+'.npy'
      files = {name}
      self._test_entry_domain(batch, entryid, files)
    for batch_idx, entry_idx, quantity_idx in [
       [0,         2,         0],
       [0,         3,         0],
       [0,         6,         0],
       [1,         3,         0],
      ]:
      batch = self.batches[batch_idx]
      entryid = self.entry_ids[entry_idx]
      time = self.quantity_create_params[quantity_idx].time
      name = get_ndarray_hash(time)+'.npy'
      files = {name}
      self._test_entry_domain(batch, entryid, files)
    return

  def _test_entry_files(self, batch, entryid, files):
    _files = batch.query("""
                         SELECT files.name FROM files
                           JOIN entry2file ON
                                entry2file.fileid = files.id
                         WHERE  entry2file.entryid = ?
                         """, entryid)
    _files = set([name for name, in _files])
    self.assertSetEqual(files, _files)
    return

  def test_quanames(self):
    batch = self.batches[0]
    self.assertDictEqual(batch.get_quanamegroups('atomsk', 'naota'),
                         self.batch_create_params[1].quanames)
    return

  def test_entry_file(self):
    batch = self.batches[0]
    entryid = self.entry_ids[5]
    entry = self.workspaces[0]
    title = {entry.getTitle(WithoutExt=False)}
    self._test_entry_files(batch, entryid, title)
    return

  def test_files_existence(self):
    batch = self.batches[0]
    dir_name = self.batch_create_params[0].dir_name
    files = batch.query('SELECT name from files')
    for name, in files:
      self.assertTrue(os.path.exists(os.path.join(dir_name, name)))
  pass


class TestMergeTwice(unittest.TestCase, Build):
  @classmethod
  def setUpClass(cls):
    cls.build()
    return

  @classmethod
  def tearDownClass(cls):
    cls.destroy()
    return

  def test_merge_twice(self):
    self.batches[0].merge(self.batches[1])
    self.batches[0].merge(self.batches[1])
    return
  
if __name__ == '__main__':
  unittest.main()
