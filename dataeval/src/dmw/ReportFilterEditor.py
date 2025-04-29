import logging

from PySide import QtGui, QtCore

from text.AnalyzeText import AnalyzeText
from textframe import TextFrame
from BatchFilterFrame import cTagSelector, SelectionError
from SyncAppEditor import Editor
from measproc.batchsqlite import filters, CountFilter
from datavis.interval_filter import Selector

class cReportFilterEditor(Editor):
  """Create analyze module."""
  TEMPLATE = 'analyzeTemplate.py'
  TextClass = AnalyzeText
  def __init__(self, root, Config, Control):
    Editor.__init__(self, root, Config, Control)

    self.Inits = []
    self.Config = Config

    self.Text.update_text_frame = self.TextFrame.update_text

    ControlFrame = QtGui.QFrame()
    AddBtn = QtGui.QPushButton('Add')

    self.OpenBtn.clicked.connect(self.open)
    self.SaveBtn.clicked.connect(self.save)
    self.UpdateBtn.clicked.connect(self.TextFrame.update_parser)
    self.ResetBtn.clicked.connect(self.reset)
    AddBtn.clicked.connect(self.add)



    self.UseLastTime = QtGui.QCheckBox('use last time')
    self.UseLastTime.setChecked(False)

    self.Filters = list([Name for Name, Filter in filters.iteritems()
                         if not isinstance(Filter, CountFilter)])
    grid = QtGui.QGridLayout()
    try:
      Batch = Control.getBatch()
    except AssertionError:
      Config.log('No batch setted, cannot upload ReFi', logging.WARNING)
      self.TagSelector = None
    else:
      self.TagSelector = cTagSelector(Batch, self.Filters)
      grid.addWidget(self.TagSelector, 0, 0)


    grid.addWidget(ControlFrame, 1, 0)

    button_vbox = QtGui.QHBoxLayout()
    dummy = QtGui.QFrame()
    button_vbox.addWidget(dummy)
    button_vbox.addWidget(AddBtn)
    ControlFrame.setLayout(button_vbox)
    ClearBtn = QtGui.QPushButton('Clear')
    ClearBtn.clicked.connect(self.TagSelector.clear)
    button_vbox.addWidget(AddBtn)
    button_vbox.addWidget(ClearBtn)
    dummy = QtGui.QFrame()
    button_vbox.addWidget(dummy)

    for Btn in (AddBtn, ClearBtn):
      Btn.setFixedSize(75, 25)

    main_vbox = QtGui.QVBoxLayout()
    main_vbox.addLayout(grid)
    main_vbox.addWidget(self.UseLastTime)
    frame = QtGui.QFrame()
    frame.setLayout(main_vbox)
    self.setCentralWidget(frame)

    pass


  def init(self):
    for init in self.Inits:
      init()
    return

  def add(self):
    if self.TagSelector is None:
      self.Config.log("Cannot add tags to analyze temp until there isnt't a " \
                      "batch setted", logging.ERROR)
    Filters = {}
    for Name in self.Filters:
      try:
        Tag = self.TagSelector.getCurrentSelection(Name)
      except SelectionError, e:
        self.Config.log(str(e), logging.WARNING)
        return
      else:
        if Tag is not None:
          Filters[Name] = "'%s'" %Tag
    if Filters:
      if self.UseLastTime.isChecked():
        Filters['start'] = 'self.batch.get_last_entry_time()'
      Entries = ', '.join(['%s=%s' %(k, v) for k, v in Filters.iteritems()])
      Lines = [
          'entries = self.batch.filter(%s)' %Entries,
          'self.interval_table.addEntries(entries)',
      ]
      self.Text.add_lines(Lines)
    self.TagSelector.reinit()
    return

