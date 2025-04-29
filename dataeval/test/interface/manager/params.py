from datavis import pyglet_workaround  # necessary as early as possible (#164)

import unittest

import interface
from interface.manager import Manager
from config.parameter import GroupParams, TypeParams
from datavis.GroupParam import cGroupParam

grouptypes = {
  'egg':  {'foo', 'bar', 'baz'},
  'spam': {'bar'},
}

groups = {
  'egg': GroupParams({
    'fillFoo-bar': {
      'group-bar': cGroupParam({'foo'}, '1', False, False),
    },
    'fillFoo-baz': {
      'group-baz': cGroupParam({'bar', 'baz'}, '2', False, False),
    },
  }),
  'spam': GroupParams({
    'fillPyon': {
      'group-pyon': cGroupParam({'bar'}, '3', False, False),
    },
  }),
}


view_angle_values = {
  'group-bar':  1,
  'group-baz':  2,
  'group-pyon': 3,
}

view_angles = {}
for prj_name, groups_ in groups.iteritems():
  view_angles_, missing = groups_.build_groupname_params(view_angle_values)
  view_angles.update(view_angles_)

legend_values = {
  'foo':  8,
  'bar':  9,
  'baz': 10,
}
legends = {}
for prj_name, groups_ in groups.iteritems():
  legends[prj_name], missing = groups_.build_type_params(legend_values)


shape_values = {
  'foo': 11,
  'bar': 12,
  'baz': 14,
}
shape_legends = {}
for prj_name, groups_ in groups.iteritems():
  shape_legends[prj_name], missing = groups_.build_type_params(shape_values)


labels = {
  'foo': (False, ['bar', 'baz']),
}
tags = {
  'spam': ['egg', 'eggegg'],
}
quanames = {
  'tarack': ['sugar', 'hanyas'],
}


class BuildGroupTypes(unittest.TestCase):
  def setUp(self):
    self.status_names = {'fillPyon', 'fillFoo-bar'}
    self.manager = Manager()
    self.types = dict()
    for prj_name, grouptypes_ in grouptypes.iteritems():
      self.manager.grouptypes.add_types(prj_name, grouptypes_)
      for type_name in grouptypes_:
        name = prj_name, type_name
        self.types[name] = self.manager.grouptypes.get_type(prj_name, type_name)
    return

  def tearDown(self):
    self.manager.close()
    return

class TestViewAngles(BuildGroupTypes):
  def setUp(self):
    BuildGroupTypes.setUp(self)
    self.manager.set_view_angles(view_angles)
    return

  def test_view_angles(self):
    self.assertDictEqual(self.manager._view_angles, view_angles)
    return

  def test_select(self):
    self.manager.select_params(self.status_names)
    selected = {
      'group-pyon': 3,
      'group-bar':  1,
    }
    self.assertDictEqual(self.manager.view_angles, selected)
    self.manager.reload_interface()
    self.assertDictEqual(interface.ViewAngles, selected)
    return
    
class TestLegends(BuildGroupTypes):
  def setUp(self):
    BuildGroupTypes.setUp(self)
    for prj_name, legends_ in legends.iteritems():
      self.manager.set_legends(prj_name, legends_)
    return

  def test_legends(self):
    self.assertDictEqual(self.manager._legends, {
      'fillFoo-bar': {self.types[('egg',  'foo')]: 8},
      'fillFoo-baz': {self.types[('egg',  'bar')]: 9,
                      self.types[('egg',  'baz')]: 10},
      'fillPyon':    {self.types[('spam', 'bar')]: 9},
    })
    return
  
  def test_select(self):
    self.manager.select_params(self.status_names)
    selected = {
      self.types[('egg',  'foo')]: 8,
      self.types[('spam', 'bar')]: 9,
    }
    self.assertDictEqual(self.manager.legends, selected)
    self.manager.reload_interface()
    self.assertDictEqual(interface.Legends, selected)
    return

class TestShapeLegends(BuildGroupTypes):
  def setUp(self):
    BuildGroupTypes.setUp(self)
    for prj_name, shape_legends_ in shape_legends.iteritems():
      self.manager.set_shape_legends(prj_name, shape_legends_)
    return

  def test_shape_legends(self):
    self.assertDictEqual(self.manager._shape_legends, {
      'fillFoo-bar': {self.types[('egg',  'foo')]: 11},
      'fillFoo-baz': {self.types[('egg',  'bar')]: 12,
                      self.types[('egg',  'baz')]: 14},
      'fillPyon':    {self.types[('spam', 'bar')]: 12},
    })
    return
  
  def test_select(self):
    self.manager.select_params(self.status_names)
    selected = {
      self.types[('egg',  'foo')]: 11,
      self.types[('spam', 'bar')]: 12,
    }
    self.assertDictEqual(self.manager.shape_legends, selected)
    self.manager.reload_interface()
    self.assertDictEqual(interface.ShapeLegends, selected)
    return

class TestGroups(BuildGroupTypes):
  def setUp(self):
    BuildGroupTypes.setUp(self)
    for prj_name, groups_ in groups.iteritems():
      self.manager.set_groups(prj_name, groups_)
    return

  def test_groups(self):
    self.assertDictEqual(self.manager._groups, {
      'fillFoo-bar': {
        'group-bar': cGroupParam({self.types[('egg',  'foo')]}, '1', False, False),
      },
      'fillFoo-baz': {
        'group-baz': cGroupParam({self.types[('egg',  'bar')],
                                  self.types[('egg',  'baz')]}, '2', False, False),
      },
      'fillPyon': {
        'group-pyon':cGroupParam({self.types[('spam', 'bar')]}, '3', False, False),
      },
    })
    return
  
  def test_select(self):
    self.manager.select_params(self.status_names)
    selected = {
      'group-bar': cGroupParam({self.types[('egg',  'foo')]}, '1', False, False),
      'group-pyon':cGroupParam({self.types[('spam', 'bar')]}, '3', False, False),
    }
    self.assertDictEqual(self.manager.groups, selected)
    self.manager.reload_interface()
    self.assertDictEqual(interface.Groups, selected)
    return

unittest.main()

