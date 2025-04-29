from PySide import QtGui, QtCore

from datavis.interval_filter import Selector

class SelectionError(BaseException):
  pass

class cTagSelector(QtGui.QFrame):
  def __init__(self, batch, tags):
    QtGui.QFrame.__init__(self)

    self.batch = batch
    self.tags = tags

    self.filters = []
    self.filters_2_buttons = {}
    self.signals_2_filters = {}
    self.vbox = QtGui.QVBoxLayout()
    scroll_area = QtGui.QScrollArea()
    frame = QtGui.QFrame()
    frame.setLayout(self.vbox)
    scroll_area.setWidget(frame)
    scroll_area.setWidgetResizable(True)
    self.add_filter()

    vbox = QtGui.QVBoxLayout()
    vbox.addWidget(scroll_area)
    self.setLayout(vbox)
    return

  def add_filter(self):
    option_selector = Selector()
    option_selector.add_items(self.tags)
    func_selector = Selector()
    func_selector.add_items(('=', ))
    value_selector = QtGui.QComboBox()
    func_selector.setEnabled(False)
    value_selector.setEnabled(False)

    filter = option_selector, func_selector, value_selector
    self.filters.append(filter)
    ndx = self.filters.index(filter)

    option_selector.item_selected.signal.connect(self.option_selected)

    option_selector.setFixedSize(150, 25)
    func_selector.setFixedSize(50, 25)
    self.signals_2_filters[option_selector.item_selected] = filter

    add_btn = QtGui.QPushButton('+')
    add_btn.clicked.connect(self.add_filter)

    rm_btn = QtGui.QPushButton('-')

    btns = add_btn, rm_btn
    self.filters_2_buttons[filter] = btns
    for btn in btns:
      btn.setFixedSize(25, 25)

    hbox = QtGui.QHBoxLayout()
    for widget in (option_selector, func_selector, value_selector, add_btn, \
                   rm_btn):
        hbox.addWidget(widget)

    if ndx == 0:
      rm_btn.clicked.connect(lambda f=filter: self.reinit_filter(f))
    else:
      rm_btn.clicked.connect(lambda f=filter: self.remove_filter(f))

    if len(self.filters) > 1:
      first_filter = self.filters[0]
      _, rm_btn = self.filters_2_buttons[first_filter]
      rm_btn.clicked.disconnect()
      rm_btn.clicked.connect(lambda f=first_filter: self.remove_filter(f))

    self.vbox.addLayout(hbox)
    return

  def reinit(self):
    for filter in self.filters[1:]:
      self.remove_filter(filter)
    self.reinit_filter(self.filters[0])
    return

  def reinit_filter(self, filter):
    opt_sel, func_sel, val_sel = filter
    val_sel.clear()
    val_sel.setEnabled(False)
    func_sel.setEnabled(False)
    opt_sel.clear_selection()
    return

  def remove_filter(self, filter):
    add_btn, rm_btn = self.filters_2_buttons[filter]
    for btn in  (add_btn, rm_btn):
      btn.close()
      btn.setParent(None)
      btn.deleteLater()
    del self.filters_2_buttons[filter]
    opt_sel, _, _ = filter
    del self.signals_2_filters[opt_sel.item_selected]
    for widget in filter:
      widget.close()
      widget.setParent(None)
      widget.deleteLater()
    self.filters.remove(filter)
    if len(self.filters) == 1:
      first_filter, = self.filters
      _, rm_btn = self.filters_2_buttons[first_filter]
      rm_btn.clicked.disconnect()
      rm_btn.clicked.connect(lambda f=first_filter: self.reinit_filter(f))
    return

  def option_selected(self):
    sender = self.sender()
    opt_sel, func_sel, val_sel = self.signals_2_filters[sender]
    option = opt_sel.get_excl_item()
    opt_sel.setText(option)

    val_sel.clear()

    func_sel.setEnabled(True)
    menu = func_sel.menu()
    for action in menu.actions():
      if action.text() == '=':
        action.setChecked(True)
        func_sel.setText('=')

    values = list(set(self.batch.get_occasions(option)))
    values.sort()
    val_sel.addItems(values)
    val_sel.clearEditText()
    val_sel.setEnabled(True)
    return

  def update(self):
    if self.Tags.count():
      self.Tags.clear()
    try:
      Batch = self.Control.getBatch()
      Tags = list(set(Batch.get_occasions(self.TagName)))
    except AssertionError:
      Tags = []
    Tags.sort()
    for Tag in Tags:
      if Tag:
        self.Tags.addItem(Tag)
    return

  def getCurrentSelection(self, name):
    founded_filters = 0
    value = None
    for filter in self.filters:
      opt_sel, _, val_sel = filter
      if opt_sel.text() == name:
        founded_filters += 1
        value = val_sel.currentText()
    if founded_filters > 1:
      raise SelectionError('%s : more than once were selected!' %name)
    return value

  def clear(self):
    self.reinit()
    return

