from aebs.fill import fill_flr20_raw_tracks, fill_flr20_acc_track
from test_fill_flr20_flc20_raw import parse_arguments, modules, TestFillResult
from test_fill_flr20_aeb_track import TestFillFlr20VirtualTrack


class TestFillFlr20AccTrack(TestFillResult, TestFillFlr20VirtualTrack):
  test_modules = { fill_flr20_acc_track : modules[fill_flr20_raw_tracks] }

  @classmethod
  def setUpClass(cls):
    super(TestFillFlr20AccTrack, cls).setUpClass()
    cls.o = cls.results[fill_flr20_acc_track]
    return


if __name__ == '__main__':
  import sys
  import unittest

  args = parse_arguments()
  TestFillFlr20AccTrack.args = args
  unittest.main(argv=[sys.argv[0]], verbosity=args.v)
