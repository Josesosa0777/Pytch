import sys
import logging

import section
from interface.Interfaces import iFill
from interface.modules import ModuleName
from interface.module import importModuleAttr

class cSection(section.cSection):
  Interface = iFill
  ParamSections = 'ViewAngles', 'Legends', 'ShapeLegends', 'Groups'
  def initConfig(self, Modules):
    self.Config.set('__doc__', self.Interface.__name__, 'Status names that will'
                    ' be filtered based on the signal of the current '
                    'measurement. Active means enabled')
    self.Config.set('__doc__', 'GroupNames', 'Set the visibility of the object '
                    'groups. Active means visible')

    self.Config.add_section('GroupNames')
    for Section in self.ParamSections:
      if self.Config.has_section(Section): continue
      self.Config.add_section(Section)

    self._initModules(Modules)
    self._validateStatusNames()
    self._setGroupNames()
    return

  def _validateStatusNames(self):
    StatusNames = set([ModuleName.create(Module, Param, Prj)
                       for Module, Param, Prj
                       in self.Config.iterModules(self.Interface.__name__)])
    for Section in self.ParamSections:
      Unhandled = {}
      for Option in self.Config.options(Section):
        ParamLoc = self.Config.get(Section, Option)
        Param = importModuleAttr(ParamLoc)
        Extra = set(Param)
        Extra.difference_update(StatusNames)
        if Extra:
          Unhandled[Option] = Extra
      if Unhandled:
        self.Config.log('Unhandled status names from\n')
        for Option, Statuses in Unhandled.iteritems():
          self.Config.log( Section + '-' + Option )
          for Status in Statuses:
            self.Config.log( '  ' + Status)
    return


  def _setGroupNames(self):
    GroupNames = set()
    for Option in self.Config.options('Groups'):
      Groups = self.Config.get('Groups', Option)
      Groups = importModuleAttr(Groups)
      for Group in Groups.itervalues():
        GroupNames.update(Group.keys())
    self.Config.initOptions('GroupNames', GroupNames, OptionValue='yes')
    return

  def group(self, GroupName):
    "set GROUP to visible"
    GroupName, Value = self.stripSelection(GroupName)
    self.Config.set('GroupNames', GroupName, Value)
    return

  def fill(self, StatusName):
    "select fill MODULE with PARAM"
    Interface = self.Interface.__name__
    StatusName, Value = self.stripSelection(StatusName)
    ModuleName_, ParamName, PrjName = ModuleName.split(StatusName)
    ModName = ModuleName.create(ModuleName_, '', PrjName)

    self.Config.set(Interface, ModName, Value)
    if ParamName:
      self.Config.set(ModName, ParamName, Value)
    return

  def procArgs(self, Args):
    for StatusName in Args.fill:
      self.fill(StatusName)
    for Group in Args.group:
      self.group(Group)
    return

  @classmethod
  def addArguments(cls, Parser):
    Group = Parser.add_argument_group(title='status names')
    Group.add_argument('--group',
                        help=cls.group.__doc__, action='append', default=[])
    Group.add_argument('--fill', metavar='MODULE-PARAM',
                        help=cls.fill.__doc__, action='append', default=[])
    return Parser

  @staticmethod
  def stripSelection(Parameter):
    if Parameter.startswith('+'):
      Parameter = Parameter[1:]
      self.Config.log('+ for module or parameter selection is obsolete')
    return Parameter, 'yes'

