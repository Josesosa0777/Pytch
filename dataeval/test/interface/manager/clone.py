from datavis import pyglet_workaround  # necessary as early as possible (#164)

import unittest

from interface.manager import Manager
from datalab.doctemplate import SimpleDocTemplate
from config.parameter import Params, GroupParams, TypeParams
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

class TestClone(unittest.TestCase):
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

    self.clone = self.manager.clone()
    return

  def test_measurement(self):
    self.assertDictEqual(self.manager._measurements, self.clone._measurements)
    return

  def test_cSource(self):
    self.assertIs(self.manager._Source, self.clone._Source)
    return

  def test_batch_params(self):
    self.assertIs(self.manager._batch_params, self.clone._batch_params)
    return

  def test_batchnav_params(self):
    self.assertIs(self.manager._batchnav_params, self.clone._batchnav_params)
    return

  def test_doctemplate(self):
    self.assertDictEqual(self.manager._doctemplates, self.clone._doctemplates)
    return

  def test_docname(self):
    self.assertEqual(self.manager._docname, self.clone._docname)
    return

  def test_grouptypes(self):
    self.assertDictEqual(self.manager.grouptypes._projects,
                         self.clone.grouptypes._projects)
    return

  def test_viewangles(self):
    self.assertDictEqual(self.manager._view_angles, self.clone._view_angles)
    self.assertIsInstance(self.clone._view_angles, Params)
    self.assertDictEqual(self.clone.view_angles, {})
    return

  def test_legends(self):
    self.assertDictEqual(self.manager._legends, self.clone._legends)
    self.assertIsInstance(self.clone._legends, TypeParams)
    self.assertDictEqual(self.clone.legends, {})
    return

  def test_shape_legends(self):
    self.assertDictEqual(self.manager._shape_legends, self.clone._shape_legends)
    self.assertIsInstance(self.clone._shape_legends, TypeParams)
    self.assertDictEqual(self.clone.shape_legends, {})
    return

  def test_groups(self):
    self.assertDictEqual(self.manager._groups, self.clone._groups)
    self.assertIsInstance(self.clone._groups, GroupParams)
    self.assertDictEqual(self.clone.groups, {})
    return

  def test_reports(self):
    self.assertDictEqual(self.clone.reports, {})
    return

  def test_report2s(self):
    self.assertDictEqual(self.clone.report2s, {})
    return

  def test_statistics(self):
    self.assertDictEqual(self.clone.statistics, {})
    return

  def test_report(self):
    self.assertIsNone(self.clone.report)
    return

  def test_meas_path(self):
    self.assertEqual(self.manager.meas_path, self.clone.meas_path)
    return

  def test_strong_time_check(self):
    self.assertEqual(self.manager.strong_time_check,
                     self.clone.strong_time_check)
    return

  def test_run_navigator(self):
    self.assertEqual(self.manager.run_navigator, self.clone.run_navigator)
    return

  def test_verbose(self):
    self.assertEqual(self.manager.verbose, self.clone.verbose)
    return


unittest.main()

