import logging
import os
import subprocess
import sys
import webbrowser
import logging
import pip
import datavis
import numpy as np
from AnalyzeConfigFrame import cAnalyzeConfigFrame
from AnalyzeControl import cAnalyzeControl
from ConfigFrame import cConfigFrame
from MeasurementFrame import cMeasurementFrame
from MeasurementView import MeasurementView
from OptionFrames import cCheckDirOption, cDirOption, cFileOption, cLazyFileOption, cListOptionFrane
from PySide import QtCore, QtGui
from PySide.QtGui import QFileDialog, QIcon, QListWidget, QListWidgetItem
from ReportFilterEditor import cReportFilterEditor
from SearchConfigFrame import cSearchConfigFrame
from ViewConfigFrame import cViewConfigFrame
from ViewControl import cBatchControl
from config.logger import _get_env_info, _get_python_info
from datavis.IntervalFrame import IntervalFrame
from dmw.EventEditorFrame import cEventEditor
from dmw.resimulation_export import cResimExportView
from interface.modules import ModuleName
from log_frame import LogFrame, log_levels
from section_table import ModuleTableFrame
from text.Text import Text
from aebs.fill.fillFLC25_RESIM_EXPORT import export


START_CLOSE_BTN_SIZE = (100, 35)
START_CLOSE_FONT_SIZE = 12
IMAGE_DIRECTORY = os.path.join(os.path.dirname(__file__), "images")

# Global Variables to close scenario visualization window
CLOSE_SCENARIO_VISUALIZATION_WINDOW = False
SCENARIO_VISUALIZATION_SUBPROCESS = None

# Global Variables to close event recorder window
CLOSE_EVENT_RECORDER_WINDOW = False
EVENT_RECORDER_SUBPROCESS = None

logger = logging.getLogger('sessionframes')


class SimpleSignal(QtCore.QObject):
		signal = QtCore.Signal()


class SessionFrame(QtGui.QFrame):
		ConfigFrame = None

		def __init__(self, config, use_simplified_interface):
				QtGui.QFrame.__init__(self)
				self.config = config
				return

		def init(self, use_simplified_interface):
				self.tab_widget = QtGui.QTabWidget()
				layout = QtGui.QVBoxLayout()
				layout.setSpacing(0)
				layout.setContentsMargins(1, 1, 1, 1)
				layout.addWidget(self.tab_widget)
				self.create_tabs(use_simplified_interface)
				self.setLayout(layout)
				return

		def create_tabs(self, use_simplified_interface):
				setup_widget = QtGui.QTabWidget()
				if not use_simplified_interface:
						self.tab_widget.addTab(self.ConfigFrame.Editor, 'Create')
						for tab, name in self.ConfigFrame.SectionFrames:
								setup_widget.addTab(tab, name)
						self.tab_widget.addTab(setup_widget, 'Setup')
				self.tab_widget.addTab(self.ConfigFrame.ControlFrame, 'Start')
				return

		def update(self):
				self.ConfigFrame._update()
				return

		def close(self):
				self.ConfigFrame.close()
				QtGui.QFrame.close(self)
				return


