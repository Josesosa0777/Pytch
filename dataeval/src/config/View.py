import os

from PySide import QtGui

import section
from datavis.figlib import parseGeometryString
from interface.Interfaces import iView
from text.ViewText import ViewText
from datavis.RecordingService import mix_recorded_videos

def rectanglesOverlap(rect1, rect2):
  """
  Check if any of rect1's four vertices is in the area defined by rect2.
  The function is asymmetrical: result may depend on the parameter order.
  """
  # Convert from (x, y, w, h) to (x1, y1, x2, y2) format
  rect1 = (rect1[0], rect1[1], rect1[2]+rect1[0], rect1[3]+rect1[1])
  rect2 = (rect2[0], rect2[1], rect2[2]+rect2[0], rect2[3]+rect2[1])
  # Check intersection with all four vertices
  overlap = ((rect1[0] >= rect2[0] and rect1[0] <= rect2[2] and rect1[1] >= rect2[1] and rect1[1] <= rect2[3]) or
             (rect1[2] >= rect2[0] and rect1[2] <= rect2[2] and rect1[1] >= rect2[1] and rect1[1] <= rect2[3]) or
             (rect1[0] >= rect2[0] and rect1[0] <= rect2[2] and rect1[3] >= rect2[1] and rect1[3] <= rect2[3]) or
             (rect1[2] >= rect2[0] and rect1[2] <= rect2[2] and rect1[3] >= rect2[1] and rect1[3] <= rect2[3]))
  return overlap


