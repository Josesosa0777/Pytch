import logging

from PySide import QtGui, QtCore

class SimpleSignal(QtCore.QObject):
  signal = QtCore.Signal()

class cPlotNavigatorFrame(QtGui.QFrame):
  def __init__(self, root, text, Text, Selector):
    QtGui.QFrame.__init__(self)

    self.logger = logging.getLogger()

    Box = QtGui.QGroupBox(text)
    CreateBtn = QtGui.QPushButton('Create')
    AddAxisBtn = QtGui.QPushButton('Add Axis')
    AddSignalsBtn = QtGui.QPushButton('Add Signals')

    CreateBtn.clicked.connect(self.create)
    AddAxisBtn.clicked.connect(self.addAxis)
    AddSignalsBtn.clicked.connect(self.addSignals)

    vbox = QtGui.QVBoxLayout()
    vbox.addStretch(0)
    vbox.addWidget(CreateBtn)
    vbox.addWidget(AddAxisBtn)
    vbox.addWidget(AddSignalsBtn)
    vbox.addStretch(0)
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
    self.GetSignal   = '%(Time)s%(ValueCounter)02d,' \
                       ' %(Value)s%(ValueCounter)02d,' \
                       ' %(UnitVar)s%(ValueCounter)02d = ' \
                       '%(Group)s.get_signal_with_unit("%(Alias)s")'
    self.AddSignal   = '%(Client)s%(CurrentClient)02d.addSignal2Axis' \
                       '(%(Axis)s%(AxisCounter)02d, "%(Alias)s%(Index)s", ' \
                       '%(Time)s%(ValueCounter)02d, ' \
                       '%(Value)s%(ValueCounter)02d%(Index)s, ' \
                       'unit=%(UnitVar)s%(ValueCounter)02d)'
    self.ClientNrIncreasedSignal = SimpleSignal()
    self.ValueNrIncreasedSignal = SimpleSignal()
    Box.setLayout(vbox)

    hbox = QtGui.QHBoxLayout()
    hbox.addWidget(Box)
    self.setLayout(hbox)
    pass

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
      self.logger.error("Please add Plot/List Navigator first by clicking on Add Plot/ Add List,Axis cannot be added before there isn't a Plot/List Navigator")
      return
    self.incrementAxisCounter()
    self.Text.add_lines((self.AddAxis %self.Tags,))
    pass

  def addSignals(self):
    if self.Tags['ClientCounter'] < 0 or self.Tags['CurrentClient'] < 0:
      self.logger.error("Please add Plot/List Navigator first by clicking on Add Plot/ Add List, Signal(s) cannot be added before there isn't a Plot/List Navigator")
      return
    Lines = []
    for DevName, SigName, Unit in self.Selector.getCurrentSelection(Unit=True):
      self.incrementValueCounter()
      self.ValueNrIncreasedSignal.signal.emit()
      if len(SigName.split('['))==2:
          (SigName, Index) = SigName.split('[')
          self.Tags['Index'] = '[' + Index
      else:
          self.Tags['Index'] = ''
      self.Tags['Alias']   = self.Text.add_signal(DevName, SigName)
      self.Tags['Group']   = self.Text.group_name
      self.Tags['Unit']    = Unit

      Lines.append(self.GetSignal %self.Tags)
      Lines.append(self.AddSignal %self.Tags)
    self.Text.add_lines(Lines)
    pass
  
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