class ViewSessionFrame(SessionFrame):
		def __init__(self, config, use_simplified_interface):
				self.ConfigFrame = cViewConfigFrame(None, config, need_cn = False)
				self.ConfigFrame.setObjectName('ViewWindow')
				SessionFrame.__init__(self, config, use_simplified_interface)
				self.analyze_control = None
				self.batch_control = None
				self.active_control = self.ConfigFrame.Control
				self.anal_mod_sel = None
				self.last_tmp = None
				self.analyze_importer = None
				self.anal_name = None
				self.entries = {}
				self.export_dialog = None
				self.plotview_dialog = None
				self.use_simplified_interface = use_simplified_interface
				if use_simplified_interface:
						self.init(use_simplified_interface)
				else:
						self.create_UI()
				return

		def create_UI(self):
				self.interval_frame = IntervalFrame()
				self.interval_frame.selected_meas_sig.signal.connect(
								self.set_meas_from_int_frame)
				self.analyze_control = cAnalyzeControl(self.config)

				self.splitter = QtGui.QSplitter()
				self.splitter.setObjectName('ViewMainSplitter')
				self.splitter.setOrientation(QtCore.Qt.Vertical)

				view_splitter = self.create_view_frame()
				analyze_splitter = self.create_table_frame()

				self.splitter.addWidget(view_splitter)
				self.splitter.addWidget(analyze_splitter)

				layout = QtGui.QVBoxLayout()
				layout.addWidget(self.splitter)
				hbox = QtGui.QHBoxLayout()

				self.start_btn = QtGui.QPushButton('&Start')
				self.close_btn = QtGui.QPushButton('&Close All')
				self.start_btn.clicked.connect(self.on_start)

				self.combo_box = QtGui.QPushButton()
				menu = QtGui.QMenu()
				self.combo_box.setMenu(menu)
				self.combo_box.menu()
				self.combo_box.setFixedSize(20, START_CLOSE_BTN_SIZE[1])
				self.close_btn.clicked.connect(self.onCloseAll)

				self.ConfigFrame.Control.ComboBoxUpdateSignal.signal.connect(
								self.add_item_2_combobox)

				for btn in (self.start_btn, self.close_btn):
						btn.setFixedSize(*START_CLOSE_BTN_SIZE)
						font = btn.font()
						font.setPointSize(START_CLOSE_FONT_SIZE)
						btn.setFont(font)

				hbox.addStretch(1)
				hbox.addWidget(self.start_btn)
				hbox.addWidget(self.close_btn)
				hbox.addWidget(self.combo_box)
				hbox.addStretch(1)

				layout.addLayout(hbox)

				self.setLayout(layout)
				return

		def create_view_frame(self):
				meas_frame = QtGui.QFrame()
				channel_layout = QtGui.QGridLayout()
				channel_layout.setSpacing(2)
				channel_layout.setContentsMargins(2, 2, 2, 2)
				self.view_splitter = QtGui.QSplitter()
				self.view_splitter.setObjectName('ViewMeasModuleSplitter')
				self.view_splitter.setOrientation(QtCore.Qt.Horizontal)
				measurement = cMeasurementFrame(self.config, self.ConfigFrame.Interface,
																				channel_layout)

				for widget in (measurement.main_ch.OpenFileBtn, measurement.main_ch.Value,
											 measurement.other_meases.OpenFileBtn,
											 measurement.other_meases.Value):
						widget.clicked.connect(self.activate_view_control)

				channel_box = QtGui.QGroupBox('Measurement Channels')
				channel_box.setLayout(channel_layout)
				channel_layout.setSizeConstraint(QtGui.QLayout.SetMaximumSize)

				batch_grid = QtGui.QGridLayout()
				batch_grid.setSpacing(2)
				batch_grid.setContentsMargins(2, 2, 2, 2)
				self.batch_file = cLazyFileOption(None, self.config, 'General', 'BatchFile')
				batch_grid.addWidget(self.batch_file.Label, 0, 0)
				batch_grid.addWidget(self.batch_file.Value, 0, 1)
				batch_grid.addWidget(self.batch_file.OpenFileBtn, 0, 2)
				batch_grid.addWidget(self.batch_file.OpenLastUsedFileBtn, 0, 3)
				self.batch_file.is_save_last_files = True
				self.batch_file.file_type = 'BatchFileDirectory'
				self.batch_file.OpenLastUsedFileBtn.clicked.connect(
						self.batch_file.showLastOpenedFilesDialog)

				self.rep_dir = cDirOption(None, self.config, 'General', 'RepDir')
				batch_grid.addWidget(self.rep_dir.Label, 1, 0)
				batch_grid.addWidget(self.rep_dir.Value, 1, 1)
				batch_grid.addWidget(self.rep_dir.OpenFileBtn, 1, 2)
				batch_grid.addWidget(self.rep_dir.OpenLastUsedFileBtn, 1, 3)
				self.rep_dir.is_save_last_files = True
				self.rep_dir.file_type = 'ReportDirectory'
				self.rep_dir.OpenLastUsedFileBtn.clicked.connect(
						self.rep_dir.showLastOpenedFilesDialog)
				batch_box = QtGui.QGroupBox('Event Database')

				batch_box.setLayout(batch_grid)
				batch_grid.setSizeConstraint(QtGui.QLayout.SetMaximumSize)

				meas_layout = QtGui.QVBoxLayout()
				meas_layout.setSpacing(0)
				meas_layout.setContentsMargins(1, 1, 1, 1)
				meas_layout.addWidget(channel_box)
				meas_layout.addWidget(batch_box)
				meas_layout.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
				dummy_vbox = QtGui.QVBoxLayout()
				dummy_vbox.setSpacing(0)
				dummy_vbox.setContentsMargins(1, 1, 1, 1)
				dummy_vbox.addLayout(meas_layout)
				dummy_frame = QtGui.QFrame()
				dummy_vbox.addWidget(dummy_frame)
				meas_frame.setLayout(dummy_vbox)

				modules_frame = QtGui.QFrame()
				modules_layour = QtGui.QVBoxLayout()
				modules_layour.setSpacing(0)
				modules_layour.setContentsMargins(1, 1, 1, 1)
				modules_layour.addWidget(self.ConfigFrame.TabWidget)
				modules_frame.setLayout(modules_layour)
				self.view_splitter.addWidget(meas_frame)
				self.view_splitter.addWidget(modules_frame)
				return self.view_splitter

		def create_table_frame(self):
				self.analyze_splitter = QtGui.QSplitter()
				self.analyze_splitter.setObjectName('AnalyzeSplitter')
				self.analyze_splitter.setOrientation(QtCore.Qt.Horizontal)
				interval_box = QtGui.QGroupBox('Intervals')
				interval_layout = QtGui.QVBoxLayout()

				interval_grid = QtGui.QGridLayout()

				self.analyzes = cListOptionFrane(self.config, 'iAnalyze')
				self.analyzes.Label.setText('Analyze Scripts')
				interval_grid.addWidget(self.analyzes.Label, 0, 0)
				interval_grid.addWidget(self.analyzes.Value, 0, 1)
				interval_grid.addWidget(self.analyzes.OpenFileBtn, 0, 2)
				self.analyzes.OpenFileBtn.clicked.connect(
								self.create_analyze_module_selector)
				self.config.UpdateCallbacks.append(self.analyzes.update)

				self.interval_header_setting = cFileOption(None, self.config, 'General',
																									 'IntervalHeaderFile')
				self.interval_header_setting.Label.setText('Query File')
				interval_grid.addWidget(self.interval_header_setting.Label, 1, 0)
				interval_grid.addWidget(self.interval_header_setting.Value, 1, 1)
				interval_grid.addWidget(self.interval_header_setting.OpenFileBtn, 1, 2)
				interval_grid.addWidget(self.interval_header_setting.OpenLastUsedFileBtn, 1, 4)
				self.interval_header_setting.is_save_last_files = True
				self.interval_header_setting.file_type = 'QueryFile'

				self.interval_header_setting.OpenLastUsedFileBtn.clicked.connect(
					self.interval_header_setting.showLastOpenedFilesDialog)

				interval_layout.addLayout(interval_grid)
				apply_btn = QtGui.QPushButton('Apply')
				apply_btn.clicked.connect(self.fill_up_int_frame)
				apply_btn.setFixedSize(75, 25)
				hbox = QtGui.QHBoxLayout()
				hbox.addWidget(apply_btn)
				hbox.setAlignment(apply_btn, QtCore.Qt.AlignHCenter)

				interval_layout.addLayout(hbox)
				interval_box.setLayout(interval_layout)

				self.interval_widget = QtGui.QMainWindow()
				self.interval_widget.setObjectName('IntervalWindow')

				interval_frame_box = QtGui.QGroupBox('Interval Frame')
				interval_frame_layout = QtGui.QVBoxLayout()
				interval_frame_layout.addWidget(self.interval_widget)
				interval_frame_box.setLayout(interval_frame_layout)

				self.interval_dw = QtGui.QDockWidget()
				self.interval_dw.setObjectName('IntDock')
				self.interval_dw.setWidget(self.interval_frame)
				dw_features = QtGui.QDockWidget.DockWidgetMovable | \
											QtGui.QDockWidget.DockWidgetFloatable
				self.interval_dw.setFeatures(dw_features)
				self.interval_widget.addDockWidget(QtCore.Qt.BottomDockWidgetArea,
																					 self.interval_dw)
				self.analyze_splitter.addWidget(interval_box)
				self.analyze_splitter.addWidget(interval_frame_box)
				return self.analyze_splitter

		def fill_up_int_frame(self):
				self.analyze_control.fillIntervalFrame(self.interval_frame)
				batch = self.analyze_control.getBatch()
				self.batch_control = cBatchControl(None, self.config, batch,
																					 self.interval_frame.get_table_model())
				self.batch_control.ComboBoxUpdateSignal.signal.connect(
								self.add_item_2_combobox)
				self.interval_frame.add_btn.clicked.connect(
								self.batch_control.addIntervalFromROI)
				self.interval_frame.rm_btn.clicked.connect(self.batch_control.rmInterval)
				self.interval_frame.rm_btn.clicked.connect(
								self.interval_frame.batchTable.clearSelection)
				self.interval_frame.export_btn.clicked.connect(
								self.show_export_dialog)
				self.interval_frame.more_options_btn.clicked.connect(
								self.show_plotview_dialog)

				self.interval_frame.more_options_btn.setEnabled(True)
				self.interval_frame.export_btn.setEnabled(True)
				self.interval_frame.add_btn.setEnabled(True)
				self.interval_frame.rm_btn.setEnabled(True)
				return

		def close(self):
				if not self.use_simplified_interface:
						self.remove_editor_temp_file()
				return SessionFrame.close(self)

		def closeEvent(self, event):
				if self.use_simplified_interface:
						return SessionFrame.closeEvent(self, event)
				self.remove_editor_temp_file()
				self.interval_frame.close()
				self.interval_frame.setParent(None)
				self.interval_frame.deleteLater()
				if self.batch_control is not None:
						self.batch_control.onCloseAll()
				if self.analyze_control is not None:
						self.analyze_control.onClose()
				if self.anal_mod_sel is not None:
						self.anal_mod_sel.close()
				return SessionFrame.closeEvent(self, event)

		def show_export_dialog(self):
				self.export_dialog = ExportWindow(self.interval_frame.batchTable, self.config)
				self.export_dialog.show()

		def show_plotview_dialog(self):
				self.plotview_dialog = PlotViewWindow(self.interval_frame.batchTable, self.config, self.ConfigFrame,
																							self.active_control)
				self.plotview_dialog.show()

		def create_analyze_module_selector(self):
				if isinstance(self.anal_mod_sel, ModuleConfigFrame):
						return

				self.remove_editor_temp_file()
				self.anal_mod_sel = ModuleConfigFrame(self.config, 'iAnalyze',
																							self.analyze_control)
				self.anal_mod_sel.close_signal.signal.connect(
								self.close_analyze_module_selector)

				self.last_tmp = self.anal_mod_sel.editor.Text.temp
				self.anal_mod_sel.show()
				self.anal_mod_sel.resize(1250, 600)
				return

		def on_start(self):
				if self.active_control == self.batch_control:
						self.ConfigFrame.Editor.Selector.set_batch_control(self.batch_control)
						self.on_start_interval()
				else:
						self.ConfigFrame.Control.onStart()
						self.ConfigFrame.Editor.Selector.BatchControl = None
				return

		def on_start_interval(self):
				QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
				entries = self.interval_frame.getEntries()
				if not entries:
						self.config.log('No interval was selected')
						QtGui.QApplication.restoreOverrideCursor()
						return
				start, end = self.interval_frame.getSelectedTimes()
				for measurement, entries in entries.iteritems():
						if self.batch_control.Batch.is_measurement_local(measurement) \
										and not os.path.exists(measurement):
								self.config.log('%s is missing on the current machine' % measurement)
								continue

						batch_results = {
								'measproc.cFileReport'   : {},
								'measproc.Report'        : self.interval_frame.storePart(),
								'measproc.cFileStatistic': {}
						}

						measurement = self.batch_control.onStart(measurement, batch_results)
						entry, = entries
						result, = batch_results['measproc.Report'].keys()
						base_name = os.path.basename(measurement)
						self.entries[base_name] = {entry: result}
				self.batch_control.seek(start)
				self.batch_control.setROI(start, end)
				QtGui.QApplication.restoreOverrideCursor()
				return

		def close_analyze_module_selector(self):
				self.last_tmp = self.anal_mod_sel.editor.Text.temp
				self.analyze_importer = self.anal_mod_sel.editor.Text.importer
				self.anal_name = self.anal_mod_sel.editor.Text.PREFIX
				self.anal_mod_sel.close_signal.signal.disconnect()
				self.anal_mod_sel.deleteLater()
				self.anal_mod_sel = None
				return

		def remove_editor_temp_file(self):
				if self.last_tmp is not None:
						Text.rm_temp_from_ext(self.config, self.analyze_control, self.anal_name,
																	self.last_tmp, self.analyze_importer)
						self.last_tmp = None
						self.analyze_importer = None
						self.anal_name = None
						self.config.update()
				return

		def set_meas_from_int_frame(self, measurement):
				self.active_control = self.batch_control
				self.config.m(measurement)
				self.config.update()
				start, end = self.interval_frame.getSelectedTimes()
				self.batch_control.seek(start)
				self.batch_control.setROI(start, end)
				return

		def activate_view_control(self):
				self.active_control = self.ConfigFrame.Control
				return

		def add_item_2_combobox(self, item_name):
				menu = self.combo_box.menu()
				item_name = 'Close ' + item_name
				for action in menu.actions():
						if item_name == action.text():
								return

				action = QtGui.QAction(item_name, menu)
				action.triggered.connect(lambda n = item_name: self.onClose(n))

				menu.addAction(action)
				return

		def onClose(self, itemName):
				if not itemName:
						return

				menu = self.combo_box.menu()
				action = [action for action in menu.actions() if itemName == action.text()]
				if len(action) != 1:
						return
				action, = action

				base_name = itemName.replace('Close ', '')
				if base_name in self.entries:
						self.batch_control.close(base_name)
						self._closeEntryGroups([base_name])
						self.interval_frame.batchTableModel.refresh()
				else:
						self.ConfigFrame.Control.close(base_name)
				menu.removeAction(action)
				action.deleteLater()
				return

		def onCloseAll(self):
				global CLOSE_SCENARIO_VISUALIZATION_WINDOW, SCENARIO_VISUALIZATION_SUBPROCESS, CLOSE_EVENT_RECORDER_WINDOW, \
						EVENT_RECORDER_SUBPROCESS
				menu = self.combo_box.menu()
				for manager in self.ConfigFrame.Control.Managers.itervalues():
						for module in manager.modules.get_selecteds():
								name, _, prj = ModuleName.split(module)
								modulename = '%s.%s' % (prj, name)
								if modulename in sys.modules:  # more module instance can exist with diff parameter, but the module is
										# imported just once
										del sys.modules[modulename]
				for action in menu.actions():
						self.onClose(action.text())

				# Close scenario visualization window
				if CLOSE_SCENARIO_VISUALIZATION_WINDOW:
						CLOSE_SCENARIO_VISUALIZATION_WINDOW = False
						SCENARIO_VISUALIZATION_SUBPROCESS.terminate()

				# Close Event Recorder window
				if CLOSE_EVENT_RECORDER_WINDOW:
						CLOSE_EVENT_RECORDER_WINDOW = False
						EVENT_RECORDER_SUBPROCESS.terminate()
				return

		def _closeEntryGroup(self, measurement):
				if measurement:
						del self.entries[measurement]
				return

		def _closeEntryGroups(self, measurements):
				for measurement in measurements:
						self._closeEntryGroup(measurement)
				return