class cSection(section.cSection):
  Interface = iView
  NeedStatuses = True
  Seeks = []
  Capture = ''
  record_intervals = None
  is_remixing = False
  record_path = ''

  def initConfig(self, Modules):
    self._initModules(Modules)
    return

  def report(self, ReportPath):
    "set REPORT as interface.Report for view modules"
    self.Config.set('General', 'Report', ReportPath)
    return

  def seek(self, Seek):
    "seek to SEEK and set X_MIN, X_MAX and Y_MIN, Y_MAX limits,\n"\
    "all the limits are optional\n\n"\
    "--seek 5           seek to 5.0\n"\
    "--seek 5lim1,2.31  seek to 5.0 and set x_min to 1.0, x_max to 2.31\n"\
    "--seek lim-1,,,-5  set x_min to -1.0, y_max to -5"
    self.Seeks.append(Seek)
    return

  def capture(self, CapDir):
    "Save the navigator captures under CAPRURE_DIR/SEEK"
    self.Capture = CapDir
    if not os.path.isdir(CapDir):
      os.makedirs(CapDir)
    return

  def layout(self, ModuleId, WindowId, Layout):
    "set the layout of WINDOW_ID navigator of MODULE with PARAM to LAYOUT\n\n"\
    "--layout viewFoo-DefParam VideoPlayer 22x33+42+67"
    Section = ModuleId + '.layout'
    if not self.has_section(Section):
      self.add_section(Section)
    self.Config.set(Section, WindowId, Layout)
    return

  def record(self, start, end, path):
    """records the navigator output between the START and END timestamps
     into a video file, to be stored at PATH"""
    if not os.path.isdir(path):
      os.makedirs(path)
    self.record_path = path
    self.record_intervals = (float(start), float(end))
    return

  def build(self, Manager):
    Sync = Manager.get_sync()
    self.loadLayout(Manager)

    for SeekAndLim in self.Seeks:
      # Separate parameters for seek and axes' limits
      SeekAndLimSplit = SeekAndLim.split('lim')
      Seek = SeekAndLimSplit[0]
      Lim  = SeekAndLimSplit[1] if len(SeekAndLimSplit) > 1 else ''
      # Seek
      if Seek:
        Manager.seek(Seek)
      # Set limits of axes
      if Lim:
        Manager.set_axes_limits(Lim)
      # Create screenshots
      if self.Capture:
        CapDir = os.path.join(self.Capture, SeekAndLim)
        Sync.capture(CapDir)
    
    if self.record_intervals is not None:
      # Get the meas name for the filename
      meas_name =  Manager.get_source().getBaseName().split('.')[0]
      # then put it together with the interval :
      filename_prefix = "%s_(%s-%s)_" % (meas_name, self.record_intervals[0],
                                       self.record_intervals[1])
      #Expand path with meas name
      self.record_path = os.path.join(self.record_path, meas_name)
      if not os.path.exists(self.record_path):
        os.makedirs(self.record_path)
      Sync.start_client_recording(self.record_path, filename_prefix)
      Sync.play_by_step(self.record_intervals[0], self.record_intervals[1])
      Sync.stop_client_recording()
      if self.is_remixing:
        mix_recorded_videos(self.record_path, filename_prefix)

    self.Config.log('View session started.')
    return

  def save(self, Manager):
    #In ViewControl there is only manager if navigators started, but it was
    #can be useful, to save the manager independent config (for example: meas
    #channels) -> check the existence of manager
    if Manager:
      self.saveLayout(Manager)
    return

  def loadLayout(self, Manager):
    # Get the geometry of the displays (list of tuples)
    displayRects = []
    desktop = QtGui.QApplication.desktop()
    for id_ in range(desktop.screenCount()):
      rect = desktop.availableGeometry(id_)
      displayRects.append(rect.getRect())
    # Loop on all clients
    Sync = Manager.get_sync()
    for Module in Sync.getModuleNames():
      for WindowId in Sync.getModuleWindowIds(Module):
        Section = Module + '.layout'
        if    self.Config.has_section(Section)\
          and self.Config.has_option(Section, WindowId):
          Client = Sync.getClient(Module, WindowId)
          Layout = self.Config.get(Section, WindowId)
          # Set window layout - only if it fits at least one of the screens
          clientWindowRect = parseGeometryString(Layout)
          for displayRect in displayRects:
            if rectanglesOverlap(clientWindowRect, displayRect):
              Client.setWindowGeometry(Layout)
              break
    return

  def saveLayout(self, Manager):
    Sync = Manager.get_sync()
    Modules = Sync.getModuleNames()
    if not Modules: return

    for Module in Sync.getModuleNames():
      Section = Module + '.layout'
      if self.Config.has_section(Section):
        self.Config.remove_section(Section)
      self.Config.add_section(Section)
      for WindowId in Sync.getModuleWindowIds(Module):
        Client = Sync.getClient(Module, WindowId)
        Layout = Sync.getLayout(Client)
        self.Config.set(Section, WindowId, Layout)
    return

  def procArgs(self, Args):
    if Args.report:
      self.report(Args.report)
    for Seek in Args.seek:
      self.seek(Seek)
    if Args.capture:
      self.capture(Args.capture)
    for Module, WindowId, Layout in Args.layout:
      self.layout(Module, WindowId, Layout)
    for start, end, path in Args.record:
      self.record(start, end, path)
    if Args.combine:
      self.is_remixing = True
    return

  def clearSectionConfig(self):
    for Section in self.getSessionSections():
        self.Config.remove_section(Section)
    return

  def getSessionSections(self):
    return [Section for Section in self.Config.sections()
            if Section.endswith('.layout')]

  def removeModule(self):
    SessionSections = self.getSessionSections()
    for SessionSection in SessionSections:
      if SessionSection.startswith(ViewText.PREFIX):
        self.Config.remove_section(SessionSection)
    return

  @classmethod
  def addArguments(cls, Parser):
    Group = Parser.add_argument_group(title='view')
    Group.add_argument('--report',
                        help=cls.report.__doc__)

    Group = Parser.add_argument_group(title='seek')
    Group.add_argument('--seek', metavar='SEEKlimX_MIN,X_MAX,Y_MIN,Y_MAX',
                        action='append', default=[], help=cls.seek.__doc__)
    Group.add_argument('--capture', metavar='CAPTURE_DIR',
                        help=cls.capture.__doc__)
    Group.add_argument('--layout', action='append', default=[], nargs=3,
                       metavar=('MODULE-PARAM', 'WINDOW_ID', 'LAYOUT'),
                       help=cls.layout.__doc__)
    Group.add_argument('--record', action='append', default=[], nargs=3,
                       metavar=('START', 'END', 'PATH'))
    Group.add_argument('--combine', action='store_true')
    return Parser

