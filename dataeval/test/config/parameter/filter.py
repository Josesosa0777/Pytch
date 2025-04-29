import unittest

from interface.grouptypes import GroupTypes
from config.parameter import GroupParams
from datavis.GroupParam import cGroupParam

prj_name = 'pyon'
grouptypes = {'foo', 'bar', 'spam', 'egg', 'pyon', 'atomsk'}

groups = GroupParams({
  'fillFoo': {
    'group-foo': cGroupParam({'foo', 'bar'}, '1', False, False),
    'group-pyon':cGroupParam({'pyon'},       '2', False, False),
  },
  'fillSpam': {
    'group-spam': cGroupParam({'spam', 'egg'}, '2', False, False),
    'group-pyon': cGroupParam({'atomsk'},      '3', False, False),
  },
})

legend_values = {
  'foo':    0,
  'bar':    1,
  'spam':   2,
  'egg':    3,
  'pyon':   4,
  'atomsk': 5,
}
legends, missing = groups.build_type_params(legend_values)

shape_values = {
  'foo':    10,
  'bar':    11,
  'spam':   12,
  'egg':    13,
  'pyon':   14,
  'atomsk': 15,
}
shapes, missing = groups.build_type_params(shape_values)

view_angle_values = {
  'group-foo':  20,
  'group-pyon': 21,
  'group-spam': 22,
}
view_angles, missing = groups.build_groupname_params(view_angle_values)

class TestGroupTypes(unittest.TestCase):
  def setUp(self):
    self.grouptypes = GroupTypes()
    self.grouptypes.add_types(prj_name, grouptypes)
    self.statusnames = {'fillFoo', 'fillSpam'}
    return

  def test_filter_view_angels(self):
    filtered = view_angles.filter(self.statusnames)
    self.assertDictEqual(filtered, view_angle_values)
    return

  def test_view_angle_with_missing_status(self):
    self.statusnames.remove('fillSpam')
    filtered = view_angles.filter(self.statusnames)
    self.assertDictEqual(filtered, {
      'group-foo':  20,
      'group-pyon': 21,
    })
    return

  def test_filter_legends(self):
    activated = legends.activate(self.grouptypes, prj_name)
    filtered = activated.filter(self.statusnames)
    for type_name, value in legend_values.iteritems():
      type_number = self.grouptypes.get_type(prj_name, type_name)
      self.assertEqual(legend_values[type_name], filtered[type_number])
    return

  def test_legends_with_missing_status(self):
    self.statusnames.remove('fillSpam')
    activated = legends.activate(self.grouptypes, prj_name)
    filtered = activated.filter(self.statusnames)
    missing = {'spam', 'egg', 'atomsk'}
    for type_name, value in legend_values.iteritems():
      if type_name in missing: continue
      type_number = self.grouptypes.get_type(prj_name, type_name)
      self.assertEqual(legend_values[type_name], filtered[type_number])
    for type_name in missing:
      type_number = self.grouptypes.get_type(prj_name, type_name)
      self.assertNotIn(type_number, filtered)
    return

  def test_set_shapes(self):
    activated = shapes.activate(self.grouptypes, prj_name)
    filtered = activated.filter(self.statusnames)
    for type_name, value in shape_values.iteritems():
      type_number = self.grouptypes.get_type(prj_name, type_name)
      self.assertEqual(shape_values[type_name], filtered[type_number])
    return

  def test_shapes_with_missing_status(self):
    self.statusnames.remove('fillSpam')
    activated = shapes.activate(self.grouptypes, prj_name)
    filtered = activated.filter(self.statusnames)
    missing = {'spam', 'egg', 'atomsk'}
    for type_name, value in shape_values.iteritems():
      if type_name in missing: continue
      type_number = self.grouptypes.get_type(prj_name, type_name)
      self.assertEqual(shape_values[type_name], filtered[type_number])
    for type_name in missing:
      type_number = self.grouptypes.get_type(prj_name, type_name)
      self.assertNotIn(type_number, filtered)
    return

  def test_set_groups(self):
    activated = groups.activate(self.grouptypes, prj_name)
    filtered = activated.filter(self.statusnames)
    gtps = self.grouptypes
    gps = {
    'group-foo': cGroupParam(set(gtps.get_types(prj_name, ('foo', 'bar'))),
                             '1', False, False),
    'group-spam': cGroupParam(set(gtps.get_types(prj_name, {'spam', 'egg'})),
                              '2', False, False),
    'group-pyon': cGroupParam(set(gtps.get_types(prj_name, {'atomsk', 'pyon'})),
                              '2', False, False),
    }
    self._test_set_groups(gps, filtered)
    return

  def _test_set_groups(self, gps, filtered):
    for group_name, group in gps.iteritems():
      self.assertIn(group_name, filtered)
      self.assertEqual(group, filtered[group_name])
    return
  
  def test_groups_with_missing_status(self):
    self.statusnames.remove('fillFoo')
    activated = groups.activate(self.grouptypes, prj_name)
    filtered = activated.filter(self.statusnames)
    gtps = self.grouptypes
    gps = {
    'group-spam': cGroupParam(set(gtps.get_types(prj_name, {'spam', 'egg'})),
                              '2', False, False),
    'group-pyon': cGroupParam({gtps.get_type(prj_name, 'atomsk')},
                              '2', False, False),
    }
    self._test_set_groups(gps, filtered)
    return

unittest.main()
