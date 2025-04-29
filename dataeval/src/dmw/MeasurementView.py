import os
import sys

from PySide import QtGui, QtCore
import numpy
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigCanvas
from matplotlib.figure import Figure

from measparser import SignalSource

class MeasurementView(QtGui.QWidget):
  """
  Main class for the Measurement Viewer widget.
  Acts as a top level widget for the Comment viewer and the Signal viewer.
  """
  
  def __init__(self, measurement_path, backup_dir=None):
    """
    Constructor for MeasurementView.
    Initializes the required GUI and sets measurement path.
    """
    super(MeasurementView, self).__init__()
    _, self.ext = os.path.splitext(measurement_path)
    self.meas_path = measurement_path
    try:
      # Use SignalSource to load measurement data
      self.meas = SignalSource.cSignalSource(self.meas_path, NpyHomeDir=backup_dir)
    except IOError as io_error:
      self.meas = None
      error_msg = QtGui.QMessageBox()
      error_msg.setText("%s\n%s" %
        (io_error.message, "Please select a valid measurement."))
      error_msg.exec_()
    else:
      self.init_UI()
      self.setGeometry(400, 400, 950, 500)
      self.setWindowTitle('Signal Information - %s' % measurement_path)
      self.load_measurement_info()
      self.show()
    return
  
  def init_UI(self):
    """
    Initializes the graphical user interface.
    """
    layout = QtGui.QVBoxLayout()
    tab_widget = QtGui.QTabWidget()
    layout.addWidget(tab_widget)
    self.setLayout(layout)

    self.meas_info_widget = MeasurementInfoWidget()
    tab_widget.addTab(self.meas_info_widget, 'Information')

    self.meas_signal_widget = MeasurementSignalsInfo()
    tab_widget.addTab(self.meas_signal_widget, 'Signals')
    return

  def load_measurement_info(self):
    """
    Loads the measurement given to the Widget on the constructor.
    """
    self.meas_info_widget.set_measurement_comment(self.meas.getFileComment())
    # Fetch other measurement info for right side (validity)
    # TODO: Signal validation not ready yet.
    # Make tab 2 load the models
    self.meas_signal_widget.load_models(self.meas)
    return

class MeasurementInfoWidget(QtGui.QWidget):
  """
  Container Widget for the Measurement Info viewer.
  At the moment, shows mainly the measurement comment.
  """
  
  def __init__(self):
    """
    Constructor for MeasurementInfoWidget. 
    Initializes the required GUI.
    """
    super(MeasurementInfoWidget, self).__init__()
    # No separate init_ui method is needed here.
    # Prepare UI on constructor: 
    layout = QtGui.QHBoxLayout()
    splitter = QtGui.QSplitter()
    layout.addWidget(splitter)
    self.setLayout(layout)

    # Prepare left side: Measurements comment. 
    self.comment_view = QtGui.QTextEdit()
    self.comment_view.setReadOnly(True)
    splitter.addWidget(self.comment_view)

    # Prepare right side: Measurements analysis.
    self.analysis_view = QtGui.QTextEdit()
    self.analysis_view.setReadOnly(True)
    splitter.addWidget(self.analysis_view)
    return
  
  def set_measurement_comment(self, comment):
    """
    Sets and displays the comment in the left-side widget.
    """
    self.comment_view.setText(comment)
    return
  
  def set_measurement_analysis(self, raw_analysis):
    """
    Sets and displays the measurement-correctness analysis
    on the right-side widget. 
    """ 
    self.analysis_view.setText(raw_analysis)
    return
  
