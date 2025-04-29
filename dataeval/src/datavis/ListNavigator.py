"""
This module contains the implementation of ListNavigator, which can show 
multiple signal values at the same time. The ListNavigator is synchronized
with the video player and has the capability
of updating the signal values as the measurement is played. 
"""

__docformat__ = "restructuredtext en"

from PySide import QtGui, QtCore
import numpy  as np

from Synchronizer import cNavigator
from figlib import generateWindowId
from ReportNavigator import changeColor
import matplotlib.pyplot as plt
import logging

logger = logging.getLogger('ListNavigator')

COLOR_TO_QT_COLOR = {
  'red': QtCore.Qt.red,
}

class Slider(QtGui.QSlider):
  """GUI Slider with offset implementation for large timestamp intervals."""
  
  def __init__(self):
    """Constructor for Slider class"""
    super(Slider, self).__init__()
    self._offset = None
    """:type: float
    Offset for the timestamp in order to handle any size."""
    self._resolution = 0.001
    """:type: float
    Resolution of the slider."""
    return
  
  def _phys2raw(self, value):
    """Convert physical slider value to raw (internal) slider value."""
    return value / self._resolution - self._offset
  
  def _raw2phys(self, value):
    """Convert raw (internal) slider value to physical slider value."""
    return (value + self._offset) * self._resolution
  
  def maximum(self):
    """Gets the maximum value for the slider. 
    Uses offset and resolution values. Overrides QSlider.maximum.
    :Return: None"""
    return self._raw2phys(super(Slider, self).maximum())

  def minimum(self):
    """Gets the minimum value for the slider. 
    Uses offset and resolution values. Overrides QSlider.minimum.
    :Return: None"""
    return self._raw2phys(super(Slider, self).minimum())
    
  def setMaximum(self, arg__1):
    """Sets the maximum value for the slider. 
    Uses offset and resolution values. Overrides QSlider.setMaximum.
    
    :Parameters:
    arg__1 : float
      Set value for maximum
    
    :Return: None"""
    raise NotImplementedError
    return
 
  def setMinimum(self, arg__1):
    """Sets the minimum value for the slider. 
    Uses offset and resolution values. Overrides QSlider.setMinimum.
    
    :Parameters:
    arg__1 : float
      Set value for minimum
    
    :Return: None"""
    raise NotImplementedError
    return
   
  def setRange(self, min_value, max_value):
    """Sets the minimum and maximum values for the slider. 
    Uses and sets offset value. Overrides QSlider.setRange.
    
    :Parameters:
    min_value : float
      Set value for minimum
    max_value : float
      Set value for maximum
     
    :Return: None"""
    min_value = min_value / self._resolution
    max_value = max_value / self._resolution
    self._offset = min_value
    super(Slider, self).setRange(0, max_value - self._offset)
    return

  def value(self):
    """Value property for the slider. Uses offset and resolution.
    Overrides QSlider.value ."""
    return self._raw2phys(super(Slider, self).value())
  
  def setValue(self, arg__1):
    """Sets value property for the slider. Uses offset and resolution. 
    Overrides QSlider.setValue ."""
    return super(Slider, self).setValue(self._phys2raw(arg__1))
 
  def mouseReleaseEvent(self, event):
    """Overrides and handles the mouse release event, in order 
    to handle the Slider's seek functionality.
    
    :Parameters:
    event : PySide.QtGui.QMouseEvent
    """
    if event.button() == QtCore.Qt.LeftButton:
      self.setValue(self.minimum() +
                  ((self.maximum() - self.minimum()) * event.x())/self.width())
      event.accept()
    super(Slider, self).mouseReleaseEvent(event)
    return

