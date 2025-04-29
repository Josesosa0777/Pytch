"""
This module contains the implementation of ListNavigator, which can show 
multiple signal values at the same time. The ListNavigator is synchronized
with the video player and has the capability
of updating the signal values as the measurement is played. 
"""

__docformat__ = "restructuredtext en"

import os
from collections import OrderedDict
import numpy as np
from PySide import QtCore, QtGui
from PySide.QtCore import Qt
from PySide.QtGui import QDesktopWidget, QIcon, QSortFilterProxyModel, QStandardItem, QStandardItemModel
from Synchronizer import cNavigator
from figlib import generateWindowId
import logging
import matplotlib.pyplot as plt

IMAGE_DIRECTORY = os.path.join(os.path.dirname(__file__), "images")
IMAGE_FORMATS = ["png", "jpeg", "jpg"]
COLOR_TO_QT_COLOR = {
    'red': QtCore.Qt.red,
}
logger = logging.getLogger('TableNavigator')


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
                          ((self.maximum() - self.minimum()) * event.x()) / self.width())
            event.accept()
        super(Slider, self).mouseReleaseEvent(event)
        return


class cTableNavigator(cNavigator):
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
        self.groups = {'Default': {"frame": None, "signals": []}}
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
        """:type: TableNavigator.Slider
        Slider along time scale"""
        self.pw = None
        self.objects = []  # list of dict of objects [{trackid : {list of signals}}]
        self.timeseries = []  # Common time
        self.table_headers = []  # Table headers to show
        """:type: QtGui.QTabWidget"""
        self.setWindowTitle(title)
        self.center()
        return

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def copyContentToFile(self, file, format=None):
        """
				Copy figure to the specified file in the specified format.
				No other parameters are allowed in order to ensure compatibility with other navigators.

				:Parameters:
					fig : matplotlib.figure.Figure
					file : str or file
					format : str
				"""
        table_data = []
        # Prepare data
        for index, object in self.iterActualObjects(self.time, self.objects, self.timeseries):
            if object['valid'][index] == True:
                row_data = []
                for idx, column in enumerate(self.table_headers_mapping.keys()):
                    cell_data = ""
                    try:
                        cell_data = object[column][index]
                    except KeyError:
                        logger.warning("missing column: {} in headers".format(column))
                    except Exception as e:
                        logger.warning(str(e))
                        pass
                    row_data.append(str(cell_data))
                table_data.append(row_data)
        if table_data is None or len(table_data) == 0: #False negative case
            table_data = [["" for i in range(len(self.table_headers))]]
        fig, ax = plt.subplots()
        ax.set_axis_off()
        fig.set_size_inches(6, 3)
        table = ax.table(
                cellText = table_data,
                # rowLabels = val2,
                colLabels = self.table_headers,
                # rowColours = ["palegreen"] * 5,
                colColours = ["palegreen"] * len(self.table_headers),
                cellLoc = 'center',
                loc = 'upper left')
        table.scale(1, 2)
        # table.set_fontsize(10)
        # table.auto_set_font_size()
        ax.set_title(self.title, fontweight = "bold")

        # fig.savefig(r"C:\KBData\__PythonToolchain\Development\pytch_bitbucket\pil_text.png")
        fig.savefig(file, format = format, bbox_inches = 'tight')


        return

    def addtabledata(self, time, objects, table_headers_mapping, **kwargs):
        """
        Configure table data with the navigator
        :param time: Common Time series of the object data
        :param objects: List of objects
        :param table_headers: List of table headers without image data
        :param kwargs:
        :return:
        """

        if len(objects) == 0:
            raise ValueError("Objects data cannot be empty")
        if len(table_headers_mapping) == 0:
            raise ValueError("Table headers cannot be empty")
        if not isinstance(table_headers_mapping, OrderedDict):
            raise ValueError("'table_headers' must be an OrderedDict")
        if not isinstance(objects, list):
            raise ValueError("'objects' must be List of objects")
        if "valid" not in objects[0].keys():
            raise ValueError("'objects' must have 'valid' key. It can be negation of mask used.")

        self.objects = objects
        self.timeseries = time
        self.table_headers_mapping = table_headers_mapping
        self.table_headers = [header for _, header in table_headers_mapping.items()]
        object_headers = objects[0].keys()
        invaid_headers = [x for x in table_headers_mapping.keys() if x not in object_headers]
        if len(invaid_headers) > 0:
            for invalid_header in invaid_headers:
                del self.table_headers_mapping[invalid_header]

            self.table_headers = self.table_headers_mapping.keys()
            logger.critical("Missing column names in objects data {}".format(invaid_headers))
            logger.info("Updated headers: {}".format(self.table_headers))
        return

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

    def printwidget(self, widget, depth=0):
        print "%s%s" % (" " * depth, str(widget))
        cd = widget.children()
        for c in cd:
            self.printwidget(c, depth + 1)
        return

    def seek(self, time):
        self.seeked = True
        self.timeScale.setValue(time)
        cNavigator.seek(self, time)
        self.refreshValues()
        return

    def play(self, time):
        self.time = time
        cNavigator.play(self, time)
        self.refreshValues()
        self.seeked = True
        self.timeScale.setValue(time)
        return

    def refreshValues(self):
        """
        Refresh the displayed values.

        :Return: None
        """
        self.update_treeview_visualizer_model()
        return

    def find_nearest(self, array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return idx

    def iterActualObjects(self, timestamp, ObjList, obj_time):
        PrevTime = None
        PrevIndex = None
        # ObjList = self.objects if ObjList is None else ObjList
        for Obj in ObjList:
            Time = obj_time
            if Time is not PrevTime:
                Index = max(Time.searchsorted(timestamp, side='right') - 1, 0)
                # Index = self.find_nearest(Time, timestamp)
                PrevTime = Time
                PrevIndex = Index
            else:  # no search required (optimization)
                Index = PrevIndex

            yield (Index, Obj)

    def update_treeview_visualizer_model(self):
        id = 0
        if self.treeview_visualizer_model.hasChildren():
            self.treeview_visualizer_model.removeRows(0, self.treeview_visualizer_model.rowCount())

        root_node = self.treeview_visualizer_model.invisibleRootItem()
        for index, object in self.iterActualObjects(self.time, self.objects, self.timeseries):
            if object['valid'][index] == True:
                row_items = []
                for idx, column in enumerate(self.table_headers_mapping.keys()):
                    row_data = ""
                    try:
                        if os.path.isfile(str(object[column][index])):
                            if object[column][index].split(".")[-1] in IMAGE_FORMATS:
                                icons = [QIcon(name) for name in ["dummy"]]
                                delegate = IconStyledItemDelegate(icons, self.treeview_visualizer)
                                self.treeview_visualizer.setItemDelegateForColumn(idx, delegate)

                        row_data = object[column][index]
                        if column == 'enable_bitfield' and row_data == 1:
                            delegate = BoldDelegate(self.treeview_visualizer)
                            self.treeview_visualizer.setItemDelegateForRow(id, delegate)
                            id = id + 1
                        elif column == 'enable_bitfield' and row_data == 0:
                            id = id + 1

                    except KeyError:
                        print("missing column: {} in headers".format(column))
                    except Exception:
                        pass
                    row_item = QStandardItem(str(row_data))
                    row_item.setEditable(False)
                    row_items.append(row_item)

                root_node.appendRow(row_items)

        # self.treeview_visualizer.setColumnWidth(1, 80)
        # self.treeview_visualizer.setColumnWidth(2, 100)
        # self.treeview_visualizer_proxy_model.sort(0)

    def start(self, selectedgroup=None):
        """
        Opens the signals list window and starts the event loop.

        :Return: None
        """
        self.selectedgroup = selectedgroup
        if self.selectedgroup is None:
            self.selectedgroup = sorted(self.groups.keys())[0]
        self.mainframe = QtGui.QFrame()
        main_layout = QtGui.QVBoxLayout()

        self.timeScale = Slider()
        self.timeScale.setOrientation(QtCore.Qt.Horizontal)
        main_layout.addWidget(self.timeScale)

        minTime = self.timeseries[0]
        maxTime = self.timeseries[-1]
        self.timeScale.setRange(minTime, maxTime)
        self.timeScale.setTickInterval((maxTime - minTime) / 4.0)
        self.timeScale.valueChanged.connect(self.ontimeScaleChanged)
        self.seeked = True

        vboxlayout_signal_selector = QtGui.QVBoxLayout()
        vboxlayout_signal_selector.setSpacing(0)
        vboxlayout_signal_selector.setContentsMargins(1, 1, 1, 1)

        # <editor-fold desc="Treeview control">
        self.treeview_visualizer = QtGui.QTreeView()
        self.treeview_visualizer.setSortingEnabled(True)
        self.treeview_visualizer.header().setStretchLastSection(True)
        self.treeview_visualizer.setAlternatingRowColors(True)

        self.treeview_visualizer.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.treeview_visualizer.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        self.treeview_visualizer.setHeaderHidden(False)

        self.treeview_visualizer_model = QStandardItemModel()
        self.treeview_visualizer_model.setHorizontalHeaderLabels(self.table_headers)

        # Make proxy model to allow seamlesss filtering
        self.treeview_visualizer_proxy_model = CustomSorter()
        self.treeview_visualizer_proxy_model.setSourceModel(self.treeview_visualizer_model)
        # self.treeview_visualizer_proxy_model.sort(0)
        self.treeview_visualizer.setModel(self.treeview_visualizer_proxy_model)
        self.setStyleSheet("QTreeView::item { padding: 10px }")
        # delegate = RowHeightDelegate()
        # self.treeview_visualizer.setItemDelegate(delegate)

        vboxlayout_signal_selector.addWidget(self.treeview_visualizer)

        self.update_treeview_visualizer_model()
        main_layout.addWidget(self.treeview_visualizer)
        self.treeview_visualizer.resizeColumnToContents(0)

        self.mainframe.setLayout(main_layout)
        self.setCentralWidget(self.mainframe)
        return

class CustomSorter(QSortFilterProxyModel):

    def sort(self, column, order):
       pass


class RowHeightDelegate(QtGui.QStyledItemDelegate):

    def sizeHint(self, option, index):
        fixed_height = 40
        size = super(RowHeightDelegate, self).sizeHint(option, index)
        size.setHeight(fixed_height)
        return size


class BoldDelegate(QtGui.QStyledItemDelegate):

    def paint(self, qpainter, option, index):
        # decide here if item should be bold and set font weight to bold if needed
        option.font.setWeight(QtGui.QFont.Bold)
        QtGui.QStyledItemDelegate.paint(self, qpainter, option, index)


class IconStyledItemDelegate(QtGui.QStyledItemDelegate):
    """
    Styled item delegate supports icons
    """

    def __init__(self, icon_set, parent=None):
        super(IconStyledItemDelegate, self).__init__(parent)
        self._icons = icon_set

    def paint(self, qpainter, qstyleoptionviewitem, qmodel_index):
        """
        override base paint method to paint icons in the column
        Parameters
        ----------
        qpainter
        qstyleoptionviewitem
        qmodel_index

        Returns
        -------

        """
        icon = QIcon(qmodel_index.data())
        icon.paint(qpainter, qstyleoptionviewitem.rect, Qt.AlignCenter)
