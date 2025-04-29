"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright:
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial
  property. We reserve all rights of disposal such as copying and passing on to
  third parties.
"""
__docformat__ = "restructuredtext en"

import sys

from PySide import QtGui, QtCore

from Synchronizer import cNavigator
from PlotNavigator import QT_KEYS_TO_STRING

DefIntervalPreTimes  = -2.0, -1.0
DefIntervalPostTimes =  1.0,  2.0

class cReportNavigator(cNavigator):
  """Create voiting table from the added Reports."""
  def __init__(self, title='', color='g',
               IntervalPreTimes=DefIntervalPreTimes,
               IntervalPostTimes=DefIntervalPostTimes):
    """
    :Parameters:
      title : str
        Main title of the window.
      color : str
        color of the ROI
      IntervalPreTimes : list
        Container of the seek times before the selected interval
        [-2.0, -1.0]
      IntervalPostTimes : list
        Container of the seek times after the selected interval
        [1.0, 2.0]
    """
    cNavigator.__init__(self)

    self.NeutralInterval = (0, 0)
    """:type: tuple
    Neutral identifier for the actual interval:
    IntervalLower, IntervalUpper)"""
    self.color = color
    """:type: str
    Color of the interval mark."""
    self.IntervalPreTimes  = []
    """:type: list
    Container of the seek times before the selected interval
    [[-2.0, ,'<--'],[-1.0, ,'<-'],]"""
    IntervalPreTimes = list(IntervalPreTimes)
    IntervalPreTimes.sort()
    Len = len(IntervalPreTimes)
    for i, Time in enumerate(IntervalPreTimes):
      Arrow = '<' + '-' * (Len - i)
      self.IntervalPreTimes.append([Time, Arrow])

    self.IntervalPostTimes = []
    """:type: list
    Container of the seek times after the selected interval
    [[1.0, ,'->'],[2.0, ,'-->'],]"""
    IntervalPostTimes = list(IntervalPostTimes)
    IntervalPostTimes.sort()
    for i, Time in enumerate(IntervalPostTimes):
      Arrow = '-' * (i + 1) + '>'
      self.IntervalPostTimes.append([Time, Arrow])

    self.ChangingCommentBtn = None

    self.NoteBook = QtGui.QTabWidget()

    self.setCentralWidget(self.NoteBook)

    VoteFrame = QtGui.QFrame()
    VoteLayout = QtGui.QGridLayout()

    VoteLabel = QtGui.QLabel('Vote')
    VoteLayout.addWidget(VoteLabel, 0, 0, 1, 2)

    self.VoteOption = QtGui.QLineEdit()
    VoteLayout.addWidget(self.VoteOption, 0, 2)

    VoteAddBtn = QtGui.QPushButton('add')
    RmAddBtn = QtGui.QPushButton('rm')

    VoteAddBtn.clicked.connect(self.onAddVoteOption)
    RmAddBtn.clicked.connect(self.onRmVoteOption)

    VoteLayout.addWidget(VoteAddBtn, 0, 3)
    VoteLayout.addWidget(RmAddBtn, 0, 4)

    ReportCtrlLabel = QtGui.QLabel('Report Comment')
    VoteLayout.addWidget(ReportCtrlLabel, 2, 0, 1, 2)

    self.ReportCommentEdit = QtGui.QLineEdit()
    self.ReportCommentEdit.returnPressed.connect(self.onReportComment)
    VoteLayout.addWidget(self.ReportCommentEdit, 2, 2, 1, 3)

    AddBtn = QtGui.QPushButton('Add Interval')
    RemoveBtn = QtGui.QPushButton('Remove Interval')

    AddBtn.clicked.connect(self.onAddInterval)
    RemoveBtn.clicked.connect(self.onRemoveInterval)

    VoteLayout.addWidget(AddBtn, 3, 0)
    VoteLayout.addWidget(RemoveBtn, 3, 1)

    VoteFrame.setLayout(VoteLayout)

    BottomDockWidget = QtGui.QDockWidget()
    BottomDockWidget.setWidget(VoteFrame)

    self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, BottomDockWidget)
    pass

  def addIntervalList(self, Name, IntervalList):
    """
    Add IntervalList to create new seek table.

    :Parameters:
      Name : str
        Name of the seek table.
      IntervalList : `measproc.cIntervalList`
        IntervalList to display.
    """
    ScrollFrame = QtGui.QScrollArea()
    ScrollFrame.setWidgetResizable(True)
    Page = QtGui.QFrame()

    Page.ActualFrame = self.NeutralInterval
    Page.Frames      = {self.NeutralInterval : Page}
    PageLayout = QtGui.QVBoxLayout()
    for k, Interval in enumerate(IntervalList):
      Lower, Upper = Interval
      Frame        = QtGui.QFrame()
      FrameLayout = QtGui.QHBoxLayout()
      Label = QtGui.QLabel('%3d' %k)
      FrameLayout.addWidget(Label)
      for Offset, Arrow in self.IntervalPreTimes:
        ArrowBtn = QtGui.QPushButton(Arrow)
        ArrowBtn.clicked.connect(lambda n=Name, i=Interval, lu=0, o=Offset:
                                        self.onButtonClick(n, i, lu, o))
        FrameLayout.addWidget(ArrowBtn)
      LowerTimeBtn = QtGui.QPushButton('%.2f' %IntervalList.Time[Lower])
      UpperTimeBtn = QtGui.QPushButton('%.2f' %IntervalList.Time[Upper-1])

      LowerTimeBtn.clicked.connect(lambda n=Name, i=Interval, lu=0:
                                   self.onButtonClick(n, i, lu))
      UpperTimeBtn.clicked.connect(lambda n=Name, i=Interval, lu=1:
                                   self.onButtonClick(n, i, lu))

      FrameLayout.addWidget(LowerTimeBtn)
      FrameLayout.addWidget(UpperTimeBtn)

      for Offset, Arrow in self.IntervalPostTimes:
        ArrowBtn = QtGui.QPushButton(Arrow)
        ArrowBtn.clicked.connect(lambda n=Name, i=Interval, lu=1, o=Offset:
                                 self.onButtonClick(n, i, lu, o))
        FrameLayout.addWidget(ArrowBtn)
      Frame.setLayout(FrameLayout)
      Page.Frames[Interval] = Frame
      PageLayout.addWidget(Frame)
    IntCommentLabel = QtGui.QLabel('Interval Comment')
    VoteLayout = QtGui.QHBoxLayout()
    VoteLayout.addWidget(IntCommentLabel)

    Page.CommentEdit = QtGui.QLineEdit()
    Page.CommentEdit.returnPressed.connect(self.saveComment)
    VoteLayout.addWidget(Page.CommentEdit)
    PageLayout.addLayout(VoteLayout)
    Page.IntervalList = IntervalList
    Page.setLayout(PageLayout)
    ScrollFrame.setWidget(Page)
    self.NoteBook.addTab(ScrollFrame, Name)
    pass

  def onAddInterval(self):
    """Handle Add button click on Interval Control frame: Get the actual Region
    Of Interest and call `addInterval` with the ROI and the actual page name if
    the instance is added to a `cSynchronizer`."""
    PageIndex = self.NoteBook.currentIndex()
    PageName = self.NoteBook.tabText(PageIndex)
    self.addInterval(PageName, self.ROIstart, self.ROIend)
    pass

  def onRemoveInterval(self):
    """Handle Remove button on the IntervalControl frame: call removeInterval
    with the `ActualFrame`."""
    ScrollWidget = self.NoteBook.currentWidget()
    Page = ScrollWidget.widget()
    TabIndex = self.NoteBook.currentIndex()
    PageName = self.NoteBook.tabText(TabIndex)
    if Page.ActualFrame != self.NeutralInterval:
      self.removeInterval(PageName, Page.ActualFrame)

    for k, Interval in enumerate(Page.Report.IntervalList):
      Frame = Page.Frames[Interval]
      Labels = findWidgets(Frame, QtGui.QLabel)
      for Label in Labels:
        Label.setText(unicode(k))
    pass

  def onButtonClick(self, PageName, Interval, LowerUpper, Offset=0.0):
    """
    Handle seek table button click: call `seekCallback` and `setROICallback` if
    the instance is added to a `cSynchronizer`.

    :Parameters:
      PageName : str
        Name of the `NoteBook` page.
      Interval : tuple
        (IntervalLowerBound, IntervalUpperBound)
      LowerUpper : int
        Interval bound index: 0 means lower, 1 means upper.
      Offset : float
         Offset in [s] to be added to the seek time.
    :Exceptions:
      ValueError
        If `NoteBook` does not contains `PageName` page.
      KeyError
        If self.NoteBook.page(`PageName`).Frames does not contains `Interval`.
    """

    Page = self.findPage(PageName)
    Time = Page.IntervalList.Time
    Lower, Upper = Interval
    Lower = Time[Lower]
    Upper = Time[Upper-1]
    if LowerUpper == 0:
      self.Time = Lower
    else:
      self.Time = Upper
    self.Time += Offset

    self.markFrame(PageName, Interval)
    self.seekSignal.signal.emit(self.Time)
    self.setROISignal.signal.emit(self, Lower, Upper, self.color)
    pass

  def markFrame(self, PageName, Interval):
    """
    Mark the frame on the `PageName` page wich belongs to the `Interval` and
    call `setROICallback` if the instance is added to a `cSynchronizer`.

    :Parameters:
      PageName : str
    :Exceptions:
      ValueError
        If `NoteBook` does not contains `PageName` page.
    """
    Page = self.findPage(PageName)
    Frames = Page.Frames.values()
    Frame = Page.Frames[Interval]
    Buttons = findWidgets(Frame, QtGui.QPushButton)
    for Button in Buttons:
      changeColor(Button, QtCore.Qt.green)
    Frames.remove(Frame)
    for Frame in Frames:
      FrameColor  = getWindowColor(Frame)
      Buttons = findWidgets(Frame, QtGui.QPushButton)
      for Button in Buttons:
        changeColor(Button, FrameColor)
    Lower, Upper = Interval
    Time = Page.IntervalList.Time
    Lower = Time[Lower]
    Upper = Time[Upper-1]
    if Interval != self.NeutralInterval:
      self.setROISignal.signal.emit(self, Lower, Upper, self.color)
    Page.ActualFrame = Interval
    pass

  def markInterval(self, PageName, TimeStamp):
    """
    Find the interval on the `PageName` page wich contains the `TimeStamp` and
    call `markFrame`.

    :Parameters:
      PageName : str
      TimeStamp : float
    :Exceptions:
      ValueError
        If `NoteBook` does not contains `PageName` page.
    """
    Page = self.findPage(PageName)
    Time = Page.IntervalList.Time
    try:
      index = min(Time.searchsorted(TimeStamp), Time.size-1)
      Interval = Page.IntervalList.findInterval(index)
    except ValueError:
      try:
        index = max(index-1, 0)
        Interval = Page.IntervalList.findInterval(index)
      except ValueError:
        Interval = self.NeutralInterval
    self.markFrame(PageName, Interval)
    pass

  def seek(self, Time):
    cNavigator.seek(self, Time)
    PageIndex = self.NoteBook.currentIndex()
    PageName = self.NoteBook.tabText(PageIndex)
    self.markInterval(PageName, Time)
    pass

  def play(self, Time):
    cNavigator.play(self, Time)
    PageIndex = self.NoteBook.currentIndex()
    PageName = self.NoteBook.tabText(PageIndex)
    self.markInterval(PageName, Time)
    pass

  def start(self):
    self.show()
    pass

  def addReport(self, Name, Report):
    """
    Add `Report` to create new voiting table.

    :Parameters:
      Name : str
        Name of the voiting table.
      Report : `measproc.cReport`
        Report to display.
    """

    Name = '#%3s %s' %(len(Report.IntervalList), Name)
    self.addIntervalList(Name, Report.IntervalList)
    Page = self.findPage(Name)
    Page.Report = Report
    for Interval in Report.IntervalList:
      Frame = Page.Frames[Interval]
      self.addReportButtons(Report, Frame, Interval, Report.getVotes())
    pass

  def editComment(self, Background=QtCore.Qt.green):
    """
    Open an Entry for editing the Comment field of `IntervalAttr`.

    :Parameters:
      Event : event
      IntervalAttr : dict
      Background : str
        Name of the background color. Default value is lightgreen
    """
    ScrolLWidget = self.NoteBook.currentWidget()
    Page = ScrolLWidget.widget()
    CommentBtn = self.sender()
    changeColor(CommentBtn, Background)
    Page.CommentEdit.setFocus()
    self.ChangingCommentBtn = CommentBtn
    pass

  def saveComment(self):
    """
    Save the `Comment` into Comment field of `IntervalAttr`, close `Toplevel`
    and set to lightgreen the backgroud color of `Button`

    :Parameters:
      Event : event
      IntervalAttr : dict
      Comment : `String`
      Button : `QtGui.QPushButtonButton`
      Background : str
        Name of the background color
    """
    ScrolLWidget     = self.NoteBook.currentWidget()
    Page = ScrolLWidget.widget()
    for Interval in Page.Report.IntervalList:
      Buttons = findWidgets(Page.Frames[Interval].VoteFrame, QtGui.QPushButton)
      for Button in Buttons:
        if Button == self.ChangingCommentBtn:
          IntervalAttr = Page.Report.IntervalAttrs[Interval]
    IntervalAttr['Comment'] = Page.CommentEdit.text()
    Color = getWindowColor(self.ChangingCommentBtn)
    changeColor(self.ChangingCommentBtn, Color)
    self.ChangingCommentBtn = None
    pass

  def addInterval(self, PageName, Lower, Upper):
    """
    Add a [`Lower`, `Upper`] interval to the `PageName` page of the `NoteBook`.

    :Parameters:
      PageName : str
      Lower : int
      Upper : int
    :Exceptions:
      ValueError
        If `NoteBook` does not contains `PageName` page.
    """
    Page = self.findPage(PageName)
    if Page:
      Time     = Page.IntervalList.Time
      Lower    = min(Time.searchsorted(Lower), Time.size-1)
      Upper    = min(Time.searchsorted(Upper), Time.size-1) + 1
      Interval = (Lower, Upper)
      if Interval not in Page.Frames:
        Frame = QtGui.QFrame()
        FrameLayout = QtGui.QHBoxLayout()
        Label = QtGui.QLabel('%3d' %len(Page.Report.IntervalList))
        FrameLayout.addWidget(Label)
        for Offset, Arrow in self.IntervalPreTimes:
          ArrowBtn = QtGui.QPushButton(Arrow)
          ArrowBtn.clicked.connect(lambda n=PageName, i=Interval, lu=0,
                                          o=Offset:
                                          self.onButtonClick(n, i, lu, o))
          FrameLayout.addWidget(ArrowBtn)
        LowerTimeBtn = QtGui.QPushButton('%.2f' %Time[Lower])
        UpperTimeBtn = QtGui.QPushButton('%.2f' %Time[Upper-1])

        LowerTimeBtn.clicked.connect(lambda n=PageName, i=Interval, lu=0:
                                            self.onButtonClick(n, i, lu))
        UpperTimeBtn.clicked.connect(lambda n=PageName, i=Interval, lu=1:
                                            self.onButtonClick(n, i, lu))

        FrameLayout.addWidget(LowerTimeBtn)
        FrameLayout.addWidget(UpperTimeBtn)

        for Offset, Arrow in self.IntervalPostTimes:
          ArrowBtn = QtGui.QPushButton(Arrow)
          ArrowBtn.clicked.connect(lambda n=PageName, i=Interval, lu=1,
                                          o=Offset:
                                          self.onButtonClick(n, i, lu, o))
          FrameLayout.addWidget(ArrowBtn)
        Frame.setLayout(FrameLayout)
        Page.IntervalList.add(Lower, Upper)
        Page.Frames[Interval] =  Frame
      else:
        Interval = self.NeutralInterval
      if Interval != self.NeutralInterval:
        Frame  = Page.Frames[Interval]
        Report = Page.Report
        Report.addInterval(Interval)
        self.addReportButtons(Report, Frame, Interval, Report.getVotes())
        PageLayout = Page.layout()
        PageLayout.insertWidget(PageLayout.count() -1, Frame)
    else:
      raise ValueError('NoteBook does not contains %s page' %PageName)
    pass

  def addVoteOption(self, Report, Layout, Interval, Vote):
    CB = QtGui.QCheckBox(Vote)
    CB.toggled.connect(lambda checked, i=Interval, v=Vote:
                              self.onVote(checked, i, v))
    Layout.insertWidget(Layout.count() -1, CB)
    CB.Interval = Interval
    CB.Vote = Vote
    if Report.checkVote(Interval, Vote):
      CB.setChecked(True)
    return

  def addReportButtons(self, Report, Frame, Interval, Votes):
    """
    Add report edit button beside the intervallist buttons.

    :Parameters:
      Report : `measproc.cReport `
      Frame : `QtGui.QFrame`
      Interval : tuple
        (LowerBound<int>, UpperBound<int>)
      Votes : set
    """
    FrameLayout = Frame.layout()
    VoteFrame = QtGui.QFrame()
    VoteFrameLayout = QtGui.QHBoxLayout()
    Frame.VoteFrame = VoteFrame
    for Vote in Votes:
      self.addVoteOption(Report, VoteFrameLayout, Interval, Vote)
    IntervalAttr = Report.IntervalAttrs[Interval]
    Button = QtGui.QPushButton('Comment')
    Button.clicked.connect(self.editComment)
    VoteFrameLayout.addWidget(Button)
    if IntervalAttr['Comment']:
      changeColor(Button, QtCore.Qt.cyan)
    VoteFrame.setLayout(VoteFrameLayout)
    VoteFrameLayout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
    FrameLayout.addWidget(VoteFrame)
    FrameLayout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
    Frame.setLayout(FrameLayout)
    pass

  def removeInterval(self, PageName, Interval):
    """
    :Parameters:
      PageName : str
        Name of the `NoteBook` page.
      Interval : tuple
        (Lower<int>, Upper<int>)
    :Exceptions:
      ValueError
        If `NoteBook` does not contains `PageName` page.
    """
    Page  = self.findPage(PageName)
    Time  = Page.IntervalList.Time
    Frame = Page.Frames[Interval]
    Frame.close()
    del Page.Frames[Interval]
    Page.IntervalList.remove(*Interval)
    FirstTime = Time[0]
    self.setROISignal.signal.emit(self, FirstTime, FirstTime, self.color)
    Page.ActualFrame = self.NeutralInterval
    Page  = self.findPage(PageName)
    Page.Report.removeInterval(Interval)
    pass

  def onAddVoteOption(self):
    ScrollWidget = self.NoteBook.currentWidget()
    Page     = ScrollWidget.widget()
    VoteOption = self.VoteOption.text()
    if VoteOption:
      Page.Report.addVote(VoteOption)
      for Interval in Page.Report.IntervalList:
        VoteFrame = Page.Frames[Interval].VoteFrame
        self.addVoteOption(Page.Report, VoteFrame.layout(), Interval,
                           VoteOption)
    return

  def onRmVoteOption(self):
    ScrolLWidget     = self.NoteBook.currentWidget()
    Page = ScrolLWidget.widget()
    VoteOption = self.VoteOption.text()
    if VoteOption in Page.Report.ReportAttrs:
      Page.Report.rmVote(VoteOption)
      for Interval in Page.Report.IntervalList:
        VoteFrame = Page.Frames[Interval].VoteFrame
        CheckBoxes = findWidgets(VoteFrame, QtGui.QCheckBox)
        for CheckBox in CheckBoxes:
          if CheckBox.Vote == VoteOption:
            CheckBox.close()
    else:
      self.logger.warning('No %s in Votes \n' %VoteOption)
    return

  def onVote(self, Checked, Interval, Vote):
    """
    :Parameters:
      Interval : tuple
        (Lower<int>, Upper<int>)
      Vote : str
        Vote to the interval 'valid', 'invalid' or 'missed'
    """

    ScrollWidget = self.NoteBook.currentWidget()
    Page     = ScrollWidget.widget()
    Page.Report.toggle(Interval, Vote)
    pass

  def closeEvent(self, event):
    """Event handler for close event."""
    for Index in range(self.NoteBook.count()):
      self.saveReport(Index)
    cNavigator.closeEvent(self, event)
    pass

  def onReportComment(self):
    """
    :Parameters:
      Event : event
    """
    ScrollWidget = self.NoteBook.currentWidget()
    Page     = ScrollWidget.widget()
    Attrs    = Page.Report.ReportAttrs
    Attrs['Comment'] = self.ReportCommentEdit.text()
    pass

  def saveReport(self, Index):
    """
    Save the Report of the `PageName` page of the `NoteBook`

    :Parameters:
      Interval : tuple
        (Lower<int>, Upper<int>)
    :Exceptions:
      ValueError
        If `NoteBook` does not contains `PageName` page.
    """
    ScrollWidget = self.NoteBook.widget(Index)
    Page = ScrollWidget.widget()
    Page.Report.save()
    pass

  def findPage(self, Name):
    for index in range(self.NoteBook.count()):
      if self.NoteBook.tabText(index) == Name:
        ScrolWidget = self.NoteBook.widget(index)
        return ScrolWidget.widget()
    return None

def findWidgets(Frame, WidgetType):
    for child in Frame.children():
      if type(child) == WidgetType:
        yield child
    return

def changeColor(widget, color):
    if not widget.autoFillBackground():
      widget.setAutoFillBackground(True)
    Palette = widget.palette()
    Palette.setColor(widget.backgroundRole(), color)
    widget.setPalette(Palette)
    return

def getWindowColor(widget):
    Palette = widget.palette()
    return Palette.color(QtGui.QPalette.Window)

if __name__ == '__main__':
  import sys
  import numpy
  import measproc
  import optparse

  app = QtGui.QApplication([])

  parser = optparse.OptionParser()
  parser.add_option('-p', '--hold-navigator',
                    help='Hold the navigator, default is %default',
                    default=False,
                    action='store_true')
  opts, args = parser.parse_args()

  t = numpy.arange(0.0, 20.0, 0.01)
  y = numpy.sin(t)
  z = numpy.cos(t)
  i = measproc.cEventFinder.compExtSigScal(t, y, measproc.greater, 0.5)
  j = measproc.cEventFinder.compExtSigScal(t, z, measproc.greater, 0.5)
  navi = cReportNavigator('foo')

  report1 = measproc.cIntervalListReport(i, 'TestReport')
  report2 = measproc.cIntervalListReport(j, 'TestReport')
  navi.addReport('baz', report1)
  navi.addReport('bar', report2)
  navi.start()
  navi.addInterval('#  4 baz',  17.0, 19.0)
  navi.setROI(navi, 2.0, 5.0, '')
  sys.exit(app.exec_())