import os
import unittest
import logging

from config.logger import Logger
from file_logger import TestFileLogger

class TestNoFileLogger(unittest.TestCase):
  def setUp(self):
    self.logger = Logger('', logging.INFO)
    return

  def test_no_log_files(self):
    self.logger.close()
    path = os.path.abspath(__file__)
    dir, file = os.path.split(path)
    logfiles = [filename for filename in os.listdir(dir)
                          if filename.startswith('log')
                             and filename.endswith('.txt')]
    self.assertEqual(logfiles, [])
    return

if __name__ == '__main__':
  unittest.main()

