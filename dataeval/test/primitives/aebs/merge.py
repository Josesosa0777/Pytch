from unittest import TestCase, main
from collections import OrderedDict

import numpy

from primitives.aebs import AebsPhases

class Test(TestCase):
  def setUp(self):
    self.phases = AebsPhases(numpy.arange(14),
      numpy.array([0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0], dtype=bool),
      numpy.array([0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0], dtype=bool),
      numpy.array([0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0], dtype=bool),
      numpy.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], dtype=bool),
      numpy.array([0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1], dtype=bool),
      numpy.array([0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1], dtype=bool))
    return

  def test_single_merge(self):
    jump, merge = self.phases.merge_phases(1)
    self.assertListEqual(jump, [[1], [3], [6], [10]])
    self.assertListEqual(merge, [(1, 2), (3, 4), (6, 7), (10, 11)])
    return

  def test_double_merge(self):
    jump, merge = self.phases.merge_phases(2)
    self.assertListEqual(jump, [[1], [3, 4], [6, 7], [10, 11]])
    self.assertListEqual(merge, [(1, 2), (3, 5), (6, 8), (10, 12)])
    return

  def test_triple_merge(self):
    jump, merge = self.phases.merge_phases(3)
    self.assertListEqual(jump, [[1], [3, 4], [6, 7, 8], [10, 11, 12]])
    self.assertListEqual(merge, [(1, 2), (3, 5), (6, 9), (10, 13)])
    return

  def test_all_merge(self):
    jump, merge = self.phases.merge_phases(4)
    self.assertListEqual(jump, [[1], [3, 4], [6, 7, 8], [10, 11, 12, 13]])
    self.assertListEqual(merge, [(1, 2), (3, 5), (6, 9), (10, 14)])
    return

main()
