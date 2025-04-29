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
    last_entries = [start for start, in
              batch.query('''SELECT * FROM last_entries''')]
    self.assertSetEqual(set(last_entries), set([
      u'7dde2591-52ac-11e3-807f-5491320a8711',
      u'7dcfcdb0-52ac-11e3-a41b-5491320a8711',
      u'7dc8c8cf-52ac-11e3-a0c2-5491320a8711',
      u'7dd4afb0-52ac-11e3-af3b-5491320a8711',
    ] ))
    return

if __name__ == '__main__':
  unittest.main(argv=sys.argv[:1], verbosity=args.v)
