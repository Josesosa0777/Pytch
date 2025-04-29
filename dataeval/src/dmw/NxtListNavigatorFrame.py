import logging

import os
import re
from PySide import QtGui, QtCore

from PlotNavigatorFrame import SimpleSignal
from PySide.QtCore import Qt
from PySide.QtGui import QIcon

IMAGE_DIRECTORY = os.path.join(os.path.dirname(__file__), "images")

class cListNavigatorFrame(QtGui.QFrame):
  def __init__(self, root, text, Text, Selector, width=10):
    QtGui.QFrame.__init__(self, parent=root)

    self.logger = logging.getLogger()

    Selector.action_add_list_navigator.triggered.connect(self.create)
    Selector.action_add_list_signals.triggered.connect(self.addSignals)

    # Connect to table view
    Selector.view_action_add_list_navigator.triggered.connect(self.create)
    Selector.view_action_add_list_signals.triggered.connect(self.addSignals)

    Selector.pbutton_add_list_navigator.clicked.connect(self.create)
    Selector.pbutton_add_list_regular_signal.clicked.connect(self.addSignals)

    Selector.addListCustomExpressionSignal.signal.connect(self.addCustomSignal)

    Box = QtGui.QGroupBox(text)

    hboxlayout_list_operations = QtGui.QHBoxLayout()
    hboxlayout_list_operations.setSpacing(0)
    hboxlayout_list_operations.setContentsMargins(1, 1, 1, 1)

    # vbox = QtGui.QVBoxLayout()
    # vbox.addStretch(0)
    CreateBtn = QtGui.QPushButton('Create')
    CreateBtn.setToolTip('Create')
    CreateBtn.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'load_file_24.png')))
    CreateBtn.clicked.connect(self.create)
    hboxlayout_list_operations.addWidget(CreateBtn, 0, Qt.AlignVCenter)

    self.GroupNameEntry = QtGui.QLineEdit(parent=self)
    self.GroupNameEntry.setText("Default")
    self.GroupNameEntry.setToolTip('Provide group name')
    hboxlayout_list_operations.addWidget(self.GroupNameEntry, 0, Qt.AlignVCenter)

    AddSignalBtn = QtGui.QPushButton('Add Signal')
    AddSignalBtn.setToolTip('Add Signal')
    AddSignalBtn.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'load_file_24.png')))
    AddSignalBtn.clicked.connect(self.addSignals)
    hboxlayout_list_operations.addWidget(AddSignalBtn, 0, Qt.AlignVCenter)

    self.ClientNrIncreasedSignal = SimpleSignal()
    self.ValueNrIncreasedSignal = SimpleSignal()


    for widget in (CreateBtn, self.GroupNameEntry, AddSignalBtn):
      widget.setFixedSize(75, 25)

    self.Text = Text
    self.Selector = Selector

    self.Imports = set()
    self.Imports.add('datavis')
    self.Imports.add('interface')

    self.Tags = dict(Client    = 'client',
                     Time      = 'time',
                     Value     = 'value',
                     Group     = Text.group_name,
                     Alias     = '',
                     Title     = '',
                     GroupName = 'Default',
                     ClientCounter = -1,
                     ValueCounter = -1,
                     CurrentClient = -1)
    self.Constructor = '%(Client)s%(CurrentClient)02d = ' \
                       'datavis.cListNavigator(title="%(Title)s")'
    self.AddClient   = 'self.sync.addClient(%(Client)s%(CurrentClient)02d )'
    self.GetSignal   = '%(Time)s_%(Alias)s, ' \
                       '%(Value)s_%(Alias)s' \
                       ' = %(Group)s.get_signal("%(OriginalAlias)s")'
    self.AddSignal   = '%(Client)s%(CurrentClient)02d.addsignal("%(OriginalAlias)s%(Index)s", ' \
                       '(%(Time)s_%(Alias)s, ' \
                       '%(Value)s_%(Alias)s%(Index)s), ' \
                       'groupname="%(GroupName)s")'
    self.AddCustomSignal   = '%(Client)s%(CurrentClient)02d.addsignal("%(OriginalAlias)s%(Index)s", ' \
                       '(%(Time)s_%(Alias)s, ' \
                       '%(Value)s_%(Alias)s), ' \
                       'groupname="%(GroupName)s")'
    self.GetCustomSignal = '%(Time)s_custom_%(Alias)s,' \
                           ' %(Value)s_custom_%(Alias)s,' \
                           ' = %(Group)s.get_signal("%(OriginalAlias)s")'

    self.GetCustomSignalWithRescale = '%(Time)s_custom_%(Alias)s,' \
                           ' %(Value)s_custom_%(Alias)s,' \
                           ' = %(Group)s.get_signal("%(OriginalAlias)s", **rescale_kwargs)'

    Box.setLayout(hboxlayout_list_operations)
    hbox = QtGui.QHBoxLayout()
    hbox.addWidget(Box)
    self.setLayout(hbox)
    pass

  def addCustomSignal(self, custom_signal_data):
    if self.Tags['ClientCounter'] < 0 or self.Tags['CurrentClient'] < 0:
      self.logger.error("Please add Plot/List Navigator first by clicking on Add Plot/ Add List, Signal(s) cannot be added before there isn't a Plot/List Navigator")
      return
    custom_signal_name = custom_signal_data[0]
    custom_signals_list= custom_signal_data[1]
    custom_signal_expression= custom_signal_data[2]
    custom_signal_unit = custom_signal_data[3]
    time_signal_name, expression = self.addCustomExpressionSupportingSignals(custom_signals_list,
                                                                             custom_signal_expression)
    custom_signal_expression = expression

    self.Tags['OriginalAlias'] = custom_signal_name
    self.Tags['Alias'] = custom_signal_name
    self.Tags['Group'] = self.Text.group_name
    self.Tags['GroupName'] = self.GroupNameEntry.text()
    Lines = []
    Lines.append("time_" + custom_signal_name + " = time_custom_" + time_signal_name)
    Lines.append("value_" + custom_signal_name + " = " + custom_signal_expression)

    Lines.append(self.AddCustomSignal % self.Tags)
    self.Text.add_lines(Lines)

  def create(self):
    self.incrementClientCounter()
    self.ClientNrIncreasedSignal.signal.emit()
    self.Tags['CurrentClient'] = self.Tags['ClientCounter']
    self.Text.add_modules(self.Imports)
    self.Text.add_lines((self.Constructor %self.Tags,
                         self.AddClient   %self.Tags))
    pass

  def addSignals(self):
    if self.Tags['ClientCounter'] < 0 or self.Tags['CurrentClient'] < 0:
      self.logger.error("Please add Plot/List Navigator first by clicking on Add Plot/ Add List, Signal(s) cannot be added before there isn't a Plot/List Navigator")
      return
    Lines = []
    if self.Selector.search_view_on is True:
      selections = self.Selector.getCurrentSelectionFromTreeViewSearch(Unit = False)
    else:
      selections = self.Selector.getCurrentSelection(Unit = False)
    for DevName, SigName in selections:
      self.incrementValueCounter()
      self.ValueNrIncreasedSignal.signal.emit()
      if len(SigName.split('[')) == 2:
        (SigName, Index) = SigName.split('[')
        self.Tags['Index'] = '[' + Index
      else:
        self.Tags['Index'] = ''
      self.Tags['OriginalAlias'] = self.Text.add_signal(DevName, SigName)
      self.Tags['Alias'] = re.sub('[^a-zA-Z0-9]+', '_', self.Text.add_signal(DevName, SigName))
      self.Tags['Group']     = self.Text.group_name
      self.Tags['GroupName'] = self.GroupNameEntry.text()
      Lines.append(self.GetSignal %self.Tags)
      Lines.append(self.AddSignal %self.Tags)
    self.Text.add_lines(Lines)
    pass

  # Retrive Signal information from table widget
  # def addSignalsFromTable(self):
  #   if self.Tags['ClientCounter'] < 0 or self.Tags['CurrentClient'] < 0:
  #     self.logger.error(
  #       "Please add Plot/List Navigator first by clicking on Add Plot/ Add List, Signal(s) cannot be added before "
  #       "there isn't a Plot/List Navigator")
  #     return
  #   Lines = []
  #   for DevName, SigName, Unit in self.Selector.getCurrentSelectionFromTreeViewSearch(Unit=True):
  #     self.incrementValueCounter()
  #     self.ValueNrIncreasedSignal.signal.emit()
  #     self.Tags['Index'] = ''
  #     if len(SigName.split('[:,')) == 2:
  #       (SigName, Index) = SigName.split('[')
  #       self.Tags['Index'] = '[' + Index
  #     alias = self.Text.add_signal(DevName, SigName)
  #     self.Tags['OriginalAlias'] = alias
  #
  #     self.Tags['Alias'] = re.sub('[^a-zA-Z0-9]+', '_', alias)
  #
  #     self.Tags['Group'] = self.Text.group_name
  #     self.Tags['Unit'] = Unit
  #
  #     Lines.append(self.GetSignal % self.Tags)
  #     Lines.append(self.AddSignal % self.Tags)
  #   self.Text.add_lines(Lines)
  #   pass

  def addCustomExpressionSupportingSignals(self, signals, expression):
    Lines = []
    first_signal = True
    for signal_custom_name, (DevName, SigName, Unit) in signals:
      self.incrementValueCounter()
      self.ValueNrIncreasedSignal.signal.emit()
      if len(SigName.split('['))==2:
          (SigName, Index) = SigName.split('[')
          self.Tags['Index'] = '[' + Index
      else:
          self.Tags['Index'] = ''

      alias = self.Text.add_signal(DevName, SigName)
      self.Tags['OriginalAlias'] = alias

      if '-' in alias:
        alias_signal_name, alias_device_name = alias.split("-")
        self.Tags['Alias'] = alias_device_name + "_" + alias_signal_name
      else:
        self.Tags['Alias'] = alias

      self.Tags['Alias'] = re.sub('[^a-zA-Z0-9]+', '_', self.Tags['Alias'])

      self.Tags['Group'] = self.Text.group_name
      self.Tags['GroupName'] = self.GroupNameEntry.text()
      if first_signal is True:
        Lines.append(self.GetCustomSignal %self.Tags)
      else:
        Lines.append(self.GetCustomSignalWithRescale % self.Tags)

      if not "value_custom_" + self.Tags['Alias']  in expression:
        expression = expression.replace("value_custom_" + SigName, "value_custom_" + self.Tags['Alias'])

      if first_signal is True:
        Lines.append("rescale_kwargs = {'ScaleTime': time_custom_" + self.Tags['Alias'] + "}")
        first_signal = False
    self.Text.add_lines(Lines)
    return self.Tags['Alias'], expression

  def update_from_metadata(self):
    """Updates the tagged counters when the script has been loaded from
    a file instead of being created manually during the current session
    """
    for _ in xrange(self.Text._number_LN):
      self.incrementClientCounter()
      self.ClientNrIncreasedSignal.signal.emit()
    self.Tags['CurrentClient'] = self.Tags['ClientCounter']
    for _ in xrange(self.Text._value_LN):
      self.incrementValueCounter()
      self.ValueNrIncreasedSignal.signal.emit()
    return

  def incrementClientCounter(self):
    self.Tags['ClientCounter'] += 1
    return

  def incrementValueCounter(self):
    self.Tags['ValueCounter'] += 1
    return

  def resetCounters(self):
    self.Tags['ClientCounter'] = -1
    self.Tags['ValueCounter'] = -1
    self.Tags['CurrentClient'] = -1
    return
