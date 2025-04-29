import logging

from PySide import QtGui, QtCore

from measproc.batchsqlite import TableQuery

comparison_funcs = {
                      'label' : ('==', '!=', 'in', 'not in'),
                      'quantity' : ('==', '!=', '>', '>=', '<', '<='),
                      'measurement' : ('==', '!=', '>', '>=', '<', '<='),
                      'comment' : ('==', '!=', 'in', 'not in'),
                      'other' : ('==', '!=', 'in', 'not in', '>', '>=', '<',
                                  '<='),
                   }

class SimpleSignal(QtCore.QObject):
  signal = QtCore.Signal()

class ObjectEmittingSignal(QtCore.QObject):
  signal = QtCore.Signal(object)

class FloatAndObjectEmittingSignal(QtCore.QObject):
  signal = QtCore.Signal(float, object)

class Selector(QtGui.QPushButton):
  def __init__(self, exclusive=True):
    QtGui.QPushButton.__init__(self)
    menu = QtGui.QMenu()
    self.setMenu(menu)
    self.menu()
    self.paramgroup = QtGui.QActionGroup(menu)
    self.paramgroup.setExclusive(exclusive)
    self.exclusive = exclusive
    self.item_selected = SimpleSignal()
    self.setFixedSize(300, 25)
    return

  def add_items(self, items):
    for item in items:
      self.add_item(item)
    return

  def add_item(self, item):
    menu = self.menu()
    actions = menu.actions()
    for action in actions:
      if action.text() == item: return

    action = QtGui.QAction(item, menu)
    action.triggered.connect(self.item_selected.signal.emit)
    action.setCheckable(True)
    self.paramgroup.addAction(action)
    menu.addAction(action)
    self.setEnabled(True)
    return

  def get_excl_item(self):
    if not self.exclusive:
      log = logging.getLogger()
      log.error("Options aren't exclusives")

    items = self.get_items()
    assert len(items) < 2, 'Multiple elements are selected'
    if len(items) == 0: return
    item, = items
    return item

  def get_items(self):
    menu = self.menu()
    items = [action.text() for action in menu.actions() if action.isChecked()]
    txt = ', '.join(items)
    self.setText(txt)
    return items

  def remove_items(self):
    menu = self.menu()
    for action in menu.actions():
      menu.removeAction(action)
      action.deleteLater()
    self.setText('')
    return

  def clear_selection(self):
    self.paramgroup.setExclusive(False)
    menu = self.menu()
    for action in menu.actions():
      action.setChecked(False)
    self.setText('')
    self.paramgroup.setExclusive(True)
    return

