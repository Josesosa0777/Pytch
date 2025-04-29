# -*- coding: utf-8 -*-

import logging
from operator import itemgetter

from PySide import QtGui, QtCore

from interface.modules import ModuleName
from section_delegates import PARAM_SEP
from base_section_model import SectionModel

class GroupModel(SectionModel):
  HEADER = 'Group',

  def get_modulename_from_table(self, row):
    element = self.visible_elements[row]
    return element['Group']

  def data(self, index, role=QtCore.Qt.DisplayRole):
    if index.isValid():
      headerName = self.HEADER[index.column()]
      module = self.get_modulename_from_table(index.row())
      if role == QtCore.Qt.DisplayRole:
          return self.visible_elements[index.row()][headerName]
      elif role == QtCore.Qt.BackgroundColorRole:
        background = QtGui.QBrush(self.visible_elements[index.row()]['color'])
        return background
      elif role == QtCore.Qt.FontRole:
        font = QtGui.QApplication.font()
        if 'Favs.' in self.EDITABLE_HEADER_ELEMENTS: #for all module model only
          check = self.config.getboolean(self.section, module)
          if check:
            new_font = QtGui.QFont(font)
            new_font.setItalic(True)
            return new_font
        return font
    else:
      return None

class AllGroupModel(GroupModel):
  HEADER = 'Favs.', 'Group'
  EDITABLE_HEADER_ELEMENTS = 'Favs.',

  def setData(self, index, value, role=QtCore.Qt.EditRole):
    if index.isValid() and role == QtCore.Qt.EditRole:
      module = self.get_modulename_from_table(index.row())

      headerName = self.HEADER[index.column()]
      if headerName == 'Favs.':
        self.elements[module]['Favs.'] = value
        if value:
          self.config.addFavorite(self.section, module)
        else:
          self.config.removeFavorite(self.section, module)
        return True
    return False

  def get_elements(self):
    if self.config.has_option('Favorites', self.section):
      favs = self.config.get('Favorites', self.section)
      favorites = favs.split(',')
      favorites = [fav.strip() for fav in favorites]
      favorites = [fav.rstrip() for fav in favorites]
    else:
      favorites = set()
    for group in self.config.options(self.section):
      if group not in self.elements:
        self.elements[group] = {}
        element = self.elements[group]
        self.visible_elements.append(element)
        element['Favs.'] = group in favorites
        element['Group'] = group
        element['color'] = self.DEFAULT_COLOR
    return

  def query_elements(self, pos_grp_tags, neg_grp_tags,
                           pos_grp_tag_mc, neg_grp_tag_mc):
    self.visible_elements = []

    for group in self.elements:
      if self.check_name(group, pos_grp_tags, neg_grp_tags,
                         pos_grp_tag_mc, neg_grp_tag_mc):
        self.visible_elements.append(self.elements[group])
    self._draw()
    return

class ActGroupModel(GroupModel):
  def get_elements(self):
    self.elements = {}
    self.visible_elements = []
    for group in self.config.options(self.section):
      if not self.config.getboolean(self.section, group): continue

      if group not in self.elements:
        self.elements[group] = {}
        element = self.elements[group]
        self.visible_elements.append(element)
        element['color'] = self.DEFAULT_COLOR
        element['Group'] = group
    self._draw()
    return

class ModuleModel(SectionModel):
  HEADER = 'Subproject', 'Module', 'Params'
  EDITABLE_HEADER_ELEMENTS = 'Params',

  def get_modulename_from_table(self, row):
    element = self.visible_elements[row]
    mod = element['Module']
    prj = element['Subproject']
    return ModuleName.create(mod, '', prj)

  def data(self, index, role=QtCore.Qt.DisplayRole):
    if index.isValid():
      module = self.get_modulename_from_table(index.row())
      headerName = self.HEADER[index.column()]
      if role == QtCore.Qt.DisplayRole:
        check = self.check_to_specific_header(module, headerName)
        if check is not None:
          return check
        mod, _, prj = ModuleName.split(module)
        if headerName == 'Module':
          module = mod.replace(self.sub_from_option, '')
          return module
        elif headerName == 'Subproject':
          return prj
        elif headerName == 'Params':
          return ', '.join(self.elements[module]['Params'])
        raise KeyError
      elif role == QtCore.Qt.BackgroundColorRole:
        background = QtGui.QBrush(self.elements[module]['color'])
        return background
      elif role == QtCore.Qt.FontRole:
        font = QtGui.QApplication.font()
        if 'Favs.' in self.EDITABLE_HEADER_ELEMENTS: #for all module model only
          check = self.config.getboolean(self.section, module)
          if check:
            new_font = QtGui.QFont(font)
            new_font.setItalic(True)
            return new_font
        return font
    else:
      return None

  def check_to_specific_header(self, *args):
    return