class cListNavigator(cNavigator):
  """Lists several signal values with synchronizable time marker. 
  Create an instance, add signals and pass it to a Synchronizer."""

  def __init__(self, title='Signals'):
    """
    Constructor of the class.

    :Parameters:
      title : string
        Main title of the list window.
    """
    cNavigator.__init__(self)

    self.title = title
    """:type: str
    Main title of the list window."""
    self.playing = False
    """:type: bool
    Playing state."""
    self.groups = {'Default' : {"frame" : None, "signals" : []}}
    """:type: dictionary
    List of the signal groups."""
    self.selectedgroup = None
    """:type: dictionary
    List of the signal groups."""
    self.time = 0.
    """:type: float
    The time of the displayed signals"""
    self.seeked = False
    """:type: bool
    Flag to indicate outer seek"""
    self._windowId = generateWindowId(title)
    """:type: str
    String to identify the window"""
    self.timeScale = None
    """:type: ListNavigator.Slider
    Slider along time scale"""
    self.pw = None
    """:type: QtGui.QTabWidget"""
    self.setWindowTitle(title)

    return

  def copyToClipboard(self):
    selected_group = self.selectedgroup
    signals_data = self.groups[selected_group]["signals"]

    clipboard_text = "signalName\tvalue\n"
    for sig in signals_data:
      clipboard_text += "{}\t{}\n".format(sig['name'], self.getSignalValueStr(sig))

    clipboard = QtGui.QApplication.clipboard()
    clipboard.setText(clipboard_text)

  def keyPressEvent(self, event):
    if event.modifiers() == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_C:
      self.copyToClipboard()

  def addsignal(self,name,signal,groupname='Default',bg=None):
    """
    Add a single signal to plots.

    :Parameters:
      name : string
        Name to display on plots.
      signal : tuple
        Two element tuple of `ndarray` (time, value).
      groupname : str
        Indicates which group (tab) the signal belongs to
      bg : str
        Background color of the signal name.
        hexadecimal digits ('#fff', '#000fff000', ..)
    :Return: None
    """
    if bg in COLOR_TO_QT_COLOR:
      bg = COLOR_TO_QT_COLOR[bg]
    if groupname not in self.groups:
      self.groups[groupname] = {"frame" : None, "signals" : []}
    self.groups[groupname]["signals"].append({'name':name,'time':signal[0],
                                              'signal':signal[1],'bg':bg})
    return

  def addsignals(self, signals, groupname='Default', **kwargs):
    """
    Add a list of signals: [{'name':name','time':time,signal':signal}]

    :Parameters:
      signals : dict
        Signals to add.
    :Keywords:
      Passed to `addsignal` method, check it for details
    :Return: None
    """
    for sig in signals:
      self.addsignal(sig['name'], (sig['time'],sig['signal']), groupname,
                                    **kwargs)
    return

  def __iadd__(self,other):
    """
    Implements the += operator for this class.

    :Parameters:
      other : dict
        This parameter can be in one of the following formats:
        A list of dictionaries to add:
        [{'name':name,'time':time,'signal':signal},
        ...
        ]
        or a single signal to add:
        [name,time,signal]
    :Return: cListNavigator object
    """
    if type(other)==list and len(other)>0:
      if type(other[0])==dict:
        self.addsignals(other)
        return self
    if type(other)==list or type(other)==tuple:
      if len(other)==3:
        self.addsignal(other[0],other[1:])
    return self

  def ontimeScaleChanged(self, value):
    """
    Event handler for scale changed event.

    :Return: None
    """ 
    rawvalue = self.timeScale.value() 
    value = float(rawvalue) 
    if not self.seeked:
      self.time = value
      self.refreshValues()
      self.onSeek(self.time)
    else:
      self.seeked = False
    return

  def onTabChange(self, index):
    if index != -1:
      self.selectedgroup = self.pw.tabText(index)
      self.refreshValues()
    return

  def printwidget(self, widget, depth=0):
    print "%s%s"%(" " * depth, str(widget))
    cd = widget.children()
    for c in cd:
      self.printwidget(c, depth+1)
    return

  def seek(self, time):
    self.seeked = True
    self.timeScale.setValue(time)
    cNavigator.seek(self, time)
    self.refreshValues()
    return

  def play(self, time):
    self.time=time
    cNavigator.play(self, time)
    self.refreshValues()
    self.seeked = True
    self.timeScale.setValue(time)
    return

  def copyContentToFile(self, file, format = None):
    """
    Copy figure to the specified file in the specified format.
    No other parameters are allowed in order to ensure compatibility with other navigators.

    :Parameters:
      fig : matplotlib.figure.Figure
      file : str or file
      format : str
    """
    table_data = []
    table_headers = ["Signal Name", "Signal Value"]
    # Prepare data
    # for index, object in self.iterActualObjects(self.time, self.objects, self.timeseries):
    #   if object['valid'][index] == True:
    #     row_data = []
    #     for idx, column in enumerate(self.table_headers_mapping.keys()):
    #       cell_data = ""
    #       try:
    #         cell_data = object[column][index]
    #       except KeyError:
    #         logger.warning("missing column: {} in headers".format(column))
    #       except Exception as e:
    #         logger.warning(str(e))
    #         pass
    #       row_data.append(str(cell_data))
    #     table_data.append(row_data)
    for sig in self.groups[self.selectedgroup]["signals"]:
      signal_name = sig['name'].split("_")[-1]
      signal_value = self.getSignalValueStr(sig)
      table_data.append([signal_name, signal_value])
    if table_data is None or len(table_data) == 0:  # False negative case
      table_data = [["" for i in range(len(table_headers))]]
    fig, ax = plt.subplots()
    ax.set_axis_off()
    fig.set_size_inches(6, 3)
    table = ax.table(
            cellText = table_data,
            # rowLabels = val2,
            colLabels = table_headers,
            # rowColours = ["palegreen"] * 5,
            colColours = ["palegreen"] * len(table_headers),
            cellLoc = 'center',
            loc = 'upper left')
    table.scale(1, 2)
    # table.set_fontsize(10)
    # table.auto_set_font_size()
    ax.set_title(self.title, fontweight = "bold")

    # fig.savefig(r"C:\KBData\__PythonToolchain\Development\pytch_bitbucket\pil_text.png")
    fig.savefig(file, format = format, bbox_inches = 'tight')

    return

  def getSignalValueStr(self, sig):
    """
    Refresh the displayed value for the given signal.

    :Return: None
    """
    idx = max(0, sig['time'].searchsorted(self.time, side='right') - 1)
    if type(sig['signal'][idx]) in [np.int8, np.int16, np.int32, np.int64]:
      val_str = str(sig['signal'][idx])
      return val_str

    try:
      val_str = "%.7f" % float(sig['signal'][idx])
    except (TypeError, ValueError):
      val_str = str(sig['signal'][idx])
    except IndexError:
      val_str = "--"
    return val_str

  def refreshValues(self):
    """
    Refresh the displayed values.

    :Return: None
    """
    for sig in self.groups[self.selectedgroup]["signals"]:
      sig['qtLabel'].setText(self.getSignalValueStr(sig))
    return

  def start(self, selectedgroup=None):
    """
    Opens the signals list window and starts the event loop.

    :Return: None
    """
    self.selectedgroup = selectedgroup
    if self.selectedgroup is None:
      self.selectedgroup = sorted(self.groups.keys())[0]
    mainframe = QtGui.QFrame()
    main_layout = QtGui.QVBoxLayout()

    self.timeScale = Slider()
    self.timeScale.setOrientation(QtCore.Qt.Horizontal)
    main_layout.addWidget(self.timeScale)

    self.pw = QtGui.QTabWidget()
    main_layout.addWidget(self.pw)

    copy_button = QtGui.QPushButton("Click to copy values or press ctrl + 'c'", self)
    copy_button.clicked.connect(self.copyToClipboard)
    main_layout.addWidget(copy_button)

    for name, group in sorted(self.groups.iteritems()):

      signals = group["signals"]

      scrolledframe= QtGui.QScrollArea()
      scrolledframe.setWidgetResizable(True)
      self.pw.addTab(scrolledframe, name)

      frame=QtGui.QFrame()
      scrolledframe.setWidget(frame)
      framelayout = QtGui.QGridLayout()

      label = QtGui.QLabel(name)
      color = QtGui.QColor(0, 0, 0)
      color.setNamedColor('#ffffff')
      changeColor(label, color)
      framelayout.addWidget(label, 0, 0, 1, 2)

      for i, sig in enumerate(signals):
        label = QtGui.QLabel(sig['name'])
        label_color = QtGui.QColor(0, 0, 0)
        bg=('#DFDFCF' if (i+1) % 2 == 0 else '#CFCFBF') if sig['bg'] is None \
                                                    else sig['bg']
        if sig['bg']:
          label_color = bg
        else:
          label_color.setNamedColor(bg)
        changeColor(label, label_color)
        framelayout.addWidget(label, (i+1), 0)

        sig['qtLabel'] = QtGui.QLabel(self.getSignalValueStr(sig))

        bg=('#FFFFFF' if (i+1) % 2 == 0 else '#EFEFEF')
        color.setNamedColor(bg)
        changeColor(sig['qtLabel'], color)
        framelayout.addWidget(sig['qtLabel'], (i+1), 1)
        framelayout.setSizeConstraint(QtGui.QLayout.SetFixedSize)

      try:
        minTime = min( sg['time'].min() for sg in signals if sg['time'].size > 0 )
        maxTime = max( sg['time'].max() for sg in signals if sg['time'].size > 0 )
      except ValueError:  # if there are no signals or only empty signals
        minTime, maxTime = 0.0, 1.0

      frame.setLayout(framelayout)
      group["frame"] = scrolledframe

      if name == self.selectedgroup:
        self.pw.addTab(scrolledframe, name)

    self.timeScale.setRange(minTime, maxTime)
    self.timeScale.setTickInterval((maxTime-minTime) / 4.0)
    self.timeScale.valueChanged.connect(self.ontimeScaleChanged)
    self.seeked = True
    self.pw.currentChanged.connect(self.onTabChange)

    mainframe.setLayout(main_layout)
    self.setCentralWidget(mainframe)
    return

