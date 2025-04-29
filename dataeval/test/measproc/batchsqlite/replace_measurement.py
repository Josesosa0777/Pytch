import os
import shutil
import unittest
import tempfile

from measproc.batchsqlite import Batch

meas_path = r'c:\KBData'

class TestCase(unittest.TestCase):
  @unittest.skipUnless(os.path.isdir(meas_path),
                       '%s does not exists' %meas_path)
  @classmethod
  def setUpClass(cls):
    cls.meas_path = tempfile.mkdtemp(dir=meas_path)
    cls.db_dir = 'files'
    cls.db_name = 'batch.db'
    
    cls.server = r'\\server'
    cls.origins = [os.path.join(cls.server, m) for m in 'foo', 'bar', 'baz']
    cls.locals = cls.create_files('spam', 'egg')

    cls.batch = Batch(cls.db_name, cls.db_dir, {}, {}, [], {})
    
    dummy_dir = r'x:\foobar'
    for name in cls.locals:
      basename = os.path.basename(name)
      dummy_name = os.path.join(dummy_dir, basename)
      cls.batch.set_measurement(dummy_name, True)
    
    for name in cls.origins:
      cls.batch.set_measurement(name, False)

    cls.batch.repl_meas(cls.meas_path)
    return

  @classmethod
  def create_files(cls, *names):
    full_names = []
    for name in names:
      full_name = os.path.join(cls.meas_path, name)
      full_names.append(full_name)
      fp = open(full_name, 'w')
      fp.close()
    return full_names

  @classmethod
  def tearDownClass(cls):
    cls.batch.save()
    for dirname in cls.meas_path, cls.db_dir:
      shutil.rmtree(dirname)
    os.remove(cls.db_name)
    return

  def test_repl_meas(self):
    dirnames = [os.path.dirname(name)
                for name, in self.batch.query('SELECT local FROM measurements '
                                              'WHERE local is not NULL')]
    self.assertSetEqual(set(dirnames), {self.meas_path})
    return

  def test_origins_are_untouched(self):
    dirnames = [os.path.dirname(name)
                for name, in self.batch.query('SELECT origin FROM measurements '
                                              'WHERE local is NULL')]
    self.assertSetEqual(set(dirnames), {self.server})
    return
  
if __name__ == '__main__':
  unittest.main()

