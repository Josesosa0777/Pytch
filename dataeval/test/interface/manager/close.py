from datavis import pyglet_workaround  # necessary as early as possible (#164)

import unittest

from interface.manager import Manager
from datalab.doctemplate import SimpleDocTemplate
from config.parameter import GroupParams
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

class TestClose(unittest.TestCase):
  def setUp(self):
    self.manager = Manager()
    self.manager.set_measurement('spamspam', channel='egg')
    self.manager.set_source_class(None)
    self.manager.set_batch_params('foo.db', 'files', {}, {}, {}, {}, False)
    self.manager.set_int_table_params([], '')
    self.manager.set_batchnav_params(None, [''], '', '', [], '')
    self.manager.set_doctemplate('foo', SimpleDocTemplate)
    self.manager.set_docname('baltazar.pdf')

    for prj_name, types in grouptypes.iteritems():
      self.manager.grouptypes.add_types(prj_name, types)
    self.manager.set_view_angles(view_angles)
    for prj_name, legends_ in legends.iteritems():
      self.manager.set_legends(prj_name, legends_)
    for prj_name, shape_legends_ in shape_legends.iteritems():
      self.manager.set_shape_legends(prj_name, shape_legends_)
    self.manager.select_params({'fillPyon', 'fillFoo-bar'})

    self.manager.reports = {1: 2}
    self.manager.report2s = {3: 4}
    self.manager.statistics = {5: 6}
    self.manager.report = 4

    self.manager.meas_path = 'egg'
    self.manager.strong_time_check = False
    self.manager.run_navigator = False
    self.manager.verbose = True

    self.types = {}
    for prj_name, types in grouptypes.iteritems():
      type_numbers = {}
      for type_name in types:
        type_number = self.manager.grouptypes.get_type(prj_name, type_name)
        type_numbers[type_name] = type_number
      self.types[prj_name] = type_numbers

    self.manager.close()
    return

  def test_measurement(self):
    self.assertDictEqual(self.manager._measurements, {'egg': 'spamspam'})
    return

  def test_cSource(self):
    self.assertIs(self.manager._Source, None)
    return

  def test_batch_params(self):
    self.assertIsNotNone(self.manager._batch_params)
    return

  def test_batchnav_params(self):
    self.assertIsNotNone(self.manager._batchnav_params)
    return

  def test_doctemplate(self):
    self.assertDictEqual(self.manager._doctemplates, {'foo': SimpleDocTemplate})
    return

  def test_docname(self):
    self.assertEqual(self.manager._docname, 'baltazar.pdf')
    return

  def test_grouptypes(self):
    for prj_name, types in grouptypes.iteritems():
      self.assertIn(prj_name, self.manager.grouptypes._projects)
      for type_name in types:
        self.assertIn(type_name, self.manager.grouptypes._projects[prj_name])
    return

  def test_viewangles(self):
    self.assertDictEqual(self.manager._view_angles, {
      'fillFoo-bar': {
        'group-bar': 1,
      },
      'fillFoo-baz': {
        'group-baz': 2,
      },
      'fillPyon': {
        'group-pyon': 3
      },
    })
    self.assertDictEqual(self.manager.view_angles, {})
    return

  def test_legends(self):
    self.assertDictEqual(self.manager._legends, {
      'fillFoo-bar': {
        self.types['egg']['foo']: 8,
      },
      'fillFoo-baz': {
        self.types['egg']['bar']: 9,
        self.types['egg']['baz']: 10,
      },
      'fillPyon': {
        self.types['spam']['bar']: 9,
      },
    })
    self.assertDictEqual(self.manager.legends, {})
    return

  def test_shape_legends(self):
    self.assertDictEqual(self.manager._shape_legends, {
      'fillFoo-bar': {
        self.types['egg']['foo']: 11,
      },
      'fillFoo-baz': {
        self.types['egg']['bar']: 12,
        self.types['egg']['baz']: 14,
      },
      'fillPyon': {
        self.types['spam']['bar']: 12,
      },
    })
    self.assertDictEqual(self.manager.shape_legends, {})
    return

  def test_reports(self):
    self.assertDictEqual(self.manager.reports, {})
    return

  def test_report2s(self):
    self.assertDictEqual(self.manager.report2s, {})
    return

  def test_statistics(self):
    self.assertDictEqual(self.manager.statistics, {})
    return

  def test_report(self):
    self.assertIsNone(self.manager.report)
    return

  def test_meas_path(self):
    self.assertEqual(self.manager.meas_path, 'egg')
    return

  def test_strong_time_check(self):
    self.assertFalse(self.manager.strong_time_check)
    return

  def test_run_navigator(self):
    self.assertFalse(self.manager.run_navigator)
    return

  def test_verbose(self):
    self.assertTrue(self.manager.verbose)
    return


unittest.main()

