# -*- coding: utf-8 -*-
from operator import itemgetter

from PySide import QtGui, QtCore

class SectionModel(QtCore.QAbstractTableModel):
  HEADER = []
  EDITABLE_HEADER_ELEMENTS = []
  DEFAULT_COLOR = QtCore.Qt.gray
  def __init__(self, config, section, sub_from_option, sub_to_option, sortbys):
    QtCore.QAbstractTableModel.__init__(self)
    self.config = config
    self.section = section
    self.elements = {}
    self.visible_elements = []
    self.control_pressed = False
    self.sub_to_option = sub_to_option
    self.sub_from_option = sub_from_option
    self.sortbys = [  [sortby, order]
                         for sortby, order in sortbys
                         if sortby in self.HEADER ]

    self.colours = {}
    self.row_color = QtCore.Qt.gray
    self.get_elements()
    self._draw()
    return

  def redraw(self):
    self._draw()
    return

  def columnCount(self, parent=QtCore.QModelIndex()):
    return len(self.HEADER)

  def rowCount(self, parent=QtCore.QModelIndex()):
    return len(self.visible_elements)

  def headerData(self, index, orientation, role=QtCore.Qt.DisplayRole):
    if (orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole):
      header = self.HEADER[index]
      prefix = ""
      sortbys = [sby for sby, _ in self.sortbys]
      if header in sortbys:
        ndx = sortbys.index(header)
        if self.sortbys[ndx][1]:
          prefix = '^'
        else:
          prefix = u'ˇ'
        prefix *= ndx + 1
      headerLabel = unicode(prefix) + unicode(header)
      return headerLabel
    else:
      return None

  def get_elements(self):
    return NotImplementedError

  def query_elements(self, *args):
    return

  def flags(self, index):
    flag = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
    name = self.HEADER[index.column()]
    if name in self.EDITABLE_HEADER_ELEMENTS:
      flag |= QtCore.Qt.ItemIsEditable
    return flag

  def toggleColor(self, prevData, data):
    if prevData != data:
      if self.row_color == QtCore.Qt.lightGray:
        self.row_color = QtCore.Qt.gray
      elif self.row_color == QtCore.Qt.gray :
        self.row_color = QtCore.Qt.lightGray
    return self.row_color

  def check_name(self, name, pos_tags, neg_tags, pos_mc, neg_mc):
    for tag_ in neg_tags:
      neg_name = name if neg_mc else name.lower()
      tag = tag_ if neg_mc else tag_.lower()
      if tag in neg_name:
        return False
    for tag_ in pos_tags:
      pos_name = name if pos_mc else name.lower()
      tag = tag_ if pos_mc else tag_.lower()
      if tag not in pos_name:
        return False
    return True

  def _draw(self):
    self.layoutAboutToBeChanged.emit()
    sortby = self.sortbys[0][0]
    for name, asc in self.sortbys[::-1]:
      self.visible_elements.sort(key=itemgetter(name), reverse=not asc)
    if self.visible_elements:
      prevData = self.visible_elements[0][sortby]
      self.row_color = QtCore.Qt.lightGray
    for element in self.visible_elements:
      data = element[sortby]
      element['color'] = self.toggleColor(prevData, data)
      prevData = data

    self.layoutChanged.emit()
    return

  def _onSort(self, index):
    if self.control_pressed:
      self._onHoldSort(index)
    else:
      self._onNormalSort(index)
    self._draw()
    return

  def _onNormalSort(self, index):
    header = self.HEADER[index]
    sortby = header

    if len(self.sortbys) == 1 and self.sortbys[0][0] == sortby:
      self.sortbys[0][1] = not self.sortbys[0][1]
    else:
      self.sortbys = [[sortby, True]]
    return

  def _onHoldSort(self, index):
    header = self.HEADER[index]
    sortby = header
    sortbys = [sby for sby, _ in self.sortbys]
    if sortby not in sortbys:
      self.sortbys.append([sortby, True])
    else:
      ndx = sortbys.index(sortby)
      self.sortbys[ndx][1] = not self.sortbys[ndx][1]
    self._draw()
    return