class Filter(QtCore.QObject):
  def __init__(self, batch=None, all_elements={}, int_label={}, quas={},
               int_comment=[]):
    QtCore.QObject.__init__(self)
    self.set_batch(batch)
    self.set_all_elements(all_elements, filtering=False)
    self.set_int_label(int_label)
    self.set_quas(quas)
    self.set_int_comment(int_comment)
    self.option_selector = Selector()
    self.option_selector.item_selected.signal.connect(self.option_selected)
    self.func_selector = Selector()
    self.func_selector.item_selected.signal.connect(self.update_value)
    self.value_selector = Selector(exclusive=False)
    self.value_selector.item_selected.signal.connect(self.filt)
    self.add_selector_object_signal = FloatAndObjectEmittingSignal()
    self.sorted_elements = ObjectEmittingSignal()
    self.logger = logging.getLogger()
    return

  def init(self):
    self.add_selector_object_signal.signal.emit(0, self.option_selector)
    self.add_selector_object_signal.signal.emit(1, self.func_selector)
    self.add_selector_object_signal.signal.emit(2, self.value_selector)
    return

  def fill_option_selector(self, options):
    self.option_selector.add_items(options)
    self.disable()
    return

  def set_batch(self, batch):
    self.batch = batch
    return

  def set_all_elements(self, all_elements, filtering=True):
    self.all_elements = all_elements
    if filtering:
      self.filt()
    return

  def set_int_label(self, int_label):
    self.int_label = int_label
    return

  def set_quas(self, quas):
    self.quas = quas
    return

  def set_int_comment(self, int_comment):
    self.int_comment = int_comment
    return

  def is_initalized(self):
    return self.all_elements and self.batch

  def option_selected(self):
    self.disable()
    self.func_selector.remove_items()
    item = self.option_selector.get_excl_item()
    if item is None: return

    if item in self.int_label:
      selected_option = 'label'
    elif item in self.quas:
      selected_option = 'quantity'
    elif item in self.int_comment:
      selected_option = 'comment'
    else:
      selected_option = 'other'
    self.update_funcs(selected_option)
    return

  def update_funcs(self, selected_option):
    funcs = comparison_funcs[selected_option]
    self.func_selector.add_items(funcs)
    if selected_option == 'label' and \
       not isinstance(self.value_selector, Selector):
      self.remove_value_selector()
      self.value_selector = Selector(exclusive=False)
      self.value_selector.setEnabled(False)
      self.add_value_selector()
      self.value_selector.item_selected.signal.connect(self.filt)
    elif selected_option != 'label' and \
         not isinstance(self.value_selector, QtGui.QLineEdit):
         self.remove_value_selector()
         self.value_selector = QtGui.QLineEdit()
         self.value_selector.setFixedSize(300, 25)
         self.value_selector.setEnabled(False)
         self.add_value_selector()
         self.value_selector.textChanged.connect(self.filt)
    elif isinstance(self.value_selector, Selector):
      self.value_selector.remove_items()
    return

  def update_value(self):
    self.value_selector.setEnabled(True)
    value = self.func_selector.get_excl_item()
    if isinstance(self.value_selector, QtGui.QLineEdit):
      return

    self.value_selector.remove_items()
    alias = self.option_selector.get_excl_item()
    labelgroup = self.int_label[alias]
    _, votes = self.batch.get_labelgroup(labelgroup)
    self.value_selector.add_items(votes)
    return

  def filt(self):
    sorted_elements = []
    option = self.option_selector.get_excl_item()

    if not option:
      sorted_elements = self.all_elements
    else:
      for element in self.all_elements:
        paramvalue = element[option]
        function = self.func_selector.get_excl_item()
        if isinstance(self.value_selector, QtGui.QLineEdit):
          value = self.value_selector.text()
          if not value:
            sorted_elements = self.all_elements
          else:
            try:
              if self.eval_from_str(function, paramvalue, value, option):
                sorted_elements.append(element)
            except AssertionError, e:
              self.logger.error(str(e))
              break
        else:
          items = self.value_selector.get_items()
          if not items:
            sorted_elements = self.all_elements
          elif function in ('in', 'not in'):
           for item in items:
            if not self.eval_from_str(function, paramvalue, item, option): break
           else:
            sorted_elements.append(element)
          else:
            if self.eval_from_str(function, paramvalue, items, option):
              sorted_elements.append(element)

    self.sorted_elements.signal.emit(sorted_elements)
    return sorted_elements

  def eval_from_str(self, function, paramvalue, value, option):
    if isinstance(paramvalue, float) or isinstance(paramvalue, int):
      eval_text = 'float("%s") %s float("%s")' %(paramvalue, function, value)
      try:
        ret = eval(eval_text)
      except ValueError, NameError:
        raise AssertionError('Cannot convert to float %s' %value)
    else:
      value = value if value is not None else TableQuery.NOT_AVAILABLE
      paramvalue = paramvalue if paramvalue is not None \
                              else TableQuery.NOT_AVAILABLE
      if option in self.int_label:
        eval_text = '"%s" %s "%s"' %(value, function, paramvalue)
      else:
        eval_text = '"%s" %s "%s"' %(paramvalue, function, value)
      ret = eval(eval_text)

    return ret

  def remove_value_selector(self):
    self.remove_selector(self.value_selector)
    return

  def remove_selector(self, selector):
    selector.setParent(None)
    selector.deleteLater()
    selector = None
    return

  def close(self):
    self.remove_selector(self.option_selector)
    self.remove_selector(self.func_selector)
    self.remove_selector(self.value_selector)
    self.deleteLater()
    return

  def add_value_selector(self):
    self.add_selector_object_signal.signal.emit(2, self.value_selector)
    return

  def clear_editor(self, editor):
    if isinstance(editor, Selector):
      exclusive = editor.paramgroup.isExclusive()
      editor.paramgroup.setExclusive(False)
      menu = editor.menu()
      for action in menu.actions():
        if action.isChecked():
          action.toggle()
      editor.paramgroup.setExclusive(exclusive)
    editor.setText('')
    return

  def disableAll(self):
    self.disable()
    self.clear_editor(self.option_selector)
    return


  def disable(self):
    for editor in (self.value_selector, self.func_selector):
        self.clear_editor(editor)
    self.value_selector.setEnabled(False)
    self.func_selector.setEnabled(False)
    self.filt()
    return

