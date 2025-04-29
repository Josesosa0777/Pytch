import logging

import os
import re
from PySide import QtGui, QtCore
from PySide.QtCore import Qt
from PySide.QtGui import QGroupBox, QIcon

IMAGE_DIRECTORY = os.path.join(os.path.dirname(__file__), "images")
class SimpleSignal(QtCore.QObject):
  signal = QtCore.Signal()

class cPlotNavigatorFrame(QtGui.QFrame):
  def __init__(self, root, text, Text, Selector):
    QtGui.QFrame.__init__(self)

    self.logger = logging.getLogger()
    Selector.action_add_plot_navigator.triggered.connect(self.create)
    Selector.action_add_plot_axes.triggered.connect(self.addAxis)
    Selector.action_add_plot_signals.triggered.connect(self.addSignals)

    Selector.view_action_add_plot_navigator.triggered.connect(self.create)
    Selector.view_action_add_plot_axes.triggered.connect(self.addAxis)
    Selector.view_action_add_plot_signals.triggered.connect(self.addSignals)

    Selector.pbutton_add_plot_navigator.clicked.connect(self.create)
    Selector.pbutton_add_axes.clicked.connect(self.addAxis)
    Selector.pbutton_add_plot_regular_signal.clicked.connect(self.addSignals)

    Selector.addPlotCustomExpressionSignal.signal.connect(self.addCustomSignal)
    Box = QtGui.QGroupBox(text)

    hboxlayout_plot_operations = QtGui.QHBoxLayout()
    hboxlayout_plot_operations.setContentsMargins(1, 1, 1, 1)

    CreateBtn = QtGui.QPushButton('Create')
    CreateBtn.setToolTip('Create')
    CreateBtn.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'load_file_24.png')))
    CreateBtn.clicked.connect(self.create)
    hboxlayout_plot_operations.addWidget(CreateBtn, 0, Qt.AlignVCenter)

    AddAxisBtn = QtGui.QPushButton('Add Axis')
    AddAxisBtn.setToolTip('Add Axis')
    AddAxisBtn.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'load_file_24.png')))
    AddAxisBtn.clicked.connect(self.addAxis)
    hboxlayout_plot_operations.addWidget(AddAxisBtn, 0, Qt.AlignVCenter)

    AddSignalsBtn = QtGui.QPushButton('Add Signals')
    AddSignalsBtn.setToolTip('Add Signals')
    AddSignalsBtn.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'load_file_24.png')))
    AddSignalsBtn.clicked.connect(self.addSignals)
    hboxlayout_plot_operations.addWidget(AddSignalsBtn, 0, Qt.AlignVCenter)

    for btn in (CreateBtn, AddAxisBtn, AddSignalsBtn):
      btn.setFixedSize(75, 25)


    self.Text = Text
    self.Selector = Selector

    self.Imports = set()
    self.Imports.add('datavis')
    self.Imports.add('interface')

    self.Tags = dict(Client   = 'client',
                     Axis     = 'axis',
                     Time     = 'time',
                     Value    = 'value',
                     Group    = Text.group_name,
                     Alias    = '',
                     UnitVar  = 'unit',
                     Title    = '',
                     ClientCounter = -1,
                     AxisCounter = -1,
                     ValueCounter = -1,
                     CurrentClient = -1)
    self.Constructor = '%(Client)s%(CurrentClient)02d = datavis.cPlotNavigator'\
                       '(title="%(Title)s")'
    self.AddClient   = 'self.sync.addClient(%(Client)s%(CurrentClient)02d)'
    self.AddAxis     = '%(Axis)s%(AxisCounter)02d = ' \
                        '%(Client)s%(CurrentClient)02d.addAxis()'
    self.GetSignal   = '%(Time)s_%(Alias)s,' \
                       ' %(Value)s_%(Alias)s,' \
                       ' %(UnitVar)s_%(Alias)s = ' \
                       '%(Group)s.get_signal_with_unit("%(OriginalAlias)s")'
    self.AddSignal   = '%(Client)s%(CurrentClient)02d.addSignal2Axis' \
                       '(%(Axis)s%(AxisCounter)02d, "%(OriginalAlias)s%(Index)s", ' \
                       '%(Time)s_%(Alias)s, ' \
                       '%(Value)s_%(Alias)s%(Index)s, ' \
                       'unit=%(UnitVar)s_%(Alias)s)'
    self.AddCustomSignal   = '%(Client)s%(CurrentClient)02d.addSignal2Axis' \
                       '(%(Axis)s%(AxisCounter)02d, "%(OriginalAlias)s%(Index)s", ' \
                       '%(Time)s_%(Alias)s, ' \
                       '%(Value)s_%(Alias)s, ' \
                       'unit=%(UnitVar)s_%(Alias)s)'
    self.GetCustomSignal   = '%(Time)s_custom_%(Alias)s,' \
                       ' %(Value)s_custom_%(Alias)s,' \
                       ' %(UnitVar)s_custom_%(Alias)s = ' \
                       '%(Group)s.get_signal_with_unit("%(OriginalAlias)s")'
    self.GetCustomSignalWithRescale = '%(Time)s_custom_%(Alias)s,' \
                       ' %(Value)s_custom_%(Alias)s,' \
                       ' %(UnitVar)s_custom_%(Alias)s = ' \
                       '%(Group)s.get_signal_with_unit("%(OriginalAlias)s", **rescale_kwargs)'
    self.ClientNrIncreasedSignal = SimpleSignal()
    self.ValueNrIncreasedSignal = SimpleSignal()
    Box.setLayout(hboxlayout_plot_operations)

    hbox = QtGui.QHBoxLayout()
    hbox.addWidget(Box)
    self.setLayout(hbox)
    pass


  def addCustomSignal(self, custom_signal_data):
    if self.Tags['ClientCounter'] < 0 or self.Tags['CurrentClient'] < 0:
      self.logger.error("Please add Plot/List Navigator first by clicking on Add Plot/ Add List, Signal(s) cannot be added before there isn't a Plot/List Navigator")
      return
    print(custom_signal_data)
    custom_signal_name = custom_signal_data[0]
    custom_signals_list= custom_signal_data[1]
    custom_signal_expression= custom_signal_data[2]
    custom_signal_unit = custom_signal_data[3]
    custom_signal_comment = custom_signal_data[4]
    time_signal_name, expression = self.addCustomExpressionSupportingSignals(custom_signals_list, custom_signal_expression)
    custom_signal_expression = expression

    self.Tags['OriginalAlias'] = custom_signal_name
    self.Tags['Alias'] = custom_signal_name
    self.Tags['Group'] = self.Text.group_name
    self.Tags['Unit'] = ''
    Lines = []
    Lines.append(custom_signal_comment)
    Lines.append("time_" + custom_signal_name + " = time_custom_" + time_signal_name)
    Lines.append("value_" + custom_signal_name + " = " + custom_signal_expression)
    Lines.append("unit_" + custom_signal_name + " = \"" + custom_signal_unit + "\"")
    Lines.append(self.AddCustomSignal % self.Tags)
    self.Text.add_lines(Lines)

  def create(self):
    self.incrementClientCounter()
    self.incrementAxisCounter()
    self.ClientNrIncreasedSignal.signal.emit()
    self.Tags['CurrentClient'] = self.Tags['ClientCounter']
    self.Text.add_modules(self.Imports)
    self.Text.add_lines((self.Constructor %self.Tags,
                         self.AddClient   %self.Tags,
                         self.AddAxis     %self.Tags))
    pass

  def addAxis(self):
    if self.Tags['ClientCounter'] < 0 or self.Tags['CurrentClient'] < 0:
      self.logger.error("Please add Plot/List Navigator first by clicking on Add Plot/ Add List, Axis cannot be added before there isn't a Plot/List Navigator")
      return
    self.incrementAxisCounter()
    self.Text.add_lines((self.AddAxis %self.Tags,))
    pass

  def addSignals(self):
    if self.Tags['ClientCounter'] < 0 or self.Tags['CurrentClient'] < 0:
      self.logger.error("Please add Plot/List Navigator first by clicking on Add Plot/ Add List, Signal(s) cannot be added before "
                  "there isn't a Plot/List Navigator")
      return
    Lines = []
    if self.Selector.search_view_on is True:
      selections = self.Selector.getCurrentSelectionFromTreeViewSearch(Unit = True)
    else:
      selections = self.Selector.getCurrentSelection(Unit = True)
    for DevName, SigName, Unit in selections:
      self.incrementValueCounter()
      self.ValueNrIncreasedSignal.signal.emit()
      self.Tags['Index'] = ''
      if len(SigName.split('[:,'))==2:
          (SigName, Index) = SigName.split('[')
          self.Tags['Index'] = '[' + Index
      alias = self.Text.add_signal(DevName, SigName)
      self.Tags['OriginalAlias'] = alias

      self.Tags['Alias'] = re.sub('[^a-zA-Z0-9]+', '_', alias)

      self.Tags['Group']   = self.Text.group_name
      self.Tags['Unit']    = Unit

      Lines.append(self.GetSignal %self.Tags)
      Lines.append(self.AddSignal %self.Tags)
    self.Text.add_lines(Lines)
    pass

  # def addSignalsFromTreeViewSearch(self):
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
    pass

  def addCustomExpressionSupportingSignals(self,signals, expression):
    Lines = []
    first_signal = True
    print("addCustomExpressionSupportingSignals")
    print(signals)
    for signal_custom_name, (DevName, SigName, Unit) in signals:
      self.incrementValueCounter()
      self.ValueNrIncreasedSignal.signal.emit()
      self.Tags['Index'] = ''
      if len(SigName.split('[:,'))==2:
          (SigName, Index) = SigName.split('[')
          self.Tags['Index'] = '[' + Index

      alias = self.Text.add_signal(DevName, SigName)
      self.Tags['OriginalAlias'] = alias

      if '-' in alias:
        alias_signal_name, alias_device_name = alias.split("-")
        self.Tags['Alias'] = alias_device_name + "_" + alias_signal_name
      else:
        self.Tags['Alias'] = alias

      self.Tags['Alias'] = re.sub('[^a-zA-Z0-9]+', '_', self.Tags['Alias'])

      self.Tags['Group'] = self.Text.group_name
      self.Tags['Unit'] = Unit
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
    for _ in xrange(self.Text._number_PN):
      self.incrementClientCounter()
      self.ClientNrIncreasedSignal.signal.emit()
    self.Tags['CurrentClient'] = self.Tags['ClientCounter']
    for _ in xrange(self.Text._number_axis):
      self.incrementAxisCounter()
    for _ in xrange(self.Text._value_PN):
      self.incrementValueCounter()
      self.ValueNrIncreasedSignal.signal.emit()
    return
    
  def incrementClientCounter(self):
    self.Tags['ClientCounter'] += 1
    return

  def incrementAxisCounter(self):
    self.Tags['AxisCounter'] += 1
    return

  def incrementValueCounter(self):
    self.Tags['ValueCounter'] += 1
    return

  def resetCounters(self):
    self.Tags['ClientCounter'] = -1
    self.Tags['AxisCounter'] = -1
    self.Tags['ValueCounter'] = -1
    self.Tags['CurrentClient'] = -1
    return
