import copy
import logging

from PySide import QtGui, QtCore

from datavis.interval_filter import Selector
funcs = '<', '>', '>=', '<=', '==', '!='

class ReportAdderFrame(QtGui.QFrame):
  LAST_LINES = [
                'intervals = cIntervalList.fromMask(time, mask)',
                'report = Report(intervals, "(no title)")',
                'self.batch.add_entry(report, result=self.PASSED)',
               ]
  def __init__(self, text, selector):
    QtGui.QFrame.__init__(self)

    self.selector = selector
    self.selector.SignalTable.clicked.connect(self.reinit)
    self.intersect_btn = QtGui.QPushButton('Intersect')
    self.union_btn = QtGui.QPushButton('Union')
    self.add_btn = QtGui.QPushButton('Add')
    self.add_btn.clicked.connect(self.add_interval)
    self.intersect_btn.clicked.connect(self.intersect_clicked)
    self.union_btn.clicked.connect(self.union_clicked)
    self.value_counter = -1
    self.func_selector = Selector()
    self.func_selector.add_items(funcs)
    self.value = QtGui.QLineEdit()
    self.value.setPlaceholderText('Threshold')
    self.text = text
    self.sig_index=''
    self.value.setEnabled(False)
    self.intersect_btn.setEnabled(False)
    self.union_btn.setEnabled(False)
    self.func_selector.setEnabled(False)
    self.func_selector.setFixedSize(50, 25)
    self.value.setFixedSize(180, 25)
    self.add_btn.setEnabled(False)
    button_layout = QtGui.QHBoxLayout()
    button_layout.addWidget(self.add_btn)
    button_layout.addWidget(self.intersect_btn)
    button_layout.addWidget(self.union_btn)
    button_layout.setAlignment(QtCore.Qt.AlignLeft)
    vbox = QtGui.QVBoxLayout()
    hbox = QtGui.QHBoxLayout()
    hbox.addWidget(self.func_selector)
    hbox.addWidget(self.value)
    hbox.setAlignment(QtCore.Qt.AlignLeft)
    vbox.addStretch(0)
    vbox.addLayout(hbox)
    vbox.addLayout(button_layout)
    vbox.addStretch(0)
    self.setLayout(vbox)
    self.funcs = []
    self.func_selector.item_selected.signal.connect(self.func_changed)
    self.value.textChanged.connect(self.value_changed)
    return

  def reinit(self, index):
    self.func_selector.paramgroup.setExclusive(False)
    menu = self.func_selector.menu()
    for action in menu.actions():
      action.setChecked(False)
    self.func_selector.paramgroup.setExclusive(True)
    self.func_selector.setEnabled(True)
    self.func_selector.setText('')
    self.value.setText('')
    self.value.setEnabled(False)
    self.disable_buttons()
    return

  def disable_buttons(self):
    self.add_btn.setEnabled(False)
    self.union_btn.setEnabled(False)
    self.intersect_btn.setEnabled(False)
    return

  def value_changed(self, txt):
    if not txt:
      self.disable_buttons()
      return
    try:
      float(txt)
    except:
      self.disable_buttons()
      logger = logging.getLogger()
      logger.error('%s cannot convert to float' %txt)
      return

    if self.value_counter == -1:
      self.add_btn.setEnabled(True)
    else:
      self.intersect_btn.setEnabled(True)
      self.union_btn.setEnabled(True)
    return

  def signal_selected(self):
    self.func_selector.setEnabled(True)
    return

  def func_changed(self):
    menu = self.func_selector.menu()
    for action in menu.actions():
      if action.isChecked():
        txt = action.text()
    self.func_selector.setText(txt)
    self.value.setEnabled(True)
    return

  def intersect_clicked(self):
    self.funcs.append(' & ')
    self.add_interval()
    return

  def union_clicked(self):
    self.funcs.append(' | ' )
    self.add_interval()
    return

  def add_report(self):
    lines = []
    line = 'mask = %s mask_00'  %('(' * (len(self.funcs) - 1))
    for i, func in enumerate(self.funcs):
      line += ' %s mask_%02d%s' %(func, i + 1, ')' * (i < len(self.funcs) - 1))
    lines.append(line)
    lines.extend(self.LAST_LINES)
    removable_lines = copy.copy(self.LAST_LINES)
    removable_lines.extend(['mask = '])
    self.text.add_report(lines, removable_lines)
    return

  def add_interval(self):
    self.value_counter += 1
    start = ''
    end = ')'
    if not self.value_counter:
      start = 'time, '
      getter_func = "get_signal"
    else:
      end = ', ScaleTime=time)'
      getter_func = 'get_value'
    sig_name = self.add_signal()
    line = '%svalue_%02d  = group.%s("%s"%s' %(start, self.value_counter,
                                               getter_func, sig_name, end)
    self.text.add_lines([line])
    self.add_mask()
    self.add_report()
    self.reinit(None)
    return

  def add_signal(self):
    selected_items = self.selector.getCurrentSelection(Unit=False)
    assert len(selected_items) == 1, 'Too many selected item'
    dev_name, sig_name = selected_items[0]
    if len(sig_name.split('[')) == 2:
      sig_name, index = sig_name.split('[')
      self.sig_index = '['+index
    else: self.sig_index=''
    return self.text.add_signal(dev_name, sig_name)

  def add_mask(self):
    menu = self.func_selector.menu()
    for action in menu.actions():
      if action.isChecked():
        func = action.text()
    value = self.value.text()
    line = 'mask_%02d = value_%02d%s %s %s' %(self.value_counter,
                                            self.value_counter, self.sig_index, func, value)
    self.text.add_lines([line])
    return
