# -*- coding: utf-8 -*-

import math

from PySide import QtGui, QtCore

from interface.modules import ModuleName

PARAM_SEP = ','

class Star(QtGui.QWidget):
  def __init__(self, is_fav, *args, **kwargs):
    QtGui.QWidget.__init__(self, *args, **kwargs)
    self.is_fav = is_fav
    return

  def mousePressEvent(self, event):
    self.is_fav = not self.is_fav
    QtGui.QWidget.mousePressEvent(self, event)
    return

class StarDelegate(QtGui.QItemDelegate):
  def createEditor(self, parent, option, index):
    model = index.model()
    module = model.get_modulename_from_table(index.row())
    value = model.elements[module]['Favs.']
    editor = Star(value, parent=parent)
    return editor

  def editorEvent(self, event, model, option, index):
    if event.type() == QtCore.QEvent.Type.MouseButtonPress:
      module = model.get_modulename_from_table(index.row())
      value = model.elements[module]['Favs.']
      model.setData(index, not value, QtCore.Qt.EditRole)
    return QtGui.QItemDelegate.editorEvent(self, event, model, option, index)

  def setModelData(self, editor, model, index):
    return

  def setEditorData(self, editor, index):
    return

  def paint(self, painter, option, index):
    model = index.model()
    module = model.get_modulename_from_table(index.row())

    #draw the background
    color = model.elements[module]['color']
    painter.save()
    painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
    painter.setBrush(QtGui.QBrush(color))
    painter.drawRect(option.rect)
    painter.restore()

    need_fill = model.elements[module]['Favs.']
    self.drawStar(painter, option.rect, option.palette, need_fill)

    return

  def updateEditorGeometry(self, editor, option, index):
    editor.setGeometry(option.rect)
    return

  def drawStar(self, painter, rect, palette, fill):
    painter.save()
    painter.setPen(QtCore.Qt.NoPen)
    brush = QtGui.QBrush(QtCore.Qt.gray)
    painter.setBackground(brush)

    y = rect.height() / 2
    x = rect.width() / 2

    painter.translate(rect.x() + x - 10, rect.y() + y - 10)

    if fill:
      brush = QtGui.QBrush(QtCore.Qt.yellow)
      painter.setBrush(brush)
    painter.setPen(QtCore.Qt.SolidLine)
    painter.setPen(QtCore.Qt.yellow)

    star = QtGui.QPolygonF()
    star.append( QtCore.QPointF(20, 10) )
    for i in range(4):
      star.append( QtCore.QPointF(10 + 10 * math.cos(0.8 * (i + 1) * math.pi),
                                  10 + 10 * math.sin(0.8 * (i + 1) * math.pi)))
    painter.drawPolygon(star, fillRule=QtCore.Qt.WindingFill)
    painter.restore()
    return

class ParamDelegate(QtGui.QItemDelegate):
  def __init__(self):
    QtGui.QItemDelegate.__init__(self)
    return

  def createEditor(self, parent, option, index):
    editor = QtGui.QPushButton(parent=parent)
    editor.setFlat(True)
    menu = QtGui.QMenu()
    paramgroup = QtGui.QActionGroup(menu)
    paramgroup.setExclusive(False)
    model = index.model()
    element = model.visible_elements[index.row()]
    mod = element['Module']
    prj = element['Subproject']
    module = ModuleName.create(mod, '', prj)
    params = model.elements[module]['ext_mod_2_param']
    for param in sorted(params):
      action = QtGui.QAction(param, editor)
      action.setCheckable(True)
      menu.addAction(action)
      paramgroup.addAction(action)
      action.triggered.connect(lambda e=editor, i=index, m=model:
                                      self.setModelData(e, m, i))

    editor.setMenu(menu)
    editor.menu()
    return editor

  def setModelData(self, editor, model, index):
    menu = editor.menu()
    value = [action.text() for action in menu.actions() if action.isChecked()]
    model.setData(index, value, QtCore.Qt.EditRole)
    return

  def setEditorData(self, editor, index):
    model = index.model()
    menu = editor.menu()
    value = index.data()
    params = value.split(PARAM_SEP)
    for action in menu.actions():
      action.setChecked(action.text() in params)
    editor.showMenu()
    return

  def updateEditorGeometry(self, editor, option, index):
    editor.setGeometry(option.rect)
    return

class CheckBoxDelegate(QtGui.QItemDelegate):
  def createEditor(self, parent, option, index):
    editor = QtGui.QWidget(parent=parent)
    return editor

  def setModelData(self, editor, model, index):
    return

  def setEditorData(self, editor, index):
    return

  def paint(self, painter, option, index):
    model = index.model()
    module = model.get_modulename_from_table(index.row())
    #draw the background
    color = model.elements[module]['color']
    painter.save()
    painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
    painter.setBrush(QtGui.QBrush(color))
    painter.drawRect(option.rect)
    painter.restore()
    value = model.elements[module]['Acts.']
    value = QtCore.Qt.Checked if value else QtCore.Qt.Unchecked
    self.drawCheck(painter, option, option.rect, value)
    return

  def editorEvent(self, event, model, option, index):
    if event.type() == QtCore.QEvent.Type.MouseButtonPress:
      module = model.get_modulename_from_table(index.row())
      value = model.elements[module]['Acts.']
      model.setData(index, not value, QtCore.Qt.EditRole)
    return QtGui.QItemDelegate.editorEvent(self, event, model, option, index)
