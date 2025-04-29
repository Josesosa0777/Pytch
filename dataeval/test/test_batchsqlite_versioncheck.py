import os
import shutil
import unittest
import sqlite3

from measproc.batchsqlite import CreateParams,\
                                 _get_init_scrpit_name,\
                                 _get_user_version,\
                                 _init_db

batch_params = CreateParams('batch.db', 
                            'files',
                            {'foo': (False, ['bar', 'baz'])},
                            {'spam': ['egg', 'egg']},
                            ('good', 'bad'),
                            {'pyon': ['atomsk', 'naota']},
                            False)

class Test(unittest.TestCase):
  def test_with_correct_version(self):
    init = _get_init_scrpit_name()
    
    con = sqlite3.connect(batch_params.db_name)
    cur = con.cursor()
    _init_db(cur, init)
    con.commit()
    con.close()
    
    batch = batch_params() 
    batch.save()
    return

  def test_with_corrupt_version(self):
    init    = _get_init_scrpit_name()
    version = _get_user_version(init)
    
    corrupt_version = 100

    con = sqlite3.connect(batch_params.db_name)
    cur = con.cursor()
    _init_db(cur, init)
    cur.execute('PRAGMA user_version = %d' %corrupt_version)
    con.commit()
    con.close()
    
    self.assertRaisesRegexp(
      ValueError, 
      'Invalid user_version: parser \(%d\) does not handle %d. '
      'Please use --batch-update to bring database up-to-date.'
      %(version, corrupt_version),
      batch_params)
    return

  def tearDown(self): 
    os.remove(batch_params.db_name)
    if os.path.exists(batch_params.dir_name):
      shutil.rmtree(batch_params.dir_name)
    return

if __name__ == '__main__':
  unittest.main()