class SettingFrame(QtGui.QFrame):
		close_signal = SimpleSignal()

		def closeEvent(self, event):
				self.close_signal.signal.emit()
				return QtGui.QFrame.closeEvent(self, event)

		def keyPressEvent(self, event):
				if event.key() == QtCore.Qt.Key_Escape:
						self.close()
				return QtGui.QFrame.keyPressEvent(self, event)


class ModuleConfigFrame(SettingFrame):
		def __init__(self, config, interface, control):
				SettingFrame.__init__(self)
				layout = QtGui.QVBoxLayout()
				tab = QtGui.QTabWidget()
				layout.addWidget(tab)
				self.setLayout(layout)
				self.editor = cReportFilterEditor(None, config, control)
				self.editor.init()
				scroll_area = QtGui.QScrollArea()
				scroll_area.setWidget(self.editor)
				scroll_area.setWidgetResizable(True)
				modules = ModuleTableFrame(config, interface)
				tab.addTab(modules, 'Modules')
				tab.addTab(scroll_area, 'New Module')
				return


class AnalyzeSessionFrame(SessionFrame):
		def __init__(self, config, use_simplified_interface):
				self.ConfigFrame = cAnalyzeConfigFrame(None, config)
				self.ConfigFrame.setObjectName('AnalyzeWindow')
				SessionFrame.__init__(self, config, use_simplified_interface)
				self.init(use_simplified_interface)
				return


class SearchSessionFrame(SessionFrame):
		def __init__(self, config, args, use_simplified_interface):
				self.ConfigFrame = cSearchConfigFrame(None, config, args,
																							NewTabWidget = False)
				self.ConfigFrame.setObjectName('SearchWindow')
				SessionFrame.__init__(self, config, use_simplified_interface)
				if use_simplified_interface:
						self.init(use_simplified_interface)
				else:
						self.create_UI()
				return

		def create_UI(self):
				self.splitter = QtGui.QSplitter()
				self.splitter.setObjectName('SearchMainsSplitter')
				self.splitter.setOrientation(QtCore.Qt.Horizontal)

				tab_widget = QtGui.QTabWidget()
				tab_widget.addTab(self.ConfigFrame.PF, 'Modules')
				scroll_area = QtGui.QScrollArea()
				scroll_area.setWidgetResizable(True)
				scroll_area.setWidget(self.ConfigFrame.Editor)
				tab_widget.addTab(scroll_area, 'New Module')

				meas_frame = QtGui.QFrame()
				meas_layout = QtGui.QVBoxLayout()
				meas_box = QtGui.QGroupBox('Measurements')
				meas_box_layout = QtGui.QVBoxLayout()
				meas_box_layout.addWidget(self.ConfigFrame.Meas)
				meas_box.setLayout(meas_box_layout)

				batch_box = QtGui.QGroupBox('Database')
				batch_grid = QtGui.QGridLayout()
				self.batch_file = cLazyFileOption(None, self.config, 'General', 'BatchFile')
				batch_grid.addWidget(self.batch_file.Label, 0, 0)
				batch_grid.addWidget(self.batch_file.Value, 0, 1)
				batch_grid.addWidget(self.batch_file.OpenFileBtn, 0, 2)
				batch_grid.addWidget(self.batch_file.OpenLastUsedFileBtn, 0, 3)
				self.batch_file.is_save_last_files = True
				self.batch_file.file_type = 'BatchFileDirectory'
				self.batch_file.OpenLastUsedFileBtn.clicked.connect(
						self.batch_file.showLastOpenedFilesDialog)

				self.rep_dir = cDirOption(None, self.config, 'General', 'RepDir')
				batch_grid.addWidget(self.rep_dir.Label, 1, 0)
				batch_grid.addWidget(self.rep_dir.Value, 1, 1)
				batch_grid.addWidget(self.rep_dir.OpenFileBtn, 1, 2)
				batch_grid.addWidget(self.rep_dir.OpenLastUsedFileBtn, 1, 3)
				self.rep_dir.is_save_last_files = True
				self.rep_dir.file_type = 'ReportDirectory'
				self.rep_dir.OpenLastUsedFileBtn.clicked.connect(
						self.rep_dir.showLastOpenedFilesDialog)
				batch_box = QtGui.QGroupBox('Event Database')

				batch_box.setLayout(batch_grid)

				meas_layout.addWidget(meas_box)
				meas_layout.addWidget(batch_box)
				meas_frame.setLayout(meas_layout)

				self.splitter.addWidget(meas_frame)
				self.splitter.addWidget(tab_widget)
				hbox = QtGui.QHBoxLayout()
				hbox.addStretch(1)

				self.start_btn = QtGui.QPushButton('&Start')
				self.start_btn.clicked.connect(self.ConfigFrame.Control.onStart)
				font = self.start_btn.font()
				font.setPointSize(START_CLOSE_FONT_SIZE)
				self.start_btn.setFont(font)

				hbox.addWidget(self.start_btn)
				hbox.addStretch(1)

				vbox = QtGui.QVBoxLayout()
				vbox.addWidget(self.splitter)
				vbox.addLayout(hbox)
				self.setLayout(vbox)
				return