class MeasurementSignalsInfo(QtGui.QWidget):
  """
  Container widget for the Measurement Signal viewer.
  Contains a tree view of the devices ans signals, a search feature
  and a stacked view of Signal data and Signal plot.
  """

  def __init__(self):
    """
    Constuctor for the MeasurementSignalsInfo class.
    Initializes the UI and actions.
    """
    super(MeasurementSignalsInfo, self).__init__()
    layout = QtGui.QGridLayout()

    layout.setColumnStretch(0, 50)
    layout.setColumnStretch(1, 50)

    self.long_device_names = {}

    # Create search widget
    self.search_widget = QtGui.QLineEdit()
    self.search_widget.textEdited.connect(self.search_text_changed)
    self.clear_search_btn = QtGui.QPushButton('Clear')
    self.clear_search_btn.clicked.connect(self.clear_search_widget)

    search_layout = QtGui.QHBoxLayout()
    search_layout.addWidget(self.search_widget)
    search_layout.addWidget(self.clear_search_btn)
    layout.addLayout(search_layout, 0, 0)

    # Create left side: Signal tree w/o headers
    self.signal_tree_view = QtGui.QTreeView()
    self.signal_tree_view.setHeaderHidden(True)
    self.signal_tree_view.doubleClicked.connect(self.on_item_doubleclick)
    layout.addWidget(self.signal_tree_view, 1, 0, 5, 1)
    
    # Create right side: A stacked layout with 2 info widgets.
    self.signal_info_stack = QtGui.QStackedWidget()
    # Stack 1: Signal data
    self.signal_text_info = QtGui.QTextEdit()
    self.signal_text_info.setReadOnly(True)
    self.signal_info_stack.addWidget(self.signal_text_info)
    
    # Stack 2: signal plots vs time
    fig = Figure(figsize=(400,400),
                 dpi=72, facecolor=(1,1,1), edgecolor=(0,0,0))
    ax = fig.add_subplot(111)
    ax.plot([0,1,2,3,4], [0,1,4,5,10])
    self.signal_plot_canvas = FigCanvas(fig)
    self.signal_info_stack.addWidget(self.signal_plot_canvas)

    self.signal_info_stack.setCurrentIndex(0)
    layout.addWidget(self.signal_info_stack, 1, 1, 5, 1)

    # Use a 'selected' signal to allow the actions to work without tricks
    self._selected_signal = None

    # Previous 2x-clk index. Used for ergonomical doubleclick on info switch
    self._prev_index = None

    self.init_actions()
    self.setLayout(layout)
    return

  def search_text_changed(self):
    """
    Called automatically when the text in the search widget is modified.
    This method updates the RegExp and automatially filters the tree view
    according to the matching search.
    """
    text = self.search_widget.text()
    self.proxy_model.setFilterRegExp(QtCore.QRegExp(text,
                                                    QtCore.Qt.CaseInsensitive,
                                                    QtCore.QRegExp.FixedString))
    self.proxy_model.setFilterKeyColumn(0)
    return

  def clear_search_widget(self):
    """
    Called whent he user presses the clear button. This method clears the search
    bar and lifts the filter on the signal tree while sorting it.
    """
    # Clear, refilter and sort
    self.search_widget.clear()
    self.search_text_changed()
    self.proxy_model.sort(0)
    return

  def init_actions(self):
    """
    Initializes the actions required for the right-click context menu.
    """
    self.action_view_measdata = QtGui.QAction("Open Measurement Data ",
                                      self, triggered=self.open_meas_data)
    self.action_view_plot = QtGui.QAction("Open Measurement Plot ",
                                      self, triggered=self.open_meas_plotting)
    return

  # Override
  def contextMenuEvent(self, event):
    """
    Handles the right-click on signals, in order to show the context menu.
    """
    # Fetch item for the index fetched from the selection
    index = self.signal_tree_view.selectedIndexes()[0]
    # Get information from base model instead
    index = self.proxy_model.mapToSource(index)
    self._selected_signal = self.proxy_model.sourceModel().itemFromIndex(index)
    if self._selected_signal.parent() is not None:
      # show menu
      ctx_menu = QtGui.QMenu()
      ctx_menu.addAction(self.action_view_measdata)
      ctx_menu.addAction(self.action_view_plot)
      ctx_menu.exec_(event.globalPos())
      # Seamless functionality for prev index
      self._prev_index = index
    return

  def on_item_doubleclick(self, index):
    """
    Handles the double-click on signal as well as the ergonomic view switch.
    """
    # Get information from base model instead
    index = self.proxy_model.mapToSource(index)
    self._selected_signal = self.proxy_model.sourceModel().itemFromIndex(index)
    stack_mode = self.signal_info_stack.currentIndex()
    # Did we 2x-click on the same index when in info mode?
    if self._prev_index == index and stack_mode == 0:
      # Same index and not None. Call plot render.
      self.open_meas_plotting()
    else:
      # Index different. Do not act if clicked on a Device
      if self._selected_signal.parent() is not None:
        self.open_meas_data()
        # Save last index for the 2x-click
        self._prev_index = index
    return

  def load_models(self, meas):
    """
    Loads the main model required for the tree view and sets the proxy
    model required for the search filtering.
    """
    self.meas = meas
    self.main_model = QtGui.QStandardItemModel()
    parent_item = self.main_model.invisibleRootItem()
    for device in self.meas.Parser.iterDeviceNames():
        short_device_name = device.split('-')[0]
        self.long_device_names[short_device_name] = device
        item = QtGui.QStandardItem(short_device_name)
        item.setEditable(False)
        parent_item.appendRow(item)
        for signal_name in self.meas.Parser.iterSignalNames(device):
          sub_item = QtGui.QStandardItem(signal_name)
          sub_item.setEditable(False)
          item.appendRow(sub_item)
    # Make proxy model to allow seamless filtering
    self.proxy_model = CustomProxyModel()
    self.proxy_model.setSourceModel(self.main_model)
    self.proxy_model.sort(0)
    self.signal_tree_view.setModel(self.proxy_model)
    return

  def open_meas_data(self):
    """
    Opens and shows the signal's data, such as signal name, device name,
    maximum value, minimum, whether or not is empty, etc.
    """
    # Set as alias for easier handling
    signal = self._selected_signal
    # Set stack to display signal data
    self.signal_info_stack.setCurrentIndex(0)
    self.signal_text_info.clear()
    # Prepare description lines
    signal_name = signal.text()
    device_name = self.long_device_names[signal.parent().text()]
    self.signal_text_info.append("SIGNAL NAME: %s\n" % signal_name)
    self.signal_text_info.append("DEVICE NAME: %s\n" % device_name)
    # Fetch the unit, handle acordingly if not present
    signal_unit = self.meas.getPhysicalUnit(device_name, signal_name)
    self.signal_text_info.append("SIGNAL UNIT: %s\n" % signal_unit)
    # Get signal length. If the signal is empty, print accordingly
    signal_length = self.meas.getSignalLength(device_name, signal_name)
    # Catch signals with strange dtypes that can't be checked.
    try:
      if signal_length > 0:
        # Signal is not empty, print some data about it
        raw_signal = self.meas.getSignal(device_name, signal_name)[1]
        signal_average = numpy.average(raw_signal)
        signal_max = numpy.amax(raw_signal)
        signal_min = numpy.amin(raw_signal)
        self.signal_text_info.append("Signal Length:  %s samples\n"
                                     % str(signal_length))
        self.signal_text_info.append("Average Value:  %s  %s\n"
                                     % (str(signal_average), signal_unit))
        self.signal_text_info.append("Maximum Value:  %s  %s\n"
                                     % (str(signal_max), signal_unit))
        self.signal_text_info.append("Minimum Value:  %s  %s\n"
                                     % (str(signal_min), signal_unit))
      else:
        self.signal_text_info.append("The signal is empty.")
    except TypeError:
      msg = "Can't gather information about signal '%s' because "\
        "it contains values of '%s' type" % (signal_name, raw_signal.dtype)
      self.signal_text_info.append(msg)
    return

  def open_meas_plotting(self):
    """
    Opens a plot of the overall behavior of the signal's value.
    """
    # Set as alias for easier handling
    signal = self._selected_signal
    self.signal_text_info.clear()
    signal_name = signal.text()
    device_name = self.long_device_names[signal.parent().text()]
    time, value = self.meas.getSignal(device_name, signal_name)
    signal_length = self.meas.getSignalLength(device_name, signal_name)
    self.signal_plot_canvas.figure.clear()
    self.signal_info_stack.setCurrentIndex(1)
    # Some signals come with a custom array dtype, catch the error
    try:
      self.signal_plot_canvas.figure.gca().plot(time, value, label='testlabel')
      if signal_length > 0:
        a_max = numpy.amax(value)
        a_min = numpy.amin(value)
        diff = (a_max-a_min)/2.0
        if a_max != a_min:
          self.signal_plot_canvas.figure.gca().set_ylim([a_min-diff,
                                                         a_max+diff])
    except ValueError:
      print >> sys.stderr, "The signal '%s' can't be rendered because "\
        "it contains values of '%s' type" % (signal_name, str(value.dtype))
    self.signal_plot_canvas.draw()
    return

