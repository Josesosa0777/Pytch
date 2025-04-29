import logging

from PySide import QtGui, QtCore

from PlotNavigatorFrame import SimpleSignal

class cListNavigatorFrame(QtGui.QFrame):
  def __init__(self, root, text, Text, Selector, width=10):
    QtGui.QFrame.__init__(self, parent=root)

    self.logger = logging.getLogger()
    Box = QtGui.QGroupBox(text)
    vbox = QtGui.QVBoxLayout()
    vbox.addStretch(0)
    CreateBtn = QtGui.QPushButton('Create')
    CreateBtn.clicked.connect(self.create)
    vbox.addWidget(CreateBtn)
    self.GroupNameEntry = QtGui.QLineEdit(parent=self)
    self.GroupNameEntry.setText("Default")
    vbox.addWidget(self.GroupNameEntry)

    AddSignalBtn = QtGui.QPushButton('Add Signal')
    AddSignalBtn.clicked.connect(self.addSignals)
    self.ClientNrIncreasedSignal = SimpleSignal()
    self.ValueNrIncreasedSignal = SimpleSignal()
    vbox.addWidget(AddSignalBtn)
    vbox.addStretch(0)

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
    self.GetSignal   = '%(Time)s%(ValueCounter)02d, ' \
                       '%(Value)s%(ValueCounter)02d' \
                       ' = %(Group)s.get_signal("%(Alias)s")'
    self.AddSignal   = '%(Client)s%(CurrentClient)02d.addsignal("%(Alias)s%(Index)s", ' \
                       '(%(Time)s%(ValueCounter)02d, ' \
                       '%(Value)s%(ValueCounter)02d%(Index)s), ' \
                       'groupname="%(GroupName)s")'
    Box.setLayout(vbox)
    hbox = QtGui.QHBoxLayout()
    hbox.addWidget(Box)
    self.setLayout(hbox)
    pass

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
    for DevName, SigName in self.Selector.getCurrentSelection(Unit=False):
      self.incrementValueCounter()
      self.ValueNrIncreasedSignal.signal.emit()
      if len(SigName.split('[')) == 2:
        (SigName, Index) = SigName.split('[')
        self.Tags['Index'] = '[' + Index
      else:
        self.Tags['Index'] = ''
      self.Tags['Alias']     = self.Text.add_signal(DevName, SigName)
      self.Tags['Group']     = self.Text.group_name
      self.Tags['GroupName'] = self.GroupNameEntry.text()
      Lines.append(self.GetSignal %self.Tags)
      Lines.append(self.AddSignal %self.Tags)
    self.Text.add_lines(Lines)
    pass
  
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