class AboutWindow(QtGui.QWidget):
		"""
		About Window for the python toolchain.
		Contains a short about text and version numbers.
		"""

		def __init__(self):
				super(AboutWindow, self).__init__()
				self.create_UI()
				return

		def create_UI(self):
				"""
				Creates the GUI for the About Window
				"""
				self.resize(400, 350)
				self.grid_layout = QtGui.QGridLayout(self)
				self.grid_layout.setContentsMargins(12, 12, 13, 12)
				self.grid_layout.setHorizontalSpacing(10)
				self.grid_layout.setObjectName("grid_layout")
				self.close_button = QtGui.QPushButton("Close", self)
				self.close_button.setObjectName("close_button")
				self.close_button.clicked.connect(self.close)
				self.grid_layout.addWidget(self.close_button, 4, 1, 1, 3)
				self.about_text_browser = QtGui.QTextBrowser(self)
				self.about_text_browser.setObjectName("about_text_browser")
				self.about_text_browser.setText(
								"MASS - Measurement Analysis Support System\n" \
								"Part of DataEval framework\n\n" \
								"Python environment version information:\n%s\n\nSystem environment:\n%s" %
								(_get_python_info(sep = '\n'), _get_env_info(sep = '\n')))
				self.grid_layout.addWidget(self.about_text_browser, 1, 0, 1, 5)
				self.title_label = QtGui.QLabel("DataEval - MASS", self)
				self.title_label.setStyleSheet("font: 75 14pt \"Verdana\";")
				self.title_label.setObjectName("title_label")
				self.grid_layout.addWidget(self.title_label, 0, 2, 1, 1)
				self.label_version = QtGui.QLabel("DataEval version: ", self)
				self.label_version.setObjectName("label_version")
				self.grid_layout.addWidget(self.label_version, 2, 0, 1, 1)
				self.version_dataeval = QtGui.QTextEdit(self)
				self.version_dataeval.setStyleSheet("background-color: rgb(136, 136, 136);")
				self.version_dataeval.setObjectName("version_dataeval")
				dists = pip.get_installed_distributions()
				ver = [pkg.version for pkg in dists if pkg.key == 'dataeval'][0]
				self.version_dataeval.setText(ver)
				self.grid_layout.addWidget(self.version_dataeval, 2, 2, 1, 3)
				self.setLayout(self.grid_layout)
				self.setWindowTitle('About')
				self.show()
				return


class ExportWindow(QtGui.QWidget):
		"""
		This class contains the GUI and functionality of the export
		functions for the intervals. It can export to either CSV files
		or to XLS (excel) files.
		"""

		def __init__(self, interval, config):
				"""
				Constructor for the Export Window class.

				:Parameters:
				interval : QTableView
					Contains the interval that will be exported.
				"""
				super(ExportWindow, self).__init__()
				self.config = config
				self.extension_options = ("CSV File", "Excel File", "Textile File")
				self.interval = interval
				self.default_delim = ","
				self.extension = '.csv'
				self.create_UI()
				return

		def on_switch_extension(self, index):
				"""
				Called when the target file type is changed on the combo box.

				:Parameters:
				index : int
					index on the combo box to which the change is made.
				"""
				if index == 0:
						self.group_box.setTitle(self.extension_options[index])
						self.text_edit_delim.setVisible(True)
						self.delim_label.setVisible(True)
						self.extension = '.csv'
				elif index == 1:
						self.group_box.setTitle(self.extension_options[index])
						self.text_edit_delim.setVisible(False)
						self.delim_label.setVisible(False)
						self.extension = '.xls'
				elif index == 2:
						self.group_box.setTitle(self.extension_options[index])
						self.text_edit_delim.setVisible(False)
						self.delim_label.setVisible(False)
						self.extension = '.txt'
				return

		def on_export_pressed(self):
				"""
				Fetches and formats the file name, extension and data for the
				exported file. Requests the export of the selected data.
				To be called when the export button is pressed.
				"""
				filename = self.text_edit_filename.Value.text()
				if not filename:
						self.config.log("The path for file export is empty. Please use a valid path.")
						return

				self.text_edit_filename.Value.setText(filename)

				if self.extension == ".csv":
						delim = str(self.text_edit_delim.toPlainText())
						if len(delim) != 1:
								self.config.log("Please use a non-empty character selection of lenght = 1 as delimiter.")
								return
						self.interval.model().export_to_csv_file(filename, delim)
				elif self.extension == ".xls":
						self.interval.model().export_to_xls_file(filename)
				elif self.extension == ".txt":
						self.interval.model().export_to_textile_file(filename)
				self.config.log("Interval data has been successfuly exported to "
												+ filename)
				self.close()
				return

		def create_UI(self):
				"""
				Creates, configures and lays out the GUI for the Export window.
				"""
				self.resize(370, 230)
				self.grid_layout = QtGui.QGridLayout(self)

				self.export_label = QtGui.QLabel("  Export As : ", self)

				self.ext_combo_box = QtGui.QComboBox(self)
				for opt in self.extension_options:
						self.ext_combo_box.addItem(opt)
				self.ext_combo_box.currentIndexChanged.connect(self.on_switch_extension)
				self.grid_layout.addWidget(self.export_label, 0, 0, 1, 1)
				self.grid_layout.addWidget(self.ext_combo_box, 0, 1, 1, 1)

				self.group_box = QtGui.QGroupBox(self.extension_options[0], self)
				self.delim_label = QtGui.QLabel("Delimiter", self.group_box)
				layout_group = QtGui.QGridLayout()
				layout_group.setSpacing(10)

				self.text_edit_filename = LazyFileWidget('File path')
				self.text_edit_filename.setMaximumHeight(25)
				layout_group.addWidget(self.text_edit_filename.Label, 1, 0)
				layout_group.addWidget(self.text_edit_filename.Value, 1, 1)
				layout_group.addWidget(self.text_edit_filename.OpenFileBtn, 1, 2)

				self.text_edit_delim = QtGui.QTextEdit(self.group_box)
				self.text_edit_delim.setMaximumHeight(25)
				self.text_edit_delim.setText(self.default_delim)
				layout_group.addWidget(self.delim_label, 2, 0)
				layout_group.addWidget(self.text_edit_delim, 2, 1)

				layout_group.setAlignment(QtCore.Qt.AlignTop)
				self.group_box.setLayout(layout_group)
				self.grid_layout.addWidget(self.group_box, 1, 0, 1, 2)

				self.text_edit_delim.setToolTip("Delimitators for the CSV file."
																				+ "The exporter only uses the first character\n"
																				+ "The most common delimiters are:  ; |  ,  ")
				self.text_edit_filename.Value.setToolTip("Full file path and file name for the "
																								 + "export file, does not need to contain it's extension.\n"
																								 + "If no path is given, it will be saved on the directory "
																								 + "from where the script was launched.")

				self.export_button = QtGui.QPushButton("Export", self)
				self.export_button.clicked.connect(self.on_export_pressed)
				self.grid_layout.addWidget(self.export_button, 2, 0, 1, 1)

				self.cancel_button = QtGui.QPushButton("Cancel", self)
				self.cancel_button.clicked.connect(self.close)
				self.grid_layout.addWidget(self.cancel_button, 2, 1, 1, 1)

				self.grid_layout.setVerticalSpacing(15)
				self.setLayout(self.grid_layout)
				self.setWindowTitle("Export Interval")
				return


