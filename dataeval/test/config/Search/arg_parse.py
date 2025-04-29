from datavis import pyglet_workaround  # necessary as early as possible (#164)

import os
import glob
import unittest
import argparse

from config.helper import procConfigFile 
from config.Config import Config

measpath = [os.path.abspath(d) 
            for d in os.getenv('measpath', '').split(os.path.pathsep)]
wildcard = '*.MF4'

measurements = set()
for d in measpath:
  measurements.update( glob.glob( os.path.join(d, wildcard) ) )


class Build:
  argv = []
  def setUp(self):
    parser = Config.addArguments( argparse.ArgumentParser() )
    args = parser.parse_args(self.argv)
    name = procConfigFile('search', args)
    self.config = Config(name)
    self.config.procArgs(args)
    return

argv = ['-w', wildcard]
for directory in measpath:
  argv.append('--scan')
  argv.append(directory)

class BuildScan(Build):
  argv = argv
  @unittest.skipUnless(all([os.path.isdir(d) for d in measpath]), 
                       'Something from %s is missing' %measpath)
  def setUp(self):
    Build.setUp(self)
    return
    
class TestScan(BuildScan, unittest.TestCase):
  def test(self):
    self.assertSetEqual(self.config.Measurements, measurements)
    return


measurements_rm = measurements.copy()

argv_rm = argv[:]
argv_rm.append('--rm')
argv_rm.append(measurements_rm.pop())

class BuildScanRm(Build):
  argv = argv_rm

class TestScanRm(BuildScanRm, unittest.TestCase):
  def test(self):
    self.assertSetEqual(self.config.Measurements, measurements_rm)
    return


if __name__ == '__main__':
  unittest.main()

