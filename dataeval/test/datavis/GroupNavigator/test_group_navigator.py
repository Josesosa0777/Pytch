import unittest

from PySide import QtGui, QtCore, QtTest

from datavis.GroupNavigator import cGroupNavigator
from datavis.GroupParam import cGroupParam


groups = {
            'FooGroup' : cGroupParam((1, 2), 'A', False, False),
            'BarGroup' : cGroupParam((0, 3), 'B', True, False),
            'BazGroup' : cGroupParam((0, 5), 'C', False, True),
            'EggGroup' : cGroupParam((0, 4), 'D', True, True),
          }

class Build(unittest.TestCase):
  def setUp(self):
    self.navigator = cGroupNavigator()
    self.init_navigator()
    self.navigator.start()
    return

  def init_navigator(self):
    self.navigator.addGroups(groups)
    return

  def tearDown(self):
    self.navigator.close()
    return

class TestAddGroup(Build):
  def init_navigator(self):
    return

  def test_add_group(self):
    for name, param in groups.iteritems():
      self.navigator.addGroup(name, param)
    self.check_groups()
    return

  def test_add_groups(self):
    self.navigator.addGroups(groups)
    self.check_groups()
    return

  def check_groups(self):
    for name, param in groups.iteritems():
      self.assertEqual(self.navigator.Groups[name], param.Types)
      self.assertEqual(self.navigator.KeyCodes[param.KeyCode], name)
      self.assertEqual(self.navigator.OrigVisibility[name], param.Visible)
    return

class TestGui(Build):    
  def test_groups_in_list(self):
    groups_in_passive_list = self.navigator.Passives.count()
    groups_in_active_list = self.navigator.Actives.count()
    groups_in_list = groups_in_active_list + groups_in_passive_list
    self.assertEqual(groups_in_list, len(groups))

    active_gropnames = [name for name, param in groups.iteritems()
                       if param.Visible]
    passive_gropnames = [name for name, param in groups.iteritems()
                       if not param.Visible]

    self.assertEqual(groups_in_active_list, len(active_gropnames))
    self.assertEqual(groups_in_passive_list, len(passive_gropnames))

    match_flag = QtCore.Qt.MatchWrap | QtCore.Qt.MatchWildcard

    for active in self.navigator.Actives.findItems('*', match_flag):
      group_name, keyCode = active.text().split(self.navigator.SEP)
      self.assertIn(group_name, active_gropnames)
      self.assertEqual(keyCode, groups[group_name].KeyCode)

    for passive in self.navigator.Passives.findItems('*', match_flag):
      group_name, keyCode = passive.text().split(self.navigator.SEP)
      self.assertIn(group_name, passive_gropnames)
      self.assertEqual(keyCode, groups[group_name].KeyCode)
    return

  def test_select_group(self):
    active_gropnames = [name for name, param in groups.iteritems()
                       if param.Visible]
    for active_name in active_gropnames:
      self.navigator.selectGroup(active_name)
    self.assertEqual(self.navigator.Actives.count(), 0)
    
    self.assertEqual(self.navigator.Passives.count(), len(groups))
    return

class TestKeyPress(Build):
  def test_escape_press(self):
    self.navigator.Passives.selectAll()
    self.assertNotEqual(len(self.navigator.Passives.selectedItems()), 0)
    QtTest.QTest.keyClick(self.navigator.Passives, QtCore.Qt.Key_Escape)
    self.assertEqual(len(self.navigator.Passives.selectedItems()), 0)
    return

  def test_return_and_enter_press(self):
    groups_in_passive_list_orig = self.navigator.Passives.count()
    groups_in_active_list_orig = self.navigator.Actives.count()
    groups_in_list_orig = groups_in_passive_list_orig + \
                          groups_in_active_list_orig
    self.navigator.Passives.selectAll()
    QtTest.QTest.keyClick(self.navigator.Passives, QtCore.Qt.Key_Return)
    self.assertEqual(self.navigator.Passives.count(), 0)
    self.assertEqual(self.navigator.Actives.count(), groups_in_list_orig)

    match_flag = QtCore.Qt.MatchWrap | QtCore.Qt.MatchWildcard
    for active in self.navigator.Actives.findItems('*', match_flag):
      group_name, keyCode = active.text().split(self.navigator.SEP)
      self.assertIn(group_name, groups)
      self.assertEqual(keyCode, groups[group_name].KeyCode)

    self.navigator.Actives.selectAll()
    QtTest.QTest.keyClick(self.navigator.Actives, QtCore.Qt.Key_Enter)
    self.assertEqual(self.navigator.Actives.count(), 0)
    self.assertEqual(self.navigator.Passives.count(), groups_in_list_orig)

    match_flag = QtCore.Qt.MatchWrap | QtCore.Qt.MatchWildcard
    for passive in self.navigator.Passives.findItems('*', match_flag):
      group_name, keyCode = passive.text().split(self.navigator.SEP)
      self.assertIn(group_name, groups)
      self.assertEqual(keyCode, groups[group_name].KeyCode)
    return

if  __name__ == '__main__':
  app = QtGui.QApplication([])
  unittest.main()