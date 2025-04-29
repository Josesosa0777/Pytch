import os
import sys
import shutil
import unittest
import argparse

from measproc.batchsqlite import CreateParams

parser = argparse.ArgumentParser()
parser.add_argument('-b', help='batch file', default='batch.db')
parser.add_argument('--repdir', help='batch attachement directory', default='files')
parser.add_argument('-v', action='count', default=0)
args = parser.parse_args()

class Test(unittest.TestCase):
  @unittest.skipUnless(os.path.isfile(args.b), 'No batch file')
  @unittest.skipUnless(os.path.isdir(args.repdir), 'No attachement directory')
  def setUp(self):
    self.dirname = args.repdir
    self.dbname = args.b+'.bak'
    shutil.copyfile(args.b, self.dbname)
    return

  def tearDown(self):
    os.remove(self.dbname)
    return

  def test_check(self):
    params = CreateParams(self.dbname, self.dirname, {}, {}, {}, {}, False)
    with self.assertRaises(ValueError):
      batch = params() 
    return

  def test_update(self):
    params = CreateParams(self.dbname, self.dirname, {}, {}, {}, {}, True)
    batch = params()
    starts = [start for start, in 
              batch.query('''
                          SELECT start FROM measurements
                          WHERE basename != "dummy"
                          ORDER BY start''')]
    self.assertListEqual(starts, [
      u'2013-03-20 15:03:34', u'2013-03-20 15:10:53', u'2013-03-20 15:12:35',
      u'2013-03-20 15:19:12', u'2013-03-20 15:28:24', u'2013-03-20 15:33:14',
      u'2013-03-20 15:47:42', u'2013-03-20 15:53:29', u'2013-03-20 15:58:10',
    ] )
    lasts = [last 
             for last, in batch.query('SELECT end_is_last FROM entryintervals')]
    self.assertListEqual(lasts, [0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0,
                                 0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1])
    return

if __name__ == '__main__':
  unittest.main(argv=sys.argv[:1], verbosity=args.v)