class AllModuleModel(ModuleModel):
  HEADER = 'Favs.', 'Subproject', 'Module', 'Params'
  EDITABLE_HEADER_ELEMENTS = 'Favs.', 'Params'

  def setData(self, index, value, role=QtCore.Qt.EditRole):
    if index.isValid() and role == QtCore.Qt.EditRole:
      module = self.get_modulename_from_table(index.row())

      headerName = self.HEADER[index.column()]
      if headerName == 'Favs.':
        self.elements[module]['Favs.'] = value
        if value:
          self.config.addFavorite(self.section, module)
        else:
          self.config.removeFavorite(self.section, module)
        return True
      elif headerName == 'Params':
        self.elements[module]['Params'] = set()
        for param in self.config.options(module):
          self.config.set(module, param, 'no')
        for param in value:
          self.elements[module]['Params'].add(param)
          self.config.set(module, param, 'yes')
        self.config.update()
        return True
    return False

  def check_to_specific_header(self, module, headerName):
    if headerName == 'Favs.':
        return self.elements[module]['Favs.']
    return

  def get_elements(self):
    if self.config.has_option('Favorites', self.section):
      favs = self.config.get('Favorites', self.section)
      favorites = favs.split(',')
      favorites = [fav.strip() for fav in favorites]
      favorites = [fav.rstrip() for fav in favorites]
    else:
      favorites = set()
    for ext_mod in self.config.options(self.section):
      if ext_mod not in self.elements:
        self.elements[ext_mod] = {}
        element = self.elements[ext_mod]
        self.visible_elements.append(element)
        element['ext_mod_2_param'] = set()
        element['color'] = self.DEFAULT_COLOR
        element['Params'] = set()
        element['Favs.'] = ext_mod in favorites

        mod, _, prj = ModuleName.split(ext_mod)
        element['Module'] = mod
        element['Subproject'] = prj
      for param in self.config.options(ext_mod):
        params = self.elements[ext_mod]['ext_mod_2_param']
        params.add(param)
        if self.config.getboolean(ext_mod, param):
          params = self.elements[ext_mod]['Params']
          params.add(param)

    return

  def query_elements(self, pos_prj_tags, pos_mod_tags, pos_param_tags,
                           neg_prj_tags, neg_mod_tags, neg_param_tags,
                           pos_prj_tag_mc, pos_mod_tag_mc, pos_param_tag_mc,
                           neg_prj_tag_mc, neg_mod_tag_mc, neg_param_tag_mc):

    self.visible_elements = []

    for ext_mod in self.elements:
      mod, _, prj = ModuleName.split(ext_mod)
      if self.check_name(prj, pos_prj_tags, neg_prj_tags,
                         pos_prj_tag_mc, neg_prj_tag_mc) and \
         self.check_name(mod, pos_mod_tags, neg_mod_tags,
                          pos_mod_tag_mc, neg_mod_tag_mc):
        params = self.elements[ext_mod]['ext_mod_2_param']
        params = params if params else ['', ]
        params_str = ','.join(params)

        if self.check_name(params_str, pos_param_tags, neg_param_tags,
                            pos_param_tag_mc, neg_param_tag_mc) and \
           self.elements[ext_mod] not in self.visible_elements:
            self.visible_elements.append(self.elements[ext_mod])
    self._draw()
    return


class ActiveModuleModel(ModuleModel):
  HEADER = 'Acts.', 'Subproject', 'Module', 'Params'
  EDITABLE_HEADER_ELEMENTS = 'Acts.', 'Params'

  def __init__(self, config, section, sub_from_option, sub_to_option, sortbys):
     ModuleModel.__init__(self, config, section, sub_from_option,
                                sub_to_option, sortbys)
     return

  def setData(self, index, value, role=QtCore.Qt.EditRole):
    if index.isValid() and role == QtCore.Qt.EditRole:
      module = self.get_modulename_from_table(index.row())
      headerName = self.HEADER[index.column()]
      if headerName == 'Acts.':
        self.elements[module]['Acts.'] = value
        if not value:
          self.config.blockModule(self.section, module)
        else:
          self.config.unBlockModule(self.section, module)
        return True
      elif headerName == 'Params':
        self.elements[module]['Params'] = set()
        for param in self.config.options(module):
          self.config.set(module, param, 'no')
        for param in value:
          self.elements[module]['Params'].add(param)
          self.config.set(module, param, 'yes')
        self.config.update()
        return True
    return False

  def check_to_specific_header(self, module, headerName):
    if headerName == 'Acts.':
        return  self.elements[module]['Acts.']
    return

  def get_elements(self):
    self.elements = {}
    self.visible_elements = []
    for ext_mod in self.config.options(self.section):
      if not self.config.getboolean(self.section, ext_mod): continue

      if ext_mod not in self.elements:
        self.elements[ext_mod] = {}
        element = self.elements[ext_mod]
        self.visible_elements.append(element)
        element['ext_mod_2_param'] = set()
        element['Params'] = set()
        element['color'] = self.DEFAULT_COLOR

        mod, _, prj = ModuleName.split(ext_mod)
        element['Module'] = mod
        element['Subproject'] = prj
        element['Acts.'] = True
      for param in self.config.options(ext_mod):
          params = self.elements[ext_mod]['ext_mod_2_param']
          params.add(param)
          if self.config.getboolean(ext_mod, param):
            params = self.elements[ext_mod]['Params']
            params.add(param)
    self._draw()
    return