class PlotViewWindow(QtGui.QWidget):
		"""
		This class contains the GUI and functionality of the visualizing database table in virtual signal plots
		"""

		def __init__(self, interval, config, ConfigFrame, active_control):
				"""
				Constructor for the plotviewer Window class.

				:Parameters:
				interval : QTableView
					Contains the interval that will be visualized in plotter.
				"""
				super(PlotViewWindow, self).__init__()
				self.active_control = active_control
				self.ConfigFrame = ConfigFrame
				self.config = config
				self.interval = interval
				self.create_UI()
				return

		def get_index(self, st_time, ed_time):
				if st_time == ed_time:
						st_time = st_time - 1
						ed_time = ed_time + 1

				st_index = max(self.common_time.searchsorted(st_time, side = 'right') - 1, 0)
				ed_index = max(self.common_time.searchsorted(ed_time, side = 'right') - 1, 0)

				if st_index == ed_index:
						ed_index += 1
				return st_index, ed_index

		def plot_signals(self):
				"""
						Opens a plot of the overall behavior of the signal's value.
						"""
				if len(self.selected_items) == 0:
						logger.info("Please select at least one column to visualize in plotter")
						return
				QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
				selected_measurement_file = os.path.basename(self.config._sections['Measurement']['main'])
				if selected_measurement_file in self.active_control.Managers.keys():
						manager = self.active_control.Managers[selected_measurement_file]
						signal_source = manager.get_source()
						for device in signal_source.Parser.iterDeviceNames():
								for signal_name in signal_source.Parser.iterSignalNames(device):
										self.common_time, _ = signal_source.getSignal(device, signal_name)
										break
								break
						pn = datavis.PlotNavigator.cPlotNavigator("Plot window")
						virtual_qua_signals = {}
						virtual_label_signals = {}
						labels = self.interval.model().int_label
						quantities = self.interval.model().quas.keys()
						sample_interval = self.interval.model().visible_intervals[0]
						for column_name in self.selected_items.keys():
								if type(sample_interval[column_name]) == float:
										virtual_qua_signals[column_name] = np.zeros(self.common_time.shape, dtype = float)
										for interval in self.interval.model().visible_intervals:
												if selected_measurement_file == interval['measurement']:
														try:
																interval_end = interval["start [s]"] + interval["duration [s]"]
																st_idx, ed_idx = self.get_index(float(interval["start [s]"]), float(interval_end))
																virtual_qua_signals[column_name][st_idx:ed_idx] = interval[column_name]
														except Exception as e:
																logger.warning(str(e))
																logger.info(
																		"Hint: Database must have start [s] and duration [s]. Update sql query file")
								elif type(sample_interval[column_name]) == list:
										_, votes = self.interval.model().batch.get_labelgroup(labels[column_name])
										mapping = dict((i + 1, vote) for i, vote in enumerate(votes))
										mapping[0] = "Undefined"
										reverse_mapping = dict((vote, i + 1) for i, vote in enumerate(votes))
										virtual_label_signals[column_name] = (np.zeros(self.common_time.shape, dtype = float), mapping)
										for interval in self.interval.model().visible_intervals:
												if selected_measurement_file == interval['measurement']:
														try:
																interval_end = interval["start [s]"] + interval["duration [s]"]
																st_idx, ed_idx = self.get_index(float(interval["start [s]"]), float(interval_end))
																virtual_label_signals[column_name][0][st_idx:ed_idx] = reverse_mapping[
																		interval[column_name][0]]
														except Exception as e:
																logger.warning(str(e))
																logger.info(
																		"Hint: Database must have start [s] and duration [s]. Update sql query file")
								else:
										logger.info("Missing quantity/label. Hint: Quantity/Label name should match column names in table")

						for virtual_signal_name, virtual_signal_value in virtual_qua_signals.iteritems():
								axis00 = pn.addAxis()
								pn.addSignal2Axis(axis00, virtual_signal_name, self.common_time, virtual_signal_value, unit = "")

						for virtual_signal_name, virtual_signal_value in virtual_label_signals.iteritems():
								ylabel_text = virtual_signal_name
								mapping = virtual_signal_value[1]
								ax = pn.addAxis(ylabel = ylabel_text, yticks = mapping, ylim = (min(mapping) - 0.5, max(mapping) +
																																								0.5))
								pn.addSignal2Axis(ax, ylabel_text, self.common_time, virtual_signal_value[0], unit = '')

						QtGui.QApplication.restoreOverrideCursor()
						pn.start()
						pn.show()
						synchronizer = manager.sync
						if synchronizer is not None:
								synchronizer.addClient(pn)
				return

		def add_signals_to_selector(self):
				"""
						Opens a plot of the overall behavior of the signal's value.
						"""
				if len(self.selected_items) == 0:
						logger.info("Please select at least one column to add signals in selector")
						return
				virtual_db_signals_dictionary = {}
				selected_measurement_file = os.path.basename(self.config._sections['Measurement']['main'])
				if selected_measurement_file in self.active_control.Managers.keys():
						manager = self.active_control.Managers[selected_measurement_file]
						signal_source = manager.get_source()
						for device in signal_source.Parser.iterDeviceNames():
								for signal_name in signal_source.Parser.iterSignalNames(device):
										self.common_time, _ = signal_source.getSignal(device, signal_name)
										break
								break
						virtual_qua_signals = {}
						virtual_label_signals = {}
						labels = self.interval.model().int_label
						quantities = self.interval.model().quas.keys()
						sample_interval = self.interval.model().visible_intervals[0]
						for column_name in self.selected_items.keys():
								if type(sample_interval[column_name]) == float:
										virtual_qua_signals[column_name] = np.zeros(self.common_time.shape, dtype = float)
										for interval in self.interval.model().visible_intervals:
												try:
														interval_end = interval["start [s]"] + interval["duration [s]"]
														st_idx, ed_idx = self.get_index(float(interval["start [s]"]), float(interval_end))
														virtual_qua_signals[column_name][st_idx:ed_idx] = interval[column_name]
												except Exception as e:
														logger.warning(str(e))
														logger.info("Hint: Database must have start [s] and duration [s]. Update sql query file")
								elif type(sample_interval[column_name]) == list:
										_, votes = self.interval.model().batch.get_labelgroup(labels[column_name])
										mapping = dict((i + 1, vote) for i, vote in enumerate(votes))
										mapping[0] = "Undefined"
										reverse_mapping = dict((vote, i + 1) for i, vote in enumerate(votes))
										virtual_label_signals[column_name] = (np.zeros(self.common_time.shape, dtype = float), mapping)
										for interval in self.interval.model().visible_intervals:
												try:
														interval_end = interval["start [s]"] + interval["duration [s]"]
														st_idx, ed_idx = self.get_index(float(interval["start [s]"]), float(interval_end))
														virtual_label_signals[column_name][0][st_idx:ed_idx] = reverse_mapping[
																interval[column_name][0]]
												except Exception as e:
														logger.warning(str(e))
														logger.info("Hint: Database must have start [s] and duration [s]. Update sql query file")
								else:
										logger.info("Missing quantity/label. Hint: Quantity/Label name should match column names in table")

						for virtual_signal_name, virtual_signal_value in virtual_qua_signals.iteritems():
								virtual_db_signals_dictionary[virtual_signal_name] = (self.common_time, virtual_signal_value, None)

						for virtual_signal_name, virtual_signal_value in virtual_label_signals.iteritems():
								mapping = virtual_signal_value[1]
								virtual_db_signals_dictionary[virtual_signal_name] = (
								self.common_time, virtual_signal_value[0], mapping)
						self.ConfigFrame.Editor.Selector.database_signals = virtual_db_signals_dictionary
						if bool(virtual_db_signals_dictionary) is False:
								logger.info("No signals found to add in signal selector")
						else:
								logger.info(
										"Signals are added in the signal selector, Please use Quick Plot with DB Signals (Synchronous) "
										"functionality, Signal list : " + ", ".join(
												virtual_db_signals_dictionary.keys()))
						self.close()
				return

		def on_plot_pressed(self):
				"""
				Fetches and formats the file name, extension and data for the
				exported file. Requests the export of the selected data.
				To be called when the export button is pressed.
				"""
				self.plot_signals()
				self.close()
				return

		def on_change(self):
				self.selected_items = {}
				for item in self.listWidgetOtherObjects.selectedItems():
						self.selected_items[item.text()] = item.data(QtCore.Qt.UserRole)

		def create_UI(self):
				"""
				Creates, configures and lays out the GUI for the Export window.
				"""
				self.resize(370, 230)
				self.grid_layout = QtGui.QGridLayout(self)

				self.export_label = QtGui.QLabel("  Select columns: ", self)

				self.listWidgetOtherObjects = QListWidget()
				self.listWidgetOtherObjects.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
				self.listWidgetOtherObjects.itemSelectionChanged.connect(self.on_change)
				otherObjects = self.interval.model().header
				for object_key in otherObjects:
						item_to_add = QListWidgetItem(object_key)
						# item_to_add.setText(object_key)
						# item_to_add.setData(QtCore.Qt.UserRole, "Signal array")
						self.listWidgetOtherObjects.addItem(item_to_add)

				self.grid_layout.addWidget(self.export_label, 0, 0, 1, 1)
				self.grid_layout.addWidget(self.listWidgetOtherObjects, 0, 1, 1, 1)

				self.plotview_button = QtGui.QPushButton("Quick Plot", self)
				self.plotview_button.clicked.connect(self.on_plot_pressed)
				self.grid_layout.addWidget(self.plotview_button, 2, 0, 1, 1)

				self.add_signals_to_selector_button = QtGui.QPushButton("Add to Module Creation", self)
				self.add_signals_to_selector_button.clicked.connect(self.add_signals_to_selector)
				self.grid_layout.addWidget(self.add_signals_to_selector_button, 2, 1, 1, 1)

				self.cancel_button = QtGui.QPushButton("Close", self)
				self.cancel_button.clicked.connect(self.close)
				self.grid_layout.addWidget(self.cancel_button, 2, 2, 1, 1)

				self.grid_layout.setVerticalSpacing(15)
				self.setLayout(self.grid_layout)
				self.setWindowTitle("Select Database Signal")
				return


