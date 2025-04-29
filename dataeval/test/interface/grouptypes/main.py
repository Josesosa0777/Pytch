import unittest

from interface.grouptypes import GroupTypes

class Test(unittest.TestCase):
  def setUp(self):
    self.grouptypes = GroupTypes()
    self.types = {'bar', 'baz', 'spam'}
    self.prj_name = 'foo'
    self.grouptypes.add_types(self.prj_name, self.types)
    return

  def test_get_type(self):
    type_ids = [self.grouptypes.get_type(self.prj_name, type_name)
                for type_name in self.types]
    type_ids.sort()
    self.assertListEqual(type_ids, range(len(self.types)))
    return

  def test_invalid_prj_name(self):
    prj_name = 'egg'
    regexp = r'%s is not a registered project name\.' %prj_name
    with self.assertRaisesRegexp(AssertionError, regexp):
      self.grouptypes.get_type(prj_name, 'dummy')
    return

  def test_invalid_type_name(self):
    name = 'egg'
    regexp = r'%s is not registered in %s project\.' %(name, self.prj_name)
    with self.assertRaisesRegexp(AssertionError, regexp):
      self.grouptypes.get_type(self.prj_name, name)
    return

  def test_clear(self):
    self.grouptypes.clear()
    self.assertDictEqual(self.grouptypes._projects, {})
    return

  def test_get_types(self):
    type_ids = self.grouptypes.get_types(self.prj_name, self.types) 
    type_ids.sort()
    self.assertListEqual(type_ids, range(len(self.types)))
    return

  def test_copy(self):
    grouptypes = self.grouptypes.copy()
    self.assertDictEqual(grouptypes._projects, self.grouptypes._projects)
    return

class TestMultipleTypes(unittest.TestCase):
  def setUp(self):
    self.grouptypes = GroupTypes()
    self.types = [{'bar', 'baz', 'spam'}, {'egg', 'eggegg'}]
    self.prj_name = 'foo'
    for types in self.types:
      self.grouptypes.add_types(self.prj_name, types)
    return

  def test_get_type(self):
    type_numbers = []
    size = 0
    for type_names in self.types:
      size += len(type_names)
      for type_name in type_names:
        type_number = self.grouptypes.get_type(self.prj_name, type_name)
        type_numbers.append(type_number)
    type_numbers.sort()
    self.assertListEqual(type_numbers, range(size))
    return

unittest.main()

