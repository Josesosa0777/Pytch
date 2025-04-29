# -*- coding: utf-8 -*-
"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright:
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial
  property. We reserve all rights of disposal such as copying and passing on to
  third parties.
"""
from measproc.IntervalList import maskToIntervals
from dmw.SignalFilters import *
__docformat__ = "restructuredtext en"

import os
from os.path import expanduser
import logging
import datavis
import h5py
import numpy as np
import time
import re
from PySide import QtCore, QtGui
from PySide.QtCore import Qt, QSize
from PySide.QtGui import QApplication, QComboBox, QDialog, QDialogButtonBox, \
    QGroupBox, QIcon, QLabel, QPixmap, \
    QPushButton, QSizePolicy, QSpacerItem, QStandardItem, QStandardItemModel, \
    QTreeWidget, QTreeWidgetItem, QVBoxLayout, QHeaderView, QDesktopWidget, \
    QTabWidget, \
    QTableWidgetItem, QTableWidget

IMAGE_DIRECTORY = os.path.join(os.path.dirname(__file__), "images")
logger = logging.getLogger('NxtSignalSelector')


class ObjectEmittingSignal(QtCore.QObject):
    signal = QtCore.Signal(object)


class cSignalSelector(QtGui.QFrame):
    """Select signal via `setSearcher` and `searchTag`."""
    Channel = 'main'
    SEP = ',\t'

    def __init__(self, root, Control, SingleSelection=False):
        """
        :Parameters:
                root : `tk.Tk`
                        Root tk widget
        """
        QtGui.QFrame.__init__(self, parent=root)
        self.root = root
        self.Control = Control
        self.BatchControl = None
        self.isBatchControl = False
        self.database_signals = {}
        self.is_signal_loaded = False
        self.search_view_on = False
        self.total_signal_count = 0
        home_directory = expanduser("~")
        temp_file_directory = os.path.join(home_directory, ".aebs")
        self.filepath_for_searching_signal_names = os.path.join(temp_file_directory, "signal_names.txt")

        vboxlayout_signal_selector = QtGui.QVBoxLayout()
        vboxlayout_signal_selector.setSpacing(0)
        vboxlayout_signal_selector.setContentsMargins(1, 1, 1, 1)

        # <editor-fold desc="Treeview operations">
        gbox_treeview_operations = QGroupBox('')
        hboxlayout_treeview_operation = QtGui.QHBoxLayout()
        hboxlayout_treeview_operation.setContentsMargins(1, 1, 1, 1)

        gbox_loading_operations = QGroupBox('')
        gridlayout_loading_operation = QtGui.QGridLayout()
        gridlayout_loading_operation.setContentsMargins(1, 1, 1, 1)

        self.label_measurement = QLabel("Measurement")
        gridlayout_loading_operation.addWidget(self.label_measurement, 0, 0, 1, 2, Qt.AlignTop)

        self.pbutton_load = QPushButton("Load")
        self.pbutton_load.setToolTip('Load measurement')
        self.pbutton_load.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'load_file_24.png')))
        self.pbutton_load.clicked.connect(self.update_model)
        gridlayout_loading_operation.addWidget(self.pbutton_load, 1, 0, 1, 2, Qt.AlignLeft)

        self.pbutton_clear_signals = QPushButton("")
        self.pbutton_clear_signals.setToolTip('Clear signals')
        self.pbutton_clear_signals.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'clear_24.png')))
        self.pbutton_clear_signals.clicked.connect(self.clear_signals)
        gridlayout_loading_operation.addWidget(self.pbutton_clear_signals, 2, 0)

        self.pbutton_show_fileinfo = QPushButton("")
        self.pbutton_show_fileinfo.setToolTip('Show file information')
        self.pbutton_show_fileinfo.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'information_24.png')))
        self.pbutton_show_fileinfo.clicked.connect(self.show_file_info)
        gridlayout_loading_operation.addWidget(self.pbutton_show_fileinfo, 2, 1)

        gbox_loading_operations.setLayout(gridlayout_loading_operation)
        hboxlayout_treeview_operation.addWidget(gbox_loading_operations)

        gbox_expand_collapse_operations = QGroupBox('')
        gridlayout_expand_collapse_operation = QtGui.QGridLayout()
        gridlayout_expand_collapse_operation.setContentsMargins(1, 1, 1, 1)

        self.label_expand_collapse = QLabel("Expand/Collapse")
        gridlayout_expand_collapse_operation.addWidget(self.label_expand_collapse, 0, 0, 1, 2, Qt.AlignTop)

        self.pbutton_expand = QPushButton("")
        self.pbutton_expand.setToolTip('Expand signals')
        self.pbutton_expand.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'tree_expand_24.png')))
        self.pbutton_expand.clicked.connect(self.expand_treeview_items)
        gridlayout_expand_collapse_operation.addWidget(self.pbutton_expand, 1, 0)

        self.pbutton_collapse = QPushButton("")
        self.pbutton_collapse.setToolTip('Collapse signals')
        self.pbutton_collapse.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'tree_collapse_24.png')))
        self.pbutton_collapse.clicked.connect(self.collapse_treeview_items)
        gridlayout_expand_collapse_operation.addWidget(self.pbutton_collapse, 1, 1)

        gbox_expand_collapse_operations.setLayout(gridlayout_expand_collapse_operation)
        hboxlayout_treeview_operation.addWidget(gbox_expand_collapse_operations)

        # if str(type(self.root)) == "<class \'dmw.NxtSyncAppEditor.cSyncAppEditor\'>":
        gbox_plot_navigator_operations = QGroupBox('')
        gridlayout_plot_navigator_operation = QtGui.QGridLayout()
        gridlayout_plot_navigator_operation.setContentsMargins(1, 1, 1, 1)
        self.label_plot_navigator = QLabel("Plot Navigator")
        gridlayout_plot_navigator_operation.addWidget(self.label_plot_navigator, 0, 0, 1, 3, Qt.AlignTop)

        self.pbutton_add_plot_navigator = QPushButton("Add Plot")
        self.pbutton_add_plot_navigator.setToolTip('Add Plot Navigator')
        self.pbutton_add_plot_navigator.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'plot_navigator_24.png')))
        gridlayout_plot_navigator_operation.addWidget(self.pbutton_add_plot_navigator, 1, 0, 1, 3, Qt.AlignLeft)

        self.pbutton_add_axes = QPushButton("")
        self.pbutton_add_axes.setToolTip('Add Axes')
        self.pbutton_add_axes.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'add_axes_24.png')))
        gridlayout_plot_navigator_operation.addWidget(self.pbutton_add_axes, 2, 0)

        self.pbutton_add_plot_regular_signal = QPushButton("")
        self.pbutton_add_plot_regular_signal.setToolTip('Add Selected Signals')
        self.pbutton_add_plot_regular_signal.setIcon(
            QIcon(os.path.join(IMAGE_DIRECTORY, 'add_regular_signal_24.png')))
        gridlayout_plot_navigator_operation.addWidget(self.pbutton_add_plot_regular_signal, 2, 1)

        self.pbutton_add_plot_custom_signal = QPushButton("")
        self.pbutton_add_plot_custom_signal.setToolTip('Add Custom Signal')
        self.pbutton_add_plot_custom_signal.setIcon(
            QIcon(os.path.join(IMAGE_DIRECTORY, 'add_custom_signal_24.png')))
        self.pbutton_add_plot_custom_signal.clicked.connect(self.show_plot_custom_signal_form)
        gridlayout_plot_navigator_operation.addWidget(self.pbutton_add_plot_custom_signal, 2, 2)

        gbox_plot_navigator_operations.setLayout(gridlayout_plot_navigator_operation)
        hboxlayout_treeview_operation.addWidget(gbox_plot_navigator_operations)

        gbox_list_navigator_operations = QGroupBox('')
        gridlayout_list_navigator_operation = QtGui.QGridLayout()
        gridlayout_list_navigator_operation.setContentsMargins(1, 1, 1, 1)
        self.label_list_navigator = QLabel("List Navigator")
        gridlayout_list_navigator_operation.addWidget(self.label_list_navigator, 0, 0, 1, 3, Qt.AlignLeft)

        self.pbutton_add_list_navigator = QPushButton("Add List")
        self.pbutton_add_list_navigator.setToolTip('Add List Navigator')
        self.pbutton_add_list_navigator.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'list_navigator_24.png')))
        gridlayout_list_navigator_operation.addWidget(self.pbutton_add_list_navigator, 1, 0, 1, 3, Qt.AlignLeft)

        self.pbutton_add_list_regular_signal = QPushButton("")
        self.pbutton_add_list_regular_signal.setToolTip('Add Selected Signals')
        self.pbutton_add_list_regular_signal.setIcon(
            QIcon(os.path.join(IMAGE_DIRECTORY, 'add_regular_signal_24.png')))
        gridlayout_list_navigator_operation.addWidget(self.pbutton_add_list_regular_signal, 2, 0)

        self.pbutton_add_list_custom_signal = QPushButton("")
        self.pbutton_add_list_custom_signal.setToolTip('Add Custom Signal')
        self.pbutton_add_list_custom_signal.setIcon(
            QIcon(os.path.join(IMAGE_DIRECTORY, 'add_custom_signal_24.png')))
        self.pbutton_add_list_custom_signal.clicked.connect(self.show_list_custom_signal_form)
        gridlayout_list_navigator_operation.addWidget(self.pbutton_add_list_custom_signal, 2, 1)

        gbox_list_navigator_operations.setLayout(gridlayout_list_navigator_operation)
        hboxlayout_treeview_operation.addWidget(gbox_list_navigator_operations)

        horizontal_spacer = QSpacerItem(0, 0, QSizePolicy.Expanding)
        hboxlayout_treeview_operation.addItem(horizontal_spacer)

        gbox_treeview_operations.setLayout(hboxlayout_treeview_operation)
        vboxlayout_signal_selector.addWidget(gbox_treeview_operations)
        # </editor-fold>

        # <editor-fold desc="Signal Filter">
        gbox_signal_filter = QGroupBox('')
        hboxlayout_signal_filter = QtGui.QHBoxLayout()
        hboxlayout_signal_filter.setSpacing(0)
        hboxlayout_signal_filter.setContentsMargins(1, 1, 1, 1)

        self.signal_name = QtGui.QLineEdit()
        self.signal_name.setToolTip('Provide signal filter expression here & press enter')
        self.signal_name.returnPressed.connect(self.search_text_changed)
        self.signal_name.textChanged.connect(self.search_text_cleared)
        hboxlayout_signal_filter.addWidget(self.signal_name, 0, Qt.AlignVCenter)

        self.pbutton_signal_filter_search = QPushButton("")
        self.pbutton_signal_filter_search.setToolTip('Search Signals')
        self.pbutton_signal_filter_search.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'search_24.png')))
        self.pbutton_signal_filter_search.setMinimumWidth(40)
        self.pbutton_signal_filter_search.pressed.connect(self.search_text_changed)
        hboxlayout_signal_filter.addWidget(self.pbutton_signal_filter_search, 0, Qt.AlignVCenter)

        self.pbutton_signal_filter_clear = QPushButton("")
        self.pbutton_signal_filter_clear.setToolTip('Clear Filter')
        self.pbutton_signal_filter_clear.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'clear_filter_24.png')))
        self.pbutton_signal_filter_clear.setMinimumWidth(40)
        self.pbutton_signal_filter_clear.pressed.connect(self.clear_filter)
        hboxlayout_signal_filter.addWidget(self.pbutton_signal_filter_clear, 0, Qt.AlignVCenter)

        self.pbutton_signal_filter_match_case = QPushButton("")
        self.pbutton_signal_filter_match_case.setToolTip('Set match case on/off')
        self.pbutton_signal_filter_match_case.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'match_case_24.png')))
        self.pbutton_signal_filter_match_case.setMinimumWidth(40)
        self.pbutton_signal_filter_match_case.setCheckable(True)
        self.pbutton_signal_filter_match_case.clicked.connect(lambda: self.search_text_changed())
        hboxlayout_signal_filter.addWidget(self.pbutton_signal_filter_match_case, 0, Qt.AlignVCenter)

        self.pbutton_signal_filter_regular_exp = QPushButton("")
        self.pbutton_signal_filter_regular_exp.setToolTip('Set regular expression on/off')
        self.pbutton_signal_filter_regular_exp.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'regex_match_24.png')))
        self.pbutton_signal_filter_regular_exp.setMinimumWidth(40)
        self.pbutton_signal_filter_regular_exp.setCheckable(True)
        self.pbutton_signal_filter_regular_exp.clicked.connect(lambda: self.search_text_changed())
        hboxlayout_signal_filter.addWidget(self.pbutton_signal_filter_regular_exp, 0, Qt.AlignVCenter)

        self.pbutton_signal_filter_help = QPushButton("")
        self.pbutton_signal_filter_help.setToolTip('Get help on how to use search expressions')
        self.pbutton_signal_filter_help.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'help_24.png')))
        self.pbutton_signal_filter_help.setMinimumWidth(40)
        self.pbutton_signal_filter_help.clicked.connect(self.show_help)
        hboxlayout_signal_filter.addWidget(self.pbutton_signal_filter_help, 0, Qt.AlignVCenter)

        gbox_signal_filter.setLayout(hboxlayout_signal_filter)

        vboxlayout_signal_selector.addWidget(gbox_signal_filter)
        # </editor-fold>

        # <editor-fold desc="Treeview control">
        self.SignalTable = QtGui.QTreeView()
        self.SignalTable.doubleClicked.connect(self.SignalTable_doubleClicked)
        self.SignalTable.clicked.connect(self.SignalTable_clicked)
        self.SignalTable.setSortingEnabled(True)
        self.SignalTable.header().setStretchLastSection(True)
        self.SignalTable.setAlternatingRowColors(True)

        if SingleSelection:
            self.SignalTable.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        else:
            self.SignalTable.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.SignalTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        self.SignalTable.setHeaderHidden(False)
        self.tree_model = QStandardItemModel()
        self.tree_model.setHorizontalHeaderLabels(['Devices', ''])

        # Make proxy model to allow seamless filtering
        self.proxy_model = LeafFilterProxyModel()
        self.proxy_model.setSourceModel(self.tree_model)
        self.proxy_model.sort(0)
        self.SignalTable.setModel(self.proxy_model)
        # </editor-fold>

        # <editor-fold desc="Search Treeview control">
        gbox_signal_viewer = QGroupBox('')
        vboxlayout_signal_viewer = QtGui.QVBoxLayout()
        vboxlayout_signal_viewer.setSpacing(0)
        vboxlayout_signal_viewer.setContentsMargins(1, 1, 1, 1)

        self.tree_widget_search = QTreeWidget()
        self.tree_widget_search.doubleClicked.connect(self.tree_widget_search_doubleClicked)
        self.tree_widget_search.setVisible(False)
        self.tree_widget_search_column_lables = ["Devices"]
        self.tree_widget_search.setHeaderLabels(self.tree_widget_search_column_lables)
        self.tree_widget_search.setAlternatingRowColors(True)
        self.tree_widget_search.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tree_widget_search.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tree_widget_search.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        # self.table_widget_search.setSortingEnabled(True)
        # Allow popup menu
        self.tree_widget_search.setContextMenuPolicy(Qt.CustomContextMenu)

        # Connect the signal request to the slot (click the right mouse button to call the method)
        self.tree_widget_search.customContextMenuRequested.connect(self.tree_view_search_show_contextmenu)

        vboxlayout_signal_viewer.addWidget(self.tree_widget_search)
        vboxlayout_signal_viewer.addWidget(self.SignalTable)

        gbox_signal_viewer.setLayout(vboxlayout_signal_viewer)
        vboxlayout_signal_selector.addWidget(gbox_signal_viewer)
        # </editor-fold>

        self.setLayout(vboxlayout_signal_selector)

        # <editor-fold desc="Context menu actions for tree view">
        self.action_plot_signals = QtGui.QAction("Quick Plot (Synchronous)", self, triggered=self.plot_signals)
        self.action_plot_signals.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'plot_16.png')))
        self.action_plot_signals_with_db_signals = QtGui.QAction("Quick Plot with DB Signals (Synchronous)", self,
                                                                 triggered=self.plot_signals_with_db_signals)
        self.action_plot_signals_with_db_signals.setIcon(
            QIcon(os.path.join(IMAGE_DIRECTORY, 'add_signal_from_db_24.png')))
        self.action_search = QtGui.QAction("Quick Search ", self, triggered=self.show_quick_search)
        self.action_search.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'advanced_search_16.png')))
        self.action_copy_signal_name = QtGui.QAction("Copy Signal Name ", self, triggered=self.copy_signal_name)
        self.action_copy_signal_name.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'copy_16.png')))

        self.action_copy_signal_name_in_script_form = QtGui.QAction("Copy Signal in Script Form ", self,
                                                                    triggered=self.copy_signal_name_in_script_form)
        self.action_copy_signal_name_in_script_form.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'copyscript_16.png')))
        self.action_copy_device_name = QtGui.QAction("Copy Device Name ", self, triggered=self.copy_device_name)
        self.action_copy_device_name.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'copy_16.png')))

        self.action_add_plot_navigator = QtGui.QAction("Add Plot Navigator ", self)
        self.action_add_plot_navigator.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'add_navigator_16.png')))

        self.action_add_plot_axes = QtGui.QAction("Add Axes ", self)
        # self.action_add_plot_axes.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'copy_16.png')))

        self.action_add_plot_signals = QtGui.QAction("Add Signals ", self)
        self.action_add_plot_signals.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'add_signal_16.png')))

        self.action_add_plot_signals_with_custom_alias = QtGui.QAction("Add signals with custom alias", self)
        self.action_add_plot_signals_with_custom_alias.setIcon(
            QIcon(os.path.join(IMAGE_DIRECTORY, 'add_signal_16.png')))

        self.action_add_plot_signals_with_custom_mapping = QtGui.QAction("Add signals with states mapping", self)
        self.action_add_plot_signals_with_custom_mapping.setIcon(
            QIcon(os.path.join(IMAGE_DIRECTORY, 'add_signal_16.png')))

        self.action_add_list_navigator = QtGui.QAction("Add List Navigator ", self)
        self.action_add_list_navigator.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'add_navigator_16.png')))

        self.action_add_list_signals = QtGui.QAction("Add Signals ", self)
        self.action_add_list_signals.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'add_signal_16.png')))

        self.action_save_signal_npz = QtGui.QAction("Numpy format (npz)", self, triggered=self.save_signals_npz)
        # self.action_save_signal_npz.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'save_16.png')))
        self.action_save_signal_hdf5 = QtGui.QAction("HDF5 format (hdf5)", self, triggered=self.save_signals_hdf5)
        # self.action_save_signal_hdf5.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'save_16.png')))

        self.action_show_signal_info = QtGui.QAction("Show Signal Information ", self,
                                                     triggered=self.show_signal_info)
        self.action_show_signal_info.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'information_16.png')))
        # </editor-fold>

        # <editor-fold desc="Table Context menu actions">
        self.view_action_plot_signals = QtGui.QAction("Quick Plot (Synchronous)", self,
                                                      triggered=self.tree_view_search_plot_signals)
        self.view_action_plot_signals.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'plot_16.png')))
        self.view_action_plot_signals_with_db_signals = QtGui.QAction("Quick Plot with DB Signals (Synchronous)",
                                                                      self,
                                                                      triggered=self.tree_view_search_plot_signals_with_db_signals)
        self.view_action_plot_signals_with_db_signals.setIcon(
            QIcon(os.path.join(IMAGE_DIRECTORY, 'add_signal_from_db_24.png')))
        self.view_action_search = QtGui.QAction("Quick Search ", self,
                                                triggered=self.tree_view_search_show_quick_search)
        self.view_action_search.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'advanced_search_16.png')))
        self.view_action_copy_signal_name = QtGui.QAction("Copy Signal Name ", self,
                                                          triggered=self.tree_view_search_copy_signal_name)
        self.view_action_copy_signal_name.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'copy_16.png')))

        self.view_action_copy_signal_name_in_script_form = QtGui.QAction("Copy Signal in Script Form ", self,
                                                                         triggered=self.tree_view_search_copy_signal_name_in_script_form)
        self.view_action_copy_signal_name_in_script_form.setIcon(
            QIcon(os.path.join(IMAGE_DIRECTORY, 'copyscript_16.png')))
        self.view_action_copy_device_name = QtGui.QAction("Copy Device Name ", self,
                                                          triggered=self.tree_view_search_copy_device_name)
        self.view_action_copy_device_name.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'copy_16.png')))

        self.view_action_add_plot_navigator = QtGui.QAction("Add Plot Navigator ", self)
        self.view_action_add_plot_navigator.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'add_navigator_16.png')))

        self.view_action_add_plot_axes = QtGui.QAction("Add Axes ", self)
        # self.action_add_plot_axes.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'copy_16.png')))

        self.view_action_add_plot_signals = QtGui.QAction("Add Signals ", self)
        self.view_action_add_plot_signals.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'add_signal_16.png')))

        self.view_action_add_plot_signals_with_custom_alias = QtGui.QAction("Add signals with custom alias", self)
        self.view_action_add_plot_signals_with_custom_alias.setIcon(
            QIcon(os.path.join(IMAGE_DIRECTORY, 'add_signal_16.png')))

        self.view_action_add_plot_signals_with_custom_mapping = QtGui.QAction("Add signals with states mapping",
                                                                              self)
        self.view_action_add_plot_signals_with_custom_mapping.setIcon(
            QIcon(os.path.join(IMAGE_DIRECTORY, 'add_signal_16.png')))

        self.view_action_add_list_navigator = QtGui.QAction("Add List Navigator ", self)
        self.view_action_add_list_navigator.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'add_navigator_16.png')))

        self.view_action_add_list_signals = QtGui.QAction("Add Signals ", self)
        self.view_action_add_list_signals.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'add_signal_16.png')))

        self.view_action_save_signal_npz = QtGui.QAction("Numpy format (npz)", self,
                                                         triggered=self.tree_view_search_save_signals_npz)
        # self.action_save_signal_npz.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'save_16.png')))
        self.view_action_save_signal_hdf5 = QtGui.QAction("HDF5 format (hdf5)", self,
                                                          triggered=self
                                                          .tree_view_search_save_signals_hdf5)
        # self.action_save_signal_hdf5.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'save_16.png')))

        self.view_action_show_signal_info = QtGui.QAction("Show Signal Information ", self,
                                                          triggered=self
                                                          .tree_view_search_show_signal_info)
        self.view_action_show_signal_info.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'information_16.png')))
        # </editor-fold>

        self.long_device_names = {}
        self.selectSignalForCustomExpressionSignal = ObjectEmittingSignal()
        self.addPlotCustomExpressionSignal = ObjectEmittingSignal()
        self.addListCustomExpressionSignal = ObjectEmittingSignal()
        self.selected_signal = None
        return

    def set_batch_control(self, batchcontrol):
        self.BatchControl = batchcontrol
        self.isBatchControl = True

    def SignalTable_doubleClicked(self, index):
        item_selection_model = self.SignalTable.selectionModel()
        selected_row = item_selection_model.selectedIndexes()[0]

        row = self.proxy_model.mapToSource(selected_row)
        signal = self.proxy_model.sourceModel().itemFromIndex(row)
        if signal.parent() is not None:
            if signal.child(0, 0) is None:
                original_signal_name = signal.text()
                signal_name = original_signal_name
                signal_index = ''
                if len(original_signal_name.split('[:,')) == 2:
                    (signal_name, index) = original_signal_name.split('[')
                    signal_index = '[' + index

                device_node = self.get_device_node(signal)
                if not device_node is signal:
                    device_node.text()
                    signal_unit = self.getPhysicalUnit(device_node.text(), signal_name)
                    self.selectSignalForCustomExpressionSignal.signal.emit(
                        (device_node.text(), original_signal_name, signal_unit))
            else:
                logger.info("Please select signals from array " + signal.text())

    def SignalTable_clicked(self, index):
        signal_source = self.Control.getSource(self.Channel)
        is_view_signal_list_available = True
        try:
            test_signal_source = signal_source.Parser.view_signal_list
        except AttributeError:
            is_view_signal_list_available = False

        proxy_index = self.proxy_model.mapToSource(index)
        node = self.proxy_model.sourceModel().itemFromIndex(proxy_index)
        device_name = node.data(Qt.UserRole)
        if node.parent() is None:
            if not node.rowCount():
                if is_view_signal_list_available:
                    device_dictionary = signal_source.Parser.view_signal_list[device_name]

                    for signal_name in device_dictionary.keys():
                        signal_dictionary = device_dictionary[signal_name]
                        sub_item = QStandardItem(signal_name)
                        sub_item.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'signal_16.png')))
                        sub_item.setToolTip(signal_name)
                        sub_item.setEditable(False)
                        node.appendRow(sub_item)
                        self.add_signals_recursively(signal_dictionary, sub_item)
                else:
                    for signal_name in signal_source.Parser.iterSignalNames(device_name):
                        sub_item = QStandardItem(signal_name)
                        sub_item.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'signal_16.png')))
                        sub_item.setToolTip(signal_name)
                        sub_item.setEditable(False)
                        node.appendRow(sub_item)

    def update_model(self):
        """
        Updates model by getting device and signals from parser
        """
        # logger.info("Loading signals from measurement, Please wait...")
        self.SignalTable.setVisible(True)
        self.tree_widget_search.setVisible(False)
        self.search_view_on = False
        self.is_signal_loaded = True
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))

        # Clear tree model
        if self.tree_model.hasChildren():
            self.tree_model.removeRows(0, self.tree_model.rowCount())
        # Clear long device name dictionary
        self.long_device_names.clear()

        root_node = self.tree_model.invisibleRootItem()
        signal_source = self.Control.getSource(self.Channel)

        # check if parser has implemented view_signal_list
        is_view_signal_list_available = True
        try:
            value = signal_source.Parser.view_signal_list

            # Generate text file with complete signal list
            with open(self.filepath_for_searching_signal_names, 'w') as f:
                for device_name, signal_name in signal_source.Parser.view_signal_list.items():
                    for device_name_1, signal_name_1 in signal_name.items():
                        f.write('%s:	%s\n' % (device_name, device_name_1))
                        if bool(device_name_1):
                            for device_name_2, signal_name_2 in signal_name_1.items():
                                f.write('%s:	%s\n' % (device_name, device_name_2))
        except AttributeError:
            is_view_signal_list_available = False
        start = time.time()
        if is_view_signal_list_available:
            for device in signal_source.Parser.iterDeviceNames():
                short_device_name = device.split('-')[0]

                device_dictionary = signal_source.Parser.view_signal_list[short_device_name]
                item = QStandardItem(short_device_name)
                item.setToolTip(device)
                item.setData(device, Qt.UserRole)
                item.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'device_16.png')))
                item.setEditable(False)
                root_node.appendRow(item)
                for signal_name in device_dictionary.keys():
                    self.long_device_names[(short_device_name, signal_name)] = device
        else:
            with open(self.filepath_for_searching_signal_names, 'w') as f:
                for device in signal_source.Parser.iterDeviceNames():
                    short_device_name = device.split('-')[0]

                    item = QStandardItem(short_device_name)
                    item.setToolTip(device)
                    item.setData(device, Qt.UserRole)
                    item.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'device_16.png')))
                    item.setEditable(False)
                    root_node.appendRow(item)
                    for signal_name in signal_source.Parser.iterSignalNames(device):
                        self.long_device_names[(short_device_name, signal_name)] = device
                        f.write('%s:	%s\n' % (short_device_name, signal_name))
                        self.total_signal_count = self.total_signal_count + 1

        self.SignalTable.setColumnWidth(0, 2000)
        end = time.time()
        self.proxy_model.sort(0)
        QtGui.QApplication.restoreOverrideCursor()
        logger.info("Total signals {} from measurement are loaded in {} seconds".format(self.total_signal_count,str(end - start)))

    def show_file_info(self):
        signal_source = self.Control.getSource(self.Channel)
        fileinfo = signal_source.getFileComment()
        if fileinfo == "":
            fileinfo = "File information not found"
        dialog = FrmShowFileInfo(fileinfo)
        dialog.show()
        dialog.exec_()

    def show_plot_custom_signal_form(self):
        if self.search_view_on is True:
            self.tree_view_search_show_plot_custom_signal_form()
        else:
            self.signal_view_show_plot_custom_signal_form()

    def show_list_custom_signal_form(self):
        if self.search_view_on is True:
            self.tree_view_search_show_list_custom_signal_form()
        else:
            self.signal_view_show_list_custom_signal_form()

    def signal_view_show_plot_custom_signal_form(self):
        signal_source = self.Control.getSource(self.Channel)
        selected_rows = self.SignalTable.selectedIndexes()
        signals = []
        for row in selected_rows:
            row = self.proxy_model.mapToSource(row)
            signal = self.proxy_model.sourceModel().itemFromIndex(row)
            if signal.parent() is not None:
                if signal.child(0, 0) is None:
                    original_signal_name = signal.text()
                    signal_name = original_signal_name
                    signal_index = ''
                    if len(original_signal_name.split('[:,')) == 2:
                        (signal_name, index) = original_signal_name.split('[')
                        signal_index = '[' + index

                    device_node = self.get_device_node(signal)
                    if not device_node is signal:
                        device_node.text()
                        signal_unit = self.getPhysicalUnit(device_node.text(), signal_name)
                        signals.append((device_node.text(), original_signal_name, signal_unit))
                else:
                    logger.info("Please select signals from array " + signal.text())

        dialog = FrmShowCustomSignalForm("Plot", signals, self.selectSignalForCustomExpressionSignal,
                                         self.addPlotCustomExpressionSignal)
        dialog.show()
        dialog.exec_()

    def signal_view_show_list_custom_signal_form(self):
        selected_rows = self.SignalTable.selectedIndexes()
        signals = []
        for row in selected_rows:
            row = self.proxy_model.mapToSource(row)
            signal = self.proxy_model.sourceModel().itemFromIndex(row)
            if signal.parent() is not None:
                if signal.child(0, 0) is None:
                    original_signal_name = signal.text()
                    signal_name = original_signal_name
                    signal_index = ''
                    if len(original_signal_name.split('[:,')) == 2:
                        (signal_name, index) = original_signal_name.split('[')
                        signal_index = '[' + index

                    device_node = self.get_device_node(signal)
                    if not device_node is signal:
                        device_node.text()
                        signal_unit = self.getPhysicalUnit(device_node.text(), signal_name)
                        signals.append((device_node.text(), original_signal_name, signal_unit))
                else:
                    logger.info("Please select signals from array " + signal.text())
        dialog = FrmShowCustomSignalForm("List", signals, self.selectSignalForCustomExpressionSignal,
                                         self.addListCustomExpressionSignal)
        dialog.show()
        dialog.exec_()

    def expand_treeview_items(self):
        self.SignalTable.expandAll()
        self.tree_widget_search.expandAll()

    def collapse_treeview_items(self):
        self.SignalTable.collapseAll()
        self.tree_widget_search.collapseAll()

    def clear_signals(self):
        if self.tree_model.hasChildren():
            self.tree_model.removeRows(0, self.tree_model.rowCount())
        self.signal_name.clear()
        self.is_signal_loaded = False

        self.tree_widget_search.clear()
        self.tree_widget_search.setVisible(False)

    # self.search_text_changed()
    # self.table_widget_search.clear()

    def search_text_cleared(self):
        text = self.signal_name.text()
        if len(text) == 0:
            self.SignalTable.setVisible(True)
            self.tree_widget_search.setVisible(False)
            self.search_view_on = False

    def search_text_changed(self):
        text = self.signal_name.text()
        if len(text) > 1:
            if self.is_signal_loaded:
                if self.pbutton_signal_filter_regular_exp.isChecked():
                    search_result = self.search_string_in_file_with_regex(self.filepath_for_searching_signal_names,
                                                                          str(text))
                elif self.pbutton_signal_filter_match_case.isChecked():
                    search_result = self.search_string_in_file(self.filepath_for_searching_signal_names, str(text))
                else:
                    search_result = self.search_string_in_file(self.filepath_for_searching_signal_names,
                                                               str(text).lower())
                self.update_search_treeview(search_result)
            else:
                logger.info("Please load measurement to search signals.")
        else:
            self.SignalTable.setVisible(True)
            self.tree_widget_search.setVisible(False)
            self.search_view_on = False
        return

    def clear_filter(self):
        self.signal_name.clear()
        self.tree_widget_search.clear()
        self.SignalTable.setVisible(True)
        self.tree_widget_search.setVisible(False)
        self.search_view_on = False

    def show_help(self):
        dialog = FrmShowHelp()
        dialog.setModal(True)
        dialog.show()
        dialog.exec_()

    def contextMenuEvent(self, event):
        """
        Handles the right-click on signals, in order to show the context menu.
        """
        if len(self.SignalTable.selectedIndexes()) != 0:
            index = self.SignalTable.selectedIndexes()[0]
            total_signals = len(self.SignalTable.selectedIndexes())
            # Get information from base model instead
            index = self.proxy_model.mapToSource(index)
            self.selected_signal = self.proxy_model.sourceModel().itemFromIndex(index)
            if self.selected_signal.parent() is not None:
                # show menu
                ctx_menu = QtGui.QMenu()
                if self.selected_signal.child(0, 0) is None:
                    ctx_menu.addAction(self.action_plot_signals)
                    ctx_menu.addAction(self.action_plot_signals_with_db_signals)

                if total_signals == 1:
                    if self.selected_signal.child(0, 0) is None:
                        ctx_menu.addAction(self.action_search)
                ctx_menu.addSeparator()
                ctx_menu.addAction(self.action_copy_signal_name)
                ctx_menu.addAction(self.action_copy_signal_name_in_script_form)
                ctx_menu.addAction(self.action_copy_device_name)
                if total_signals == 1:
                    ctx_menu.addSeparator()
                    ctx_menu.addAction(self.action_show_signal_info)
                # if str(type(self.root)) == "<class \'dmw.NxtSyncAppEditor.cSyncAppEditor\'>":
                ctx_menu.addSeparator()
                if self.selected_signal.child(0, 0) is None:
                    plot_navigator_submenu = ctx_menu.addMenu('Plot Navigator')
                    plot_navigator_submenu.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'plot_navigator_16.png')))
                    plot_navigator_submenu.addAction(self.action_add_plot_navigator)
                    plot_navigator_submenu.addAction(self.action_add_plot_axes)
                    plot_navigator_submenu.addAction(self.action_add_plot_signals)

                    list_navigator_submenu = ctx_menu.addMenu('List Navigator')
                    list_navigator_submenu.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'list_navigator_16.png')))
                    list_navigator_submenu.addAction(self.action_add_list_navigator)
                    list_navigator_submenu.addAction(self.action_add_list_signals)
                    ctx_menu.addSeparator()
                if self.selected_signal.child(0, 0) is None:
                    save_submenu = ctx_menu.addMenu('Save Signals')
                    save_submenu.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'save_16.png')))
                    save_submenu.addAction(self.action_save_signal_hdf5)
                    save_submenu.addAction(self.action_save_signal_npz)
                ctx_menu.exec_(event.globalPos())
                # Seamless functionality for prev index
                self._prev_index = index
            return

    def copy_signal_name(self):
        signal_names = ""
        item_selection_model = self.SignalTable.selectionModel()
        selected_rows = item_selection_model.selectedIndexes()
        for row in selected_rows:
            row = self.proxy_model.mapToSource(row)
            signal = self.proxy_model.sourceModel().itemFromIndex(row)
            if signal.parent() is not None:
                if signal.child(0, 0) is None:
                    signal_names += signal.text() + "\n"
                else:
                    logger.info("Please select signals from array : " + signal.text())
        QApplication.clipboard().setText(signal_names)
        logger.info("Signal name is copied")

    def copy_signal_name_in_script_form(self):
        # "vx_kmh": ("EBC2_0B", "EBC2_MeanSpdFA_0B"),
        signal_names = ""
        item_selection_model = self.SignalTable.selectionModel()
        selected_rows = item_selection_model.selectedIndexes()
        for row in selected_rows:
            row = self.proxy_model.mapToSource(row)
            signal = self.proxy_model.sourceModel().itemFromIndex(row)
            if signal.parent() is not None:
                if signal.child(0, 0) is None:
                    original_signal_name = signal.text()
                    signal_name = original_signal_name
                    signal_index = ''
                    if len(original_signal_name.split('[:,')) == 2:
                        (signal_name, index) = original_signal_name.split('[')
                        signal_index = '[' + index

                    device_node = self.get_device_node(signal)
                    device_name = device_node.text()
                    if self.need_device_name_in_alias(signal_name, signal_names.split("\n")):
                        alias = signal_name + "-" + device_name
                    else:
                        alias = signal_name

                    script_signal_text = "\"" + alias + "\": (\"" + device_node.text() + "\",\"" + signal_name + "\"),"
                    signal_names += script_signal_text + "\n"
                else:
                    logger.info("Please select signals from array : " + signal.text())
        QApplication.clipboard().setText(signal_names)
        logger.info("Signal name in script form is copied")

    def need_device_name_in_alias(self, signal_name_to_add, selected_signal_names):
        for signal_name in selected_signal_names:
            alias = signal_name.split(":")[0].replace('"', '')
            if alias == signal_name_to_add:
                return True
        return False

    def copy_device_name(self):
        item_selection_model = self.SignalTable.selectionModel()
        selected_row = item_selection_model.selectedIndexes()[0]

        row = self.proxy_model.mapToSource(selected_row)
        signal = self.proxy_model.sourceModel().itemFromIndex(row)

        original_signal_name = signal.text()
        signal_name = original_signal_name
        if len(original_signal_name.split('[')) == 2:
            (signal_name, index) = original_signal_name.split('[')
            signal_index = '[' + index
        else:
            signal_index = ''
        device_node = self.get_device_node(signal)
        device_name = device_node.text()

        if selected_row.parent() is not None:
            QApplication.clipboard().setText(device_node.text())
            logger.info("Device name is copied")

    def show_signal_info(self):
        """
        Opens and shows the signal's data, such as signal name, device name,
        maximum value, minimum, whether or not is empty, etc.
        """
        signal_source = self.Control.getSource(self.Channel)
        self.signal_text_info = QtGui.QTextEdit()
        self.signal_text_info.setReadOnly(True)
        extended_signal_information = {}
        signal_information = ""
        # Set as alias for easier handling
        signal = self.selected_signal
        # Prepare description lines

        original_signal_name = signal.text()
        signal_name = original_signal_name
        if len(original_signal_name.split('[')) == 2:
            (signal_name, index) = original_signal_name.split('[')
            signal_index = '[' + index
        else:
            signal_index = ''
        device_node = self.get_device_node(signal)
        try:
            device_name = self.long_device_names[(device_node.text(), signal_name)]
        except:
            device_name = self.long_device_names[(device_node.text(), original_signal_name)]
            signal_name = original_signal_name
        signal_unit = signal_source.Parser.getPhysicalUnit(device_name, signal_name)
        if signal_source.BaseName.split('.', -1)[-1] == 'mat':
            extended_signal_information = signal_source.Parser.getExtendedSignalInformation(device_name, signal_name)
            for key, value in extended_signal_information.iteritems():
                signal_information = signal_information + key + ":  " + extended_signal_information[key] + '\n'
                self.signal_text_info.append(key + ":  " + extended_signal_information[key])
                self.signal_text_info.setToolTip(signal_information)
        # signal_information = ""
        elif signal_source.BaseName.split('.', -1)[-1] == 'h5' or signal_source.BaseName.split('.', -1)[-1] == '.hdf5':
            try:
                extended_signal_information = signal_source.Parser.getExtendedSignalInformation(device_name,
                                                                                                signal_name)
                for key, value in extended_signal_information.iteritems():
                    signal_information = signal_information + key + ":  " + str(extended_signal_information[key]) + '\n'
                    self.signal_text_info.append(key + ":  " + str(extended_signal_information[key]))
                    self.signal_text_info.setToolTip(signal_information)
            except:
                if bool(re.findall('_CAN[0-9]+', device_name)):
                    original_device_name = device_name.replace(re.findall('_CAN[0-9]+', device_name)[0], '')
                    for can_channels in signal_source.Parser.Hdf5['devices'][original_device_name].keys():
                        can_channel_number = '_CAN' + can_channels.split('-')[1]
                        if can_channel_number in device_name:
                            signal_information = original_device_name + "-" + \
                                                 can_channels + "-" + signal_name
                            self.signal_text_info.append("Extended Information: %s" % signal_information)
                            self.signal_text_info.append("Device Name: %s" % original_device_name)
                            self.signal_text_info.append("Signal Name: %s" % original_signal_name)
                            # Fetch the unit, handle acordingly if not present
                            self.signal_text_info.append("Unit: %s" % signal_unit)
        else:
            # information = information + key + ": " + extended_information[key] + '\n'
            self.signal_text_info.append("Signal Name: %s" % original_signal_name)
            self.signal_text_info.append("Device Name: %s" % device_name)
            # Fetch the unit, handle acordingly if not present
            self.signal_text_info.append("Unit: %s" % signal_unit)

        # Get signal length. If the signal is empty, print accordingly
        signal_length = signal_source.Parser.getSignalLength(device_name, signal_name)
        # Catch signals with strange dtypes that can't be checked.
        try:
            if signal_length > 0:
                # Signal is not empty, print some data about it
                raw_signal, _ = signal_source.Parser.getSignal(device_name, signal_name)
                signal_average = np.average(raw_signal)
                signal_max = np.amax(raw_signal)
                signal_min = np.amin(raw_signal)
                self.signal_text_info.append("Length:  %s samples"
                                             % str(signal_length))
                self.signal_text_info.append("Average:  %s  %s"
                                             % (str(signal_average), signal_unit))
                self.signal_text_info.append("Max:  %s  %s"
                                             % (str(signal_max), signal_unit))
                self.signal_text_info.append("Min:  %s  %s"
                                             % (str(signal_min), signal_unit))
            else:
                self.signal_text_info.append("The signal is empty.")
        except TypeError:
            msg = "Can't gather information about signal '%s'" % (signal_name)
            self.signal_text_info.append(msg)

        dialog = FrmShowSignalInfo(self.signal_text_info)
        dialog.show()
        dialog.exec_()
        return

    def plot_signals(self):
        """
                Opens a plot of the overall behavior of the signal's value.
                """
        # logger.info("Plotting signals, Please wait...")
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
        if self.isBatchControl:
            # print(self.BatchControl)`
            selected_measurement_file = os.path.basename(self.BatchControl.Config._sections['Measurement']['main'])
            manager = self.BatchControl.Managers[selected_measurement_file]
            signal_source = manager.get_source()

        else:
            # print(self.Control)
            signal_source = self.Control.getSource(self.Channel)
            manager = self.Control.Managers[signal_source.BaseName]

        pn = datavis.PlotNavigator.cPlotNavigator("Plot window")
        pn.setWindowTitle("PlotNavigator-" + signal_source.BaseName)
        # Fetch item for the index fetched from the selection
        selected_row = self.SignalTable.selectedIndexes()
        axis00 = pn.addAxis()
        for row in selected_row:
            row = self.proxy_model.mapToSource(row)
            signal = self.proxy_model.sourceModel().itemFromIndex(row)
            if signal.parent() is not None:
                if signal.child(0, 0) is None:
                    original_signal_name = signal.text()
                    signal_name = original_signal_name

                    signal_index = ''
                    if len(original_signal_name.split('[:,')) == 2:
                        (signal_name, index) = original_signal_name.split('[')
                        signal_index = '[' + index
                    device_node = self.get_device_node(signal)
                    try:
                        device_name = self.long_device_names[(device_node.text(), signal_name)]
                    except:
                        device_name = self.long_device_names[(device_node.text(), original_signal_name)]

                    value, time_key = signal_source.Parser.getSignal(device_name, signal_name)
                    time = signal_source.Parser.getTime(time_key)
                    unit = signal_source.Parser.getPhysicalUnit(device_name, signal_name)
                    # Check if duplicate signal names selected from different devices
                    if original_signal_name in axis00.label2line:
                        original_signal_name = original_signal_name + "-" + device_name

                    if signal_index == '':
                        pn.addSignal2Axis(axis00, original_signal_name, time, value, unit=unit)
                    else:
                        pn.addSignal2Axis(axis00, original_signal_name, time, eval('value' + signal_index),
                                          unit=unit)
                else:
                    logger.info("Please select signals from array : " + signal.text())
        QtGui.QApplication.restoreOverrideCursor()
        pn.start()
        pn.show()

        synchronizer = manager.sync

        if synchronizer is not None:
            synchronizer.addClient(pn)
        return

    def plot_signals_with_db_signals(self):
        """
                Opens a plot of the overall behavior of the signal's value.
                """
        if bool(self.database_signals) is True:
            # logger.info("Plotting signals, Please wait...")
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
            if self.isBatchControl:
                # print(self.BatchControl)
                selected_measurement_file = os.path.basename(self.BatchControl.Config._sections['Measurement']['main'])
                manager = self.BatchControl.Managers[selected_measurement_file]
                signal_source = manager.get_source()

            else:
                # print(self.Control)
                signal_source = self.Control.getSource(self.Channel)
                manager = self.Control.Managers[signal_source.BaseName]

            pn = datavis.PlotNavigator.cPlotNavigator("Plot window")
            pn.setWindowTitle("PlotNavigator-" + signal_source.BaseName)
            # Fetch item for the index fetched from the selection
            selected_row = self.SignalTable.selectedIndexes()
            axis00 = pn.addAxis()
            common_time = None
            for row in selected_row:
                row = self.proxy_model.mapToSource(row)
                signal = self.proxy_model.sourceModel().itemFromIndex(row)
                if signal.parent() is not None:
                    if signal.child(0, 0) is None:
                        original_signal_name = signal.text()
                        signal_name = original_signal_name

                        signal_index = ''
                        if len(original_signal_name.split('[:,')) == 2:
                            (signal_name, index) = original_signal_name.split('[')
                            signal_index = '[' + index
                        device_node = self.get_device_node(signal)
                        try:
                            device_name = self.long_device_names[(device_node.text(), signal_name)]
                        except:
                            device_name = self.long_device_names[(device_node.text(), original_signal_name)]
                        value, time_key = signal_source.Parser.getSignal(device_name, signal_name)
                        time = signal_source.Parser.getTime(time_key)
                        common_time = time
                        unit = signal_source.Parser.getPhysicalUnit(device_name, signal_name)
                        # Check if duplicate signal names selected from different devices
                        if original_signal_name in axis00.label2line:
                            original_signal_name = original_signal_name + "-" + device_name

                        if signal_index == '':
                            pn.addSignal2Axis(axis00, original_signal_name, time, value, unit=unit)
                        else:
                            pn.addSignal2Axis(axis00, original_signal_name, time, eval('value' + signal_index),
                                              unit=unit)
                    else:
                        logger.info("Please select signals from array : " + signal.text())
            for signal_name, signal_data in self.database_signals.items():
                time_data = signal_data[0]
                value_data = signal_data[1]
                mapping = signal_data[2]
                if mapping is None:
                    pn.addSignal2Axis(axis00, signal_name, time_data, value_data, unit="")
                else:
                    ax = pn.addAxis(ylabel=signal_name, yticks=mapping,
                                    ylim=(min(mapping) - 0.5, max(mapping) + 0.5))
                    pn.addSignal2Axis(ax, signal_name, time_data, value_data, unit='')

            QtGui.QApplication.restoreOverrideCursor()
            pn.start()
            pn.show()

            synchronizer = manager.sync

            if synchronizer is not None:
                synchronizer.addClient(pn)
            return
        else:
            logger.info(
                "No Signal found from Database.. Please execute analyze and click on More Options->Add to Module "
                "Creation...")

    def show_quick_search(self):
        signal_source = self.Control.getSource(self.Channel)
        selected_rows = self.SignalTable.selectedIndexes()
        signals = {}
        for row in selected_rows:
            row = self.proxy_model.mapToSource(row)
            signal = self.proxy_model.sourceModel().itemFromIndex(row)
            if signal.parent() is not None:
                if signal.child(0, 0) is None:
                    original_signal_name = signal.text()
                    signal_name = original_signal_name
                    signal_index = ''
                    if len(original_signal_name.split('[:,')) == 2:
                        (signal_name, index) = original_signal_name.split('[')
                        signal_index = '[' + index

                    device_node = self.get_device_node(signal)
                    try:
                        device_name = self.long_device_names[(device_node.text(), signal_name)]
                    except:
                        device_name = self.long_device_names[(device_node.text(), original_signal_name)]

                    value, time_key = signal_source.Parser.getSignal(device_name, signal_name)
                    time = signal_source.Parser.getTime(time_key)
                    unit = signal_source.Parser.getPhysicalUnit(device_name, signal_name)
                    if signal_index == '':
                        signals[signal_name] = (value, time, unit)
                    else:
                        signals[signal_name] = (eval('value' + signal_index), time, unit)
                else:
                    logger.info("Please select signals from array : " + signal.text())
        dialog = FrmQuickSearch(signals)
        dialog.show()
        dialog.exec_()

    def add_signals_recursively(self, signal_dictionary, item):
        if not bool(signal_dictionary):
            return
        for signal_name in signal_dictionary.keys():
            if signal_name == u'TimeAxis' or signal_name == u'Unit':
                continue
            child_signal_dictionary = signal_dictionary[signal_name]
            sub_item = QStandardItem(signal_name)
            sub_item.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'signal_16.png')))
            sub_item.setToolTip(signal_name)
            sub_item.setEditable(False)
            item.appendRow(sub_item)

            self.add_signals_recursively(child_signal_dictionary, sub_item)
        return

    def save_signals_npz(self):
        """
                Save signal's value.
        """
        logger.info("Saving signals in Numpy format, Please wait...")
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
        signal_source = self.Control.getSource(self.Channel)
        # Fetch item for the index fetched from the selection
        selected_row = self.SignalTable.selectedIndexes()
        allsignals_nparray = {}
        for row in selected_row:
            signal_nparray = []
            row = self.proxy_model.mapToSource(row)
            signal = self.proxy_model.sourceModel().itemFromIndex(row)
            if signal.parent() is not None:
                if signal.child(0, 0) is None:
                    original_signal_name = signal.text()
                    signal_name = original_signal_name
                    signal_index = ''
                    if len(original_signal_name.split('[:,')) == 2:
                        (signal_name, index) = original_signal_name.split('[')
                        signal_index = '[' + index

                    device_node = self.get_device_node(signal)
                    try:
                        device_name = self.long_device_names[(device_node.text(), signal_name)]
                    except:
                        device_name = self.long_device_names[(device_node.text(), original_signal_name)]

                    value, time_key = signal_source.Parser.getSignal(device_name, signal_name)
                    time = signal_source.Parser.getTime(time_key)
                    unit = signal_source.Parser.getPhysicalUnit(device_name, signal_name)
                    signal_nparray.append(time)
                    if signal_index == '':
                        signal_nparray.append(value)
                    else:
                        signal_nparray.append(eval('value' + signal_index))
                    allsignals_nparray[original_signal_name] = np.array(signal_nparray)
                else:
                    logger.info("Please select signals from array : " + signal.text())
        directory_path = os.path.dirname(signal_source.FileName)
        measurement_filename = os.path.splitext(signal_source.BaseName)[0]
        directory_name = measurement_filename + "_processed"

        directory_path = os.path.join(directory_path, directory_name)
        if not os.path.isdir(directory_path):
            os.mkdir(directory_path)

        npz_file_name = os.path.join(directory_path, measurement_filename + "_signals.npz")
        np.savez(npz_file_name, allsignals_nparray)
        logger.info("Signals are saved at " + npz_file_name)
        QtGui.QApplication.restoreOverrideCursor()
        return

    def save_signals_hdf5(self):
        """
                Save signal's value.
        """
        logger.info("Saving signals in HDF5 format, Please wait...")
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
        signal_source = self.Control.getSource(self.Channel)
        # Fetch item for the index fetched from the selection
        selected_row = self.SignalTable.selectedIndexes()

        # folder creation for storing h5 file
        directory_path = os.path.dirname(signal_source.FileName)
        measurement_filename = os.path.splitext(signal_source.BaseName)[0]
        directory_name = measurement_filename + "_processed"
        directory_path = os.path.join(directory_path, directory_name)
        if not os.path.isdir(directory_path):
            os.mkdir(directory_path)

        # create h5 file
        h5_file_name = os.path.join(directory_path, measurement_filename + "_signals.h5")
        h5_file_handle = h5py.File(h5_file_name, 'w')

        for row in selected_row:
            row = self.proxy_model.mapToSource(row)
            signal = self.proxy_model.sourceModel().itemFromIndex(row)
            if signal.parent() is not None:
                if signal.child(0, 0) is None:
                    original_signal_name = signal.text()
                    signal_name = original_signal_name
                    signal_index = ''
                    if len(original_signal_name.split('[:,')) == 2:
                        (signal_name, index) = original_signal_name.split('[')
                        signal_index = '[' + index

                    device_node = self.get_device_node(signal)
                    try:
                        device_name = self.long_device_names[(device_node.text(), signal_name)]
                    except:
                        device_name = self.long_device_names[(device_node.text(), original_signal_name)]

                    value, time_key = signal_source.Parser.getSignal(device_name, signal_name)
                    h5_signal = h5_file_handle.create_group(signal_name)

                    signal_time = signal_source.Parser.getTime(time_key)
                    unit = signal_source.Parser.getPhysicalUnit(device_name, signal_name)

                    h5_signal.attrs['unit'] = unit
                    h5_signal.attrs['device_name'] = device_name

                    if signal_index == '':
                        signal_value = value
                    else:
                        signal_value = eval('value' + signal_index)
                    h5_signal.create_dataset("time", data=signal_time)
                    h5_signal.create_dataset("value", data=signal_value)
                else:
                    logger.info("Please select signals from array : " + signal.text())
        h5_file_handle.close()
        logger.info("Signals are saved at " + h5_file_name)
        QtGui.QApplication.restoreOverrideCursor()
        return

    def getCurrentSelection(self, Unit=True):
        selected_signals_list = []
        item_selection_model = self.SignalTable.selectionModel()
        selected_rows = item_selection_model.selectedIndexes()

        for row in selected_rows:
            row = self.proxy_model.mapToSource(row)
            signal = self.proxy_model.sourceModel().itemFromIndex(row)
            if signal.parent() is not None:
                if signal.child(0, 0) is None:
                    original_signal_name = signal.text()
                    signal_name = original_signal_name
                    signal_index = ''
                    if len(original_signal_name.split('[:,')) == 2:
                        (signal_name, index) = original_signal_name.split('[')
                        signal_index = '[' + index

                    device_node = self.get_device_node(signal)
                    device_node.text()
                    if Unit:
                        signal_unit = self.getPhysicalUnit(device_node.text(), signal_name)
                        selected_signals_list.append((device_node.text(), original_signal_name, signal_unit))
                    else:
                        selected_signals_list.append((device_node.text(), original_signal_name))
                else:
                    logger.info("Please select signals to from array : " + signal.text())
        return selected_signals_list

    def getPhysicalUnit(self, ShortDeviceName, SignalName):
        Source = self.Control.getSource(self.Channel)
        DeviceName = Source.getUniqueName(SignalName, ShortDeviceName, FavorMatch=True)
        return Source.getPhysicalUnit(DeviceName, SignalName)

    def getSignalShape(self, ShortDeviceName, SignalName):
        Source = self.Control.getSource(self.Channel)
        DeviceName = Source.getUniqueName(SignalName, ShortDeviceName, FavorMatch=True)
        return Source.getSignalShape(DeviceName, SignalName)

    def get_device_node(self, node):
        while node.parent() is not None:
            node = node.parent()
        return node

    def search_string_in_file(self, file_name, string_to_search):
        """Search for the given string in file and return lines containing that string,
        along with line numbers"""
        start_time = time.time()
        line_number = 0
        result_list = []
        # if " " in text:
        # 		text = text.replace(" ", ".*")
        # Open the file in read only mode
        with open(file_name, 'r') as file_obj:
            # Read all lines in the file one by one
            for line in file_obj:
                # For each line, check if line contains the string
                line_number += 1
                if self.pbutton_signal_filter_match_case.isChecked():
                    # If yes, then add the line number & line as a tuple in the list
                    if string_to_search in line:
                        if '\tTimeAxis\n' in line or '\tUnit\n' in line:
                            continue
                        else:
                            result_list.append((line))
                else:
                    if " " in string_to_search:
                        string_to_search_list = string_to_search.split(" ")
                        if all([x in line.lower() for x in string_to_search_list]) is True:
                            if '\tTimeAxis\n' in line or '\tUnit\n' in line:
                                continue
                            else:
                                result_list.append((line))
                    elif string_to_search in line.lower():
                        # If yes, then add the line number & line as a tuple in the list
                        if '\tTimeAxis\n' in line or '\tUnit\n' in line:
                            continue
                        else:
                            result_list.append((line))

        # Return list of tuples containing line numbers and lines where string is found
        end_time = time.time()
        # logger.debug("Searching completed in :  " + str(end_time - start_time) + " Seconds")
        return result_list

    def search_string_in_file_with_regex(self, file_name, regex_expr):
        """Search for the given string in file and return lines containing that string,
        along with line numbers"""
        start_time = time.time()
        line_number = 0
        result_list = []

        pattern = re.compile(regex_expr)
        # Open the file in read only mode
        with open(file_name, 'r') as file_obj:
            # Read all lines in the file one by one
            for line in file_obj:
                # For each line, check if line contains the string
                line_number += 1
                result = pattern.search(line)
                if result is not None:
                    result_list.append((line))

        # Return list of tuples containing line numbers and lines where string is found
        end_time = time.time()
        # logger.debug("Searching completed in :  " + str(end_time - start_time) + " Seconds")
        return result_list

    def update_search_treeview(self, searched_items):
        # self.tree_widget_search.setRowCount(len(searched_items))
        # self.tree_widget_search.setColumnCount(2)
        # self.tree_widget_search_column_lables = ["Device Name", "Signal Name"]
        # self.tree_widget_search.setHorizontalHeaderLabels(self.tree_widget_search_column_lables)
        self.tree_widget_search.setVisible(True)
        self.SignalTable.setVisible(False)
        self.search_view_on = True
        self.tree_widget_search.clear()
        if searched_items:
            old_device_name = ""
            device_node = self.tree_widget_search
            for row_counter, items in enumerate(searched_items):
                device_name, signal_name = items.split(':\t')
                device_name = device_name.strip()
                signal_name = signal_name.strip()
                if old_device_name != device_name:
                    device_node = QTreeWidgetItem(self.tree_widget_search, [device_name])
                    device_node.setIcon(0, QIcon(os.path.join(IMAGE_DIRECTORY, 'device_16.png')))
                    device_node.setToolTip(0, device_name)
                    # device_node.setEditable(False)
                    old_device_name = device_name

                # device.setTextAlignment(Qt.AlignLeft| Qt.AlignVCenter)
                # self.tree_widget_search.setItem(row_counter, 0, device)
                signal_node = QTreeWidgetItem(device_node, [signal_name])
                signal_node.setIcon(0, QIcon(os.path.join(IMAGE_DIRECTORY, 'signal_16.png')))
                signal_node.setToolTip(0, signal_name)
            # signal_node.setEditable(False)
            # signal.setTextAlignment(Qt.AlignCenter)
            # self.tree_widget_search.setItem(row_counter, 1, signal)
            # self.tree_widget_search.setRowHeight(row_counter, 25)
            # Sorting signal names in ascending order
            self.tree_widget_search.sortByColumn(0, Qt.AscendingOrder)
        # self.tree_widget_search[0].resizeColumnToContents()
        # self.tree_widget_search.hori.horizontalHeader().setStretchLastSection(True)
        else:
            logger.info("Signal name not available")

    def tree_view_search_show_contextmenu(self, position):
        if len(self.tree_widget_search.selectedIndexes()) != 0:
            index = self.tree_widget_search.selectedIndexes()[0]
            total_signals = len(self.tree_widget_search.selectedIndexes())
            selected_signal = self.tree_widget_search.itemFromIndex(index)
            if selected_signal.parent() is not None:
                ctx_menu = QtGui.QMenu()
                ctx_menu.addAction(self.view_action_plot_signals)
                ctx_menu.addAction(self.view_action_plot_signals_with_db_signals)

                if total_signals == 1:
                    ctx_menu.addAction(self.view_action_search)
                ctx_menu.addSeparator()
                ctx_menu.addAction(self.view_action_copy_signal_name)
                ctx_menu.addAction(self.view_action_copy_signal_name_in_script_form)
                ctx_menu.addAction(self.view_action_copy_device_name)

                if total_signals == 1:
                    ctx_menu.addSeparator()
                    ctx_menu.addAction(self.view_action_show_signal_info)

                ctx_menu.addSeparator()
                plot_navigator_submenu = ctx_menu.addMenu('Plot Navigator')
                plot_navigator_submenu.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'plot_navigator_16.png')))
                plot_navigator_submenu.addAction(self.view_action_add_plot_navigator)
                plot_navigator_submenu.addAction(self.view_action_add_plot_axes)
                plot_navigator_submenu.addAction(self.view_action_add_plot_signals)

                list_navigator_submenu = ctx_menu.addMenu('List Navigator')
                list_navigator_submenu.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'list_navigator_16.png')))
                list_navigator_submenu.addAction(self.view_action_add_list_navigator)
                list_navigator_submenu.addAction(self.view_action_add_list_signals)
                ctx_menu.addSeparator()

                save_submenu = ctx_menu.addMenu('Save Signals')
                save_submenu.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'save_16.png')))
                save_submenu.addAction(self.view_action_save_signal_hdf5)
                save_submenu.addAction(self.view_action_save_signal_npz)
                ctx_menu.exec_(self.tree_widget_search.viewport().mapToGlobal(position))
                return

    def tree_view_search_plot_signals(self):
        """
                Opens a plot of the overall behavior of the signal's value.
                """
        # logger.info("Plotting signals, Please wait...")
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
        if self.isBatchControl:
            selected_measurement_file = os.path.basename(
                self.BatchControl.Config._sections['Measurement']['main'])
            manager = self.BatchControl.Managers[selected_measurement_file]
            signal_source = manager.get_source()

        else:
            signal_source = self.Control.getSource(self.Channel)
            manager = self.Control.Managers[signal_source.BaseName]

        pn = datavis.PlotNavigator.cPlotNavigator("Plot window")
        pn.setWindowTitle("PlotNavigator-" + signal_source.BaseName)
        selected_rows = self.tree_widget_search.selectedIndexes()
        axis00 = pn.addAxis()
        for row in selected_rows:
            signal = self.tree_widget_search.itemFromIndex(row)
            if signal.parent() is not None:
                if signal.child(0) is None:
                    signal_index = ''
                    original_signal_name = signal.text(0)
                    signal_name = original_signal_name
                    if len(original_signal_name.split('[:,')) == 2:
                        (signal_name, index) = original_signal_name.split('[')
                        signal_index = '[' + index
                    device_node = self.get_device_node(signal)
                    try:
                        device_name = self.long_device_names[(device_node.text(0), signal_name)]
                    except:
                        device_name = self.long_device_names[(device_node.text(0), original_signal_name)]
                    value, time_key = signal_source.Parser.getSignal(device_name, signal_name)
                    time = signal_source.Parser.getTime(time_key)
                    unit = signal_source.Parser.getPhysicalUnit(device_name, signal_name)
                    # Check if duplicate signal names selected from different devices
                    if original_signal_name in axis00.label2line:
                        original_signal_name = original_signal_name + "-" + device_name

                    if signal_index == '':
                        pn.addSignal2Axis(axis00, original_signal_name, time, value, unit=unit)
                    else:
                        pn.addSignal2Axis(axis00, original_signal_name, time, eval('value' + signal_index),
                                          unit=unit)
                else:
                    logger.info("Please select signals from array : " + signal.text())
        QtGui.QApplication.restoreOverrideCursor()
        pn.start()
        pn.show()

        synchronizer = manager.sync

        if synchronizer is not None:
            synchronizer.addClient(pn)
        return

    def tree_view_search_show_plot_custom_signal_form(self):
        signal_source = self.Control.getSource(self.Channel)
        selected_rows = self.tree_widget_search.selectedIndexes()
        signals = []
        for row in selected_rows:
            signal = self.tree_widget_search.itemFromIndex(row)
            if signal.parent() is not None:
                if signal.child(0) is None:
                    original_signal_name = signal.text(0)
                    signal_name = original_signal_name
                    signal_index = ''
                    if len(original_signal_name.split('[:,')) == 2:
                        (signal_name, index) = original_signal_name.split('[')
                        signal_index = '[' + index
                    device_node = self.get_device_node(signal)
                    if not device_node is signal:
                        unit = signal_source.Parser.getPhysicalUnit(device_node.text(0), signal_name)
                        signals.append((device_node.text(0), original_signal_name, unit))

        dialog = FrmShowCustomSignalForm("Plot", signals, self.selectSignalForCustomExpressionSignal,
                                         self.addPlotCustomExpressionSignal)
        dialog.show()
        dialog.exec_()

    def tree_view_search_show_list_custom_signal_form(self):
        signal_source = self.Control.getSource(self.Channel)
        selected_rows = self.tree_widget_search.selectedIndexes()
        signals = []
        for row in selected_rows:
            signal = self.tree_widget_search.itemFromIndex(row)
            if signal.parent() is not None:
                if signal.child(0) is None:
                    original_signal_name = signal.text(0)
                    signal_name = original_signal_name
                    signal_index = ''
                    if len(original_signal_name.split('[:,')) == 2:
                        (signal_name, index) = original_signal_name.split('[')
                        signal_index = '[' + index
                    device_node = self.get_device_node(signal)
                    if not device_node is signal:
                        unit = signal_source.Parser.getPhysicalUnit(device_node.text(0), signal_name)
                        signals.append((device_node.text(0), original_signal_name, unit))

        dialog = FrmShowCustomSignalForm("List", signals, self.selectSignalForCustomExpressionSignal,
                                         self.addListCustomExpressionSignal)
        dialog.show()
        dialog.exec_()

    def tree_view_search_plot_signals_with_db_signals(self):
        """
                Opens a plot of the overall behavior of the signal's value.
                """
        if bool(self.database_signals) is True:
            # logger.info("Plotting signals, Please wait...")
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
            if self.isBatchControl:
                # print(self.BatchControl)
                selected_measurement_file = os.path.basename(
                    self.BatchControl.Config._sections['Measurement']['main'])
                manager = self.BatchControl.Managers[selected_measurement_file]
                signal_source = manager.get_source()

            else:
                signal_source = self.Control.getSource(self.Channel)
                manager = self.Control.Managers[signal_source.BaseName]

            pn = datavis.PlotNavigator.cPlotNavigator("Plot window")
            pn.setWindowTitle("PlotNavigator-" + signal_source.BaseName)
            selected_rows = self.tree_widget_search.selectedIndexes()
            axis00 = pn.addAxis()
            for row in selected_rows:
                signal = self.tree_widget_search.itemFromIndex(row)
                if signal.parent() is not None:
                    if signal.child(0) is None:
                        signal_index = ''
                        original_signal_name = signal.text(0)
                        signal_name = original_signal_name
                        if len(original_signal_name.split('[:,')) == 2:
                            (signal_name, index) = original_signal_name.split('[')
                            signal_index = '[' + index
                        device_node = self.get_device_node(signal)
                        try:
                            device_name = self.long_device_names[(device_node.text(0), signal_name)]
                        except:
                            device_name = self.long_device_names[(device_node.text(0), original_signal_name)]
                        value, time_key = signal_source.Parser.getSignal(device_name, signal_name)
                        time = signal_source.Parser.getTime(time_key)
                        unit = signal_source.Parser.getPhysicalUnit(device_name, signal_name)
                        # Check if duplicate signal names selected from different devices
                        if original_signal_name in axis00.label2line:
                            original_signal_name = original_signal_name + "-" + device_name

                        if signal_index == '':
                            pn.addSignal2Axis(axis00, original_signal_name, time, value, unit=unit)
                        else:
                            pn.addSignal2Axis(axis00, original_signal_name, time, eval('value' + signal_index),
                                              unit=unit)

            for signal_name, signal_data in self.database_signals.items():
                time_data = signal_data[0]
                value_data = signal_data[1]
                mapping = signal_data[2]
                if mapping is None:
                    pn.addSignal2Axis(axis00, signal_name, time_data, value_data, unit="")
                else:
                    ax = pn.addAxis(ylabel=signal_name, yticks=mapping,
                                    ylim=(min(mapping) - 0.5, max(mapping) + 0.5))
                    pn.addSignal2Axis(ax, signal_name, time_data, value_data, unit='')

            QtGui.QApplication.restoreOverrideCursor()
            pn.start()
            pn.show()

            synchronizer = manager.sync

            if synchronizer is not None:
                synchronizer.addClient(pn)
            return

        else:
            logger.info(
                "No Signal found from Database.. Please execute analyze and click on More Options->Add to Module "
                "Creation...")

    def tree_view_search_show_quick_search(self):
        signal_source = self.Control.getSource(self.Channel)
        signals = {}
        selected_rows = self.tree_widget_search.selectedIndexes()
        for row in selected_rows:
            signal = self.tree_widget_search.itemFromIndex(row)
            if signal.parent() is not None:
                if signal.child(0) is None:
                    signal_index = ''
                    original_signal_name = signal.text(0)
                    signal_name = original_signal_name
                    if len(original_signal_name.split('[:,')) == 2:
                        (signal_name, index) = original_signal_name.split('[')
                        signal_index = '[' + index
                    device_node = self.get_device_node(signal)
                    try:
                        device_name = self.long_device_names[(device_node.text(0), signal_name)]
                    except:
                        device_name = self.long_device_names[(device_node.text(0), original_signal_name)]
                    value, time_key = signal_source.Parser.getSignal(device_name, signal_name)
                    time = signal_source.Parser.getTime(time_key)
                    unit = signal_source.Parser.getPhysicalUnit(device_name, signal_name)
                    if signal_index == '':
                        signals[signal_name] = (value, time, unit)
                    else:
                        signals[signal_name] = (eval('value' + signal_index), time, unit)
                else:
                    logger.info("Please select signals from array : " + signal.text())
        dialog = FrmQuickSearch(signals)
        dialog.show()
        dialog.exec_()

    def tree_view_search_copy_signal_name(self):
        signal_names = ""
        selected_row = self.tree_widget_search.selectedIndexes()
        for row in selected_row:
            signal = self.tree_widget_search.itemFromIndex(row)
            if signal.parent() is not None:
                if signal.child(0) is None:
                    signal_names += signal.text(0) + "\n"
                else:
                    logger.info("Please select signals from array : " + signal.text(0))
        QApplication.clipboard().setText(signal_names)
        logger.info("Signal name is copied")

    def tree_view_search_copy_signal_name_in_script_form(self):
        # "vx_kmh": ("EBC2_0B", "EBC2_MeanSpdFA_0B"),
        signal_names = ""
        selected_row = self.tree_widget_search.selectedIndexes()
        for row in selected_row:
            signal = self.tree_widget_search.itemFromIndex(row)
            if signal.parent() is not None:
                if signal.child(0) is None:
                    original_signal_name = signal.text(0)
                    signal_name = original_signal_name
                    signal_index = ''
                    if len(original_signal_name.split('[:,')) == 2:
                        (signal_name, index) = original_signal_name.split('[')
                        signal_index = '[' + index
                    device_node = self.get_device_node(signal)
                    device_name = device_node.text(0)
                    if self.need_device_name_in_alias(signal_name, signal_names.split("\n")):
                        alias = signal_name + "-" + device_name
                    else:
                        alias = signal_name

                    script_signal_text = "\"" + alias + "\": (\"" + device_node.text(0) + "\",\"" + signal_name + "\"),"
                    signal_names += script_signal_text + "\n"
                else:
                    logger.info("Please select signals from array : " + signal.text())
        QApplication.clipboard().setText(signal_names)
        logger.info("Signal name in script form is copied")

    def tree_view_search_copy_device_name(self):
        row = self.tree_widget_search.selectedIndexes()[0]
        signal = self.tree_widget_search.itemFromIndex(row)
        device_names = " "
        original_signal_name = signal.text(0)
        signal_name = original_signal_name
        if len(original_signal_name.split('[:,')) == 2:
            (signal_name, index) = original_signal_name.split('[')
            signal_index = '[' + index
        else:
            signal_index = ''
        device_node = self.get_device_node(signal)
        device_name = device_node.text(0)
        if row.parent() is not None:
            QApplication.clipboard().setText(device_name)
            logger.info("Device name is copied")

    def tree_view_search_save_signals_npz(self):
        """
                Save signal's value.
        """
        logger.info("Saving signals in Numpy format, Please wait...")
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
        signal_source = self.Control.getSource(self.Channel)

        selected_rows = self.tree_widget_search.selectedIndexes()
        allsignals_nparray = {}
        for row in selected_rows:
            signal_nparray = []
            signal = self.tree_widget_search.itemFromIndex(row)
            if signal.parent() is not None:
                if signal.child(0) is None:
                    signal_index = ''
                    original_signal_name = signal.text(0)
                    signal_name = original_signal_name
                    if len(original_signal_name.split('[:,')) == 2:
                        (signal_name, index) = original_signal_name.split('[')
                        signal_index = '[' + index
                    device_node = self.get_device_node(signal)
                    try:
                        device_name = self.long_device_names[(device_node.text(0), signal_name)]
                    except:
                        device_name = self.long_device_names[(device_node.text(0), original_signal_name)]
                    value, time_key = signal_source.Parser.getSignal(device_name, signal_name)
                    time = signal_source.Parser.getTime(time_key)
                    unit = signal_source.Parser.getPhysicalUnit(device_name, signal_name)
                    signal_nparray.append(time)
                    if signal_index == '':
                        signal_nparray.append(value)
                    else:
                        signal_nparray.append(eval('value' + signal_index))
                    allsignals_nparray[original_signal_name] = np.array(signal_nparray)
                else:
                    logger.info("Please select signals from array : " + signal.text())

        directory_path = os.path.dirname(signal_source.FileName)
        measurement_filename = os.path.splitext(signal_source.BaseName)[0]
        directory_name = measurement_filename + "_processed"

        directory_path = os.path.join(directory_path, directory_name)
        if not os.path.isdir(directory_path):
            os.mkdir(directory_path)

        npz_file_name = os.path.join(directory_path, measurement_filename + "_signals.npz")
        np.savez(npz_file_name, allsignals_nparray)
        logger.info("Signals are saved at " + npz_file_name)
        QtGui.QApplication.restoreOverrideCursor()
        return

    def tree_view_search_save_signals_hdf5(self):
        """
                Save signal's value.
        """
        logger.info("Saving signals in HDF5 format, Please wait...")
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
        signal_source = self.Control.getSource(self.Channel)

        # folder creation for storing h5 file
        directory_path = os.path.dirname(signal_source.FileName)
        measurement_filename = os.path.splitext(signal_source.BaseName)[0]
        directory_name = measurement_filename + "_processed"
        directory_path = os.path.join(directory_path, directory_name)
        if not os.path.isdir(directory_path):
            os.mkdir(directory_path)

        # create h5 file
        h5_file_name = os.path.join(directory_path, measurement_filename + "_signals.h5")
        h5_file_handle = h5py.File(h5_file_name, 'w')
        selected_rows = self.tree_widget_search.selectedIndexes()
        for row in selected_rows:
            signal = self.tree_widget_search.itemFromIndex(row)
            if signal.parent() is not None:
                if signal.child(0) is None:
                    signal_index = ''
                    original_signal_name = signal.text(0)
                    signal_name = original_signal_name
                    if len(original_signal_name.split('[:,')) == 2:
                        (signal_name, index) = original_signal_name.split('[')
                        signal_index = '[' + index
                    device_node = self.get_device_node(signal)
                    try:
                        device_name = self.long_device_names[(device_node.text(0), signal_name)]
                    except:
                        device_name = self.long_device_names[(device_node.text(0), original_signal_name)]
                    value, time_key = signal_source.Parser.getSignal(device_name, signal_name)
                    h5_signal = h5_file_handle.create_group(signal_name)

                    signal_time = signal_source.Parser.getTime(time_key)
                    unit = signal_source.Parser.getPhysicalUnit(device_name, signal_name)

                    h5_signal.attrs['unit'] = unit
                    h5_signal.attrs['device_name'] = device_name

                    if signal_index == '':
                        signal_value = value
                    else:
                        signal_value = eval('value' + signal_index)
                    h5_signal.create_dataset("time", data=signal_time)
                    h5_signal.create_dataset("value", data=signal_value)
        h5_file_handle.close()
        logger.info("Signals are saved at " + h5_file_name)
        QtGui.QApplication.restoreOverrideCursor()
        return

    def tree_view_search_show_signal_info(self):
        """
        Opens and shows the signal's data, such as signal name, device name,
        maximum value, minimum, whether or not is empty, etc.
        """
        extended_signal_information = {}
        signal_information = ""
        signal_source = self.Control.getSource(self.Channel)
        self.signal_text_info = QtGui.QTextEdit()
        self.signal_text_info.setReadOnly(True)
        row = self.tree_widget_search.selectedIndexes()[0]
        signal = self.tree_widget_search.itemFromIndex(row)
        # Prepare description lines
        original_signal_name = signal.text(0)
        signal_name = original_signal_name
        if len(original_signal_name.split('[:,')) == 2:
            (signal_name, index) = original_signal_name.split('[')
            signal_index = '[' + index
        else:
            signal_index = ''
        device_node = self.get_device_node(signal)
        try:
            device_name = self.long_device_names[(device_node.text(0), signal_name)]
        except:
            device_name = self.long_device_names[(device_node.text(0), original_signal_name)]
        signal_unit = signal_source.Parser.getPhysicalUnit(device_name, signal_name)

        if signal_source.BaseName.split('.', -1)[-1] == 'mat':
            extended_signal_information = signal_source.Parser.getExtendedSignalInformation(device_name, signal_name)
            for key, value in extended_signal_information.iteritems():
                signal_information = signal_information + key + ":  " + extended_signal_information[key] + '\n'
                self.signal_text_info.append(key + ":  " + extended_signal_information[key])
                self.signal_text_info.setToolTip(signal_information)
        # signal_information = ""
        elif signal_source.BaseName.split('.', -1)[-1] == 'h5' or signal_source.BaseName.split('.', -1)[
            -1] == '.hdf5':
            try:
                extended_signal_information = signal_source.Parser.getExtendedSignalInformation(device_name,
                                                                                                signal_name)
                for key, value in extended_signal_information.iteritems():
                    signal_information = signal_information + key + ":  " + str(
                        extended_signal_information[key]) + '\n'
                    self.signal_text_info.append(key + ":  " + str(extended_signal_information[key]))
                    self.signal_text_info.setToolTip(signal_information)
            except:
                self.signal_text_info.append("Signal Name: %s" % original_signal_name)
                self.signal_text_info.append("Device Name: %s" % device_name)
                signal_information = device_name + "-" + signal_source.Parser.Hdf5['devices'][device_name].keys()[
                    0] + "-" + signal_name
                self.signal_text_info.append("Extended Information: %s" % signal_information)
                # Fetch the unit, handle acordingly if not present
                self.signal_text_info.append("Unit: %s" % signal_unit)
        else:
            # information = information + key + ": " + extended_information[key] + '\n'
            self.signal_text_info.append("Signal Name: %s" % original_signal_name)
            self.signal_text_info.append("Device Name: %s" % device_name)
            # Fetch the unit, handle acordingly if not present
            self.signal_text_info.append("Unit: %s" % signal_unit)

        # self.signal_text_info.append("Signal Name: %s" % original_signal_name)
        # self.signal_text_info.append("Device Name: %s" % device_name)
        # # Fetch the unit, handle acordingly if not present
        #
        # self.signal_text_info.append("Unit: %s" % signal_unit)
        # Get signal length. If the signal is empty, print accordingly
        signal_length = signal_source.Parser.getSignalLength(device_name, signal_name)

        try:
            if signal_length > 0:
                # Signal is not empty, print some data about it
                raw_signal, _ = signal_source.Parser.getSignal(device_name, signal_name)
                # raw_signal, _ = signal_source.Parser.getSignal(device_name, signal_name)
                signal_average = np.average(raw_signal)
                signal_max = np.amax(raw_signal)
                signal_min = np.amin(raw_signal)
                self.signal_text_info.append("Length:  %s samples"
                                             % str(signal_length))
                self.signal_text_info.append("Average:  %s  %s"
                                             % (str(signal_average), signal_unit))
                self.signal_text_info.append("Max:  %s  %s"
                                             % (str(signal_max), signal_unit))
                self.signal_text_info.append("Min:  %s  %s"
                                             % (str(signal_min), signal_unit))
            else:
                self.signal_text_info.append("The signal is empty.")
        except TypeError:
            msg = "Can't gather information about signal '%s'" % (signal_name)
            self.signal_text_info.append(msg)

        dialog = FrmShowSignalInfo(self.signal_text_info)
        dialog.show()
        dialog.exec_()
        return

    def tree_widget_search_doubleClicked(self, index):
        selected_row = self.tree_widget_search.selectedIndexes()[0]

        signal = self.tree_widget_search.itemFromIndex(selected_row)
        if signal.parent() is not None:
            if signal.child(0) is None:
                original_signal_name = signal.text(0)
                signal_name = original_signal_name
                signal_index = ''
                if len(original_signal_name.split('[:,')) == 2:
                    (signal_name, index) = original_signal_name.split('[')
                    signal_index = '[' + index

                device_node = self.get_device_node(signal)

                if not device_node is signal:
                    device_name = device_node.text(0)
                    signal_unit = self.getPhysicalUnit(device_name, signal_name)
                    self.selectSignalForCustomExpressionSignal.signal.emit(
                        (device_name, original_signal_name, signal_unit))
            else:
                logger.info("Please select signals from array " + signal.text())

    def getCurrentSelectionFromTreeViewSearch(self, Unit=True):
        selected_signals_list = []
        selected_rows = self.tree_widget_search.selectedIndexes()
        for row in selected_rows:
            signal = self.tree_widget_search.itemFromIndex(row)
            if signal.parent() is not None:
                if signal.child(0) is None:
                    original_signal_name = signal.text(0)
                    signal_name = original_signal_name
                    signal_index = ''
                    if len(original_signal_name.split('[:,')) == 2:
                        (signal_name, index) = original_signal_name.split('[')
                        signal_index = '[' + index
                    device_node = self.get_device_node(signal)
                    if Unit:
                        signal_unit = self.getPhysicalUnit(device_node.text(0), signal_name)
                        selected_signals_list.append((device_node.text(0), original_signal_name, signal_unit))
                    else:
                        selected_signals_list.append((device_node.text(0), original_signal_name))
                else:
                    logger.info("Please select signals to from array : " + signal.text())
        return selected_signals_list
    # </editor-fold>


class FrmShowFileInfo(QDialog):

    def __init__(self, file_info):
        super(FrmShowFileInfo, self).__init__()
        self.setModal(False)
        self.setMinimumSize(800, 400)
        gbox_file_info = QGroupBox("")
        hboxlayout_file_info = QtGui.QHBoxLayout()

        self.txt_file_info = QtGui.QTextEdit()
        self.txt_file_info.setReadOnly(True)
        self.txt_file_info.setText(file_info)
        hboxlayout_file_info.addWidget(self.txt_file_info)
        gbox_file_info.setLayout(hboxlayout_file_info)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.ok_clicked)

        main_layout = QVBoxLayout()
        main_layout.addWidget(gbox_file_info)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

        self.setWindowTitle("File Information")

    def ok_clicked(self):
        self.close()


class FrmShowSignalInfo(QDialog):

    def __init__(self, signal_text_info):
        super(FrmShowSignalInfo, self).__init__()
        self.setModal(False)
        self.setMinimumSize(1000, 260)
        gbox_signal_info = QGroupBox("")
        hboxlayout_signinfo = QtGui.QHBoxLayout()

        hboxlayout_signinfo.addWidget(signal_text_info)
        gbox_signal_info.setLayout(hboxlayout_signinfo)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.ok_clicked)

        main_layout = QVBoxLayout()
        main_layout.addWidget(gbox_signal_info)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

        self.setWindowTitle("Signal Information")

    def ok_clicked(self):
        self.close()


class FrmQuickSearch(QDialog):

    def __init__(self, signals):
        super(FrmQuickSearch, self).__init__()
        self.setModal(False)
        self.setMinimumSize(800, 400)

        dict_pairs = signals.items()
        pairs_iterator = iter(dict_pairs)
        first_pair = next(pairs_iterator)
        signal_name_to_check = first_pair[0]
        self.value, self.time, self.unit = first_pair[1]
        vboxlayout_search_criteria = QtGui.QVBoxLayout()
        vboxlayout_search_criteria.setSpacing(0)
        vboxlayout_search_criteria.setContentsMargins(1, 1, 1, 1)

        # <editor-fold desc="Search operations">
        gbox_search_criteria = QGroupBox('')
        hboxlayout_search_criteria = QtGui.QHBoxLayout()
        lbl_signal_name = QLabel(signal_name_to_check)

        hboxlayout_search_criteria.addWidget(lbl_signal_name, 0, Qt.AlignVCenter)
        lbl_spacer = QLabel("")
        hboxlayout_search_criteria.addWidget(lbl_spacer, 0, Qt.AlignVCenter)
        self.selected_operator = QComboBox()
        self.selected_operator.addItems(["==", ">=", "<=", "!=", ">", "<"])
        hboxlayout_search_criteria.addWidget(self.selected_operator, 0, Qt.AlignVCenter)

        self.value_to_compare = QtGui.QLineEdit()
        self.value_to_compare.setToolTip('Provide value to compare')
        hboxlayout_search_criteria.addWidget(self.value_to_compare, 0, Qt.AlignVCenter)

        gbox_search_criteria.setLayout(hboxlayout_search_criteria)

        vboxlayout_search_criteria.addWidget(gbox_search_criteria, 0, Qt.AlignTop)
        # </editor-fold>

        # <editor-fold desc="interval table">
        gbox_interval_table = QGroupBox('')
        hboxlayout_interval_table = QtGui.QHBoxLayout()

        self.interval_table_model = QStandardItemModel()
        self.interval_table_model.setHorizontalHeaderLabels(
            ['Start Index', 'End Index', 'Start Timestamp', 'End Timestamp'])

        self.interval_table = QtGui.QTableView()
        self.interval_table.setAlternatingRowColors(True)
        self.interval_table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.interval_table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        header = self.interval_table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignHCenter)

        self.interval_table.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        self.interval_table.setModel(self.interval_table_model)
        hboxlayout_interval_table.addWidget(self.interval_table)
        gbox_interval_table.setLayout(hboxlayout_interval_table)
        vboxlayout_search_criteria.addWidget(gbox_interval_table)
        # </editor-fold>

        # <editor-fold desc="buttons">
        gbox_buttons = QGroupBox('')
        hboxlayout_buttons = QtGui.QHBoxLayout()
        self.lbl_status = QLabel("")
        hboxlayout_buttons.addWidget(self.lbl_status, 0, Qt.AlignRight)

        pbutton_show_result = QPushButton("Show result")
        pbutton_show_result.setToolTip('Click to view result')
        pbutton_show_result.clicked.connect(self.show_result)
        hboxlayout_buttons.addWidget(pbutton_show_result, 1, Qt.AlignRight)

        pbutton_close = QPushButton("Close")
        pbutton_close.setToolTip('Close this window')
        pbutton_close.clicked.connect(self.close_clicked)
        hboxlayout_buttons.addWidget(pbutton_close, 0, Qt.AlignRight)
        gbox_buttons.setLayout(hboxlayout_buttons)
        vboxlayout_search_criteria.addWidget(gbox_buttons, 0, Qt.AlignBottom)
        # </editor-fold>
        self.setLayout(vboxlayout_search_criteria)

        self.setWindowTitle("Search signal value")

    def show_result(self):
        result = None
        self.interval_table_model.clear()
        if self.value_to_compare.text() != "":
            if self.selected_operator.currentText() == '==':
                result = self.value == float(self.value_to_compare.text())
            elif self.selected_operator.currentText() == '>=':
                result = self.value >= float(self.value_to_compare.text())
            elif self.selected_operator.currentText() == '<=':
                result = self.value <= float(self.value_to_compare.text())
            elif self.selected_operator.currentText() == '!=':
                result = self.value != float(self.value_to_compare.text())
            elif self.selected_operator.currentText() == '>':
                result = self.value > float(self.value_to_compare.text())
            elif self.selected_operator.currentText() == '<':
                result = self.value < float(self.value_to_compare.text())

            if np.any(result) == True:
                self.lbl_status.setText("")
            else:
                self.lbl_status.setText("No result found")

            intervals = maskToIntervals(result)
            jumps = [[start] for start, end in intervals]
            self.interval_table_model.setHorizontalHeaderLabels(
                ['Start Index', 'End Index', 'Start Timestamp', 'End Timestamp'])
            for jump, interval in zip(jumps, intervals):
                item_start_index = QStandardItem(str(interval[0]))
                item_end_index = QStandardItem(str(interval[1]))
                item_start_timestamp = QStandardItem(str(self.time[interval[0]]))

                if interval[1] == len(self.time):
                    item_end_timestamp = QStandardItem(str(self.time[interval[1] - 1]))
                else:
                    item_end_timestamp = QStandardItem(str(self.time[interval[1]]))

                item_start_index.setEditable(False)
                item_end_index.setEditable(False)
                item_start_timestamp.setEditable(False)
                item_end_timestamp.setEditable(False)

                self.interval_table_model.appendRow(
                    [item_start_index, item_end_index, item_start_timestamp, item_end_timestamp])
        else:
            self.lbl_status.setText("Provide value for comparison")

    def close_clicked(self):
        self.close()


class FrmShowCustomSignalForm(QDialog):

    def __init__(self, name, selectedSignals, selectSignalForCustomExpressionSignal, addCustomExpressionSignal,addCommentForCustome=""):
        super(FrmShowCustomSignalForm, self).__init__()
        self.setWindowTitle(name + " Custom expression editor")
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint
            | QtCore.Qt.WindowMaximizeButtonHint)
        self.setWindowIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'add_custom_signal_24.png')))
        self.setModal(False)
        self.center()
        self.addCustomExpressionSignal = addCustomExpressionSignal
        selectSignalForCustomExpressionSignal.signal.connect(self.addSignalsFromSelector)

        self.selected_custom_signals_list = []
        self.comment=""


        vboxlayout_custom_signal = QtGui.QVBoxLayout()
        vboxlayout_custom_signal.setSpacing(0)
        vboxlayout_custom_signal.setContentsMargins(1, 1, 1, 1)

        # <editor-fold desc="Custom Signal name">
        gbox_custom_signals_name = QGroupBox('')
        hboxlayout_custom_signals_name = QtGui.QHBoxLayout()
        lbl_signal_name = QLabel("Signal Name : ")
        hboxlayout_custom_signals_name.addWidget(lbl_signal_name)

        self.lineedit_custom_signal_name = QtGui.QLineEdit()
        self.lineedit_custom_signal_name.setToolTip('Provide name of the custom signal')
        hboxlayout_custom_signals_name.addWidget(self.lineedit_custom_signal_name)

        lbl_signal_unit = QLabel("Unit  : ")
        hboxlayout_custom_signals_name.addWidget(lbl_signal_unit)

        self.lineedit_custom_signal_unit = QtGui.QLineEdit()
        self.lineedit_custom_signal_unit.setToolTip('Provide unit of the custom signal')
        hboxlayout_custom_signals_name.addWidget(self.lineedit_custom_signal_unit)

        gbox_custom_signals_name.setLayout(hboxlayout_custom_signals_name)
        vboxlayout_custom_signal.addWidget(gbox_custom_signals_name)
        # </editor-fold>

        # <editor-fold desc="Custom Signal calculation">

        gbox_custom_signals_calculation = QGroupBox('')
        hboxlayout_custom_signals_calculation = QtGui.QHBoxLayout()

        lbl_custom_signal_info = QLabel("Add signals by double clicking desired signal in Signal Selector")
        lbl_custom_signal_info.setStyleSheet("""QLabel {font-size: 8pt; color:darkgrey;}""")
        vboxlayout_custom_signal.addWidget(lbl_custom_signal_info, 0, Qt.AlignCenter)

        lbl_signal_calculation = QLabel("Calculation   : ")
        hboxlayout_custom_signals_calculation.addWidget(lbl_signal_calculation, 0, Qt.AlignTop)

        self.lineedit_custom_signal_expression = QtGui.QPlainTextEdit()
        self.lineedit_custom_signal_expression.setStyleSheet(
            """QPlainTextEdit {font-size: 10pt; font-family: Consolas;}""")
        self.lineedit_custom_signal_expression.setToolTip('Provide expression for custom signal')
        hboxlayout_custom_signals_calculation.addWidget(self.lineedit_custom_signal_expression, 0, Qt.AlignVCenter)

        gbox_custom_signals_calculation.setLayout(hboxlayout_custom_signals_calculation)
        vboxlayout_custom_signal.addWidget(gbox_custom_signals_calculation)
        # </editor-fold>
        if len(selectedSignals) != 0:
            for selectedSignal in selectedSignals:
                self.addSignalsFromSelector(selectedSignal)

        # <editor-fold desc="Calculation Helper buttons">
        vboxlayout_buttons = QtGui.QVBoxLayout()
        hboxlayout_buttons = QtGui.QHBoxLayout()
        vboxlayout_buttons.setSpacing(0)
        vboxlayout_buttons.setContentsMargins(1, 1, 1, 1)
        hboxlayout_buttons.setSpacing(0)
        hboxlayout_buttons.setContentsMargins(1, 1, 1, 1)
        btnSize = QSize(30, 20)

        gbox_buttons1 = QGroupBox('')
        gridlayout1 = QtGui.QGridLayout()
        gridlayout1.setSpacing(0)
        gridlayout1.setContentsMargins(1, 1, 1, 1)

        gridlayout1.setSpacing(0)
        push7 = QPushButton("7", self)
        push7.setFixedSize(btnSize)
        push7.clicked.connect(self.action7)
        gridlayout1.addWidget(push7, 0, 0)
        push8 = QPushButton("8", self)
        push8.setFixedSize(btnSize)
        push8.clicked.connect(self.action8)
        gridlayout1.addWidget(push8, 0, 1)
        push9 = QPushButton("9", self)
        push9.setFixedSize(btnSize)
        push9.clicked.connect(self.action9)
        gridlayout1.addWidget(push9, 0, 2)
        push4 = QPushButton("4", self)
        push4.setFixedSize(btnSize)
        push4.clicked.connect(self.action4)
        gridlayout1.addWidget(push4, 1, 0)
        push5 = QPushButton("5", self)
        push5.setFixedSize(btnSize)
        push5.clicked.connect(self.action5)
        gridlayout1.addWidget(push5, 1, 1)
        push6 = QPushButton("6", self)
        push6.setFixedSize(btnSize)
        push6.clicked.connect(self.action6)
        gridlayout1.addWidget(push6, 1, 2)
        push1 = QPushButton("1", self)
        push1.setFixedSize(btnSize)
        push1.clicked.connect(self.action1)
        gridlayout1.addWidget(push1, 2, 0)
        push2 = QPushButton("2", self)
        push2.setFixedSize(btnSize)
        push2.clicked.connect(self.action2)
        gridlayout1.addWidget(push2, 2, 1)
        push3 = QPushButton("3", self)
        push3.setFixedSize(btnSize)
        push3.clicked.connect(self.action3)
        gridlayout1.addWidget(push3, 2, 2)
        push0 = QPushButton("0", self)
        push0.setFixedSize(btnSize)
        push0.clicked.connect(self.action0)
        gridlayout1.addWidget(push0, 3, 0)
        push_point = QPushButton(".", self)
        push_point.setFixedSize(btnSize)
        push_point.clicked.connect(self.action_point)
        gridlayout1.addWidget(push_point, 3, 1)
        push_spc = QPushButton("SPC", self)
        push_spc.setFixedSize(btnSize)
        push_spc.clicked.connect(self.action_spc)
        gridlayout1.addWidget(push_spc, 3, 2)
        gbox_buttons1.setLayout(gridlayout1)

        gbox_buttons2 = QGroupBox('')
        gridlayout2 = QtGui.QGridLayout()
        gridlayout2.setSpacing(0)
        gridlayout2.setContentsMargins(1, 1, 1, 1)
        gridlayout2.setSpacing(0)
        push_a = QPushButton("A", self)
        push_a.setFixedSize(btnSize)
        push_a.clicked.connect(self.action_a)
        gridlayout2.addWidget(push_a, 0, 0)
        push_b = QPushButton("B", self)
        push_b.setFixedSize(btnSize)
        push_b.clicked.connect(self.action_b)
        gridlayout2.addWidget(push_b, 1, 0)
        push_c = QPushButton("C", self)
        push_c.setFixedSize(btnSize)
        push_c.clicked.connect(self.action_c)
        gridlayout2.addWidget(push_c, 2, 0)
        push_d = QPushButton("D", self)
        push_d.setFixedSize(btnSize)
        push_d.clicked.connect(self.action_d)
        gridlayout2.addWidget(push_d, 3, 0)
        push_e = QPushButton("E", self)
        push_e.setFixedSize(btnSize)
        push_e.clicked.connect(self.action_e)
        gridlayout2.addWidget(push_e, 0, 1)
        push_f = QPushButton("F", self)
        push_f.setFixedSize(btnSize)
        push_f.clicked.connect(self.action_f)
        gridlayout2.addWidget(push_f, 1, 1)
        push_x = QPushButton("x", self)
        push_x.setFixedSize(btnSize)
        push_x.clicked.connect(self.action_x)
        gridlayout2.addWidget(push_x, 2, 1)
        push_ff = QPushButton("0xFF", self)
        push_ff.setFixedSize(btnSize)
        push_ff.clicked.connect(self.action_ff)
        gridlayout2.addWidget(push_ff, 3, 1)
        gbox_buttons2.setLayout(gridlayout2)

        gbox_buttons3 = QGroupBox('')
        gridlayout3 = QtGui.QGridLayout()
        gridlayout3.setSpacing(0)
        gridlayout3.setContentsMargins(1, 1, 1, 1)
        gridlayout3.setSpacing(0)
        push_plus = QPushButton("+", self)
        push_plus.setFixedSize(btnSize)
        push_plus.clicked.connect(self.action_plus)
        gridlayout3.addWidget(push_plus, 3, 0)
        push_minus = QPushButton("-", self)
        push_minus.setFixedSize(btnSize)
        push_minus.clicked.connect(self.action_minus)
        gridlayout3.addWidget(push_minus, 2, 0)
        push_mul = QPushButton("*", self)
        push_mul.setFixedSize(btnSize)
        push_mul.clicked.connect(self.action_mul)
        gridlayout3.addWidget(push_mul, 1, 0)
        push_div = QPushButton("/", self)
        push_div.setFixedSize(btnSize)
        push_div.clicked.connect(self.action_div)
        gridlayout3.addWidget(push_div, 0, 0)
        push_mod = QPushButton("%", self)
        push_mod.setFixedSize(btnSize)
        push_mod.clicked.connect(self.action_mod)
        gridlayout3.addWidget(push_mod, 0, 1)
        push_openbracket = QPushButton("(", self)
        push_openbracket.setFixedSize(btnSize)
        push_openbracket.clicked.connect(self.action_openbracket)
        gridlayout3.addWidget(push_openbracket, 1, 1)
        push_closebracket = QPushButton(")", self)
        push_closebracket.setFixedSize(btnSize)
        push_closebracket.clicked.connect(self.action_closebracket)
        gridlayout3.addWidget(push_closebracket, 2, 1)
        push_colon = QPushButton(":", self)
        push_colon.setFixedSize(btnSize)
        push_colon.clicked.connect(self.action_colon)
        gridlayout3.addWidget(push_colon, 3, 1)
        gbox_buttons3.setLayout(gridlayout3)

        gbox_buttons4 = QGroupBox('')
        gridlayout4 = QtGui.QGridLayout()
        gridlayout4.setSpacing(0)
        gridlayout4.setContentsMargins(1, 1, 1, 1)
        gridlayout4.setSpacing(0)
        push_clear = QPushButton("C", self)
        push_clear.setFixedSize(btnSize)
        push_clear.clicked.connect(self.action_clear)
        gridlayout4.addWidget(push_clear, 0, 0)
        push_backspace = QPushButton("BAK", self)
        push_backspace.setFixedSize(btnSize)
        push_backspace.clicked.connect(self.action_backspace)
        gridlayout4.addWidget(push_backspace, 0, 1)
        push_opensquare = QPushButton("[", self)
        push_opensquare.setFixedSize(btnSize)
        push_opensquare.clicked.connect(self.action_opensquare)
        gridlayout4.addWidget(push_opensquare, 1, 0)
        push_closesquare = QPushButton("]", self)
        push_closesquare.setFixedSize(btnSize)
        push_closesquare.clicked.connect(self.action_closesquare)
        gridlayout4.addWidget(push_closesquare, 1, 1)
        push_opencurle = QPushButton("{", self)
        push_opencurle.setFixedSize(btnSize)
        push_opencurle.clicked.connect(self.action_opencurle)
        gridlayout4.addWidget(push_opencurle, 2, 0)
        push_closecurle = QPushButton("}", self)
        push_closecurle.setFixedSize(btnSize)
        push_closecurle.clicked.connect(self.action_closecurle)
        gridlayout4.addWidget(push_closecurle, 2, 1)
        gbox_buttons4.setLayout(gridlayout4)

        gbox_buttons5 = QGroupBox('Logical')
        gridlayout5 = QtGui.QGridLayout()
        gridlayout5.setSpacing(0)
        gridlayout5.setContentsMargins(1, 1, 1, 1)
        gridlayout5.setSpacing(0)
        push_equal = QPushButton("==", self)
        push_equal.setFixedSize(btnSize)
        push_equal.clicked.connect(self.action_equal)
        gridlayout5.addWidget(push_equal, 0, 0)
        push_notequal = QPushButton("!=", self)
        push_notequal.setFixedSize(btnSize)
        push_notequal.clicked.connect(self.action_notequal)
        gridlayout5.addWidget(push_notequal, 0, 1)
        push_and = QPushButton("and", self)
        push_and.setFixedSize(btnSize)
        push_and.clicked.connect(self.action_and)
        gridlayout5.addWidget(push_and, 0, 2)
        push_or = QPushButton("or", self)
        push_or.setFixedSize(btnSize)
        push_or.clicked.connect(self.action_or)
        gridlayout5.addWidget(push_or, 1, 2)
        push_less = QPushButton("<", self)
        push_less.setFixedSize(btnSize)
        push_less.clicked.connect(self.action_less)
        gridlayout5.addWidget(push_less, 1, 1)
        push_greater = QPushButton(">", self)
        push_greater.setFixedSize(btnSize)
        push_greater.clicked.connect(self.action_greater)
        gridlayout5.addWidget(push_greater, 1, 0)
        push_greater_equal = QPushButton(">=", self)
        push_greater_equal.setFixedSize(btnSize)
        push_greater_equal.clicked.connect(self.action_greater_equal)
        gridlayout5.addWidget(push_greater_equal, 2, 0)
        push_less_equal = QPushButton("<=", self)
        push_less_equal.setFixedSize(btnSize)
        push_less_equal.clicked.connect(self.action_less_equal)
        gridlayout5.addWidget(push_less_equal, 2, 1)
        push_not = QPushButton("!", self)
        push_not.setFixedSize(btnSize)
        push_not.clicked.connect(self.action_not)
        gridlayout5.addWidget(push_not, 2, 2)
        gbox_buttons5.setLayout(gridlayout5)

        gbox_buttons6 = QGroupBox('Bitwise')
        gridlayout6 = QtGui.QGridLayout()
        gridlayout6.setSpacing(0)
        gridlayout6.setContentsMargins(1, 1, 1, 1)
        gridlayout6.setSpacing(0)
        push_bit_and = QPushButton("&&", self)
        push_bit_and.setFixedSize(btnSize)
        push_bit_and.clicked.connect(self.action_bit_and)
        gridlayout6.addWidget(push_bit_and, 0, 0)
        push_negation = QPushButton("~", self)
        push_negation.setFixedSize(btnSize)
        push_negation.clicked.connect(self.action_negation)
        gridlayout6.addWidget(push_negation, 0, 1)
        push_bit_or = QPushButton("|", self)
        push_bit_or.setFixedSize(btnSize)
        push_bit_or.clicked.connect(self.action_bit_or)
        gridlayout6.addWidget(push_bit_or, 1, 0)
        push_leftshift = QPushButton("<<", self)
        push_leftshift.setFixedSize(btnSize)
        push_leftshift.clicked.connect(self.action_leftshift)
        gridlayout6.addWidget(push_leftshift, 1, 1)
        push_cap = QPushButton("^", self)
        push_cap.setFixedSize(btnSize)
        push_cap.clicked.connect(self.action_cap)
        gridlayout6.addWidget(push_cap, 2, 0)
        push_rightshift = QPushButton(">>", self)
        push_rightshift.setFixedSize(btnSize)
        push_rightshift.clicked.connect(self.action_rightshift)
        gridlayout6.addWidget(push_rightshift, 2, 1)
        gbox_buttons6.setLayout(gridlayout6)

        hboxlayout_buttons.addWidget(gbox_buttons1)
        hboxlayout_buttons.addWidget(gbox_buttons2)
        hboxlayout_buttons.addWidget(gbox_buttons3)
        hboxlayout_buttons.addWidget(gbox_buttons4)
        hboxlayout_buttons.addWidget(gbox_buttons5)
        hboxlayout_buttons.addWidget(gbox_buttons6)
        vboxlayout_buttons.addLayout(hboxlayout_buttons)

        vboxlayout_custom_signal.addLayout(vboxlayout_buttons)

        # </editor-fold>

        # <editor-fold desc="numpy functions">
        gbox_numpy_buttons = QGroupBox('')
        hboxlayout_numpy_buttons = QtGui.QHBoxLayout()
        hboxlayout_numpy_buttons.setSpacing(0)
        hboxlayout_numpy_buttons.setContentsMargins(1, 1, 1, 1)

        self.combo_numpy_functions = QComboBox()

        savgol_info= " \"\"\" window_length : int The length of the filter window and must be a positive odd integer. \n polyorder : int The order of the polynomial used to fit the samples and must be less than window_length \n deriv : nonnegative integer optional. The order of the derivative to compute.The default is 0 which means to filter the data without differentiating.\"\"\"\n"
        zero_phase_info = "\"\"\"  Filter type = zero phase low pass ,\n Default cutoff_frequency = 2 \"\"\"\n"

        """The Savitzky Golay filter is a particular type of low-pass filter, well adapted for data smoothing.
        Typically used to "smooth out" a noisy signal whose frequency span (without noise) is large
        """

        function_names = {
            "WHERE": " np.where(CONDITION, TRUE_VALUE, FALSE_VALUE) ",
            "GRADIENT": " np.gradient(VALUE, np.gradient(TIME)) ",
            "DIFF": " np.diff(VALUE) ",
            "SAVGOL FILTER": savgol_info+"savgol_filter(VALUE,window_length=9,polyorder=2,deriv=0)",
            "ZERO PHASE LOW PASS FILTER": zero_phase_info + " zero_phase_low_pass_filter(TIME,VALUE,cutoff_freq=2) ",
        }

        for function_name, function_string in function_names.iteritems():
            self.combo_numpy_functions.addItem(function_name, function_string)
        self.combo_numpy_functions.setCurrentIndex(0)
        self.combo_numpy_functions.setToolTip("Select function")
        pbutton_numpy_add = QPushButton("Add")
        pbutton_numpy_add.clicked.connect(self.add_numpy_functions)
        hboxlayout_numpy_buttons.addWidget(self.combo_numpy_functions, 0, Qt.AlignLeft)
        hboxlayout_numpy_buttons.addWidget(pbutton_numpy_add, 1, Qt.AlignLeft)

        horizontal_spacer = QSpacerItem(0, 0, QSizePolicy.Expanding)
        hboxlayout_numpy_buttons.addItem(horizontal_spacer)

        gbox_numpy_buttons.setLayout(hboxlayout_numpy_buttons)
        vboxlayout_custom_signal.addWidget(gbox_numpy_buttons)
        # </editor-fold>

        # <editor-fold desc="buttons">
        gbox_buttons = QGroupBox('')
        hboxlayout_buttons = QtGui.QHBoxLayout()

        pbutoon_verify_syntax = QPushButton("Verify Syntax")
        pbutoon_verify_syntax.setToolTip('Verify syntax')
        pbutoon_verify_syntax.clicked.connect(self.verify_syntax)
        hboxlayout_buttons.addWidget(pbutoon_verify_syntax, 1, Qt.AlignRight)

        pbutton_add_to_script = QPushButton("Add To Script")
        pbutton_add_to_script.setToolTip('Add custom signal to script')
        pbutton_add_to_script.clicked.connect(self.addToScript)
        hboxlayout_buttons.addWidget(pbutton_add_to_script, 0, Qt.AlignRight)

        pbutton_close = QPushButton("Close")
        pbutton_close.setToolTip('Close this window')
        pbutton_close.clicked.connect(self.close_clicked)
        hboxlayout_buttons.addWidget(pbutton_close, 0, Qt.AlignRight)
        gbox_buttons.setLayout(hboxlayout_buttons)

        vboxlayout_custom_signal.addWidget(gbox_buttons, 0, Qt.AlignBottom)
        # </editor-fold>

        self.setLayout(vboxlayout_custom_signal)

    def verify_syntax(self):
        expression = self.lineedit_custom_signal_expression.toPlainText().strip()
        if expression == "":
            logger.error("Please provide custom signal expression")
            return
        if str(expression).__contains__("low_pass_filter"):
            if str(expression).__contains__('time_custom_') and str(expression).__contains__('value_custom_'):
                logger.info("Valid custom expression found")
                return True
        elif str(expression).__contains__("savgol_filter"):
            if expression.__contains__("\"\"\""):
                res = expression.split("\"\"\"\n")
                expression = res[1]
        if "time_custom_" in expression:
            expression = expression.replace("time_custom_", "value_custom_")
        for signal_name, custom_signal in self.selected_custom_signals_list:
            if signal_name in expression:
                expression = expression.replace(signal_name, " np.array([1,2,3,4,5,6,7,8,9])")
        try:
            eval(expression)
            logger.info("Valid custom expression found")
        except Exception as e:
            logger.error("Custom expression is not correct :" + str(e))
            return False
        return True

    def addSignalsFromSelector(self, custom_signal):
        self.refresh_signal_list()
        need_device_name_in_alias = False
        signal_available_in_the_list = False
        for csignal_name, selected_custom_signal in self.selected_custom_signals_list:
            if selected_custom_signal == custom_signal:
                signal_available_in_the_list = True
                break
            if custom_signal[1] == selected_custom_signal[1]:
                need_device_name_in_alias = True
                break
        signal_name = ""
        if need_device_name_in_alias is True:
            signal_name = "value_custom_" + custom_signal[0] + "_" + custom_signal[1]
        else:
            signal_name = "value_custom_" + custom_signal[1]
        self.lineedit_custom_signal_expression.insertPlainText(signal_name + " ")
        #self.comment=get_zerophase_filter_info(custom_signal)
        if signal_available_in_the_list is False:
            self.selected_custom_signals_list.append((signal_name, custom_signal))

    def refresh_signal_list(self):
        expression = self.lineedit_custom_signal_expression.toPlainText().strip()
        expression = expression + " "
        unused_signals = []
        for signal_name, custom_signal in self.selected_custom_signals_list:
            if signal_name in expression:
                continue

            unused_signals.append((signal_name, custom_signal))

        for unused_signal in unused_signals:
            self.selected_custom_signals_list.remove(unused_signal)

    def addToScript(self):
        name = self.lineedit_custom_signal_name.text().strip()
        if name == "":
            logger.error("Please provide custom signal name")
            return
        expression = self.lineedit_custom_signal_expression.toPlainText().strip()

        if expression.__contains__("\"\"\""):
            res=expression.split("\"\"\"\n")
            self.comment = res[0]+" \"\"\""
            expression = res[1]
        if expression == "":
            logger.error("Please provide custom signal expression")
            return
        unit = self.lineedit_custom_signal_unit.text()

        if self.verify_syntax() is True:
            self.refresh_signal_list()

            if len(self.selected_custom_signals_list) == 0:
                logger.error("Signals have not added in the expression")
                return
            self.addCustomExpressionSignal.signal.emit((name, self.selected_custom_signals_list, expression, unit,self.comment))
        else:
            logger.error("Please provide valid custom expression")

    def close_clicked(self):
        self.close()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # <editor-fold desc="Button actions">
    def action_plus(self):
        # appending label text

        self.lineedit_custom_signal_expression.insertPlainText(" + ")

    def action_minus(self):
        # appending label text

        self.lineedit_custom_signal_expression.insertPlainText(" - ")

    def action_div(self):
        # appending label text

        self.lineedit_custom_signal_expression.insertPlainText(" / ")

    def action_mul(self):
        # appending label text

        self.lineedit_custom_signal_expression.insertPlainText(" * ")

    def action_point(self):
        # appending label text

        self.lineedit_custom_signal_expression.insertPlainText(".")

    def action0(self):
        # appending label text

        self.lineedit_custom_signal_expression.insertPlainText("0")

    def action1(self):
        # appending label text

        self.lineedit_custom_signal_expression.insertPlainText("1")

    def action2(self):
        # appending label text

        self.lineedit_custom_signal_expression.insertPlainText("2")

    def action3(self):
        # appending label text

        self.lineedit_custom_signal_expression.insertPlainText("3")

    def action4(self):
        # appending label text

        self.lineedit_custom_signal_expression.insertPlainText("4")

    def action5(self):
        # appending label text

        self.lineedit_custom_signal_expression.insertPlainText("5")

    def action6(self):
        # appending label text

        self.lineedit_custom_signal_expression.insertPlainText("6")

    def action7(self):
        # appending label text

        self.lineedit_custom_signal_expression.insertPlainText("7")

    def action8(self):
        # appending label text

        self.lineedit_custom_signal_expression.insertPlainText("8")

    def action9(self):
        # appending label text

        self.lineedit_custom_signal_expression.insertPlainText("9")

    def action_clear(self):
        # clearing the label text
        self.lineedit_custom_signal_expression.clear()

    def action_backspace(self):
        # clearing a single digit
        self.lineedit_custom_signal_expression.setPlainText(self.lineedit_custom_signal_expression.toPlainText()[:-1])

    def action_a(self):
        # appending label text

        self.lineedit_custom_signal_expression.insertPlainText("A")

    def action_b(self):
        # appending label text

        self.lineedit_custom_signal_expression.insertPlainText("B")

    def action_c(self):
        # appending label text

        self.lineedit_custom_signal_expression.insertPlainText("C")

    def action_d(self):
        # appending label text

        self.lineedit_custom_signal_expression.insertPlainText("D")

    def action_e(self):
        # appending label text

        self.lineedit_custom_signal_expression.insertPlainText("E")

    def action_f(self):
        # appending label text

        self.lineedit_custom_signal_expression.insertPlainText("F")

    def action_openbracket(self):
        # appending label text

        self.lineedit_custom_signal_expression.insertPlainText(" (")

    def action_closebracket(self):
        # appending label text

        self.lineedit_custom_signal_expression.insertPlainText(") ")

    def action_opensquare(self):
        # appending label text

        self.lineedit_custom_signal_expression.insertPlainText(" [")

    def action_closesquare(self):
        # appending label text

        self.lineedit_custom_signal_expression.insertPlainText("] ")

    def action_opencurle(self):
        # appending label text

        self.lineedit_custom_signal_expression.insertPlainText(" {")

    def action_closecurle(self):
        # appending label text

        self.lineedit_custom_signal_expression.insertPlainText("} ")

    def action_spc(self):
        self.lineedit_custom_signal_expression.insertPlainText(" ")

    def action_x(self):
        self.lineedit_custom_signal_expression.insertPlainText("x")

    def action_ff(self):
        self.lineedit_custom_signal_expression.insertPlainText(" 0xFF ")

    def action_mod(self):
        self.lineedit_custom_signal_expression.insertPlainText(" % ")

    def action_colon(self):
        self.lineedit_custom_signal_expression.insertPlainText(" : ")

    def action_equal(self):
        self.lineedit_custom_signal_expression.insertPlainText(" == ")

    def action_notequal(self):
        self.lineedit_custom_signal_expression.insertPlainText(" != ")

    def action_and(self):
        self.lineedit_custom_signal_expression.insertPlainText(" and ")

    def action_or(self):
        self.lineedit_custom_signal_expression.insertPlainText(" or ")

    def action_less(self):
        self.lineedit_custom_signal_expression.insertPlainText(" < ")

    def action_greater(self):
        self.lineedit_custom_signal_expression.insertPlainText(" > ")

    def action_greater_equal(self):
        self.lineedit_custom_signal_expression.insertPlainText(" >= ")

    def action_less_equal(self):
        self.lineedit_custom_signal_expression.insertPlainText(" <= ")

    def action_not(self):
        self.lineedit_custom_signal_expression.insertPlainText(" ! ")

    def action_bit_and(self):
        self.lineedit_custom_signal_expression.insertPlainText(" & ")

    def action_negation(self):
        self.lineedit_custom_signal_expression.insertPlainText(" ~ ")

    def action_bit_or(self):
        self.lineedit_custom_signal_expression.insertPlainText(" | ")

    def action_leftshift(self):
        self.lineedit_custom_signal_expression.insertPlainText(" << ")

    def action_rightshift(self):
        self.lineedit_custom_signal_expression.insertPlainText(" >> ")

    def action_cap(self):
        self.lineedit_custom_signal_expression.insertPlainText(" ^ ")

    def add_numpy_functions(self):

        numpy_function_string = self.combo_numpy_functions.itemData(self.combo_numpy_functions.currentIndex())
        self.lineedit_custom_signal_expression.insertPlainText(" " + numpy_function_string + " ")


# </editor-fold>


class FrmShowHelp(QDialog):

    def __init__(self):
        super(FrmShowHelp, self).__init__()
        self.setModal(False)
        self.setMinimumSize(800, 400)
        help_text = """\
								<font size=3>
								<p><big> This is quick help about filter </big></p>
								Once measurement is loaded, Press key to filter required signals. You can also use following options.
								<p><big> 1. Clear : Clear Filter</big></p>
								Reset filter and get view in original state
								<p><big> 2. Aa : Match case</big></p>
								Pressed : Match Case is ON <br>
								Unpressed : Match Case is OFF 
								<p><big> 3. RegEx : Regular expression</big></p>
								A regular expression is a sequence of characters that define a search pattern. <br>
								Please follow this link to learn how to use regular expressions<br>
								<a href="https://regexone.com/"> https://regexone.com/</a><br><br>
								Example 1. Extract all uiObjectRef signals from Hypothesis array<br>
								ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_HypothesisI0I_uiObjectRef <br>
								RegEx: ARS4xx_Device_AlgoSenCycle_pFCTCDHypotheses_HypothesisI<font color="red">\d{1,
								2}</font>I_uiObjectRef<br><br>
								Example 2. Extract all AEBS1 2A signals<br>
								AEBS1_AEBSState_2A<br>
								RegEx: AEBS1_<font color="red">[a-z]+</font>_2A
								</font>
								"""
        gbox_help = QGroupBox("")
        hboxlayout_help = QtGui.QHBoxLayout()

        self.txt_help = QtGui.QTextEdit()
        self.txt_help.setReadOnly(True)
        self.txt_help.setText(help_text)

        hboxlayout_help.addWidget(self.txt_help)
        gbox_help.setLayout(hboxlayout_help)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.ok_clicked)

        main_layout = QVBoxLayout()
        main_layout.addWidget(gbox_help)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

        self.setWindowTitle("Signal Filter Help")

    def ok_clicked(self):
        self.close()


class LeafFilterProxyModel(QtGui.QSortFilterProxyModel):
    """ Class to override the following behaviour:
                            If a parent item doesn't match the filter,
                            none of its children will be shown.

                    This Model matches items which are descendants
                    or ascendants of matching items.
            """

    def filterAcceptsRow(self, row_num, source_parent):
        ''' Overriding the parent function '''

        # Check if the current row matches
        if self.filter_accepts_row_itself(row_num, source_parent):
            return True

        # Traverse up all the way to root and check if any of them match
        if self.filter_accepts_any_parent(source_parent):
            return True

        # Finally, check if any of the children match
        return self.has_accepted_children(row_num, source_parent)

    def filter_accepts_row_itself(self, row_num, parent):
        return super(LeafFilterProxyModel, self).filterAcceptsRow(row_num, parent)

    def filter_accepts_any_parent(self, parent):
        ''' Traverse to the root node and check if any of the
                ancestors match the filter
        '''
        while parent.isValid():
            if self.filter_accepts_row_itself(parent.row(), parent.parent()):
                return True
            parent = parent.parent()
        return False

    def has_accepted_children(self, row_num, parent):
        ''' Starting from the current node as root, traverse all
                the descendants and test if any of the children match
        '''
        model = self.sourceModel()
        source_index = model.index(row_num, 0, parent)

        children_count = model.rowCount(source_index)
        for i in xrange(children_count):
            if self.filterAcceptsRow(i, source_index):
                return True
        return False