class LazyFileWidget(QtGui.QFrame):
		"""
		Widget class for lazy loading of folders with filename.
		This class's widget is not tied at all with the Config.
		Config-related functionality has been stripped out.
		"""

		def __init__(self, title, **kwargs):
				"""
				Constructor for Lazyfilewidget class.

				:Parameters:
				title : string
					Title label to be shown inside the widget.
				"""
				super(LazyFileWidget, self).__init__()
				self.selected_file = None
				self.Label = QtGui.QLabel(title)
				self.Value = QtGui.QLineEdit('')
				self.OpenFileBtn = QtGui.QPushButton('Browse...')
				self.OpenFileBtn.clicked.connect(self.find)
				self.kwargs = kwargs
				return

		def ask(self, **kwargs):
				"""
				Opens up a dialog for searching the file name and path.
				"""
				Dialog = QtGui.QFileDialog()
				Dialog.setFileMode(QtGui.QFileDialog.AnyFile)
				Dialog.filesSelected.connect(self.selectFile)
				Dialog.exec_()
				return self.selected_file

		def selectFile(self, File):
				"""
				File selection used for Lazy loading.
				"""
				self.selected_file, = File
				return

		def find(self):
				"""
				Calls for file-dialog opening and lazy-loading of filename an path.
				"""
				Value = self.ask(**self.kwargs)
				if Value:
						Value = os.path.abspath(Value)
						self.Value.setText(Value)
				pass