if __name__=='__main__':
  import sys
  import optparse

  parser = optparse.OptionParser()
  parser.add_option('-p', '--hold-navigator',
                    help='Hold the navigator, default is %default',
                    default=False,
                    action='store_true')
  opts, args = parser.parse_args()
  app = QtGui.QApplication([])
  t = np.arange(0,10,1)
  ln = cListNavigator("Test ListNavigator")
  ln.addsignal('sine' ,(t , np.sin(t)), "bla")
  ln.addsignal('sine2' ,(t , np.sin(t)), "bla")
  ln.addsignal('sine3' ,(t , np.sin(t)), "bla")
  ln.addsignal('sine4' ,(t , np.sin(t)), "egg")
  ln.addsignal('sine5' ,(t , np.sin(t)), "egg")
  ln.addsignal('sine6' ,(t , np.sin(t)), "egg")
  ln += ('cosine', t, np.cos(t))
  ln.addsignals([
    {'name':'sine/cosine','time':t,'signal':np.sin(t) / np.cos(t)}])
  ln.addsignals([
    {'name':'sine/cosine','time':t,'signal':np.sin(t) / np.cos(t)},
    {'name':'sine/2cosine','time':t,'signal':np.sin(t) / 2 * np.cos(t)},
    {'name':'sine/3cosine','time':t,'signal':np.sin(t) / 2 * np.cos(t)},
    {'name':'sine/4cosine','time':t,'signal':np.sin(t) / 2 * np.cos(t)},
    {'name':'sine/5cosine','time':t,'signal':np.sin(t) / 2 * np.cos(t)},
    {'name':'sine/2cosine','time':t,'signal':np.sin(t) / 2 * np.cos(t)},
    {'name':'sine/2cosine','time':t,'signal':np.sin(t) / 2 * np.cos(t)},
    {'name':'sine/2cosine','time':t,'signal':np.sin(t) / 2 * np.cos(t)},
    {'name':'sine/2cosine','time':t,'signal':np.sin(t) / 2 * np.cos(t)},
    {'name':'sine/2cosine','time':t,'signal':np.sin(t) / 2 * np.cos(t)},
    {'name':'sine/2cosine','time':t,'signal':np.sin(t) / 2 * np.cos(t)},
    {'name':'sine/2cosine','time':t,'signal':np.sin(t) / 2 * np.cos(t)},
    ], '2nd Group')
  ln.start()
  ln.show()
  if opts.hold_navigator:
      sys.exit(app.exec_())
  ln.close()
