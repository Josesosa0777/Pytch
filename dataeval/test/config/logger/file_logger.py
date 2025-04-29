import os
import logging
import unittest
from config.logger import Logger

class TestFileLogger(unittest.TestCase):
  def setUp(self):
    path = os.path.abspath(__file__)
    self.dir = os.path.dirname(path)
    self.create_logger()
    self.msg_foo = 'Foo'
    self.logger.log(self.msg_foo, 20)
    self.msg_bar = 'Bar'
    self.logger.log(self.msg_bar, 50)
    logfiles = [filename for filename in os.listdir(self.dir)
                            if filename.endswith('.log')]
    self.assertEqual(len(logfiles), 1)
    logfile, = logfiles
    logfile = os.path.join(self.dir, logfile)
    self.file = open(logfile, 'r')
    self.file_content = self.file.read()
    return

  def create_logger(self):
    return

  def tearDown(self):
    self.file.close()
    self.logger.close()
    # Handler-removal is not advised, this is only for testing : 
    self.logger.handlers = []
    logfiles = [filename for filename in os.listdir(self.dir)
                            if filename.endswith('.log')]
    for file in logfiles:
      file = os.path.join(self.dir, file)
      os.remove(file)
    return

class TestFileLoggerLowLevel(TestFileLogger):
  def create_logger(self):
    log_path = os.path.join(self.dir, 'dataeval_%(Y)s-%(m)s-%(d)s_%(H)s-%(M)s-%(S)s_%(cnt)d.log')
    logging.getLogger().handlers = []
    self.logger = Logger(log_path, logging.DEBUG)
    return

  def test_log_files(self):
    logfiles = [filename for filename in os.listdir(self.dir)
                            if filename.endswith('.log')]
    self.assertNotEqual(logfiles, [])
    return

  def test_log(self):
    self.assertIn(self.msg_foo, self.file_content)
    self.assertIn(self.msg_bar, self.file_content)
    return


class TestFileLoggerHighLevel(TestFileLogger):
  def create_logger(self):
    log_path = os.path.join(self.dir, 'dataeval_%(Y)s-%(m)s-%(d)s_%(H)s-%(M)s-%(S)s_%(cnt)d.log')
    logging.getLogger().handlers = []
    self.logger = Logger(log_path, logging.ERROR,
                          file_logger_level=logging.ERROR)
    return

  def test_log(self):
    self.assertNotIn(self.msg_foo, self.file_content)
    self.assertIn(self.msg_bar, self.file_content)
    return

if __name__ == '__main__':
  unittest.main()