class MassFrame(cConfigFrame):
		def __init__(self, config, args, use_simplified_interface = False):
				cConfigFrame.__init__(self, None, config)
				tab_widget = QtGui.QTabWidget()

				self.view_widget = ViewSessionFrame(config, use_simplified_interface)
				self.search_widget = SearchSessionFrame(config, args,
																								use_simplified_interface)

				config.UpdateCallbacks.append(self.view_widget.update)
				config.UpdateCallbacks.append(self.search_widget.update)

				self.Closes.append(self.view_widget.close)
				self.Closes.append(self.search_widget.close)

				tab_widget.addTab(self.view_widget, 'View')
				tab_widget.addTab(self.search_widget, 'Search')

				def snk():
						try:
								import subprocess
								snk_path = os.path.join(os.path.dirname(__file__), 'snk.py')
								subprocess.call((sys.executable, snk_path))
						except:
								pass

				snk_act = QtGui.QAction("snk", tab_widget)
				snk_act.setShortcut(self.tr("F8"))
				snk_act.triggered.connect(snk)
				tab_widget.addAction(snk_act)

				self.MainLayout.addWidget(tab_widget)

				self.Closes.append(config.save)
				self.setLayout(self.MainLayout)
				self.config = config
				self.general_frame = None
				self.general_frame_backup_checked = None
				self.general_frame_backup_text = None

				self.create_menus()

				logframe = LogFrame(config)
				dw = QtGui.QDockWidget()
				dw.setWidget(logframe)
				dw.setObjectName('LogDock')
				dw_features = QtGui.QDockWidget.DockWidgetMovable | \
											QtGui.QDockWidget.DockWidgetFloatable
				dw.setFeatures(dw_features)
				self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dw)

				if not use_simplified_interface:
						self.view_widget.batch_file.UpdateSignal.signal.connect(
										self.search_widget.batch_file.update)

						self.search_widget.batch_file.UpdateSignal.signal.connect(
										self.view_widget.batch_file.update)

						self.view_widget.rep_dir.UpdateSignal.signal.connect(
										self.search_widget.rep_dir.update)

						self.search_widget.rep_dir.UpdateSignal.signal.connect(
										self.view_widget.rep_dir.update)
						self.view_widget.view_splitter.setSizes([250, 1000])
						self.view_widget.analyze_splitter.setSizes([100, 1000])
						self.view_widget.splitter.setSizes([1000, 450])
						self.search_widget.splitter.setSizes([150, 1000])
				else:
						analyze_widget = AnalyzeSessionFrame(config, use_simplified_interface)
						config.UpdateCallbacks.append(analyze_widget.update)
						self.Closes.append(analyze_widget.close)
						tab_widget.addTab(analyze_widget, 'Analyze')
				return

		def closeEvent(self, event):
				self.saveLayout()
				if self.general_frame is not None:
						self.general_frame.close()
				if self.general_frame_backup_text is not None:
						self.config.u(self.general_frame_backup_text)
				return cConfigFrame.closeEvent(self, event)

		def start(self):
				cConfigFrame.start(self)
				self.showMaximized()
				if self.config.options('MASS Layout'):
						self.restoreLayout()
				return

		def create_menus(self):
				menu_bar = self.menuBar()
				self.file_menu = QtGui.QMenu('&File')
				self.option_menu = QtGui.QMenu('S&ettings')
				self.conversion_menu = QtGui.QMenu('C&onversion')

				self.tools_menu = QtGui.QMenu('&Tools')
				self.help_menu = QtGui.QMenu('&Help')
				self.flc25_menu = QtGui.QMenu('FLC25')

				menu_bar.addMenu(self.file_menu)
				menu_bar.addMenu(self.option_menu)
				menu_bar.addMenu(self.conversion_menu)

				menu_bar.addMenu(self.tools_menu)
				menu_bar.addMenu(self.help_menu)


				actions = []
				open_ = QtGui.QAction('&Open...', self.file_menu)
				open_.setShortcut(QtGui.QKeySequence.Open)
				open_.triggered.connect(self.loadCfg)
				actions.append(open_)

				save = QtGui.QAction('S&ave', self.file_menu)
				save.setShortcut(QtGui.QKeySequence.Save)
				save.triggered.connect(self.save)
				actions.append(save)

				save_as = QtGui.QAction('Sa&ve a Copy As...', self.file_menu)
				save_as.setShortcut(self.tr("Ctrl+Shift+S"))
				save_as.triggered.connect(self.exportCfg)
				actions.append(save_as)

				save_on_exit = QtGui.QAction('A&uto Save on Exit', self.file_menu)
				save_on_exit.setCheckable(True)
				save_on_exit.setChecked(not self.config.NoSave)
				save_on_exit.toggled.connect(self.toggle_save_conf)
				actions.append(save_on_exit)

				actions.append(self.file_menu.addSeparator())

				meas_info = QtGui.QAction('Open &Measurement Info...', self.file_menu)
				meas_info.setShortcut(self.tr("Ctrl+M"))
				meas_info.triggered.connect(self.open_meas_info)
				actions.append(meas_info)

				actions.append(self.file_menu.addSeparator())

				exit_ = QtGui.QAction('&Exit', self.file_menu)
				exit_.setShortcut(self.tr("Alt+F4"))
				exit_.triggered.connect(self.close)
				actions.append(exit_)

				for action in actions:
						self.file_menu.addAction(action)

				actions = []
				general = QtGui.QAction('&General...', self.option_menu)
				general.setShortcut(self.tr("Ctrl+G"))
				general.triggered.connect(self.show_general_settings)
				actions.append(general)

				for action in actions:
						self.option_menu.addAction(action)

				actions = []
				mf4_to_hdf5_conversion = QtGui.QAction('MDF/MF4 -> HDF5', self.option_menu)
				mf4_to_hdf5_conversion.setShortcut(self.tr("Ctrl+M"))
				mf4_to_hdf5_conversion.setToolTip(
						"Conversion is using latest asammdf parser, Please use this option if you have any issue with opening "
						"MDF/MF4 measurements files")
				mf4_to_hdf5_conversion.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'convert_24.ico')))
				mf4_to_hdf5_conversion.triggered.connect(self.convert_mf4_to_hdf5)
				actions.append(mf4_to_hdf5_conversion)

				for action in actions:
						self.conversion_menu.addAction(action)




				actions = []
				scenario_visualization = QtGui.QAction('Scenario &Visualization', self.tools_menu)
				scenario_visualization.setShortcut(self.tr("Ctrl+V"))
				scenario_visualization.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'scenario_visualization_24.png')))
				scenario_visualization.triggered.connect(self.open_scenario_visualization)
				actions.append(scenario_visualization)

				event_recording = QtGui.QAction('Event &Recorder', self.tools_menu)
				event_recording.setShortcut(self.tr("Ctrl+A"))
				event_recording.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'event_recording_24.png')))
				event_recording.triggered.connect(self.open_event_recording)
				actions.append(event_recording)

				event_editor = QtGui.QAction('&Event Editor', menu_bar)
				event_editor.setShortcut(self.tr("Ctrl+E"))
				event_editor.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'event_editor_24.png')))
				event_editor.triggered.connect(self.open_event_editor)
				actions.append(event_editor)

				resimulation_export = QtGui.QAction('&Resimulation Export', menu_bar)
				resimulation_export.setShortcut(self.tr("Ctrl+R"))
				resimulation_export.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'convert_24.ico')))
				resimulation_export.triggered.connect(self.open_resimulation_export)
				actions.append(resimulation_export)

				for action in actions:
						self.tools_menu.addAction(action)

				actions = []
				about = QtGui.QAction('&About...', self.help_menu)
				about.setShortcut(QtGui.QKeySequence.WhatsThis)
				about.triggered.connect(self.show_about_window)
				actions.append(about)

				contents = QtGui.QAction('&Contents...', self.help_menu)
				contents.setShortcut(QtGui.QKeySequence.HelpContents)
				contents.triggered.connect(self.show_help_window)
				actions.append(contents)

				for action in actions:
						self.help_menu.addAction(action)

				return

		def saveLayout(self):
				state = self.saveState()
				self.config.set('MASS Layout', 'MainState', state.toHex())
				geom = self.saveGeometry()
				self.config.set('MASS Layout', 'MainGeometry', geom.toHex())

				for option, widget in [('ReCre state',
																self.search_widget.ConfigFrame.Editor),
															 ('SAG state', self.view_widget.ConfigFrame.Editor),
															 ('IntervalWindow state',
																self.view_widget.interval_widget),
															 ]:
						state = widget.saveState()
						self.config.set('MASS Layout', option, state.toHex())

				for splitter in self.findChildren(QtGui.QSplitter):
						name = splitter.objectName()
						sizes = [str(size) for size in splitter.sizes()]
						sizes = ','.join(sizes)
						self.config.set('MASS Layout', name, sizes)
				return

		def restoreLayout(self):
				for option, widget in [('ReCre state',
																self.search_widget.ConfigFrame.Editor),
															 ('SAG state', self.view_widget.ConfigFrame.Editor),
															 ('IntervalWindow state',
																self.view_widget.interval_widget),
															 ]:
						state = self.config.get('MASS Layout', option)
						state = QtCore.QByteArray.fromHex(state)
						widget.restoreState(state)

				state = self.config.get('MASS Layout', 'MainState')
				state = QtCore.QByteArray.fromHex(state)
				self.restoreState(state)

				geom = self.config.get('MASS Layout', 'MainGeometry')
				geom = QtCore.QByteArray.fromHex(geom)
				self.restoreGeometry(geom)

				for splitter in self.findChildren(QtGui.QSplitter):
						name = splitter.objectName()
						sizes = self.config.get('MASS Layout', name)
						sizes = sizes.split(',')
						sizes = [int(size) for size in sizes]
						splitter.setSizes(sizes)

				return

		def close_general_frame(self):
				# save internal states
				self.general_frame_backup_checked = self.backup.Check.isChecked()
				self.general_frame_backup_text = self.backup.Value.text()
				# close
				self.general_frame.close_signal.signal.disconnect()
				self.general_frame.deleteLater()
				self.general_frame = None
				return

		def show_general_settings(self):
				self.general_frame = SettingFrame()
				self.general_frame.setWindowTitle('General Settings')
				self.general_frame.close_signal.signal.connect(self.close_general_frame)
				vbox = QtGui.QVBoxLayout()
				self.general_frame.setLayout(vbox)

				backup_box = QtGui.QGroupBox('Measurement Cache')
				backup_frame_kwargs = {}  # to restore previous states
				if self.general_frame_backup_checked is not None:
						backup_frame_kwargs['CheckedInit'] = self.general_frame_backup_checked
				if self.general_frame_backup_text is not None:
						backup_frame_kwargs['TextInit'] = self.general_frame_backup_text
				self.backup = cCheckDirOption(None, self.config, 'General', 'Backup',
																			**backup_frame_kwargs)
				backup_grid = QtGui.QGridLayout()
				backup_grid.addWidget(self.backup.Label, 0, 0)
				backup_grid.addWidget(self.backup.Check, 0, 1)
				backup_grid.addWidget(self.backup.Value, 0, 2)
				backup_grid.addWidget(self.backup.OpenFileBtn, 0, 3)

				log_box = QtGui.QGroupBox('Logger')
				self.log = cLazyFileOption(None, self.config, 'General', 'LogFile')

				log_grid = QtGui.QGridLayout()

				self.verbose_check = QtGui.QCheckBox()
				self.verbose_check.setChecked(self.config.Verbose)
				self.verbose_check.toggled.connect(self.config.toggleVerbose)

				verbose_label = QtGui.QLabel('Verbose Mode')

				log_grid.addWidget(verbose_label, 0, 1, 1, 2)
				log_grid.addWidget(self.verbose_check, 0, 0)

				log_grid.addWidget(self.log.Label, 2, 0)
				log_grid.addWidget(self.log.Value, 2, 2)
				log_grid.addWidget(self.log.OpenFileBtn, 2, 3)

				self.log_level_editor = QtGui.QPushButton()
				menu = QtGui.QMenu()
				self.log_level_editor.setMenu(menu)
				group = QtGui.QActionGroup(menu)
				group.setExclusive(True)

				config_log_level = str(self.config.get('General', 'StreamLogLevel'))
				for level in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'):
						action = QtGui.QAction(level, menu)
						action.setCheckable(True)
						log_level = str(log_levels[level])
						check = log_level == config_log_level
						if check:
								self.log_level_editor.setText(level)
						action.setChecked(check)

						action.triggered.connect(self.change_log_level)
						group.addAction(action)
						menu.addAction(action)

				label = QtGui.QLabel('Stream Logger Level')
				log_grid.addWidget(self.log_level_editor, 1, 2, 1, 2)
				log_grid.addWidget(label, 1, 0, 1, 2)
				self.log_level_editor.menu()

				mapdb_box = QtGui.QGroupBox('Map Database')
				self.mapdb = cFileOption(None, self.config, 'General', 'MapDb')
				self.osm_file = cFileOption(None, self.config, 'General', 'OsmFile')
				mapdb_grid = QtGui.QGridLayout()
				mapdb_grid.addWidget(self.mapdb.Label, 0, 0)
				mapdb_grid.addWidget(self.mapdb.Value, 0, 1)
				mapdb_grid.addWidget(self.mapdb.OpenFileBtn, 0, 2)
				mapdb_grid.addWidget(self.osm_file.Label, 1, 0)
				mapdb_grid.addWidget(self.osm_file.Value, 1, 1)
				mapdb_grid.addWidget(self.osm_file.OpenFileBtn, 1, 2)

				backup_box.setLayout(backup_grid)
				log_box.setLayout(log_grid)
				mapdb_box.setLayout(mapdb_grid)
				vbox.addWidget(backup_box)
				vbox.addWidget(mapdb_box)
				vbox.addWidget(log_box)
				self.general_frame.show()
				return

		def convert_mf4_to_hdf5(self):
				exe_path = os.path.join(os.path.dirname(__file__), "..\..\scripts\mf4converter")
				filepath = QFileDialog.getOpenFileNames(self, 'Select file(s) to convert', dir = '.',
																							 filter = "MDF Files (*.mf4 *.mdf)")

				if filepath[0] != "":
						for file in filepath[0]:
								logger.info("Please wait.. Converting file " + file)
								os.chdir(exe_path)
								command = os.path.join(exe_path, "mf4converter.exe -f hdf5 -c zlib -l 9 \"" + file + "\"")
								process = subprocess.Popen(command, stdout = subprocess.PIPE)
								stdout = process.communicate()[0]
								logger.info(stdout)
				else:
						logger.info("No file selected")
				return



		def open_scenario_visualization(self):
				global CLOSE_SCENARIO_VISUALIZATION_WINDOW, SCENARIO_VISUALIZATION_SUBPROCESS
				CLOSE_SCENARIO_VISUALIZATION_WINDOW = True
				exe_path = os.path.join(os.path.dirname(__file__), "..\..\scripts\scenario_visualization")
				os.chdir(exe_path)
				command = os.path.join(exe_path, "scenario_visualization.exe")
				SCENARIO_VISUALIZATION_SUBPROCESS = subprocess.Popen(command)
				return

		def open_event_recording(self):
				global CLOSE_EVENT_RECORDER_WINDOW, EVENT_RECORDER_SUBPROCESS
				CLOSE_EVENT_RECORDER_WINDOW = True
				command = "python -m EventRecorder"
				EVENT_RECORDER_SUBPROCESS = subprocess.Popen(command)
				return
		def open_event_editor(self):
				dialog_event_editor = cEventEditor(self)
				dialog_event_editor.setMinimumSize(500, 300)
				dialog_event_editor.setGeometry(300, 100, 500, 300)
				dialog_event_editor.setWindowTitle("Event Editor")
				dialog_event_editor.setWindowIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'event_editor_24.png')))
				dialog_event_editor.show()

		def open_resimulation_export(self):
				dialog_resim_export = cResimExportView()
				dialog_resim_export.resize(1000, 500)
				dialog_resim_export.setWindowTitle("Resimulation Export")
				dialog_resim_export.setWindowIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'convert_24.ico')))
				result = dialog_resim_export.exec_()
				if result == dialog_resim_export.Accepted:
						dialog_resim_export.onAccepted()
						self.dspace_asm_export()

		def dspace_asm_export(self):

				filepath = QFileDialog.getOpenFileName(self, 'Select file to export', dir = '.',
																							 filter = "Mat/H5 file(*.h5 *.mat)")

				if filepath[0] != "":
						logger.info("Export started...")
						export(filepath[0])
						logger.info("Export Completed")
				else:
						logger.info("No file selected")
				return

		def change_log_level(self):
				menu = self.log_level_editor.menu()
				level = None
				for action in menu.actions():
						if action.isChecked():
								level = action.text()
								break
				loglevel = log_levels[level]
				self.config.changeStreamLoggerLevel(loglevel)
				self.log_level_editor.setText(level)
				return

		def show_about_window(self):
				"""
				Opens and shows an About Window.
				"""
				self.about_window = AboutWindow()
				self.about_window.show()

		def show_help_window(self):
				"""
				Open the default web browser and show the help contents.
				"""
				dataeval_root = os.path.join(os.path.dirname(__file__), '../..')
				doc_name = 'doc/index.html'
				doc_fullname = os.path.normpath(os.path.join(dataeval_root, doc_name))
				if os.path.isfile(doc_fullname):
						webbrowser.open(os.path.join(dataeval_root, doc_name))
				else:
						# should not happen
						logger = logging.getLogger()
						logger.error("Cannot open help: '%s' not found" % doc_fullname)
				return

		def open_meas_info(self):
				meas_path = self.config.get('Measurement', 'main')
				self.meas_view_window = MeasurementView(
								meas_path, self.config.get('General', 'Backup') or None)
				return


if __name__ == '__main__':
		from argparse import ArgumentParser, RawTextHelpFormatter

		from config.Config import Config
		from config.funclib import procConfigFile, getConfigPath
		from config.modules import Modules

		modules_name = getConfigPath('modules', '.csv')
		modules = Modules()
		modules.read(modules_name)

		parser = ArgumentParser(formatter_class = RawTextHelpFormatter)
		args = Config.addArguments(parser).parse_args()
		name = procConfigFile('dataeval', args)
		config = Config(name, modules)
		config.init(args)

		app = QtGui.QApplication([])

		config_frame = MassFrame(config, args)
		config_frame.setWindowTitle('MASS')
		config_frame.show()

		app_status = app.exec_()
		modules.protected_write(modules_name)

		sys.exit(app_status)
