#!/usr/bin/python
import logging
import os

from ConfigFrame import cConfigFrame
from PySide import QtCore, QtGui
from PySide.QtCore import Qt
from PySide.QtGui import QApplication, QFileDialog, QIcon, QLineEdit, QPushButton, QGroupBox, QLabel, QRadioButton, \
		QCheckBox
from ViewControl import cViewControl
from dmw.EventEditorFrame import cEventEditor
from dmw.log_frame import LogFrame
from reportgen.kbendrun_20_weekly.create_video_captures import clean, copy_final_captures, create_captures, read_config
from section_table import ModuleTableFrame

IMAGE_DIRECTORY = os.path.join(os.path.dirname(__file__), "images")

logger = logging.getLogger()


class SimpleSignal(QtCore.QObject):
		signal = QtCore.Signal()


class cEventRecorderViewConfigFrame(cConfigFrame):
		Interface = 'iView'

		def browse_configuration(self):
				path = QFileDialog.getOpenFileName(self, 'Open a file', '',
																					 'CSV Files (*.csv)')

				self.txt_configuration_filepath.setText(str(path[0]))
				return

		def onclicked_event_editor(self):
				dialog_event_editor = cEventEditor(self)
				dialog_event_editor.setMinimumSize(500, 300)
				dialog_event_editor.setGeometry(300, 100, 500, 300)
				dialog_event_editor.setWindowTitle("Event Editor")
				dialog_event_editor.setWindowIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'event_editor_24.png')))
				dialog_event_editor.show()

		def browse_measurement(self):
				path = QFileDialog.getOpenFileName(self, 'Open measurement', '')

				self.txt_measurement_filepath.setText(str(path[0]))
				return

		def onclicked_checkbox_manual_entry(self):
				cbutton = self.sender()
				if cbutton.isChecked():
						cbutton.setText("Uncheck here to make csv entry!!")
						self.txt_measurement_filepath.setVisible(True)
						self.button_select_measurement.setVisible(True)
						self.txt_start_time.setVisible(True)
						self.txt_duration.setVisible(True)
						self.lbl_start_time.setVisible(True)
						self.lbl_duration.setVisible(True)
						self.txt_configuration_filepath.setVisible(False)
						self.button_select_csv.setVisible(False)
				else:
						cbutton.setText("Check here to make manual entry!!")
						self.txt_measurement_filepath.setVisible(False)
						self.button_select_measurement.setVisible(False)
						self.txt_start_time.setVisible(False)
						self.txt_duration.setVisible(False)
						self.lbl_start_time.setVisible(False)
						self.lbl_duration.setVisible(False)
						self.txt_configuration_filepath.setVisible(True)
						self.button_select_csv.setVisible(True)

		def browse_directorypath(self):
				folderpath = QFileDialog.getExistingDirectory(self, 'Select Folder')
				self.txt_output_directory_path.setText(str(folderpath))
				return

		def onStart(self):
				if self.checkbox_manual_entry.isChecked():
						if self.txt_start_time.text().strip() != "" and self.txt_duration.text().strip() != "" and self.txt_measurement_filepath.text().strip() != "":
								bfrds = [(self.txt_measurement_filepath.text(), float(self.txt_start_time.text()), float(self.txt_duration.text()))]
								first_tuple_elements = []
								for ele in bfrds:
										first_tuple_elements.append(ele[0])
								basename, selected_module_list = self.Control.onStartRecord(first_tuple_elements[0])
								if (len(selected_module_list[0][0]) <= 4):
										local_capture_dir = create_captures(bfrds, selected_module_list)
										if self.txt_output_directory_path.text().strip() != "":
												logger.info("Selected output directory: " + self.txt_output_directory_path.text().strip())
												copy_final_captures(bfrds, local_capture_dir, self.txt_output_directory_path.text().strip())
												clean(local_capture_dir)
												logger.info("Recording completed")
										else:
												default_dir = os.path.dirname(self.txt_measurement_filepath.text().strip())
												logger.info("Default output directory: " + str(default_dir))
												copy_final_captures(bfrds, local_capture_dir, default_dir)
												clean(local_capture_dir)
												logger.info("Recording completed")
								else:
										logger.warning("Please select at most 4 scripts")
						else:
								logger.warning("Please provide all inputs")
						return
				else:
						if self.txt_configuration_filepath.text().strip() != "":
								bfrds = read_config(self.txt_configuration_filepath.text().strip())
								first_tuple_elements = []
								for ele in bfrds:
										first_tuple_elements.append(ele[0])
								basename, selected_module_list = self.Control.onStartRecord(first_tuple_elements[0])
								if (len(selected_module_list[0][0])<=4):
										local_capture_dir = create_captures(bfrds, selected_module_list)
										if self.txt_output_directory_path.text().strip() != "" :
												logger.info("Selected output directory: " + self.txt_output_directory_path.text().strip())
												copy_final_captures(bfrds, local_capture_dir, self.txt_output_directory_path.text().strip())
												clean(local_capture_dir)
												logger.info("Recording completed")
										else:
												default_dir = os.path.dirname(self.txt_configuration_filepath.text().strip())
												logger.info("Default output directory: "+str(default_dir))
												copy_final_captures(bfrds, local_capture_dir,default_dir )
												clean(local_capture_dir)
												logger.info("Recording completed")
								else:
										logger.warning("Please select at most 4 scripts")
						else:
								logger.warning("Please select configuration file")
						return

		def __init__(self, root, Config, need_cn = True):

				cConfigFrame.__init__(self, root, Config)
				Config.UpdateCallbacks.append(self._update)
				self.controlPressed = False
				self.CloseSignal = SimpleSignal()

				self.TabWidget = QtGui.QTabWidget()
				self.MainLayout.addWidget(self.ControlFrame, 0, Qt.AlignTop)
				self.MainLayout.addWidget(self.TabWidget, 0, Qt.AlignTop)

				self.Control = cViewControl(None, Config)
				self.Closes.append(self.Control.onCloseAll)

				control_panel_grid = QtGui.QVBoxLayout()
				control_panel_grid.setSpacing(0)
				control_panel_grid.setContentsMargins(1, 1, 1, 1)

				# <editor-fold desc="Select measurements">
				gbox_manual_entry = QGroupBox('')
				formlayout_manual_entry = QtGui.QFormLayout()
				formlayout_manual_entry.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
				# formlayout_manual_entry.setFieldGrowthPolicy(QtGui.QFormLayout.FieldsStayAtSizeHint)
				formlayout_manual_entry.setLabelAlignment(Qt.AlignLeft)
				self.checkbox_manual_entry = QCheckBox("Manual entry")

				self.checkbox_manual_entry.toggled.connect(self.onclicked_checkbox_manual_entry)
				formlayout_manual_entry.addRow(self.checkbox_manual_entry)

				self.txt_measurement_filepath = QLineEdit()
				self.button_select_measurement = QPushButton("Select measurement")
				self.button_select_measurement.clicked.connect(self.browse_measurement)
				formlayout_manual_entry.addRow(self.button_select_measurement, self.txt_measurement_filepath)

				self.txt_start_time = QLineEdit()
				self.lbl_start_time = QLabel("Start time (s):")
				formlayout_manual_entry.addRow(self.lbl_start_time, self.txt_start_time)

				self.txt_duration = QLineEdit()
				self.lbl_duration = QLabel("Duration (s):")
				formlayout_manual_entry.addRow(self.lbl_duration, self.txt_duration)

				self.txt_configuration_filepath = QLineEdit()
				self.txt_configuration_filepath.setEnabled(False)
				self.button_select_csv = QPushButton("Select configuration file (csv)")
				self.button_select_csv.clicked.connect(self.browse_configuration)
				formlayout_manual_entry.addRow(self.button_select_csv, self.txt_configuration_filepath)

				gbox_manual_entry.setLayout(formlayout_manual_entry)
				control_panel_grid.addWidget(gbox_manual_entry)
				self.checkbox_manual_entry.setChecked(True)
				# </editor-fold>

							
				# <editor-fold desc="Select output directory">
				formlayout_output_directory = QtGui.QHBoxLayout()
				lbl_output_directory = QtGui.QLabel("Output directory : ")
				formlayout_output_directory.addWidget(lbl_output_directory)
				self.txt_output_directory_path = QLineEdit()
				self.txt_output_directory_path.setEnabled(False)
				formlayout_output_directory.addWidget(self.txt_output_directory_path)
				button_browse_directorypath = QPushButton("Browse...")
				button_browse_directorypath.clicked.connect(self.browse_directorypath)
				formlayout_output_directory.addWidget(button_browse_directorypath)
				control_panel_grid.addLayout(formlayout_output_directory)
				# </editor-fold>

				# <editor-fold desc="Buttonlayout start and closeall">
				formlayout_start_close = QtGui.QHBoxLayout()
				button_start = QtGui.QPushButton('Start')
				button_start.clicked.connect(self.onStart)
				self.button_closeall = QtGui.QPushButton('Close All')
				formlayout_start_close.addWidget(button_start)
				formlayout_start_close.addWidget(self.button_closeall)
				control_panel_grid.addLayout(formlayout_start_close)
				# </editor-fold>

				self.create_menus()

				self.ControlFrame.setLayout(control_panel_grid)
				control_panel_grid.setSpacing(0)
				control_panel_grid.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
				# <editor-fold desc="LogFrame">
				logframe = LogFrame(Config)
				dw = QtGui.QDockWidget()
				dw.setWidget(logframe)
				dw.setObjectName('LogDock')
				dw_features = QtGui.QDockWidget.DockWidgetMovable | \
											QtGui.QDockWidget.DockWidgetFloatable
				dw.setFeatures(dw_features)
				self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dw)

				# </editor-fold>

				# <editor-fold desc="TabWidget">
				ModuleTab = ModuleTableFrame(Config, self.Interface)
				self.TabWidget.addTab(ModuleTab, QIcon(os.path.join(IMAGE_DIRECTORY, 'main_module_execution_24.png')),
															' View Selection')
				self.TabWidget.setTabToolTip(0, "Add/select modules for Recording Service ")
				self.SectionFrames.append((ModuleTab, 'View Selection '))

				StatusTab = ModuleTableFrame(Config, Config.StatusSection,
																		 sub_from_option = 'fill')
				self.TabWidget.addTab(StatusTab, QIcon(os.path.join(IMAGE_DIRECTORY, 'status_names_24.png')), 'Status names')
				self.setTabToolTip(StatusTab, Config.get('__doc__', Config.StatusSection))
				self.SectionFrames.append((StatusTab, 'Status names'))
				# </editor-fold>
				for Tab in (ModuleTab, StatusTab):
						Tab.activate_modules()

				pass

		def create_menus(self):
				menu_bar = self.menuBar()
				action_event_editor = QtGui.QAction('&Event Editor', menu_bar)
				action_event_editor.setShortcut(self.tr("Alt+O"))
				action_event_editor.triggered.connect(self.onclicked_event_editor)
				menu_bar.addAction(action_event_editor)

		def onClose(self, itemName):
				if not itemName:
						return

				menu = self.ComboBox.menu()
				action = [action for action in menu.actions() if itemName == action.text()]
				if len(action) != 1:
						return
				action, = action

				BaseName = itemName.replace('Close ', '')
				self.Control.close(BaseName)
				menu.removeAction(action)
				return

		def onCloseAll(self):
				menu = self.ComboBox.menu()
				for action in menu.actions():
						menu.removeAction(action)
				self.Control.onCloseAll()
				return

		def addItemToCombobox(self, itemName):
				menu = self.ComboBox.menu()
				itemName = 'Close ' + itemName
				for action in menu.actions():
						if itemName == action.text():
								return

				action = QtGui.QAction(itemName, menu)
				action.triggered.connect(lambda n = itemName: self.onClose(n))

				menu.addAction(action)
				return

		def keyPressEvent(self, event):
				if event.key() == QtCore.Qt.Key_Control:
						self.controlPressed = True
				if event.key() == QtCore.Qt.Key_Tab and self.controlPressed:
						self.changeTab()
				return

		def keyReleaseEvent(self, event):
				if event.key() == QtCore.Qt.Key_Control:
						self.controlPressed = False
				return

		def changeTab(self):
				CurrentIndex = self.TabWidget.currentIndex()
				MaxIndex = self.TabWidget.count() - 1
				if CurrentIndex < MaxIndex:
						self.TabWidget.setCurrentIndex(CurrentIndex + 1)
				else:
						self.TabWidget.setCurrentIndex(0)
				return

		def _update(self):
				cConfigFrame._update(self)

				return
#
#
# if __name__ == '__main__':
#
# 		import sys
# 		from argparse import ArgumentParser
#
# 		from config.helper import procConfigFile, getConfigPath
# 		from config.View import cLoad
# 		from config.modules import Modules
#
# 		app = QtGui.QApplication([])
# 		modules_name = getConfigPath('modules', '.csv')
# 		modules = Modules()
# 		modules.read(modules_name)
# 		args = cLoad.addArguments(ArgumentParser()).parse_args()
# 		name = procConfigFile('view', args)
# 		config = cLoad(name, modules)
# 		config.init(args)
#
# 		config_frame = cEventRecorderViewConfigFrame(None, config)
# 		config_frame.show()
# 		app_status = app.exec_()
#
# 		# config.wait(args) TODO: wait app in config
# 		modules.protected_write(modules_name)
# 		sys.exit(app_status)