class CustomProxyModel(QtGui.QSortFilterProxyModel):
  """
  Custom Proxy model used for filtering during real-time search.
  This model is needed in order to show the device's children even if the device
  itself does not match the RegExp.
  """

  def filterAcceptsRow(self, sourceRow, sourceParent):
    """
    Checks and accepts the row againt the RegExp.
    Reimplementing this method is needed to override the default behavior,
    which consists of not showing the node's children if the father node does
    not match the RegExp. In this new implementation, the father node (Device)
    is shown if at least one children (Signal) matches the RegExp search.
    """
    if self.filterRegExp().isEmpty():
      # Do not filter if regular expression is empty
      return True
    else:
      # Regexpt not empty, check the node's validity
      source_index = self.sourceModel().index(sourceRow,
                                              self.filterKeyColumn(),
                                              sourceParent)
      if source_index.isValid():
        # Node is valid, check it's children (No pythonic iter available)
        row_number = self.sourceModel().rowCount(source_index)
        for i in xrange(row_number):
          if self.filterAcceptsRow(i, source_index):
            return True
        # Check the item itself.
        item_text = self.sourceModel().data(source_index, self.filterRole())
        return self.filterRegExp().indexIn(item_text) >= 0
      else:
        # Node not valid, do not show it.
        return False

if __name__ == '__main__':
  app = QtGui.QApplication(sys.argv)
  app.setStyle("cleanlooks")
  view = MeasurementView(r'c:\KBData\DAS\measurements\HMCBus\2014-12-05_ACC\HMC_Bus__2014-12-05_13-14-37_.mf4')
  sys.exit(app.exec_())
