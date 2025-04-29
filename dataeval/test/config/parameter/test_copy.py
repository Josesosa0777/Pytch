import unittest

from config.parameter import Params, GroupParams, TypeParams


class TestParams(unittest.TestCase):
  Params = Params
  def setUp(self):
    self.params = self.Params()
    return

  def test_copy(self):
    params = self.params.copy()
    self.assertIsInstance(params, self.Params)
    return

class TestGroupParams(TestParams):
  Params = GroupParams

class TestTypeParams(TestParams):
  Params = TypeParams

unittest.main()
