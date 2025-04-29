import os
import shutil
import unittest

from measparser.BackupParser import BackupParser
from measparser.Hdf5Parser import cHdf5Parser, init, setHeader

class TestBackupVersionChange(unittest.TestCase):
  def setUp(self):
    meas = 'bar'
    self.npydir = os.path.join('foo', meas)
    version = 'Backup 0.1.0'
    __version__  = BackupParser.__version__
    BackupParser.__version__ = version
    parser = BackupParser(self.npydir, meas, version, version, '')
    parser.save()
    BackupParser.__version__ = __version__
    return

  def tearDown(self):
    shutil.rmtree(os.path.dirname(self.npydir))
    return

  def test(self):
    parser = BackupParser.fromDir(self.npydir)
    self.assertEqual(open(os.path.join(self.npydir, 'Version')).read(),
                     BackupParser.getVersion())
    parser.save()
    return

class TestParserVersionCheck(unittest.TestCase):
  def setUp(self):
    self.meas = 'foo.h5'
    self.backup = 'bar'

    h5, devs, times = init(self.meas)
    setHeader(h5, 0, 'egg')
    h5.close()

    backup = BackupParser.fromFile(self.meas, self.backup)
    backup.save()
    return

  def tearDown(self):
    os.remove(self.meas)
    shutil.rmtree(self.backup)
    return

  def test(self):
    cHdf5Parser.__version__ = 'early'
    backup = BackupParser.fromFile(self.meas, self.backup)
    parser_version = open(os.path.join(self.backup,
                                       self.meas,
                                       'ParserVersion')).read()
    self.assertEqual(parser_version, 'cHdf5Parser early')
    backup.save()
    return

if __name__ == '__main__':
  unittest.main()
