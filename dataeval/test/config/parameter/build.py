import unittest

from config.parameter import GroupParams
from datavis.GroupParam import cGroupParam

groups = GroupParams({
  'fillFoo': {
    'group-foo':  cGroupParam({'foo', 'bar'}, '1', False, False),
    'group-pyon': cGroupParam({'pyon'},       '2', False, False),
  },
  'fillSpam': {
    'group-spam': cGroupParam({'spam', 'egg'}, '2', False, False),
    'group-pyon': cGroupParam({'atomsk'},      '3', False, False),
  },
})



class TestBuildByType(unittest.TestCase):
  def test_build_by_type(self):
    legend_values = {
      'foo':    1,
      'bar':    2,
      'spam':   3,
      'egg':    4,
      'pyon':   5,
      'atomsk': 6,
    }
    legends, missing = groups.build_type_params(legend_values)
    self.assertDictEqual(legends, {
      'fillFoo': {'foo': 1, 'bar': 2, 'pyon': 5},
      'fillSpam': {'spam': 3, 'egg': 4, 'atomsk': 6},
    })
    self.assertSetEqual(missing, set())
    return

  def test_missing_type(self):
    legend_values = {
      'bar':    2,
      'spam':   3,
      'egg':    4,
      'pyon':   5,
      'atomsk': 6,
    }
    legends, missing = groups.build_type_params(legend_values)
    self.assertDictEqual(legends, {
      'fillFoo': {'bar': 2, 'pyon': 5},
      'fillSpam': {'spam': 3, 'egg': 4, 'atomsk': 6},
    })
    self.assertSetEqual(missing, {'foo'})
    return

class testBuildByGroupName(unittest.TestCase):
  def test_build_by_groupname(self):
    viewangle_values = {
      'group-foo':  1,
      'group-pyon': 2,
      'group-spam': 3,
    }
    viewangles, missing = groups.build_groupname_params(viewangle_values)
    self.assertDictEqual(viewangles, {
      'fillFoo': {'group-foo': 1, 'group-pyon': 2},
      'fillSpam': {'group-spam': 3, 'group-pyon': 2},
    })
    self.assertSetEqual(missing, set())
    return

  def test_missing_groupname(self):
    viewangle_values = {
      'group-foo':  1,
      'group-spam': 3,
    }
    viewangles, missing = groups.build_groupname_params(viewangle_values)
    self.assertDictEqual(viewangles, {
      'fillFoo': {'group-foo': 1},
      'fillSpam': {'group-spam': 3},
    })
    self.assertSetEqual(missing, {'group-pyon'})
    return
unittest.main()

