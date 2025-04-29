import copy
import datetime
import logging
import os
import time
from collections import OrderedDict
from os.path import expanduser

import numpy as np
from PySide import QtCore, QtGui
from PySide.QtCore import Qt, QSize
from PySide.QtGui import QApplication, QColorDialog, QComboBox, QDesktopWidget, QDialog, QDialogButtonBox, \
		QFileDialog, \
		QFormLayout, QGroupBox, QHBoxLayout, QIcon, QLabel, QLineEdit, QPixmap, QPlainTextEdit, QPushButton, QSizePolicy, \
		QSortFilterProxyModel, QSpacerItem, QSpinBox, QSplitter, QStandardItem, QStandardItemModel, QVBoxLayout, \
		QMessageBox,QTabWidget,QTableWidget,QTableWidgetItem
from dmw.NxtListNavigatorUpdater import cListNavigatorUpdater
from dmw.NxtPlotNavigatorUpdater import cPlotNavigatorUpdater
from dmw.NxtSignalSelector import LeafFilterProxyModel
from measproc.StandardTemplateDBManager import DatabaseManagement
from text.ViewText import ViewTextTemplateRunner1, ViewTextTemplateRunner2, ViewTextTemplateRunner3, \
		ViewTextTemplateRunner4, ViewTextTemplateRunner5, ViewTextTemplateRunner6, ViewTextTemplateRunner7, \
		ViewTextTemplateRunner8, ViewTextTemplateRunner9, ViewTextTemplateRunner10

IMAGE_DIRECTORY = os.path.join(os.path.dirname(__file__), "images")
DATABASE_PATH = os.path.abspath(
				os.path.join(os.path.dirname(__file__), '../../../',
										 'dataevalaebs\src\standardtemplates\StandardTemplates.db'))
logger = logging.getLogger('ExecuteScriptRuntime')


class ObjectEmittingSignal(QtCore.QObject):
		signal = QtCore.Signal(object)


class cExecuteScriptRuntime(QtGui.QMainWindow):
		def __init__(self, root, Config, Control):
				QtGui.QMainWindow.__init__(self)
				ModuleTab = root.widget(0)
				Selector = StandardTemplateViewer(self, Config, Control, ModuleTab)
				vboxlayout_main = QtGui.QVBoxLayout()
				vboxlayout_main.setSpacing(0)
				vboxlayout_main.setContentsMargins(1, 1, 1, 1)
				frame = QtGui.QFrame()
				vboxlayout_main.addWidget(Selector)

				frame.setLayout(vboxlayout_main)
				self.setCentralWidget(frame)

		def close(self, template_runner_object):
				template_runner_object.close()
				return

		def save(self, template_runner_object):
				InitDir = template_runner_object.get_init_dir()
				Name = QtGui.QFileDialog.getSaveFileName(filter = 'python *.py',
																								 caption = "view" + template_runner_object.PREFIX,
																								 dir = InitDir)[0]
				if Name:
						template_runner_object.save(Name)
				return

		def open(self, template_runner_object):
				InitDir = template_runner_object.get_init_dir()
				Name = QtGui.QFileDialog.getOpenFileName(filter = 'python *.py',
																								 dir = InitDir)[0]
				if Name:
						template_runner_object.open(Name)
				return

		def reset(self, template_runner_object):
				template_runner_object.open(self.FileName)
				return

		def update_navigator_metadata(self):
				self.PlotNav.update_from_metadata()
				self.ListNav.update_from_metadata()
				return


class StandardTemplateViewer(QtGui.QFrame):
		DatabaseManagement.db_file_path = DATABASE_PATH
		database_management = DatabaseManagement()

		def __init__(self, root, config, control, active_modules_table):
				QtGui.QFrame.__init__(self, parent = root)

				templates_relative_directory = 'text\\templates'
				parent_directory = os.path.dirname(os.path.dirname(__file__))
				template_directory = os.path.join(parent_directory, templates_relative_directory)

				self.config = config
				self.control = control
				self.active_modules_table = active_modules_table

				# Template Runner holders
				self.template_runners = OrderedDict()
				for counter in range(1, 10):
						template_name = 'viewTemplateRunner' + str(counter) + '.py'
						template_file_path = os.path.join(template_directory, 'viewTemplateRunner' + str(counter) + '.py')
						self.template_runners['TemplateRunner' + str(counter)] = {
								"name"            : template_name,
								"used"            : False,
								"python_file_path": template_file_path,
								"template_object" : None,
								"template_class"  : eval("ViewTextTemplateRunner" + str(counter))
						}
				self.update_selected_modules()
				self.active_modules_table.act_module_frame.update_standard_templates.signal.connect(
								self.update_template_runners)
				hboxlayout_standard_template = QtGui.QHBoxLayout()
				hboxlayout_standard_template.setSpacing(1)
				hboxlayout_standard_template.setContentsMargins(1, 1, 1, 1)

				gbox_template_selector = QGroupBox('')
				vboxlayout_template_selector = QtGui.QVBoxLayout()
				vboxlayout_template_selector.setSpacing(1)
				vboxlayout_template_selector.setContentsMargins(1, 1, 1, 1)

				# <editor-fold desc="standard template operations">
				gbox_standard_template_operations = QGroupBox('')
				hboxlayout_standard_template_operations = QtGui.QHBoxLayout()
				hboxlayout_standard_template_operations.setContentsMargins(1, 1, 1, 1)

				gbox_main_loading = QGroupBox('')
				gridlayout_main_loading = QtGui.QGridLayout()
				gridlayout_main_loading.setContentsMargins(1, 1, 1, 1)

				self.label_execution = QLabel("Execution")
				gridlayout_main_loading.addWidget(self.label_execution, 0, 0, 1, 2, Qt.AlignTop)

				self.pbutton_add_to_main_modules = QPushButton("Add To Execution")
				self.pbutton_add_to_main_modules.setToolTip(
								'This standard module will be added in main modules active section for execution')
				self.pbutton_add_to_main_modules.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'add_module_24.png')))
				self.pbutton_add_to_main_modules.clicked.connect(self.add_to_main_modules)
				gridlayout_main_loading.addWidget(self.pbutton_add_to_main_modules, 1, 0, 1, 2, Qt.AlignCenter)

				gbox_main_loading.setLayout(gridlayout_main_loading)
				hboxlayout_standard_template_operations.addWidget(gbox_main_loading)

				gbox_templates_operations = QGroupBox('')
				gridlayout_templates_operations = QtGui.QGridLayout()
				gridlayout_templates_operations.setContentsMargins(1, 1, 1, 1)

				self.label_templates = QLabel("Templates")
				gridlayout_templates_operations.addWidget(self.label_templates, 0, 0, 1, 2, Qt.AlignTop | Qt.AlignCenter)

				self.pbutton_add_module = QPushButton("")
				self.pbutton_add_module.setToolTip('Add new standard template')
				self.pbutton_add_module.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'add_24.png')))
				self.pbutton_add_module.clicked.connect(self.add_module)
				gridlayout_templates_operations.addWidget(self.pbutton_add_module, 1, 0)

				self.pbutton_edit_module = QPushButton("")
				self.pbutton_edit_module.setToolTip('Edit existing standard template')
				self.pbutton_edit_module.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'edit_24.png')))
				self.pbutton_edit_module.clicked.connect(self.edit_module)
				gridlayout_templates_operations.addWidget(self.pbutton_edit_module, 1, 1)

				self.pbutton_delete_module = QPushButton("")
				self.pbutton_delete_module.setToolTip('Delete standard template')
				self.pbutton_delete_module.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'remove_24.png')))
				self.pbutton_delete_module.clicked.connect(self.delete_module)
				gridlayout_templates_operations.addWidget(self.pbutton_delete_module, 1, 2)

				self.pbutton_copy_module = QPushButton("")
				self.pbutton_copy_module.setToolTip('Copy standard template')
				self.pbutton_copy_module.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'copy_16.png')))
				self.pbutton_copy_module.clicked.connect(self.copy_module)
				gridlayout_templates_operations.addWidget(self.pbutton_copy_module, 1, 3)

				gbox_templates_operations.setLayout(gridlayout_templates_operations)
				hboxlayout_standard_template_operations.addWidget(gbox_templates_operations)

				gbox_axes_operations = QGroupBox('')
				gridlayout_axes_operations = QtGui.QGridLayout()
				gridlayout_axes_operations.setContentsMargins(1, 1, 1, 1)

				self.label_axes = QLabel("Axes")
				gridlayout_axes_operations.addWidget(self.label_axes, 0, 0, 1, 2, Qt.AlignTop | Qt.AlignCenter)

				self.pbutton_add_axes = QPushButton("")
				self.pbutton_add_axes.setToolTip('Add Axes to standard template')
				self.pbutton_add_axes.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'add_1_24.png')))
				self.pbutton_add_axes.clicked.connect(self.add_axes_details)
				self.pbutton_add_axes.setEnabled(False)
				gridlayout_axes_operations.addWidget(self.pbutton_add_axes, 1, 0)

				self.pbutton_edit_axes = QPushButton("")
				self.pbutton_edit_axes.setToolTip('Edit Axes in existing standard template')
				self.pbutton_edit_axes.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'edit_1_24.png')))
				self.pbutton_edit_axes.clicked.connect(self.edit_axes_details)
				self.pbutton_edit_axes.setEnabled(False)
				gridlayout_axes_operations.addWidget(self.pbutton_edit_axes, 1, 1)

				self.pbutton_delete_axes = QPushButton("")
				self.pbutton_delete_axes.setToolTip('Delete Axes from standard template')
				self.pbutton_delete_axes.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'remove_1_24.png')))
				self.pbutton_delete_axes.clicked.connect(self.delete_axes_details)
				self.pbutton_delete_axes.setEnabled(False)
				gridlayout_axes_operations.addWidget(self.pbutton_delete_axes, 1, 2)

				self.pbutton_copy_axes = QPushButton("")
				self.pbutton_copy_axes.setToolTip('Copy Axes from standard template')
				self.pbutton_copy_axes.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'copy_16.png')))
				self.pbutton_copy_axes.clicked.connect(self.copy_axes_details)
				self.pbutton_copy_axes.setEnabled(False)
				gridlayout_axes_operations.addWidget(self.pbutton_copy_axes, 1, 3)

				gbox_axes_operations.setLayout(gridlayout_axes_operations)
				hboxlayout_standard_template_operations.addWidget(gbox_axes_operations)

				gbox_group_operations = QGroupBox('')
				gridlayout_group_operations = QtGui.QGridLayout()
				gridlayout_group_operations.setContentsMargins(1, 1, 1, 1)

				self.label_group = QLabel("Groups")
				gridlayout_group_operations.addWidget(self.label_group, 0, 0, 1, 2, Qt.AlignTop | Qt.AlignCenter)

				self.pbutton_add_group = QPushButton("")
				self.pbutton_add_group.setToolTip('Add group to standard template')
				self.pbutton_add_group.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'add_2_24.png')))
				self.pbutton_add_group.clicked.connect(self.add_listdetails)
				self.pbutton_add_group.setEnabled(False)
				gridlayout_group_operations.addWidget(self.pbutton_add_group, 1, 0)

				self.pbutton_edit_group = QPushButton("")
				self.pbutton_edit_group.setToolTip('Edit group in existing standard template')
				self.pbutton_edit_group.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'edit_2_24.png')))
				self.pbutton_edit_group.clicked.connect(self.edit_listdetails)
				self.pbutton_edit_group.setEnabled(False)
				gridlayout_group_operations.addWidget(self.pbutton_edit_group, 1, 1)

				self.pbutton_delete_group = QPushButton("")
				self.pbutton_delete_group.setToolTip('Delete group from standard template')
				self.pbutton_delete_group.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'remove_2_24.png')))
				self.pbutton_delete_group.clicked.connect(self.delete_listdetails)
				self.pbutton_delete_group.setEnabled(False)
				gridlayout_group_operations.addWidget(self.pbutton_delete_group, 1, 2)

				self.pbutton_copy_group = QPushButton("")
				self.pbutton_copy_group.setToolTip('Copy group from standard template')
				self.pbutton_copy_group.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'copy_16.png')))
				self.pbutton_copy_group.clicked.connect(self.copy_list_details)
				self.pbutton_copy_group.setEnabled(False)
				gridlayout_group_operations.addWidget(self.pbutton_copy_group, 1, 3)

				gbox_group_operations.setLayout(gridlayout_group_operations)
				hboxlayout_standard_template_operations.addWidget(gbox_group_operations)

				gbox_signal_operations = QGroupBox('')
				gridlayout_signal_operations = QtGui.QGridLayout()
				gridlayout_signal_operations.setContentsMargins(1, 1, 1, 1)

				self.label_signals = QLabel("Signals")
				gridlayout_signal_operations.addWidget(self.label_signals, 0, 0, 1, 2, Qt.AlignTop | Qt.AlignCenter)

				self.pbutton_add_edit_signals = QPushButton("")
				self.pbutton_add_edit_signals.setToolTip('Add signals to standard template')
				self.pbutton_add_edit_signals.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'edit_3_24.png')))
				self.pbutton_add_edit_signals.clicked.connect(self.add_edit_signals)
				gridlayout_signal_operations.addWidget(self.pbutton_add_edit_signals, 1, 0)

				gbox_signal_operations.setLayout(gridlayout_signal_operations)
				hboxlayout_standard_template_operations.addWidget(gbox_signal_operations)

				horizontal_spacer = QSpacerItem(0, 0, QSizePolicy.Expanding)
				hboxlayout_standard_template_operations.addItem(horizontal_spacer)
				gbox_standard_template_operations.setLayout(hboxlayout_standard_template_operations)
				vboxlayout_template_selector.addWidget(gbox_standard_template_operations)

				# </editor-fold>

				# <editor-fold desc="Template Filter">
				gbox_template_filter = QGroupBox('')
				hboxlayout_template_filter = QtGui.QHBoxLayout()
				hboxlayout_template_filter.setSpacing(0)
				hboxlayout_template_filter.setContentsMargins(1, 1, 1, 1)
				lbl_template_name = QLabel("")
				lbl_template_name.setPixmap(QPixmap(os.path.join(IMAGE_DIRECTORY, 'search_24.png')))

				hboxlayout_template_filter.addWidget(lbl_template_name, 0, Qt.AlignVCenter)
				lbl_spacer = QLabel("")
				hboxlayout_template_filter.addWidget(lbl_spacer, 0, Qt.AlignVCenter)

				self.template_name = QtGui.QLineEdit()
				self.template_name.setToolTip('Provide template name here')
				self.template_name.textEdited.connect(self.search_text_changed)
				hboxlayout_template_filter.addWidget(self.template_name, 0, Qt.AlignVCenter)

				self.pbutton_template_filter_clear = QPushButton("")
				self.pbutton_template_filter_clear.setToolTip('Clear Filter')
				self.pbutton_template_filter_clear.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'clear_filter_24.png')))
				self.pbutton_template_filter_clear.setMinimumWidth(50)
				self.pbutton_template_filter_clear.pressed.connect(self.clear_filter)
				hboxlayout_template_filter.addWidget(self.pbutton_template_filter_clear, 0, Qt.AlignVCenter)

				self.pbutton_template_filter_match_case = QPushButton("Aa")
				self.pbutton_template_filter_match_case.setToolTip('Set match case on/off')
				self.pbutton_template_filter_match_case.setMaximumWidth(50)
				self.pbutton_template_filter_match_case.setCheckable(True)
				self.pbutton_template_filter_match_case.clicked.connect(lambda: self.search_text_changed())
				hboxlayout_template_filter.addWidget(self.pbutton_template_filter_match_case, 0, Qt.AlignVCenter)

				gbox_template_filter.setLayout(hboxlayout_template_filter)

				vboxlayout_template_selector.addWidget(gbox_template_filter)
				# </editor-fold>

				# <editor-fold desc="Treeview control">
				self.listview_templates = QtGui.QTreeView()
				self.listview_templates.doubleClicked.connect(self.listview_templates_doubleClicked)
				self.listview_templates.clicked.connect(self.listview_templates_clicked)
				self.listview_templates.setSortingEnabled(True)
				self.listview_templates.header().setStretchLastSection(True)
				self.listview_templates.setAlternatingRowColors(True)

				self.listview_templates.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
				self.listview_templates.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

				self.listview_templates.setHeaderHidden(False)
				self.listview_templates_model = QStandardItemModel()
				self.listview_templates_model.setHorizontalHeaderLabels(
								['Name', 'Description', 'Author', 'Version', 'Date', 'Type', 'ID'])

				# Make proxy model to allow seamless filtering
				self.listview_templates_proxy_model = QSortFilterProxyModel()
				self.listview_templates_proxy_model.setSourceModel(self.listview_templates_model)
				self.listview_templates_proxy_model.sort(1)
				self.listview_templates.setModel(self.listview_templates_proxy_model)

				vboxlayout_template_selector.addWidget(self.listview_templates)

				self.update_model()
				# </editor-fold>
				gbox_template_selector.setLayout(vboxlayout_template_selector)

				# <editor-fold desc="Template details">
				gbox_template_details = QGroupBox('')
				vboxlayout_template_details = QtGui.QVBoxLayout()
				vboxlayout_template_details.setSpacing(0)
				vboxlayout_template_details.setContentsMargins(1, 1, 1, 1)

				self.lbl_template_details = QLabel("Details")
				self.lbl_template_details.setStyleSheet("background-color: white;")
				vboxlayout_template_details.addWidget(self.lbl_template_details)
				vboxlayout_template_details.setAlignment(Qt.AlignTop)

				gbox_template_details.setLayout(vboxlayout_template_details)

				self.splitter_standard_template = QSplitter(Qt.Horizontal)
				self.splitter_standard_template.setObjectName('StandardTemplateSplitter')
				self.splitter_standard_template.setOrientation(QtCore.Qt.Horizontal)

				self.splitter_standard_template.addWidget(gbox_template_selector)
				self.splitter_standard_template.addWidget(gbox_template_details)
				widget_width = QApplication.desktop().screenGeometry().width()

				self.splitter_standard_template.setSizes([widget_width, widget_width])
				hboxlayout_standard_template.addWidget(self.splitter_standard_template)
				# </editor-fold>

				self.setLayout(hboxlayout_standard_template)

				# <editor-fold desc="Context menu actions">
				self.action_add_to_main_modules = QtGui.QAction("Add To Execution ", self, triggered =
				self.add_to_main_modules)
				self.action_add_to_main_modules.setToolTip(
								'This standard module will be added in main modules active section for execution')
				self.action_add_to_main_modules.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'add_module_24.png')))

				self.action_add_module = QtGui.QAction("Add new standard template ", self, triggered = self.add_module)
				self.action_add_module.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'add_24.png')))

				self.action_edit_module = QtGui.QAction("Edit standard template ", self, triggered = self.edit_module)
				self.action_edit_module.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'edit_24.png')))

				self.action_delete_module = QtGui.QAction("Delete standard template ", self, triggered = self.delete_module)
				self.action_delete_module.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'remove_24.png')))

				self.action_copy_module = QtGui.QAction("Copy standard template ", self, triggered = self.copy_module)
				self.action_copy_module.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'copy_16.png')))

				self.action_add_axes = QtGui.QAction("Add Axes", self, triggered = self.add_axes_details)
				self.action_add_axes.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'add_1_24.png')))

				self.action_edit_axes = QtGui.QAction("Edit Axes", self, triggered = self.edit_axes_details)
				self.action_edit_axes.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'edit_1_24.png')))

				self.action_delete_axes = QtGui.QAction("Delete Axes", self, triggered = self.delete_axes_details)
				self.action_delete_axes.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'remove_1_24.png')))

				self.action_copy_axes = QtGui.QAction("Copy Axes from other template", self, triggered =
				self.copy_axes_details)
				self.action_copy_axes.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'copy_16.png')))

				self.action_add_group = QtGui.QAction("Add Group", self, triggered = self.add_listdetails)
				self.action_add_group.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'add_2_24.png')))

				self.action_edit_group = QtGui.QAction("Edit Group", self, triggered = self.edit_listdetails)
				self.action_edit_group.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'edit_2_24.png')))

				self.action_delete_group = QtGui.QAction("Delete Group", self, triggered = self.delete_listdetails)
				self.action_delete_group.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'remove_2_24.png')))

				self.action_copy_group = QtGui.QAction("Copy Group from other template", self,
																							 triggered = self.copy_list_details)
				self.action_copy_group.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'copy_16.png')))

				self.action_add_edit_signals = QtGui.QAction("Add/Edit signals", self, triggered = self.add_edit_signals)
				self.action_add_edit_signals.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'edit_3_24.png')))

		# </editor-fold>

		def contextMenuEvent(self, event):
				item_selection_model = self.listview_templates.selectionModel()
				if len(item_selection_model.selectedIndexes()) != 0:
						selected_row = item_selection_model.selectedIndexes()[6]

						row = self.listview_templates_proxy_model.mapToSource(selected_row)
						template = self.listview_templates_proxy_model.sourceModel().itemFromIndex(row)

						template_id = template.text()
						ctx_menu = QtGui.QMenu()
						ctx_menu.addAction(self.action_add_to_main_modules)
						ctx_menu.addSeparator()
						ctx_menu.addAction(self.action_add_module)
						ctx_menu.addAction(self.action_edit_module)
						ctx_menu.addAction(self.action_delete_module)
						ctx_menu.addAction(self.action_copy_module)
						ctx_menu.addSeparator()

						template_details = self.database_management.select_module_by_id(template_id)
						template_type = template_details[9]
						if template_details is not None:
								module_type = self.database_management.select_type_by_id(template_type)
								if module_type is not None:
										if module_type[0] == 'List':
												ctx_menu.addAction(self.action_add_group)
												ctx_menu.addAction(self.action_edit_group)
												ctx_menu.addAction(self.action_delete_group)
												ctx_menu.addSeparator()
												ctx_menu.addAction(self.action_copy_group)
												ctx_menu.addSeparator()
										if module_type[0] == 'Plot':
												ctx_menu.addAction(self.action_add_axes)
												ctx_menu.addAction(self.action_edit_axes)
												ctx_menu.addAction(self.action_delete_axes)
												ctx_menu.addSeparator()
												ctx_menu.addAction(self.action_copy_axes)
												ctx_menu.addSeparator()

						ctx_menu.addAction(self.action_add_edit_signals)
						ctx_menu.addSeparator()
						ctx_menu.exec_(event.globalPos())

		def get_available_runner(self, selected_template_name):
				for template_name, template_details in self.template_runners.items():
						if template_details["used"] is True and selected_template_name == template_details[
																																									"template_object"].PREFIX[4:]:
								template_details["template_object"].open(template_details["python_file_path"])
								return self.template_runners[template_name]
						if template_details["used"] is True:
								continue
						else:
								template_details["used"] = True
								return self.template_runners[template_name]

		def print_used_runners(self):
				for template_name, template_details in self.template_runners.items():
						if template_details["used"] is False:
								break
						print(template_details["name"])
						print(template_details["used"])
						print(template_details["python_file_path"])
						print(template_details["template_object"])
						print(template_details["template_class"])
						if template_details["template_object"] is not None:
								print(template_details["template_object"].get_text())
						print("--------------------------------------------------")

		def update_template_runners(self):
				# print("FUNCTION update_template_runners START")
				# self.print_used_runners()
				remove_templates = []
				modules = self.active_modules_table.act_module_frame.get_selected_modules()
				for module in modules:
						remove_templates.append(module.split('@')[0][4:])
				for template_name, template_details in self.template_runners.items():
						if template_details["template_object"] is None:
								continue
						standard_template_name = template_details["template_object"].PREFIX[4:]
						if standard_template_name in remove_templates:

								template_details["name"] = template_name
								template_details["used"] = False
								del template_details["template_object"]
								template_details["template_object"] = None
				# print("AFTER")
				# self.print_used_runners()
				# print("FUNCTION update_template_runners END")

		def update_selected_modules(self):
				# print("FUNCTION update_selected_modules")
				# self.print_used_runners()
				modules = self.active_modules_table.act_module_frame.get_active_modules()
				for module in modules:
						template_name = module.split('@')[0][4:]
						template_details = self.database_management.select_module_by_name(template_name)

						if template_details is not None:
								template_name = template_details[1]
								template_geometry = template_details[8]
								template_runner = self.get_available_runner(template_name)
								template_class = template_runner["template_class"]
								template_class.PREFIX = "view" + template_details[1]
								if template_runner["template_object"] is None:
										template_runner["template_object"] = template_class(template_runner["python_file_path"],
																																				self.config,
																																				self.control)
								template_type = template_details[9]
								module_type = self.database_management.select_type_by_id(template_type)
								if module_type is not None:
										if module_type[0] == 'List':
												list_details = self.database_management.select_list_details_by_module_id(template_details[0])
												if len(list_details) == 0:
														logger.info("No group added to " + template_details[1] + " module")
												else:
														listnav = cListNavigatorUpdater(template_runner["template_object"], template_name)
														listnav.create()
														for list_detail in list_details:
																list_detail_id = list_detail[0]
																list_detail_group_name = list_detail[1]
																list_detail_background_color = list_detail[2]
																list_detail_Module_id = list_detail[3]
																signal_details = self.database_management.select_list_signal_details_by_list_id(
																				list_detail_id)
																if signal_details is not None:
																		signals = []
																		for signal_detail in signal_details:
																				signal_detail_plot_signal_detail_id = signal_detail[0]
																				signal_detail_label = signal_detail[1]
																				signal_detail_offset = signal_detail[2]
																				signal_detail_factor = signal_detail[3]
																				signal_detail_display_scaled = signal_detail[4]
																				signal_detail_unit = signal_detail[5]
																				signal_detail_alias_name = signal_detail[6]
																				signal_detail_device_name = signal_detail[7]
																				signal_detail_signal_name = signal_detail[8]
																				signal_detail_is_custom_expression = signal_detail[9]
																				signal_detail_custom_expression = signal_detail[10]
																				signal_detail_custom_expression_signal_list = eval(signal_detail[11])
																				if signal_detail_is_custom_expression:
																						listnav.addCustomSignal(list_detail_group_name,(signal_detail_signal_name,
																																		 signal_detail_custom_expression_signal_list,
																																		 signal_detail_custom_expression,
																																		 signal_detail_unit),list_detail_background_color)
																				else:
																						signals.append(
																								(signal_detail_device_name, signal_detail_signal_name, signal_detail_unit))

																		listnav.addSignals(list_detail_group_name, signals, list_detail_background_color)
														# logger.info("Added " + template_details[1] + " module for execution")
										if module_type[0] == 'Plot':
												plot_details = self.database_management.select_plot_details_by_module_id(
																template_details[0])

												if len(plot_details) == 0:
														logger.info("No axes added to " + template_details[1] + " module")
												else:
														plotnav = cPlotNavigatorUpdater(template_runner["template_object"], template_name,
																														template_geometry)
														plotnav.create(plot_details[0])
														for plot_index, plot_detail in enumerate(plot_details):
																if plot_index != 0:
																		plotnav.addAxis(plot_detail)
																plot_detail_id = plot_detail[0]
																plot_detail_axes_name = plot_detail[1]
																plot_detail_xlabel = plot_detail[2]
																plot_detail_ylabel = plot_detail[3]
																plot_detail_yticks = plot_detail[4]
																plot_detail_row_number = plot_detail[5]
																plot_detail_column_number = plot_detail[6]
																signal_details = self.database_management.select_plot_signal_details_by_plot_id(
																				plot_detail_id)
																if signal_details is not None:
																		# list of tuples with device name signal name unit
																		signals = []
																		for signal_detail in signal_details:
																				signal_detail_plot_signal_detail_id = signal_detail[0]
																				signal_detail_label = signal_detail[1]
																				signal_detail_offset = signal_detail[2]
																				signal_detail_factor = signal_detail[3]
																				signal_detail_display_scaled = signal_detail[4]
																				signal_detail_unit = signal_detail[5]
																				signal_detail_alias_name = signal_detail[6]
																				signal_detail_device_name = signal_detail[7]
																				signal_detail_signal_name = signal_detail[8]
																				signal_detail_is_custom_expression = signal_detail[9]
																				signal_detail_custom_expression = signal_detail[10]
																				signal_detail_custom_expression_signal_list = eval(signal_detail[11])
																				if signal_detail_is_custom_expression:
																						plotnav.addCustomSignal((signal_detail_signal_name,
																																		 signal_detail_custom_expression_signal_list,
																																		 signal_detail_custom_expression,
																																		 signal_detail_unit,
																																		 signal_detail_label,
																																		 signal_detail_offset,
																																		 signal_detail_factor,
																																		 signal_detail_display_scaled))
																				else:
																						signals.append(
																								(signal_detail_device_name, signal_detail_signal_name,
																								 signal_detail_unit, signal_detail_label, signal_detail_offset,signal_detail_factor, signal_detail_display_scaled))
																		plotnav.addSignals(signals)
														# logger.info("Added " + template_details[1] + " module for execution")
				# print("AFTER")
				# self.print_used_runners()
				# print("FUNCTION update_selected_modules END")

		def add_to_main_modules(self):
				# print("FUNCTION add_to_main_modules START")
				# self.print_used_runners()
				item_selection_model = self.listview_templates.selectionModel()
				if len(item_selection_model.selectedIndexes()) != 0:
						selected_row = item_selection_model.selectedIndexes()[6]

						row = self.listview_templates_proxy_model.mapToSource(selected_row)
						template = self.listview_templates_proxy_model.sourceModel().itemFromIndex(row)

						template_id = template.text()
						template_details = self.database_management.select_module_by_id(template_id)

						if template_details is not None:
								template_id = template_details[0]
								template_name = template_details[1]
								template_description = template_details[2]
								template_author = template_details[3]
								template_revision = template_details[4]
								template_date = template_details[5]
								template_image = template_details[6]
								template_image_type = template_details[7]
								template_geometry = template_details[8]
								template_type = template_details[9]
								template_runner = self.get_available_runner(template_details[1])
								template_class = template_runner["template_class"]
								template_class.PREFIX = "view" + template_name
								if template_runner["template_object"] is None:
										template_runner["template_object"] = template_class(template_runner["python_file_path"],
																																				self.config,
																																				self.control)

						module_type = self.database_management.select_type_by_id(template_type)
						if module_type is not None:
								if module_type[0] == 'List':

										list_details = self.database_management.select_list_details_by_module_id(
														template_details[0])
										if len(list_details) == 0:
												logger.info("No group added to " + template_details[1] + " module")
										else:
												listnav = cListNavigatorUpdater(template_runner["template_object"], template_name)
												listnav.create()
												for list_detail in list_details:
														list_detail_id = list_detail[0]
														list_detail_group_name = list_detail[1]
														list_detail_background_color = list_detail[2]
														list_detail_Module_id = list_detail[3]
														signal_details = self.database_management.select_list_signal_details_by_list_id(
																		list_detail_id)
														if signal_details is not None:
																signals = []
																for signal_detail in signal_details:
																		signal_detail_plot_signal_detail_id = signal_detail[0]
																		signal_detail_label = signal_detail[1]
																		signal_detail_offset = signal_detail[2]
																		signal_detail_factor = signal_detail[3]
																		signal_detail_display_scaled = signal_detail[4]
																		signal_detail_unit = signal_detail[5]
																		signal_detail_alias_name = signal_detail[6]
																		signal_detail_device_name = signal_detail[7]
																		signal_detail_signal_name = signal_detail[8]

																		signal_detail_is_custom_expression = signal_detail[9]
																		signal_detail_custom_expression = signal_detail[10]
																		signal_detail_custom_expression_signal_list = eval(signal_detail[11])
																		if signal_detail_is_custom_expression:
																				listnav.addCustomSignal(list_detail_group_name,(signal_detail_signal_name,
																																 signal_detail_custom_expression_signal_list,
																																 signal_detail_custom_expression, signal_detail_unit),list_detail_background_color)
																		else:
																				signals.append(
																								(signal_detail_device_name, signal_detail_signal_name, signal_detail_unit))
																listnav.addSignals(list_detail_group_name, signals, list_detail_background_color)
										logger.info("Added " + template_details[1] + " module for execution")
								if module_type[0] == 'Plot':
										plot_details = self.database_management.select_plot_details_by_module_id(
														template_details[0])

										if len(plot_details) == 0:
												logger.info("No axes added to " + template_details[1] + " module")
										else:
												plotnav = cPlotNavigatorUpdater(template_runner["template_object"], template_name,
																												template_geometry)
												plotnav.create(plot_details[0])
												for plot_index, plot_detail in enumerate(plot_details):
														if plot_index != 0:
																plotnav.addAxis(plot_detail)
														plot_detail_id = plot_detail[0]
														plot_detail_axes_name = plot_detail[1]
														plot_detail_xlabel = plot_detail[2]
														plot_detail_ylabel = plot_detail[3]
														plot_detail_yticks = plot_detail[4]
														plot_detail_row_number = plot_detail[5]
														plot_detail_column_number = plot_detail[6]

														signal_details = self.database_management.select_plot_signal_details_by_plot_id(
																		plot_detail_id)
														if signal_details is not None:
																# list of tuples with device name signal name unit
																signals = []
																for signal_detail in signal_details:
																		signal_detail_plot_signal_detail_id = signal_detail[0]
																		signal_detail_label = signal_detail[1]
																		signal_detail_offset = signal_detail[2]
																		signal_detail_factor = signal_detail[3]
																		signal_detail_display_scaled = signal_detail[4]
																		signal_detail_unit = signal_detail[5]
																		signal_detail_alias_name = signal_detail[6]
																		signal_detail_device_name = signal_detail[7]
																		signal_detail_signal_name = signal_detail[8]

																		signal_detail_is_custom_expression = signal_detail[9]
																		signal_detail_custom_expression = signal_detail[10]
																		signal_detail_custom_expression_signal_list = eval(signal_detail[11])
																		if signal_detail_is_custom_expression:
																				plotnav.addCustomSignal((signal_detail_signal_name,signal_detail_custom_expression_signal_list,signal_detail_custom_expression,signal_detail_unit,signal_detail_label,
																																		 signal_detail_offset,
																																		 signal_detail_factor,
																																		 signal_detail_display_scaled))
																		else:
																				signals.append(
																						(signal_detail_device_name, signal_detail_signal_name, signal_detail_unit, signal_detail_label,signal_detail_offset,signal_detail_factor, signal_detail_display_scaled))
																plotnav.addSignals(signals)

										logger.info("Added " + template_details[1] + " module for execution")

						self.active_modules_table.act_module_frame.refresh_elemnents()
						# print("AFTER")
						# self.print_used_runners()
						# print("FUNCTION add_to_main_modules END")

		def listview_templates_doubleClicked(self):
				self.add_to_main_modules()

		def listview_templates_clicked(self):
				item_selection_model = self.listview_templates.selectionModel()
				detailed_text = ""
				if len(item_selection_model.selectedIndexes()) != 0:

						self.lbl_template_details.clear()
						selected_row = item_selection_model.selectedIndexes()[6]
						row = self.listview_templates_proxy_model.mapToSource(selected_row)
						template = self.listview_templates_proxy_model.sourceModel().itemFromIndex(row)
						template_id = template.text()
						template_details = self.database_management.select_module_by_id(template_id)
						module_type = None
						if template_details is not None:
								detailed_text = "<!DOCTYPE html><head><style>"
								detailed_text += "body {font-size:11px; background-color: white;}" \
																 "table {border:1px solid black;font-family: arial, sans-serif;  border-collapse: " \
																 "collapse; }" \
																 "td,th {border:1px solid black; padding: 8px; word-wrap: " \
																 "break-word;}" \
																 "th {  text-align: left; background-color: lightblue;}" \
																 "div {width:100%;height:50%}" \
																 "h3 {width:100%;height:10%;background-color: white; font:8px }"

								detailed_text += "</style></head><body >"
								detailed_text += "<div><h3><b>Module Summary</b></h3>"
								detailed_text += "<p><b>Name : </b>" + str(template_details[1]) + "</p>"
								detailed_text += "<p><b>Description : </b>" + str(template_details[2]) + "</p>"
								detailed_text += "<p><b>Author : </b>" + str(template_details[3]) + "</p>"
								detailed_text += "<p><b>Revision : </b>" + str(template_details[4]) + "</p>"
								detailed_text += "<p><b>Date : </b>" + str(template_details[5]).replace('"', '') + "</p>"
								detailed_text += "<p><b>Geometry : </b>" + str(template_details[8]).replace('"', '') + "</p>"
								module_type = self.database_management.select_type_by_id(template_details[9])
								if module_type is not None:
										detailed_text += "<p><b>Type : </b>" + module_type[0] + "</p></div>\n"
										if module_type[0] == "List":
												self.pbutton_add_group.setEnabled(True)
												self.pbutton_edit_group.setEnabled(True)
												self.pbutton_delete_group.setEnabled(True)
												self.pbutton_copy_group.setEnabled(True)
										else:
												self.pbutton_add_group.setEnabled(False)
												self.pbutton_edit_group.setEnabled(False)
												self.pbutton_delete_group.setEnabled(False)
												self.pbutton_copy_group.setEnabled(False)
										if module_type[0] == "Plot":
												self.pbutton_add_axes.setEnabled(True)
												self.pbutton_edit_axes.setEnabled(True)
												self.pbutton_delete_axes.setEnabled(True)
												self.pbutton_copy_axes.setEnabled(True)
										else:
												self.pbutton_add_axes.setEnabled(False)
												self.pbutton_edit_axes.setEnabled(False)
												self.pbutton_delete_axes.setEnabled(False)
												self.pbutton_copy_axes.setEnabled(False)
								image_blob_data = template_details[6]
								image_type = template_details[7]
								if image_blob_data is not None:

										home_directory = expanduser("~")
										temp_image_directory = os.path.join(home_directory, ".aebs")

										filename = os.path.join(temp_image_directory, "temp_standard_template_image." + image_type)
										with open(filename, 'wb') as output_file:
												output_file.write(image_blob_data)

										detailed_text += "<hr><div>"
										detailed_text += "<img src='" + filename + "'>" \
																		 + "</div>"
						if module_type is not None:
								if module_type[0] == 'List':
										list_details = self.database_management.select_list_details_by_module_id(
														template_details[0])
										if list_details is not None:
												for list_detail in list_details:
														detailed_text += "\n\n <hr><h3><b> Group Name : </b>" + str(list_detail[1]) + \
																						 "</h3></div>\n"
														detailed_text += "\t\t<div><h3><b>Signals</b></h3>"
														signal_details = self.database_management.select_list_signal_details_by_list_id(
																		list_detail[0])
														detailed_text += "< table width='100%' >" \
																						 "< tr ><th> Alias Name </th >" \
																						 "< th> Device Name < / th >" \
																						 "< th > Signal Name < / th >< / tr >"
														for signal_detail in signal_details:
																detailed_text += "<tr> <td>" + str(signal_detail[6]) + \
																								 "</td><td>" + str(signal_detail[7]) + \
																								 "</td><td>" + str(signal_detail[8]) + \
																								 "</td></tr>"
														detailed_text += "</table></div>"

												detailed_text += "</body></html>"
								if module_type[0] == 'Plot':

										plot_details = self.database_management.select_plot_details_by_module_id(
														template_details[0])
										if plot_details is not None:
												for plot_detail in plot_details:
														detailed_text += "\n\n<div><hr><h3>" \
																						 "<b>Axes Name : </b>" + str(plot_detail[1]) + "</h3>\n"
														detailed_text += "<p><b> Xlabel : </b>" + str(
																		plot_detail[2]) + "\t<b> Ylabel : </b>" + str(
																		plot_detail[3]) + "</p>\n"
														detailed_text += "<p><b> YTicks : </b>" + str(
																		plot_detail[4]) + "</p>\n"
														detailed_text += "<p><b> RowNumber : </b>" + str(
																		plot_detail[5]) + "\t<b> ColumnNumber : </b>" + str(
																		plot_detail[6]) + "</p></div> " \
																											"\n"
														detailed_text += "\t\t<div><h3><b>Signals</b></h3>"
														signal_details = self.database_management.select_plot_signal_details_by_plot_id(
																		plot_detail[0])
														detailed_text += "< table width='100%' >" \
																						 "< tr >< th > Alias Name < / th >" \
																						 "< th > Device Name < / th >" \
																						 "< th > Signal Name < / th >< / tr >"
														for signal_detail in signal_details:
																detailed_text += "<tr> <td>" + str(signal_detail[6]) + \
																								 "</td><td>" + str(signal_detail[7]) \
																								 + "</td><td>" + str(signal_detail[8]) + \
																								 "</td></tr>"
														detailed_text += "</table></div>"
												detailed_text += "</body></html>"

				self.lbl_template_details.setText(detailed_text)

		def add_module(self):
				dialog_add_module = FrmAddTemplate()
				result = dialog_add_module.exec_()
				self.update_model()

		def edit_module(self):
				item_selection_model = self.listview_templates.selectionModel()
				if len(item_selection_model.selectedIndexes()) != 0:
						selected_row = item_selection_model.selectedIndexes()[6]

						row = self.listview_templates_proxy_model.mapToSource(selected_row)
						template = self.listview_templates_proxy_model.sourceModel().itemFromIndex(row)

						template_id = template.text()
						dialog_edit_module = FrmEditTemplate(template_id)
						result = dialog_edit_module.exec_()
						self.update_model()
						self.update_selected_modules()
				else:
						logger.info("Please select template first")

		def copy_module(self):
				item_selection_model = self.listview_templates.selectionModel()
				if len(item_selection_model.selectedIndexes()) != 0:
						selected_row = item_selection_model.selectedIndexes()[6]

						row = self.listview_templates_proxy_model.mapToSource(selected_row)
						template = self.listview_templates_proxy_model.sourceModel().itemFromIndex(row)

						template_id = template.text()
						dialog_edit_module = FrmCopyTemplate(template_id)
						result = dialog_edit_module.exec_()
						self.update_model()
				else:
						logger.info("Please select template first")

		def delete_module(self):
				item_selection_model = self.listview_templates.selectionModel()
				if len(item_selection_model.selectedIndexes()) != 0:
						msgBox = QMessageBox()
						msgBox.setText("Deleting standard template")
						msgBox.setInformativeText("Do you want to delete the standard template?")
						msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
						msgBox.setDefaultButton(QMessageBox.Yes)
						ret = msgBox.exec_()
						if ret == QMessageBox.Yes:
								selected_row = item_selection_model.selectedIndexes()[6]

								row = self.listview_templates_proxy_model.mapToSource(selected_row)
								template = self.listview_templates_proxy_model.sourceModel().itemFromIndex(row)

								template_id = template.text()
								self.database_management.delete_module(template_id)
								self.update_model()
				else:
						logger.info("Please select template first")

		def add_axes_details(self):
				item_selection_model = self.listview_templates.selectionModel()
				if len(item_selection_model.selectedIndexes()) != 0:
						selected_row = item_selection_model.selectedIndexes()[6]

						row = self.listview_templates_proxy_model.mapToSource(selected_row)
						template = self.listview_templates_proxy_model.sourceModel().itemFromIndex(row)

						template_id = template.text()
						dialog_add_axes = FrmAddAxesDetails(template_id)
						result = dialog_add_axes.exec_()
						self.update_selected_modules()
						self.listview_templates_clicked()
				else:
						logger.info("Please select template first")

		def edit_axes_details(self):
				item_selection_model = self.listview_templates.selectionModel()
				if len(item_selection_model.selectedIndexes()) != 0:
						selected_row = item_selection_model.selectedIndexes()[6]

						row = self.listview_templates_proxy_model.mapToSource(selected_row)
						template = self.listview_templates_proxy_model.sourceModel().itemFromIndex(row)

						template_id = template.text()
						dialog_edit_axes = FrmEditAxesDetails(template_id)
						if dialog_edit_axes.user_cancelled != True:
								result = dialog_edit_axes.exec_()
								self.update_selected_modules()
								self.listview_templates_clicked()
				else:
						logger.info("Please select template first")

		def copy_axes_details(self):
				item_selection_model = self.listview_templates.selectionModel()
				if len(item_selection_model.selectedIndexes()) != 0:
						selected_row = item_selection_model.selectedIndexes()[6]

						row = self.listview_templates_proxy_model.mapToSource(selected_row)
						template = self.listview_templates_proxy_model.sourceModel().itemFromIndex(row)

						template_id = template.text()
						dialog_copy_axes = FrmCopyAxesDetails(template_id)
						if dialog_copy_axes.user_cancelled != True:
								result = dialog_copy_axes.exec_()
								self.update_selected_modules()
								self.listview_templates_clicked()
				else:
						logger.info("Please select template first")

		def delete_axes_details(self):
				item_selection_model = self.listview_templates.selectionModel()
				if len(item_selection_model.selectedIndexes()) != 0:
						selected_row = item_selection_model.selectedIndexes()[6]

						row = self.listview_templates_proxy_model.mapToSource(selected_row)
						template = self.listview_templates_proxy_model.sourceModel().itemFromIndex(row)

						template_id = template.text()
						axes_details = self.database_management.select_plot_details_by_module_id(template_id)
						if len(axes_details) != 0:
								dialog_edit_module = FrmShowAxesList(axes_details)
								result = dialog_edit_module.exec_()
								if result == QDialog.Accepted:
										msgBox = QMessageBox()
										msgBox.setText("Deleting axes")
										msgBox.setInformativeText("Do you want to delete the axes?")
										msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
										msgBox.setDefaultButton(QMessageBox.Yes)
										ret = msgBox.exec_()
										if ret == QMessageBox.Yes:
												selected_axes_detail = dialog_edit_module.get_selected_axes()
												plot_detail_id = selected_axes_detail[0]
												self.database_management.delete_axesdetails(plot_detail_id)
												self.update_selected_modules()
												self.listview_templates_clicked()
				else:
						logger.info("Please select template first")

		def add_listdetails(self):
				item_selection_model = self.listview_templates.selectionModel()
				if len(item_selection_model.selectedIndexes()) != 0:
						selected_row = item_selection_model.selectedIndexes()[6]

						row = self.listview_templates_proxy_model.mapToSource(selected_row)
						template = self.listview_templates_proxy_model.sourceModel().itemFromIndex(row)

						template_id = template.text()
						dialog_add_groups = FrmAddListDetails(template_id)
						result = dialog_add_groups.exec_()
						self.update_selected_modules()
						self.listview_templates_clicked()
				else:
						logger.info("Please select template first")

		def edit_listdetails(self):
				item_selection_model = self.listview_templates.selectionModel()
				if len(item_selection_model.selectedIndexes()) != 0:
						selected_row = item_selection_model.selectedIndexes()[6]

						row = self.listview_templates_proxy_model.mapToSource(selected_row)
						template = self.listview_templates_proxy_model.sourceModel().itemFromIndex(row)

						template_id = template.text()
						dialog_edit_groups = FrmEditListDetails(template_id)
						if dialog_edit_groups.user_cancelled != True:
								result = dialog_edit_groups.exec_()
								self.update_selected_modules()
								self.listview_templates_clicked()
				else:
						logger.info("Please select template first")

		def copy_list_details(self):
				item_selection_model = self.listview_templates.selectionModel()
				if len(item_selection_model.selectedIndexes()) != 0:
						selected_row = item_selection_model.selectedIndexes()[6]

						row = self.listview_templates_proxy_model.mapToSource(selected_row)
						template = self.listview_templates_proxy_model.sourceModel().itemFromIndex(row)

						template_id = template.text()
						dialog_edit_list = FrmCopyGroupDetails(template_id)
						if dialog_edit_list.user_cancelled != True:
								result = dialog_edit_list.exec_()
								self.update_selected_modules()
								self.listview_templates_clicked()
				else:
						logger.info("Please select template first")

		def delete_listdetails(self):
				item_selection_model = self.listview_templates.selectionModel()
				if len(item_selection_model.selectedIndexes()) != 0:
						selected_row = item_selection_model.selectedIndexes()[6]

						row = self.listview_templates_proxy_model.mapToSource(selected_row)
						template = self.listview_templates_proxy_model.sourceModel().itemFromIndex(row)

						template_id = template.text()
						group_details = self.database_management.select_list_details_by_module_id(template_id)
						if len(group_details) != 0:
								dialog_delete_module = FrmShowGroupList(group_details)
								result = dialog_delete_module.exec_()
								if result == QDialog.Accepted:
										msgBox = QMessageBox()
										msgBox.setText("Deleting group")
										msgBox.setInformativeText("Do you want to delete the group?")
										msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
										msgBox.setDefaultButton(QMessageBox.Yes)
										ret = msgBox.exec_()
										if ret == QMessageBox.Yes:
												selected_group_detail = dialog_delete_module.get_selected_group()
												list_detail_id = selected_group_detail[0]
												self.database_management.delete_listdetails(list_detail_id)
												self.update_selected_modules()
												self.listview_templates_clicked()
				else:
						logger.info("Please select template first")

		def add_edit_signals(self):
				item_selection_model = self.listview_templates.selectionModel()
				if len(item_selection_model.selectedIndexes()) != 0:
						selected_row_id = item_selection_model.selectedIndexes()[6]
						selected_row_type = item_selection_model.selectedIndexes()[5]

						row_id = self.listview_templates_proxy_model.mapToSource(selected_row_id)
						row_type = self.listview_templates_proxy_model.mapToSource(selected_row_type)

						template_id = self.listview_templates_proxy_model.sourceModel().itemFromIndex(row_id)
						template_type = self.listview_templates_proxy_model.sourceModel().itemFromIndex(row_type)

						template_id = template_id.text()
						template_type = template_type.text()

						if template_type == "List":
								details = self.database_management.select_list_details_by_module_id(template_id)
								if len(details) != 0:
										dialog_edit_module = FrmShowGroupList(details)
										result = dialog_edit_module.exec_()
										if result == QDialog.Accepted:
												selected_group_detail = dialog_edit_module.get_selected_group()
												list_detail_id = selected_group_detail[0]
												signals = self.database_management.select_list_signal_details_by_list_id(list_detail_id)
												signal_dict = {}
												for signal in signals:
														new_signal = {}
														new_signal["ID"] = signal[0]
														new_signal["Label"] = signal[1]
														new_signal["Offset"] = signal[2]
														new_signal["Factor"] = signal[3]
														new_signal["DisplayScaled"] = signal[4]
														new_signal["Unit"] = signal[5]
														new_signal["AliasName"] = signal[6]
														new_signal["DeviceName"] = signal[7]
														new_signal["SignalName"] = signal[8]
														new_signal["IsCustomExpression"] = signal[9]
														new_signal["CustomExpression"] = signal[10]
														new_signal["CustomExpressionSignalList"] = signal[11]
														signal_dict[str(new_signal["ID"])] = new_signal
												original_signal_dict = copy.deepcopy(signal_dict)
												obj_add_edit_signals = FrmAddEditSignals(self.control, signal_dict)
												result = obj_add_edit_signals.exec_()
												self.database_management.update_list_signal_details(list_detail_id,
																																						obj_add_edit_signals.signals,
																																						original_signal_dict)
												self.update_selected_modules()
												self.listview_templates_clicked()
								else:
										logger.warning("Please add axes first to add signals")

						elif template_type == "Plot":
								details = self.database_management.select_plot_details_by_module_id(template_id)
								if len(details) != 0:
										dialog_edit_module = FrmShowAxesList(details)
										result = dialog_edit_module.exec_()
										if result == QDialog.Accepted:
												selected_axes_detail = dialog_edit_module.get_selected_axes()
												plot_detail_id = selected_axes_detail[0]
												signals = self.database_management.select_plot_signal_details_by_plot_id(plot_detail_id)
												signal_dict = {}
												for signal in signals:
														new_signal = {}
														new_signal["ID"] = signal[0]
														new_signal["Label"] = signal[1]
														new_signal["Offset"] = signal[2]
														new_signal["Factor"] = signal[3]
														new_signal["DisplayScaled"] = signal[4]
														new_signal["Unit"] = signal[5]
														new_signal["AliasName"] = signal[6]
														new_signal["DeviceName"] = signal[7]
														new_signal["SignalName"] = signal[8]
														new_signal["IsCustomExpression"] = signal[9]
														new_signal["CustomExpression"] = signal[10]
														new_signal["CustomExpressionSignalList"] = signal[11]
														signal_dict[str(new_signal["ID"])] = new_signal
												original_signal_dict = copy.deepcopy(signal_dict)
												# print("Prining Original signals")
												# print(original_signal_dict)
												obj_add_edit_signals = FrmAddEditSignals(self.control, signal_dict)
												result = obj_add_edit_signals.exec_()
												# print("Prining Changed signals")
												# print(obj_add_edit_signals.signals)
												self.database_management.update_plot_signal_details(plot_detail_id,
																																						obj_add_edit_signals.signals,
																																						original_signal_dict)
												self.update_selected_modules()
												self.listview_templates_clicked()
								else:
										logger.warning("Please add axes first to add signals")

				else:
						logger.info("Please select template first")

		def search_text_changed(self):
				text = self.template_name.text()
				search_type = QtCore.QRegExp.FixedString
				match_type = QtCore.Qt.CaseInsensitive

				if self.pbutton_template_filter_match_case.isChecked():
						match_type = QtCore.Qt.CaseSensitive

				self.listview_templates_proxy_model.setFilterRegExp(QtCore.QRegExp(text, match_type, search_type))
				self.listview_templates_proxy_model.setFilterKeyColumn(0)
				return

		def clear_filter(self):
				self.template_name.clear()
				self.search_text_changed()
				self.listview_templates_proxy_model.sort(1)

		def update_model(self):
				if self.listview_templates_model.hasChildren():
						self.listview_templates_model.removeRows(0, self.listview_templates_model.rowCount())

				root_node = self.listview_templates_model.invisibleRootItem()

				modules = self.database_management.select_all_modules()

				for module in modules:
						item_name = QStandardItem(module[1])
						item_name.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'module_24.png')))
						item_name.setEditable(False)
						item_description = QStandardItem(module[2])
						item_description.setEditable(False)
						item_author = QStandardItem(module[3])
						item_author.setEditable(False)
						item_revision = QStandardItem(module[4])
						item_revision.setEditable(False)

						item_date = QStandardItem(module[5])
						item_date.setEditable(False)

						module_type = self.database_management.select_type_by_id(module[9])
						if module_type is not None:
								item_module_type = QStandardItem(module_type[0])
								item_module_type.setEditable(False)
						else:
								item_module_type = QStandardItem(module_type[0])
								item_module_type.setEditable(False)

						item_id = QStandardItem(str(module[0]))
						item_id.setEditable(False)
						root_node.appendRow(
										[item_name, item_description, item_author, item_revision, item_date, item_module_type, item_id])
				# self.listview_templates.setCurrentIndex(0)
				self.listview_templates.setColumnWidth(6, 2000)
				self.listview_templates_proxy_model.sort(0)


class FrmAddTemplate(QDialog):
		DatabaseManagement.db_file_path = DATABASE_PATH
		database_management = DatabaseManagement()

		def __init__(self):
				super(FrmAddTemplate, self).__init__()
				self.setWindowIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'add_24.png')))
				self.setModal(True)
				# self.setMinimumSize(300, 350)
				# self.setMaximumSize(300, 350)
				self.center()
				self.setWindowTitle("Add New Template ")
				group_box_module_summary = QGroupBox(" ")
				form_layout_module_summary = QFormLayout()

				self.module_name = QLineEdit()
				self.module_name.setToolTip("Set module name")
				self.module_name.textChanged[str].connect(self.onChanged)
				form_layout_module_summary.addRow(QLabel("(*) Name:"), self.module_name)
				self.module_name_lbl = QLabel(self)
				form_layout_module_summary.addRow(QLabel(" "), self.module_name_lbl)

				self.description = QPlainTextEdit()
				self.description.setToolTip("Set description of module")
				form_layout_module_summary.addRow(QLabel("Description:"), self.description)

				self.combo_type_id = QComboBox()
				type_list = []
				rows = self.database_management.select_all_type_info()
				for row in rows:
						type_list.append(str(row[1]))
				self.combo_type_id.addItems(type_list)
				self.combo_type_id.setCurrentIndex(0)
				self.combo_type_id.currentIndexChanged[str].connect(self.onItemChanged)
				self.combo_type_id.setToolTip("Select module type")
				form_layout_module_summary.addRow(QLabel("Type:"), self.combo_type_id)

				self.txt_geometry_row = QLineEdit()
				self.txt_geometry_col = QLineEdit()
				self.txt_geometry_row.setToolTip("Set Geometry Row, Only applicable for Plots")
				self.txt_geometry_col.setToolTip("Set Geometry Column, Only applicable for Plots")
				form_layout_module_summary.addRow(QLabel("Geometry (Row):"), self.txt_geometry_row)
				form_layout_module_summary.addRow(QLabel("Geometry (Column):"), self.txt_geometry_col)

				group_box_module_summary.setLayout(form_layout_module_summary)

				group_box_module_image = QGroupBox("")
				form_layout_module_image = QFormLayout()
				self.img_btn = QPushButton('Select Image')
				self.img_btn.setToolTip("Select image")
				self.img_btn.clicked.connect(self.get_image_file)
				self.labelImage = QLabel()
				form_layout_module_image.addRow(self.img_btn)
				form_layout_module_image.addRow(self.labelImage)

				group_box_module_image.setLayout(form_layout_module_image)

				button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
				button_box.accepted.connect(self.store)
				button_box.rejected.connect(self.cancel)

				main_layout = QVBoxLayout()
				main_layout.setSpacing(0)
				main_layout.setContentsMargins(1, 1, 1, 1)
				main_layout.addWidget(group_box_module_summary)
				main_layout.addWidget(group_box_module_image)
				main_layout.addWidget(button_box)
				self.setLayout(main_layout)
				self.setTabOrder(self.module_name, self.description)
				self.setTabOrder(self.description, self.img_btn)

		def onChanged(self, text):

				if text.strip() == "":
						self.module_name_lbl.setText("need user input for module name")
						self.module_name_lbl.setStyleSheet('color: red;')
						logger.info("Please input module name")
						return
				self.module_name_lbl.setText(" ")

		def onItemChanged(self,text):
				if text.strip()!= "List":
						self.txt_geometry_row.setEnabled(True)
						self.txt_geometry_col.setEnabled(True)
				else:
						self.txt_geometry_row.setEnabled(False)
						self.txt_geometry_col.setEnabled(False)

		def center(self):
				qr = self.frameGeometry()
				cp = QDesktopWidget().availableGeometry().center()
				qr.moveCenter(cp)
				self.move(qr.topLeft())

		def get_image_file(self):
				file_name, _ = QFileDialog.getOpenFileName(self, 'Open Image File', r"<Default dir>",
																									 "Image files (*.jpg *.jpeg *.png)")
				self.labelImage.setText(file_name)

		def store(self):
				if self.module_name.text().strip() == "":
						self.module_name_lbl.setText("Please provide module name")
						self.module_name_lbl.setStyleSheet('color: red;')
						logger.warning("Please provide different module name")
						return

				check_if_module_with_same_name_exists = self.database_management.select_module_by_name(
						self.module_name.text().strip())
				if check_if_module_with_same_name_exists is None:
						import getpass
						author_name = getpass.getuser()
						date = datetime.datetime.now()
						revision = "1.0"

						type_info = self.database_management.select_id_by_type(self.combo_type_id.currentText())

						self.database_management.create_module(self.module_name.text().strip(), self.description.toPlainText(),
																									 author_name,
																									 date, self.labelImage.text(), type_info[0], revision,
																									 self.txt_geometry_row.text().strip(),
																									 self.txt_geometry_col.text().strip())
						logger.info("Added " + self.module_name.text() + " template successfully")
						self.close()
				else:
						self.module_name_lbl.setText("Module with same name exists, Please provide different module name")
						self.module_name_lbl.setStyleSheet('color: red;')
						logger.warning("Module with same name exists, Please provide different module name")
						return

		def cancel(self):
				self.close()


class FrmEditTemplate(QDialog):
		DatabaseManagement.db_file_path = DATABASE_PATH
		database_management = DatabaseManagement()

		def __init__(self, module_id):
				super(FrmEditTemplate, self).__init__()

				self.module_id = module_id
				self.setWindowIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'edit_24.png')))
				self.setModal(True)
				# self.setMinimumSize(300, 350)
				# self.setMaximumSize(300, 350)
				self.center()

				template_details = self.database_management.select_module_by_id(module_id)
				geometry_row, geometry_col = eval(template_details[8])
				self.setWindowTitle("Edit Module ")

				group_box_module = QGroupBox(" ")
				form_layout_module = QFormLayout()

				self.label_type_id = QLabel()
				self.type_id = template_details[9]
				self.type_info = self.database_management.select_type_by_id(self.type_id)
				self.label_type_id.setText(self.type_info[0])
				self.label_type_id.setToolTip("Module type")


				form_layout_module.addRow(QLabel("Module Type:"), self.label_type_id)
				group_box_module.setLayout(form_layout_module)

				group_box_module_summary = QGroupBox("")
				form_layout_module_summary = QFormLayout()
				self.module_name = QLineEdit()
				self.module_name.setText(template_details[1])
				self.module_name.setToolTip("Set module name")
				self.module_name.textChanged[str].connect(self.onChanged)
				form_layout_module_summary.addRow(QLabel("Name:"), self.module_name)
				self.module_name_lbl = QLabel(self)
				form_layout_module_summary.addRow(QLabel(" "), self.module_name_lbl)

				self.description = QPlainTextEdit()
				self.description.setPlainText(template_details[2])
				self.description.setToolTip("Set description of module")
				form_layout_module_summary.addRow(QLabel("Module Description:"), self.description)

				self.txt_geometry_row = QLineEdit()
				self.txt_geometry_col = QLineEdit()
				self.txt_geometry_row.setText(str(geometry_row))
				self.txt_geometry_col.setText(str(geometry_col))
				self.txt_geometry_row.setToolTip("Set Geometry Row, Only applicable for Plots")
				self.txt_geometry_col.setToolTip("Set Geometry Column, Only applicable for Plots")
				form_layout_module_summary.addRow(QLabel("Geometry (Row):"), self.txt_geometry_row)
				form_layout_module_summary.addRow(QLabel("Geometry (Column):"), self.txt_geometry_col)

				if self.label_type_id.text().strip() != "List":
						self.txt_geometry_row.setEnabled(True)
						self.txt_geometry_col.setEnabled(True)
				else:
						self.txt_geometry_row.setEnabled(False)
						self.txt_geometry_col.setEnabled(False)

				group_box_module_summary.setLayout(form_layout_module_summary)
				group_box_module_image = QGroupBox("")
				form_layout_module_image = QFormLayout()
				self.img_btn = QPushButton('Select Image')
				self.img_btn.setToolTip("select image respective of module")
				self.img_btn.clicked.connect(self.get_image_file)

				self.labelImage = QLabel()
				form_layout_module_image.addRow(self.img_btn)
				form_layout_module_image.addRow(self.labelImage)
				group_box_module_image.setLayout(form_layout_module_image)

				button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
				button_box.accepted.connect(self.store)
				button_box.rejected.connect(self.cancel)

				main_layout = QVBoxLayout()
				main_layout.setSpacing(0)
				main_layout.setContentsMargins(1, 1, 1, 1)
				main_layout.addWidget(group_box_module)
				main_layout.addWidget(group_box_module_summary)
				main_layout.addWidget(group_box_module_image)
				main_layout.addWidget(button_box)
				self.setLayout(main_layout)
				self.setTabOrder(self.module_name, self.description)
				self.setTabOrder(self.description, self.img_btn)

				self.revision = float(template_details[4])

		def onChanged(self, text):
				if text == "":
						self.module_name_lbl.setText("need user input for module name")
						self.module_name_lbl.setStyleSheet('color: red;')
						logger.info("Please input module name")
						return
				self.module_name_lbl.setText(" ")

		def center(self):
				qr = self.frameGeometry()
				cp = QDesktopWidget().availableGeometry().center()
				qr.moveCenter(cp)
				self.move(qr.topLeft())

		def get_image_file(self):
				file_name, _ = QFileDialog.getOpenFileName(self, 'Open Image File', r"<Default dir>",
																									 "Image files (*.jpg *.jpeg *.png)")
				self.labelImage.setText(file_name)

		def store(self):
						if self.module_name.text().strip() == "":
								self.module_name_lbl.setText("Please provide module name")
								self.module_name_lbl.setStyleSheet('color: red;')
								logger.info("Please provide module name")
								return

						import getpass
						author_name = getpass.getuser()
						date = datetime.datetime.now()
						import math
						fractional, whole = math.modf(self.revision)

						if fractional > 0.20:
								revision = self.revision + 1
						else:
								revision = self.revision + 0.1
						self.database_management.update_module(self.module_id, self.module_name.text().strip(),
																									 self.description.toPlainText(),
																									 author_name, date, self.labelImage.text(), self.type_id,
																									 revision, self.txt_geometry_row.text(), self.txt_geometry_col.text())
						logger.info("Module updated successfully")
						self.close()

		def cancel(self):
				self.close()


class FrmAddAxesDetails(QDialog):
		DatabaseManagement.db_file_path = DATABASE_PATH
		database_management = DatabaseManagement()

		def __init__(self, module_id):
				super(FrmAddAxesDetails, self).__init__()

				self.module_id = module_id
				self.setWindowIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'add_1_24.png')))
				self.setModal(True)
				# self.setMinimumSize(300, 350)
				# self.setMaximumSize(300, 350)
				self.center()

				self.setWindowTitle("Add Axes Details ")
				group_box_module = QGroupBox("")
				form_layout_module = QFormLayout()
				self.module_info = self.database_management.select_module_by_id(self.module_id)
				self.geometry_row, self.geometry_column = eval(self.module_info[8])
				self.label_module_name = QLabel()
				self.label_module_name.setText(self.module_info[1])
				form_layout_module.addRow(QLabel("Selected Module:"), self.label_module_name)
				group_box_module.setLayout(form_layout_module)

				group_box_plotdetails = QGroupBox("")
				form_layout_plotdetails = QFormLayout()
				self.axes_name = QLineEdit()
				self.axes_name.setToolTip("Provide Axes Name")
				self.axes_name.textChanged[str].connect(self.onChanged)
				form_layout_plotdetails.addRow(QLabel("(*) Name:"), self.axes_name)

				self.xlabel = QLineEdit()
				self.xlabel.setToolTip("Provide X-Axis Label")
				form_layout_plotdetails.addRow(QLabel("X-Axis Label:"), self.xlabel)

				self.ylabel = QLineEdit()
				self.ylabel.setToolTip("Provide Y-Axis Label")
				form_layout_plotdetails.addRow(QLabel("Y-Axis Label:"), self.ylabel)

				self.yticks = QPlainTextEdit()
				self.yticks.setToolTip("Provide Y-ticks Labels in dictionary format e.g {0:'POINT', 1:'CAR', 2:'TRUCK', 3:'PEDESTRIAN', 4:'MOTORCYCLE', 5:'BICYCLE'}")
				form_layout_plotdetails.addRow(QLabel("Y-Ticks Labels:"), self.yticks)

				self.rownumber = QSpinBox(self)
				self.rownumber.setMinimum(1)
				self.rownumber.setMaximum(self.geometry_row)
				self.rownumber.setToolTip("Provide Row Position")
				form_layout_plotdetails.addRow(QLabel("Row Position:"), self.rownumber)

				self.columnnumber = QSpinBox(self)
				self.columnnumber.setMinimum(1)
				self.columnnumber.setMaximum(self.geometry_column)
				self.columnnumber.setToolTip("Provide Column Position")
				form_layout_plotdetails.addRow(QLabel("Column Position:"), self.columnnumber)
				self.axes_name_lbl = QLabel(self)
				form_layout_plotdetails.addRow(QLabel(" "), self.axes_name_lbl)
				if self.geometry_row != 0 or self.geometry_column != 0:
						self.rownumber.setEnabled(True)
						self.columnnumber.setEnabled(True)
				else:
						self.rownumber.setEnabled(False)
						self.columnnumber.setEnabled(False)
				group_box_plotdetails.setLayout(form_layout_plotdetails)
				button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
				button_box.accepted.connect(self.store)
				button_box.rejected.connect(self.cancel)

				main_layout = QVBoxLayout()
				main_layout.addWidget(group_box_module)
				main_layout.addWidget(group_box_plotdetails)
				main_layout.addWidget(button_box)
				self.setLayout(main_layout)

				self.setTabOrder(self.axes_name, self.xlabel)
				self.setTabOrder(self.xlabel, self.ylabel)
				self.setTabOrder(self.ylabel, self.yticks)
				self.setTabOrder(self.yticks, self.rownumber)
				self.setTabOrder(self.rownumber, self.columnnumber)

		def onChanged(self, text):
				if text == "":
						self.axes_name_lbl.setText("need user input for axes name")
						self.axes_name_lbl.setStyleSheet('color: red;')
						logger.info("Please input axes name")
						return
				self.axes_name_lbl.setText(" ")

		def center(self):
				qr = self.frameGeometry()
				cp = QDesktopWidget().availableGeometry().center()
				qr.moveCenter(cp)
				self.move(qr.topLeft())

		def store(self):
				if self.axes_name.text().strip() == "":
						self.axes_name_lbl.setText("Please provide axes name")
						self.axes_name_lbl.setStyleSheet('color: red;')
						logger.info("Please provide axes name")
						return

				if self.geometry_row != 0 or self.geometry_column != 0:
						if self.rownumber.text().strip() != "":
								if not self.rownumber.text().strip().isnumeric():
										self.axes_name_lbl.setText("Please provide row number")
										self.axes_name_lbl.setStyleSheet('color: red;')
										logger.info("Please provide row number")
										return
								if not int(self.rownumber.text().strip()) > 0:
										self.axes_name_lbl.setText("Please provide row number >= 1")
										self.axes_name_lbl.setStyleSheet('color: red;')
										logger.info("Please provide row number >= 1")
										return

						if self.columnnumber.text().strip() != "":
								if not self.columnnumber.text().strip().isnumeric():
										self.axes_name_lbl.setText("Please provide column number")
										self.axes_name_lbl.setStyleSheet('color: red;')
										logger.info("Please provide column number")
										return
								if not int(self.columnnumber.text().strip()) > 0:
										self.axes_name_lbl.setText("Please provide column number >= 1")
										self.axes_name_lbl.setStyleSheet('color: red;')
										logger.info("Please provide column number >= 1")
										return
				self.database_management.create_axesdetails(self.axes_name.text().strip(), self.xlabel.text(),
																										self.ylabel.text(), self.yticks.toPlainText(),
																										self.rownumber.text(), self.columnnumber.text(),
																										self.module_id)
				logger.info("Axes details added successfully")
				self.close()

		def cancel(self):
				self.close()


class FrmEditAxesDetails(QDialog):
		DatabaseManagement.db_file_path = DATABASE_PATH
		database_management = DatabaseManagement()

		def __init__(self, module_id):
				super(FrmEditAxesDetails, self).__init__()

				self.module_id = module_id
				self.setWindowIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'edit_1_24.png')))
				self.setModal(True)
				# self.setMinimumSize(350, 350)
				# self.setMaximumSize(350, 350)
				self.center()
				self.user_cancelled = False
				axes_details = self.database_management.select_plot_details_by_module_id(self.module_id)
				if len(axes_details) != 0:
						dialog_edit_module = FrmShowAxesList(axes_details)
						result = dialog_edit_module.exec_()
						if result == QDialog.Accepted:
								selected_axes_detail = dialog_edit_module.get_selected_axes()
								self.plot_detail_id = selected_axes_detail[0]
								plot_detail_axes_name = selected_axes_detail[1]
								plot_detail_xlabel = selected_axes_detail[2]
								plot_detail_ylabel = selected_axes_detail[3]
								plot_detail_yticks = selected_axes_detail[4]
								plot_detail_row_number = selected_axes_detail[5]
								plot_detail_column_number = selected_axes_detail[6]

								group_box_module = QGroupBox("")
								form_layout_module = QFormLayout()

								self.module_info = self.database_management.select_module_by_id(self.module_id)
								self.geometry_row, self.geometry_column = eval(self.module_info[8])
								form_layout_module.addRow(QLabel("Selected Module:" + self.module_info[1]))
								form_layout_module.addRow(QLabel("Selected Axes:" + plot_detail_axes_name))
								group_box_module.setLayout(form_layout_module)

								self.setWindowTitle("Edit Axes Details " + self.module_info[1] + "-" + plot_detail_axes_name)
								group_box_plotdetails = QGroupBox("")
								form_layout_plotdetails = QFormLayout()
								self.axes_name = QLineEdit()
								self.axes_name.setText(plot_detail_axes_name)
								self.axes_name.textChanged[str].connect(self.onChanged)
								form_layout_plotdetails.addRow(QLabel("(*) Name:"), self.axes_name)


								self.xlabel = QLineEdit()
								self.xlabel.setText(plot_detail_xlabel)
								self.xlabel.setToolTip("Provide X-Axis Label")
								form_layout_plotdetails.addRow(QLabel("X-Axis Label:"), self.xlabel)

								self.ylabel = QLineEdit()
								self.ylabel.setText(plot_detail_ylabel)
								self.ylabel.setToolTip("Provide Y-Axis Label")
								form_layout_plotdetails.addRow(QLabel("Y-Axis Label:"), self.ylabel)

								self.yticks = QPlainTextEdit()
								self.yticks.setPlainText(plot_detail_yticks)
								self.yticks.setToolTip("Provide Y-ticks Labels in dictionary format e.g. {0:'POINT', 1:'CAR', 2:'TRUCK', 3:'PEDESTRIAN', 4:'MOTORCYCLE', 5:'BICYCLE'}")
								form_layout_plotdetails.addRow(QLabel("Y-Ticks Labels:"), self.yticks)



								self.rownumber = QSpinBox(self)
								self.rownumber.setMinimum(1)
								self.rownumber.setMaximum(self.geometry_row)
								self.rownumber.setValue(plot_detail_row_number)
								self.rownumber.setAlignment(Qt.AlignRight)
								self.rownumber.setToolTip("Provide Row Position")
								form_layout_plotdetails.addRow(QLabel("Row Position:"), self.rownumber)

								self.columnnumber = QSpinBox(self)
								self.columnnumber.setMinimum(1)
								self.columnnumber.setMaximum(self.geometry_column)
								self.columnnumber.setValue(plot_detail_column_number)
								self.columnnumber.setAlignment(Qt.AlignRight)
								self.columnnumber.setToolTip("Provide Column Position")
								form_layout_plotdetails.addRow(QLabel("Column Position:"), self.columnnumber)
								if self.geometry_row != 0 or self.geometry_column != 0:
										self.rownumber.setEnabled(True)
										self.columnnumber.setEnabled(True)
								else:
										self.rownumber.setEnabled(False)
										self.columnnumber.setEnabled(False)
								self.axes_name_lbl = QLabel(self)
								form_layout_plotdetails.addRow(QLabel(" "), self.axes_name_lbl)
								group_box_plotdetails.setLayout(form_layout_plotdetails)
								button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
								button_box.accepted.connect(self.store)
								button_box.rejected.connect(self.reject)

								main_layout = QVBoxLayout()
								main_layout.addWidget(group_box_module)
								main_layout.addWidget(group_box_plotdetails)
								main_layout.addWidget(button_box)
								self.setLayout(main_layout)

								self.setTabOrder(self.axes_name, self.xlabel)
								self.setTabOrder(self.xlabel, self.ylabel)
								self.setTabOrder(self.ylabel, self.yticks)
								self.setTabOrder(self.yticks, self.rownumber)
								self.setTabOrder(self.rownumber, self.columnnumber)
						else:
								self.user_cancelled = True
				else:
						self.user_cancelled = True
						logger.warning("No axes available for update, Please add one")

		def onChanged(self, text):
				if text == "":
						self.axes_name_lbl.setText("need user input for axes name")
						self.axes_name_lbl.setStyleSheet('color: red;')
						logger.info("Please input axes name")
						return
				self.axes_name_lbl.setText(" ")

		def center(self):
				qr = self.frameGeometry()
				cp = QDesktopWidget().availableGeometry().center()
				qr.moveCenter(cp)
				self.move(qr.topLeft())

		def store(self):
				if self.axes_name.text().strip() == "":
						self.axes_name_lbl.setText("Please provide axes name")
						self.axes_name_lbl.setStyleSheet('color: red;')
						logger.info("Please provide axes name")
						return

				if self.rownumber.text().strip() != "":
						if not self.rownumber.text().strip().isnumeric():
								self.axes_name_lbl.setText("Please provide row number")
								self.axes_name_lbl.setStyleSheet('color: red;')
								logger.info("Please provide row number")
								return
						if not int(self.rownumber.text().strip()) > 0:
								self.axes_name_lbl.setText("Please provide row number >= 1")
								self.axes_name_lbl.setStyleSheet('color: red;')
								logger.info("Please provide row number >= 1")
								return

				if self.columnnumber.text().strip() != "":
						if not self.columnnumber.text().strip().isnumeric():
								self.axes_name_lbl.setText("Please provide column number")
								self.axes_name_lbl.setStyleSheet('color: red;')
								logger.info("Please provide column number")
								return
						if not int(self.columnnumber.text().strip()) > 0:
								self.axes_name_lbl.setText("Please provide column number >= 1")
								self.axes_name_lbl.setStyleSheet('color: red;')
								logger.info("Please provide column number >= 1")
								return

				self.database_management.update_axesdetails(self.axes_name.text().strip(), self.xlabel.text(),
																										self.ylabel.text(), self.yticks.toPlainText(),
																										self.rownumber.text(), self.columnnumber.text(),
																										self.plot_detail_id)
				logger.info("Axes details updated successfully")
				self.accept()


class FrmShowAxesList(QDialog):

		def __init__(self, axes_list):
				super(FrmShowAxesList, self).__init__()
				self.setWindowTitle("Select axes for modification")

				self.setWindowIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'edit_1_24.png')))
				self.setModal(True)

				self.selected_items = []
				vbox_axes_selection = QVBoxLayout(self)

				self.combo_box_selected_axes = QComboBox()
				for axes_detail in axes_list:
						self.combo_box_selected_axes.addItem(str(axes_detail[1]), axes_detail)
				vbox_axes_selection.addWidget(self.combo_box_selected_axes)

				button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
				button_box.accepted.connect(self.accept)
				button_box.rejected.connect(self.reject)

				vbox_axes_selection.addWidget(button_box)

				self.setLayout(vbox_axes_selection)
				# self.setMinimumSize(300, 80)
				# self.setMaximumSize(300, 80)
				self.center()

		def get_selected_axes(self):
				return self.combo_box_selected_axes.itemData(self.combo_box_selected_axes.currentIndex())

		def center(self):
				qr = self.frameGeometry()
				cp = QDesktopWidget().availableGeometry().center()
				qr.moveCenter(cp)
				self.move(qr.topLeft())


class FrmAddListDetails(QDialog):
		DatabaseManagement.db_file_path = DATABASE_PATH
		database_management = DatabaseManagement()

		def __init__(self, module_id):
				super(FrmAddListDetails, self).__init__()
				self.module_id = module_id
				self.setWindowIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'add_2_24.png')))
				self.setModal(True)
				# self.setMinimumSize(300, 180)
				# self.setMaximumSize(300, 180)
				self.center()

				self.setWindowTitle("Add List Details ")

				group_box_module = QGroupBox("")
				form_layout_module = QFormLayout()
				module_info = self.database_management.select_module_by_id(self.module_id)
				form_layout_module.addRow(QLabel("Selected Module: " + module_info[1]))
				group_box_module.setLayout(form_layout_module)

				group_box_listdetails = QGroupBox("")
				form_layout_listdetails = QFormLayout()
				self.group_name = QLineEdit()
				self.group_name.setToolTip("set group name")
				self.group_name.textChanged[str].connect(self.onChanged)
				form_layout_listdetails.addRow(QLabel("(*) List Group Name:"), self.group_name)
				self.group_name_lbl = QLabel(self)
				form_layout_listdetails.addRow(QLabel(" "), self.group_name_lbl)

				self.color = QLineEdit()
				self.color.setToolTip("selected color")
				self.background_color = QPushButton('Open Color Dialog', self)
				self.background_color.setToolTip('Opens color dialog')
				self.background_color.move(10, 10)
				self.background_color.clicked.connect(self.open_color_dialog)
				form_layout_listdetails.addRow(QLabel("List Background Color:"), self.background_color)
				form_layout_listdetails.addRow(QLabel(""), self.color)

				group_box_listdetails.setLayout(form_layout_listdetails)
				button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
				button_box.accepted.connect(self.store)
				button_box.rejected.connect(self.reject)

				main_layout = QVBoxLayout()
				main_layout.addWidget(group_box_module)
				main_layout.addWidget(group_box_listdetails)
				main_layout.addWidget(button_box)
				self.setLayout(main_layout)
				self.setTabOrder(self.background_color, self.color)

		def onChanged(self, text):
				if text == "":
						self.group_name_lbl.setText("need user input for group name")
						self.group_name_lbl.setStyleSheet('color: red;')
						logger.info("Please input group name")
						return
				self.group_name_lbl.setText(" ")

		def center(self):
				qr = self.frameGeometry()
				cp = QDesktopWidget().availableGeometry().center()
				qr.moveCenter(cp)
				self.move(qr.topLeft())

		def open_color_dialog(self):
				color = QColorDialog.getColor()

				if color.isValid():
						self.color.setText(color.name())

		def store(self):
				if self.group_name.text().strip() == "":
						self.group_name_lbl.setText("Please provide group name")
						self.group_name_lbl.setStyleSheet('color: red;')
						logger.info("Please provide group name")
						return
				self.database_management.create_listdetails(self.group_name.text().strip(), self.color.text(), self.module_id)
				logger.info("List details added successfully")
				self.accept()


class FrmEditListDetails(QDialog):
		DatabaseManagement.db_file_path = DATABASE_PATH
		database_management = DatabaseManagement()

		def __init__(self, module_id):
				super(FrmEditListDetails, self).__init__()

				self.module_id = module_id
				self.setWindowIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'edit_3_24.png')))
				self.setModal(True)
				# self.setMinimumSize(300, 210)
				# self.setMaximumSize(300, 210)
				self.center()
				self.user_cancelled = False
				list_details = self.database_management.select_list_details_by_module_id(self.module_id)
				if len(list_details) != 0:
						dialog_edit_module = FrmShowGroupList(list_details)
						result = dialog_edit_module.exec_()
						if result == QDialog.Accepted:
								selected_group_detail = dialog_edit_module.get_selected_group()
								self.list_detail_id = selected_group_detail[0]
								list_detail_group_name = selected_group_detail[1]
								list_detail_background_color = selected_group_detail[2]

								group_box_module = QGroupBox("")
								form_layout_module = QFormLayout()

								module_info = self.database_management.select_module_by_id(self.module_id)
								form_layout_module.addRow(QLabel("Selected Module: " + module_info[1]))
								form_layout_module.addRow(QLabel("Selected Group: " + list_detail_group_name))
								group_box_module.setLayout(form_layout_module)

								self.setWindowTitle("Edit Group Details " + module_info[1] + "-" + list_detail_group_name)
								group_box_listdetails = QGroupBox("")
								form_layout_listdetails = QFormLayout()
								self.group_name = QLineEdit()
								self.group_name.setText(list_detail_group_name)
								self.group_name.setToolTip(("Set Group Name"))
								self.group_name.textChanged[str].connect(self.onChanged)
								form_layout_listdetails.addRow(QLabel("(*) List Group Name:"), self.group_name)
								self.group_name_lbl = QLabel(self)
								form_layout_listdetails.addRow(QLabel(" "), self.group_name_lbl)

								self.color = QLineEdit()
								self.color.setToolTip("selected color")
								self.color.setText(list_detail_background_color)
								self.background_color = QPushButton('Open Color Dialog', self)
								self.background_color.setToolTip('Opens color dialog')
								self.background_color.move(10, 10)
								self.background_color.clicked.connect(self.open_color_dialog)
								form_layout_listdetails.addRow(QLabel("List Background Color:"), self.background_color)
								form_layout_listdetails.addRow(QLabel(""), self.color)

								group_box_listdetails.setLayout(form_layout_listdetails)
								button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
								button_box.accepted.connect(self.store)
								button_box.rejected.connect(self.reject)

								main_layout = QVBoxLayout()
								main_layout.addWidget(group_box_module)
								main_layout.addWidget(group_box_listdetails)
								main_layout.addWidget(button_box)
								self.setLayout(main_layout)

								self.setTabOrder(self.group_name, self.background_color)
						else:
								self.user_cancelled = True
				else:
						self.user_cancelled = True
						logger.warning("No group available for update, Please add one")

		def onChanged(self, text):
				if text == "":
						self.group_name_lbl.setText("need user input for group name")
						self.group_name_lbl.setStyleSheet('color: red;')
						logger.info("Please input group name")
						return
				self.group_name_lbl.setText(" ")

		def open_color_dialog(self):
				color = QColorDialog.getColor()

				if color.isValid():
						self.color.setText(color.name())

		def center(self):
				qr = self.frameGeometry()
				cp = QDesktopWidget().availableGeometry().center()
				qr.moveCenter(cp)
				self.move(qr.topLeft())

		def store(self):
				if self.group_name.text().strip() == "":
						self.group_name_lbl.setText("Please provide group name")
						self.group_name_lbl.setStyleSheet('color: red;')
						logger.info("Please provide group name")
						return
				self.database_management.update_listdetails(self.group_name.text().strip(), self.color.text(),
																										self.list_detail_id)
				logger.info("List details updated successfully")
				self.accept()


class FrmShowGroupList(QDialog):

		def __init__(self, group_list):
				super(FrmShowGroupList, self).__init__()
				self.setWindowTitle("Select group for modification")

				self.setWindowIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'edit_3_24.png')))
				self.setModal(True)

				self.selected_items = []
				vbox_group_selection = QVBoxLayout(self)

				self.combo_box_selected_groups = QComboBox()
				for group_detail in group_list:
						self.combo_box_selected_groups.addItem(str(group_detail[1]), group_detail)
				vbox_group_selection.addWidget(self.combo_box_selected_groups)

				button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
				button_box.accepted.connect(self.accept)
				button_box.rejected.connect(self.reject)

				vbox_group_selection.addWidget(button_box)

				self.setLayout(vbox_group_selection)
				# self.setMinimumSize(300, 80)
				# self.setMaximumSize(300, 80)
				self.center()

		def get_selected_group(self):
				return self.combo_box_selected_groups.itemData(self.combo_box_selected_groups.currentIndex())

		def center(self):
				qr = self.frameGeometry()
				cp = QDesktopWidget().availableGeometry().center()
				qr.moveCenter(cp)
				self.move(qr.topLeft())


class FrmAddEditSignals(QDialog):
		Channel = 'main'
		SEP = ',\t'

		def __init__(self, control, signals):
				super(FrmAddEditSignals, self).__init__()
				self.selectSignalForCustomExpressionInStandardTemplate = ObjectEmittingSignal()

				self.setModal(False)
				self.signals = signals
				self.Control = control
				self.setWindowTitle("Add/Edit Signals")
				self.setWindowIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'edit_4_24.png')))
				# self.setModal(True)
				# self.setMinimumSize(650, 550)
				# self.setMaximumSize(350, 350)
				self.center()
				vboxlayout_main = QtGui.QVBoxLayout()
				self.selected_signals = {}
				self.final_signals_list = []
				home_directory = expanduser("~")
				temp_file_directory = os.path.join(home_directory, ".aebs")
				self.filename = os.path.join(temp_file_directory, "signal_data_cache.txt")

				gbox_horizontal_signal_selector = QGroupBox('')
				hboxlayout_signal_selector = QtGui.QHBoxLayout()
				hboxlayout_signal_selector.setSpacing(0)
				hboxlayout_signal_selector.setContentsMargins(1, 1, 1, 1)

				gbox_signal_selector = QGroupBox('')
				vboxlayout_signal_selector = QtGui.QVBoxLayout()
				vboxlayout_signal_selector.setSpacing(0)
				vboxlayout_signal_selector.setContentsMargins(1, 1, 1, 1)

				# <editor-fold desc="Signals Treeview operations">
				gbox_treeview_operations = QGroupBox('')
				hboxlayout_treeview_operation = QtGui.QHBoxLayout()
				hboxlayout_treeview_operation.setContentsMargins(1, 1, 1, 1)

				gbox_expand_collapse_operations = QGroupBox('')
				gridlayout_expand_collapse_operation = QtGui.QGridLayout()
				gridlayout_expand_collapse_operation.setContentsMargins(1, 1, 1, 1)

				self.label_expand_collapse = QLabel("Expand/Collapse")
				gridlayout_expand_collapse_operation.addWidget(self.label_expand_collapse, 0, 0, 1, 2, Qt.AlignTop)

				self.pbutton_expand = QPushButton("")
				self.pbutton_expand.setToolTip('Expand signals')
				self.pbutton_expand.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'tree_expand_24.png')))
				self.pbutton_expand.clicked.connect(self.expand_treeview_signal_table_items)
				gridlayout_expand_collapse_operation.addWidget(self.pbutton_expand, 1, 0)

				self.pbutton_collapse = QPushButton("")
				self.pbutton_collapse.setToolTip('Collapse signals')
				self.pbutton_collapse.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'tree_collapse_24.png')))
				self.pbutton_collapse.clicked.connect(self.collapse_treeview_signal_table_items)
				gridlayout_expand_collapse_operation.addWidget(self.pbutton_collapse, 1, 1)

				gbox_expand_collapse_operations.setLayout(gridlayout_expand_collapse_operation)
				hboxlayout_treeview_operation.addWidget(gbox_expand_collapse_operations)

				gbox_plot_navigator_operations = QGroupBox('')
				gridlayout_plot_navigator_operation = QtGui.QGridLayout()
				gridlayout_plot_navigator_operation.setContentsMargins(1, 1, 1, 1)
				self.label_plot_navigator = QLabel("Add Signals")
				gridlayout_plot_navigator_operation.addWidget(self.label_plot_navigator, 0, 0, 1, 3,
																											Qt.AlignTop | Qt.AlignCenter)

				self.pbutton_add_regular_signal = QPushButton("")
				self.pbutton_add_regular_signal.setToolTip('Add Selected Signals')
				self.pbutton_add_regular_signal.setIcon(
								QIcon(os.path.join(IMAGE_DIRECTORY, 'add_regular_signal_24.png')))
				self.pbutton_add_regular_signal.clicked.connect(self.add_signals)
				gridlayout_plot_navigator_operation.addWidget(self.pbutton_add_regular_signal, 2, 1)

				self.pbutton_add_custom_signal = QPushButton("")
				self.pbutton_add_custom_signal.setToolTip('Add Custom Signal')
				self.pbutton_add_custom_signal.setIcon(
								QIcon(os.path.join(IMAGE_DIRECTORY, 'add_custom_signal_24.png')))
				self.pbutton_add_custom_signal.clicked.connect(self.show_table_plot_custom_signal_form)
				gridlayout_plot_navigator_operation.addWidget(self.pbutton_add_custom_signal, 2, 2)

				gbox_plot_navigator_operations.setLayout(gridlayout_plot_navigator_operation)
				hboxlayout_treeview_operation.addWidget(gbox_plot_navigator_operations)

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
				lbl_signal_name = QLabel("")
				lbl_signal_name.setPixmap(QPixmap(os.path.join(IMAGE_DIRECTORY, 'search_24.png')))

				hboxlayout_signal_filter.addWidget(lbl_signal_name, 0, Qt.AlignVCenter)
				lbl_spacer = QLabel("")
				hboxlayout_signal_filter.addWidget(lbl_spacer, 0, Qt.AlignVCenter)

				self.signal_name = QtGui.QLineEdit()
				self.signal_name.setToolTip('Provide signal filter expression here & press enter')
				# self.signal_name.textEdited.connect(self.search_text_changed)
				hboxlayout_signal_filter.addWidget(self.signal_name, 0, Qt.AlignVCenter)

				self.pbutton_signal_filter_clear = QPushButton("")
				self.pbutton_signal_filter_clear.setToolTip('Clear Filter')
				self.pbutton_signal_filter_clear.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'clear_filter_24.png')))
				self.pbutton_signal_filter_clear.setMinimumWidth(50)
				self.pbutton_signal_filter_clear.pressed.connect(self.clear_filter)
				hboxlayout_signal_filter.addWidget(self.pbutton_signal_filter_clear, 0, Qt.AlignVCenter)

				self.pbutton_signal_filter_search = QPushButton("Search")
				self.pbutton_signal_filter_search.setToolTip('Search Signals')
				self.pbutton_signal_filter_search.setMaximumWidth(80)
				self.pbutton_signal_filter_search.pressed.connect(self.search_text_changed)
				hboxlayout_signal_filter.addWidget(self.pbutton_signal_filter_search, 0, Qt.AlignVCenter)

				self.pbutton_signal_filter_match_case = QPushButton("Aa")
				self.pbutton_signal_filter_match_case.setToolTip('Set match case on/off')
				self.pbutton_signal_filter_match_case.setMaximumWidth(50)
				self.pbutton_signal_filter_match_case.setCheckable(True)
				self.pbutton_signal_filter_match_case.clicked.connect(lambda: self.search_text_changed())
				hboxlayout_signal_filter.addWidget(self.pbutton_signal_filter_match_case, 0, Qt.AlignVCenter)

				self.pbutton_signal_filter_regular_exp = QPushButton("RegEx")
				self.pbutton_signal_filter_regular_exp.setToolTip('Set regular expression on/off')
				self.pbutton_signal_filter_regular_exp.setMaximumWidth(80)
				self.pbutton_signal_filter_regular_exp.setCheckable(True)
				self.pbutton_signal_filter_regular_exp.clicked.connect(lambda: self.search_text_changed())
				hboxlayout_signal_filter.addWidget(self.pbutton_signal_filter_regular_exp, 0, Qt.AlignVCenter)

				gbox_signal_filter.setLayout(hboxlayout_signal_filter)

				vboxlayout_signal_selector.addWidget(gbox_signal_filter)
				# </editor-fold>

				# <editor-fold desc="Treeview control">
				self.treeview_signal_table = QtGui.QTreeView()
				self.treeview_signal_table.doubleClicked.connect(self.treeview_signal_table_doubleClicked)
				self.treeview_signal_table.setSortingEnabled(True)
				self.treeview_signal_table.header().setStretchLastSection(True)
				self.treeview_signal_table.setAlternatingRowColors(True)

				self.treeview_signal_table.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
				self.treeview_signal_table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

				self.treeview_signal_table.setHeaderHidden(False)
				self.treeview_signal_table_model = QStandardItemModel()
				self.treeview_signal_table_model.setHorizontalHeaderLabels(['Devices', ''])

				# Make proxy model to allow seamless filtering
				self.treeview_signal_table_proxy_model = LeafFilterProxyModel()
				self.treeview_signal_table_proxy_model.setSourceModel(self.treeview_signal_table_model)
				self.treeview_signal_table_proxy_model.sort(0)
				self.treeview_signal_table.setModel(self.treeview_signal_table_proxy_model)

				# vboxlayout_signal_selector.addWidget(self.treeview_signal_table)

				# <editor-fold desc="Tabview control">
				self.tabwidget = QTabWidget()
				self.tabwidget.addTab(self.treeview_signal_table, "Signals")

				self.table_widget_search = QTableWidget(1, 2)
				self.table_widget_search_column_lables = ["Device Name", "Signal Name"]
				self.table_widget_search.setHorizontalHeaderLabels(self.table_widget_search_column_lables)
				self.table_widget_search.setAlternatingRowColors(True)
				self.table_widget_search.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
				self.table_widget_search.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
				self.table_widget_search.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
				# Allow popup menu
				# self.table_widget_search.setContextMenuPolicy(Qt.CustomContextMenu)

				# Connect the signal request to the slot (click the right mouse button to call the method)
				# self.table_widget_search.customContextMenuRequested.connect(self.createContextMenu)

				self.tabwidget.addTab(self.table_widget_search, "Search Result")

				vboxlayout_signal_selector.addWidget(self.tabwidget)
				# </editor-fold>

				# self.setLayout(vboxlayout_signal_selector)

				# </editor-fold>
				gbox_signal_selector.setLayout(vboxlayout_signal_selector)

				hboxlayout_signal_selector.addWidget(gbox_signal_selector)

				gbox_selected_signals_operations = QGroupBox('')
				vboxlayout_selected_signals_operations = QVBoxLayout()
				vboxlayout_selected_signals_operations.setSpacing(0)
				vboxlayout_selected_signals_operations.setContentsMargins(1, 1, 1, 1)

				# <editor-fold desc="Selected Signals Treeview operations">
				gbox_selected_signals_treeview_operations = QGroupBox('')
				hboxlayout_selected_signals_treeview_operations = QtGui.QHBoxLayout()
				hboxlayout_selected_signals_treeview_operations.setContentsMargins(1, 1, 1, 1)

				gbox_selected_temp_signals_operations = QGroupBox('')
				gridlayout_selected_temp_signals_operation = QtGui.QGridLayout()
				gridlayout_selected_temp_signals_operation.setContentsMargins(1, 1, 1, 1)
				self.label_selected_signals = QLabel("Signal Operations")
				gridlayout_selected_temp_signals_operation.addWidget(self.label_selected_signals, 0, 0, 1, 3,
																														 Qt.AlignTop | Qt.AlignCenter)

				self.pbutton_remove_signal = QPushButton("Remove")
				self.pbutton_remove_signal.setToolTip('Remove Selected Signals')
				self.pbutton_remove_signal.setIcon(
								QIcon(os.path.join(IMAGE_DIRECTORY, 'delete_24.png')))
				self.pbutton_remove_signal.clicked.connect(self.selected_signal_remove)
				gridlayout_selected_temp_signals_operation.addWidget(self.pbutton_remove_signal, 2, 1)

				self.pbutton_replace_signal = QPushButton("Replace")
				self.pbutton_replace_signal.setToolTip('Update selected signal (Change Device Name and Signal Name only)')
				self.pbutton_replace_signal.setIcon(
								QIcon(os.path.join(IMAGE_DIRECTORY, 'replace_24.png')))
				self.pbutton_replace_signal.clicked.connect(self.selected_signal_replace)
				gridlayout_selected_temp_signals_operation.addWidget(self.pbutton_replace_signal, 2, 2)

				gbox_selected_temp_signals_operations.setLayout(gridlayout_selected_temp_signals_operation)
				hboxlayout_selected_signals_treeview_operations.addWidget(gbox_selected_temp_signals_operations)

				horizontal_spacer = QSpacerItem(0, 0, QSizePolicy.Expanding)
				hboxlayout_selected_signals_treeview_operations.addItem(horizontal_spacer)

				gbox_selected_signals_treeview_operations.setLayout(hboxlayout_selected_signals_treeview_operations)
				vboxlayout_selected_signals_operations.addWidget(gbox_selected_signals_treeview_operations)
				# </editor-fold>

				# <editor-fold desc="Selected Signal Filter">
				gbox_selected_signal_filter = QGroupBox('')
				hboxlayout_selected_signal_filter = QtGui.QHBoxLayout()
				hboxlayout_selected_signal_filter.setSpacing(0)
				hboxlayout_selected_signal_filter.setContentsMargins(1, 1, 1, 1)
				lbl_selected_selected_signal_name = QLabel("")
				lbl_selected_selected_signal_name.setPixmap(QPixmap(os.path.join(IMAGE_DIRECTORY, 'search_24.png')))

				hboxlayout_selected_signal_filter.addWidget(lbl_selected_selected_signal_name, 0, Qt.AlignVCenter)
				lbl_spacer = QLabel("")
				hboxlayout_selected_signal_filter.addWidget(lbl_spacer, 0, Qt.AlignVCenter)

				self.selected_signal_name = QtGui.QLineEdit()
				self.selected_signal_name.setToolTip('Provide signal filter expression here')
				self.selected_signal_name.textEdited.connect(self.search_selected_text_changed)
				hboxlayout_selected_signal_filter.addWidget(self.selected_signal_name, 0, Qt.AlignVCenter)

				self.pbutton_selected_signal_filter_clear = QPushButton("")
				self.pbutton_selected_signal_filter_clear.setToolTip('Clear Filter')
				self.pbutton_selected_signal_filter_clear.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'clear_filter_24.png')))
				self.pbutton_selected_signal_filter_clear.setMinimumWidth(50)
				self.pbutton_selected_signal_filter_clear.pressed.connect(self.selected_signal_clear_filter)
				hboxlayout_selected_signal_filter.addWidget(self.pbutton_selected_signal_filter_clear, 0, Qt.AlignVCenter)

				self.pbutton_selected_signal_filter_match_case = QPushButton("Aa")
				self.pbutton_selected_signal_filter_match_case.setToolTip('Set match case on/off')
				self.pbutton_selected_signal_filter_match_case.setMaximumWidth(50)
				self.pbutton_selected_signal_filter_match_case.setCheckable(True)
				self.pbutton_selected_signal_filter_match_case.clicked.connect(lambda: self.search_selected_text_changed())
				hboxlayout_selected_signal_filter.addWidget(self.pbutton_selected_signal_filter_match_case, 0, Qt.AlignVCenter)

				self.pbutton_selected_signal_filter_regular_exp = QPushButton("RegEx")
				self.pbutton_selected_signal_filter_regular_exp.setToolTip('Set regular expression on/off')
				self.pbutton_selected_signal_filter_regular_exp.setMaximumWidth(80)
				self.pbutton_selected_signal_filter_regular_exp.setCheckable(True)
				self.pbutton_selected_signal_filter_regular_exp.clicked.connect(lambda: self.search_selected_text_changed())
				hboxlayout_selected_signal_filter.addWidget(self.pbutton_selected_signal_filter_regular_exp, 0,
																										Qt.AlignVCenter)

				gbox_selected_signal_filter.setLayout(hboxlayout_selected_signal_filter)

				vboxlayout_selected_signals_operations.addWidget(gbox_selected_signal_filter)
				# </editor-fold>

				# <editor-fold desc="Selected signals Treeview">
				self.treeview_selected_signals = QtGui.QTreeView()
				self.treeview_selected_signals.doubleClicked.connect(self.treeview_selected_signals_double_clicked)
				self.treeview_selected_signals.clicked.connect(self.treeview_selected_signals_clicked)
				self.treeview_selected_signals.setSortingEnabled(True)
				self.treeview_selected_signals.header().setStretchLastSection(True)
				self.treeview_selected_signals.setAlternatingRowColors(True)

				self.treeview_selected_signals.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
				self.treeview_selected_signals.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

				self.treeview_selected_signals.setHeaderHidden(False)
				self.treeview_selected_signals_model = QStandardItemModel()
				self.treeview_selected_signals_model.setHorizontalHeaderLabels(
								['Alias', 'Device Name', 'Signal Name', 'ID'])

				# Make proxy model to allow seamless filtering
				self.treeview_selected_signals_proxy_model = QSortFilterProxyModel()
				self.treeview_selected_signals_proxy_model.setSourceModel(self.treeview_selected_signals_model)
				self.treeview_selected_signals_proxy_model.sort(1)
				self.treeview_selected_signals.setModel(self.treeview_selected_signals_proxy_model)

				vboxlayout_selected_signals_operations.addWidget(self.treeview_selected_signals)
				# </editor-fold>

				# <editor-fold desc="Signal Info">
				gbox_signal_details = QGroupBox('')
				vboxlayout_signal_details = QVBoxLayout()
				vboxlayout_signal_details.setSpacing(0)
				vboxlayout_signal_details.setContentsMargins(1, 1, 1, 1)

				gbox_signal_detail_operations = QGroupBox('')
				hboxlayout_signal_detail_operations = QHBoxLayout()
				hboxlayout_signal_detail_operations.setSpacing(0)
				hboxlayout_signal_detail_operations.setContentsMargins(1, 1, 1, 1)
				self.pbutton_signal_details_save = QPushButton("")
				self.pbutton_signal_details_save.clicked.connect(self.save_signal_details)
				self.pbutton_signal_details_save.setToolTip('Save signal details')
				self.pbutton_signal_details_save.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'save_24.png')))
				self.pbutton_signal_details_save.setMinimumWidth(50)
				self.pbutton_signal_details_save.setEnabled(False)
				# self.pbutton_signal_details_save.pressed.connect(self.save_signal_details)
				hboxlayout_signal_detail_operations.addWidget(self.pbutton_signal_details_save, 0, Qt.AlignLeft)
				gbox_signal_detail_operations.setLayout(hboxlayout_signal_detail_operations)
				# button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
				# button_box.accepted.connect(self.store)
				# # button_box.rejected.connect(self.cancel)
				vboxlayout_signal_details.addWidget(gbox_signal_detail_operations, 0, Qt.AlignTop)

				self.group_box_signal_information = QGroupBox("Signal Information")
				self.form_layout_signal_information = QFormLayout()

				self.line_edit_label = QLineEdit()
				self.line_edit_label.setToolTip("Provide signal label to be displayed in legend")
				self.line_edit_label.textChanged.connect(self.line_edit_label_onchanged)
				self.form_layout_signal_information.addRow(QLabel("Label :"), self.line_edit_label)

				self.line_edit_unit = QLineEdit()
				self.line_edit_unit.setToolTip("Provide physical unit of the signal (displayed in legend)")
				self.line_edit_unit.setAlignment(Qt.AlignRight)
				self.line_edit_unit.textChanged.connect(self.line_edit_unit_onchanged)
				self.form_layout_signal_information.addRow(QLabel("Unit :"), self.line_edit_unit)

				self.line_edit_offset = QLineEdit()
				self.line_edit_offset.setToolTip("Provide offset to be added to value array")
				self.line_edit_offset.textChanged.connect(self.line_edit_offset_onchanged)
				self.line_edit_offset.setAlignment(Qt.AlignRight)
				self.form_layout_signal_information.addRow(QLabel("Offset :"), self.line_edit_offset)

				self.line_edit_factor = QLineEdit()
				self.line_edit_factor.setToolTip("Provide factor for multiplying value array")
				self.line_edit_factor.textChanged.connect(self.line_edit_factor_onchanged)
				self.line_edit_factor.setAlignment(Qt.AlignRight)
				self.form_layout_signal_information.addRow(QLabel("Factor :"), self.line_edit_factor)

				# self.line_edit_display_scaled = QLineEdit()
				# self.line_edit_display_scaled.textChanged.connect(self.line_edit_display_scaled_onchanged)
				# self.line_edit_display_scaled.setAlignment(Qt.AlignRight)
				# self.form_layout_signal_information.addRow(QLabel("Display Scaled :"), self.line_edit_display_scaled)
				self.line_edit_display_scaled = QComboBox()
				self.line_edit_display_scaled.setToolTip("Provide display the scaled (offset/factor affected) value in legend. Default is True. If False is given, the original value is displayed in legend (while the scaled value is plotted on the axis)")
				option_list = ["True", "False"]
				self.line_edit_display_scaled.addItems(option_list)
				self.line_edit_display_scaled.setCurrentIndex(0)
				self.line_edit_display_scaled.currentIndexChanged.connect(self.line_edit_display_scaled_onchanged)
				self.form_layout_signal_information.addRow(QLabel("Display Scaled :"), self.line_edit_display_scaled)

				self.group_box_signal_information.setLayout(self.form_layout_signal_information)
				vboxlayout_signal_details.addWidget(self.group_box_signal_information, 0, Qt.AlignTop)

				gbox_signal_details.setLayout(vboxlayout_signal_details)

				vboxlayout_selected_signals_operations.addWidget(gbox_signal_details)
				gbox_selected_signals_operations.setLayout(vboxlayout_selected_signals_operations)

				hboxlayout_signal_selector.addWidget(gbox_selected_signals_operations)
				# </editor-fold>

				gbox_horizontal_signal_selector.setLayout(hboxlayout_signal_selector)
				vboxlayout_main.addWidget(gbox_horizontal_signal_selector)
				button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
				button_box.accepted.connect(self.store)
				button_box.rejected.connect(self.reject)

				vboxlayout_main.addWidget(button_box)
				self.setLayout(vboxlayout_main)
				self.long_device_names = {}
				self.update_treeview_signal_table_model()
				self.update_treeview_selected_signals_model()
				self.save_enabled = False

		# <editor-fold desc="Methods Common">
		def center(self):
				qr = self.frameGeometry()
				cp = QDesktopWidget().availableGeometry().center()
				qr.moveCenter(cp)
				self.move(qr.topLeft())

		def store(self):
				self.accept()

		# </editor-fold>

		# <editor-fold desc="Methods Signal Table Treeview operations">
		def update_treeview_signal_table_model(self):
				"""
				Updates model by getting device and signals from parser
				"""
				logger.info("Loading signals from measurement, Please wait...")
				QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
				start = time.time()
				# Clear tree model
				if self.treeview_signal_table_model.hasChildren():
						self.treeview_signal_table_model.removeRows(0, self.treeview_signal_table_model.rowCount())
				# Clear long device name dictionary
				self.long_device_names.clear()

				root_node = self.treeview_signal_table_model.invisibleRootItem()
				signal_source = self.Control.getSource(self.Channel)

				# check if parser has implemented view_signal_list
				is_view_signal_list_available = True
				try:
						value = signal_source.Parser.view_signal_list

						with open(self.filename, 'w') as f:
							for device_name, signal_name in signal_source.Parser.view_signal_list.items():
								for device_name_1, signal_name_1 in signal_name.items():
									f.write('%s:	%s\n' % (device_name, device_name_1))
									if bool(device_name_1):
										for device_name_2, signal_name_2 in signal_name_1.items():
											f.write('%s:	%s\n' % (device_name, device_name_2))
				except AttributeError:
						is_view_signal_list_available = False

				if is_view_signal_list_available:
						for device in signal_source.Parser.iterDeviceNames():
								short_device_name = device.split('-')[0]
								device_dictionary = signal_source.Parser.view_signal_list[short_device_name]

								item = QStandardItem(short_device_name)
								item.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'device_16.png')))
								item.setEditable(False)
								root_node.appendRow(item)
								for signal_name in device_dictionary.keys():
										self.long_device_names[(short_device_name, signal_name)] = device
										signal_dictionary = device_dictionary[signal_name]
										sub_item = QStandardItem(signal_name)
										sub_item.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'signal_16.png')))
										sub_item.setEditable(False)
										item.appendRow(sub_item)
										self.add_signals_recursively(signal_dictionary, sub_item)
				else:
					with open(self.filename, 'w') as f:
						for device in signal_source.Parser.iterDeviceNames():
								short_device_name = device.split('-')[0]

								item = QStandardItem(short_device_name)
								item.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'device_16.png')))
								item.setEditable(False)
								root_node.appendRow(item)
								for signal_name in signal_source.Parser.iterSignalNames(device):
										self.long_device_names[short_device_name, signal_name] = device
										sub_item = QStandardItem(signal_name)
										sub_item.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'signal_16.png')))
										sub_item.setEditable(False)
										item.appendRow(sub_item)
										f.write('%s:	%s\n' % (short_device_name, signal_name))

				self.treeview_signal_table.setColumnWidth(0, 500)
				end = time.time()
				self.treeview_signal_table_proxy_model.sort(0)
				QtGui.QApplication.restoreOverrideCursor()
				logger.info("Signals from measurement are loaded in " + str(end - start) + " Seconds")

		def add_signals_recursively(self, signal_dictionary, item):
				if not bool(signal_dictionary):
						return
				for signal_name in signal_dictionary.keys():
						child_signal_dictionary = signal_dictionary[signal_name]
						sub_item = QStandardItem(signal_name)
						sub_item.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'signal_16.png')))
						sub_item.setEditable(False)
						item.appendRow(sub_item)

						self.add_signals_recursively(child_signal_dictionary, sub_item)
				return

		def get_device_node(self, node):
				while node.parent() is not None:
						node = node.parent()
				return node

		def expand_treeview_signal_table_items(self):
				self.treeview_signal_table.expandAll()

		def collapse_treeview_signal_table_items(self):
				self.treeview_signal_table.collapseAll()

		def getPhysicalUnit(self, ShortDeviceName, SignalName):
				Source = self.Control.getSource(self.Channel)
				DeviceName = Source.getUniqueName(SignalName, ShortDeviceName, FavorMatch = True)
				return Source.getPhysicalUnit(DeviceName, SignalName)

		def show_custom_signal_form(self):
				signal_source = self.Control.getSource(self.Channel)
				selected_rows = self.treeview_signal_table.selectedIndexes()
				signals = []
				for row in selected_rows:
						row = self.treeview_signal_table_proxy_model.mapToSource(row)
						signal = self.treeview_signal_table_proxy_model.sourceModel().itemFromIndex(row)
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

				dialog = FrmShowCustomSignalForm("Standard Template", signals,
																				 self.selectSignalForCustomExpressionInStandardTemplate)
				result = dialog.exec_()
				if dialog.custom_expression is not None:
						# print(dialog.custom_expression)
						custom_signal_name, selected_custom_signals_list, custom_signal_expression, custom_signal_unit = \
								dialog.custom_expression
						signal = dict()
						signal["Label"] = custom_signal_name
						signal["Offset"] = None
						signal["Factor"] = None
						signal["DisplayScaled"] = True
						signal["Unit"] = custom_signal_unit
						signal["AliasName"] = custom_signal_name
						signal["DeviceName"] = None
						signal["SignalName"] = custom_signal_name
						signal["IsCustomExpression"] = True
						signal["CustomExpression"] = custom_signal_expression
						signal["CustomExpressionSignalList"] = selected_custom_signals_list
						signal["ID"] = None
						self.signals[custom_signal_name] = signal
						# for main_signal_name, (device_name, signal_name, signal_unit) in selected_custom_signals_list:
						# 		support_signal = dict()
						# 		support_signal["Label"] = main_signal_name
						# 		support_signal["Offset"] = None
						# 		support_signal["Factor"] = None
						# 		support_signal["DisplayScaled"] = True
						# 		support_signal["Unit"] = signal_unit
						# 		support_signal["AliasName"] = signal_name
						# 		support_signal["DeviceName"] = device_name
						# 		support_signal["SignalName"] = signal_name
						# 		support_signal["IsCustomExpression"] = False
						# 		support_signal["CustomExpression"] = None
						# 		support_signal["ID"] = None
						# 		self.signals[device_name + "-" + signal_name] = support_signal
						self.update_treeview_selected_signals_model()

		def search_text_changed(self):
				"""
				Called automatically when the text in the search widget is modified.
				This method updates the RegExp and automatially filters the tree view
				according to the matching search.
				"""
				# start = time.time()
				text = self.signal_name.text()
				# Set Focus to search tab
				self.tabwidget.setCurrentIndex(1)
				if len(text) > 1:
					logger.info("Filtering signals, Please wait...")
					QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
					start = time.time()

					# search_type = QtCore.QRegExp.FixedString
					# match_type = QtCore.Qt.CaseInsensitive
					#
					# if self.pbutton_signal_filter_regular_exp.isChecked():
					# 		search_type = QtCore.QRegExp.RegExp
					#
					# if self.pbutton_signal_filter_match_case.isChecked():
					# 		match_type = QtCore.Qt.CaseSensitive

					# call search function
					if self.pbutton_signal_filter_match_case.isChecked():
						self.search_result = self.search_string_in_file(self.filename, str(text))
						self.update_table(self.search_result)
					else:
						self.search_result = self.search_string_in_file(self.filename, str(text).lower())
						self.update_table(self.search_result)

					# self.treeview_signal_table_proxy_model.setFilterRegExp(QtCore.QRegExp(text, match_type, search_type))
					# self.treeview_signal_table_proxy_model.setFilterKeyColumn(0)
					# self.proxy_model.setRecursiveFilteringEnabled(True)
					# self.treeview_signal_table.setColumnWidth(0, 500)
					end = time.time()
					QtGui.QApplication.restoreOverrideCursor()
					logger.debug("Filtering signals done in " + str(end - start) + " Seconds")

				else:
						logger.warning("Please type characters to search")
						self.tabwidget.setCurrentIndex(0)
				return

		def clear_filter(self):
				logger.info("Clearing filter, Please wait...")
				self.signal_name.clear()
				self.table_widget_search.clear()
				# self.table_widget_search.clearContents()
				self.table_widget_search.setRowCount(0)
				self.search_text_changed()
				self.treeview_signal_table_proxy_model.sort(0)
				logger.info("Filter is removed")

		def add_signals(self):
				self.selected_signal_list()
				signal_source = self.Control.getSource(self.Channel)

				for data in self.final_signals_list:
					for device_name, signal_name in data.iteritems():
						signal_index = ''

						original_signal_name = signal_name
						if len(original_signal_name.split('[:,')) == 2:
							(signal_name, index) = original_signal_name.split('[')
							signal_index = '[' + index
						device_name = self.long_device_names[(device_name, signal_name)]
						value, time_key = signal_source.Parser.getSignal(device_name, signal_name)
						time = signal_source.Parser.getTime(time_key)
						unit = signal_source.Parser.getPhysicalUnit(device_name, signal_name)

						signal = dict()
						signal["Label"] = signal_name
						signal["Offset"] = None
						signal["Factor"] = None
						signal["DisplayScaled"] = True
						signal["Unit"] = unit
						signal["AliasName"] = original_signal_name
						signal["DeviceName"] = device_name
						signal["SignalName"] = original_signal_name
						signal["IsCustomExpression"] = False
						signal["CustomExpression"] = None
						signal["CustomExpressionSignalList"] = None
						signal["ID"] = None
						self.signals[device_name + "-" + signal_name] = signal

						self.update_treeview_selected_signals_model()

				# Fetch item for the index fetched from the selection
				# selected_row = self.treeview_signal_table.selectedIndexes()
				# for row in selected_row:
				# 		row = self.treeview_signal_table_proxy_model.mapToSource(row)
				# 		signal = self.treeview_signal_table_proxy_model.sourceModel().itemFromIndex(row)
				# 		if signal.parent() is not None:
				# 				if signal.child(0, 0) is None:
				# 						original_signal_name = signal.text()
				# 						signal_name = original_signal_name
				# 						signal_index = ''
				# 						if len(original_signal_name.split('[:,')) == 2:
				# 								(signal_name, index) = original_signal_name.split('[')
				# 								signal_index = '[' + index
				#
				# 						device_node = self.get_device_node(signal)
				# 						if device_node is not signal:
				# 								device_name = self.long_device_names[(device_node.text(), signal_name)]
				#
				# 								unit = signal_source.Parser.getPhysicalUnit(device_name, signal_name)
				#
				# 								signal = dict()
				# 								signal["Label"] = signal_name
				# 								signal["Offset"] = None
				# 								signal["Factor"] = None
				# 								signal["DisplayScaled"] = True
				# 								signal["Unit"] = unit
				# 								signal["AliasName"] = original_signal_name
				# 								signal["DeviceName"] = device_name
				# 								signal["SignalName"] = original_signal_name
				# 								signal["IsCustomExpression"] = False
				# 								signal["CustomExpression"] = None
				# 								signal["CustomExpressionSignalList"] = None
				# 								signal["ID"] = None
				# 								self.signals[device_name + "-" + signal_name] = signal
				#
				# 								self.update_treeview_selected_signals_model()
				# 		else:
				# 				logger.info("Please select signals from array : " + signal.text())

		def treeview_signal_table_doubleClicked(self):
				item_selection_model = self.treeview_signal_table.selectionModel()
				selected_row = item_selection_model.selectedIndexes()[0]

				row = self.treeview_signal_table_proxy_model.mapToSource(selected_row)
				signal = self.treeview_signal_table_proxy_model.sourceModel().itemFromIndex(row)
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
										self.selectSignalForCustomExpressionInStandardTemplate.signal.emit(
														(device_node.text(), original_signal_name, signal_unit))
						else:
								logger.info("Please select signals from array " + signal.text())

		# </editor-fold>

		# <editor-fold desc="Table method implementation (Fast Searching)">
		def selected_signal_list(self):
			counter = 0
			self.final_signals_list = []

			# Get index
			for i in self.table_widget_search.selectionModel().selection().indexes():
				rowNum = i.row()
				counter = counter + 1
				if counter <= len(self.table_widget_search.selectionModel().selection().indexes()):
					self.selected_signals[self.table_widget_search.item(rowNum, 0).text()] = \
						self.table_widget_search.item(rowNum, 1).text().split('\n')[0]
					if self.selected_signals in self.final_signals_list:
						self.selected_signals = {}
						continue
					else:
						self.final_signals_list.append(self.selected_signals)
						self.selected_signals = {}
				else:
					break

			return

		def show_table_plot_custom_signal_form(self):
				self.selected_signal_list()
				signal_source = self.Control.getSource(self.Channel)
				# selected_rows = self.SignalTable.selectedIndexes()
				signals = []
				for data in self.final_signals_list:
					for device_name, signal_name in data.iteritems():
						signal_index = ''
						original_signal_name = signal_name
						original_device_name = device_name
						if len(original_signal_name.split('[:,')) == 2:
							(signal_name, index) = original_signal_name.split('[')
							signal_index = '[' + index
						device_name = self.long_device_names[(device_name, signal_name)]
						value, time_key = signal_source.Parser.getSignal(device_name, signal_name)
						time = signal_source.Parser.getTime(time_key)
						unit = signal_source.Parser.getPhysicalUnit(device_name, signal_name)
						signals.append((original_device_name, original_signal_name, unit))

				dialog = FrmShowCustomSignalForm("Standard Template", signals,
												 self.selectSignalForCustomExpressionInStandardTemplate)
				# dialog.show()
				dialog.exec_()
				if dialog.custom_expression is not None:
						# print(dialog.custom_expression)
						custom_signal_name, selected_custom_signals_list, custom_signal_expression, custom_signal_unit = \
								dialog.custom_expression
						signal = dict()
						signal["Label"] = custom_signal_name
						signal["Offset"] = None
						signal["Factor"] = None
						signal["DisplayScaled"] = True
						signal["Unit"] = custom_signal_unit
						signal["AliasName"] = custom_signal_name
						signal["DeviceName"] = None
						signal["SignalName"] = custom_signal_name
						signal["IsCustomExpression"] = True
						signal["CustomExpression"] = custom_signal_expression
						signal["CustomExpressionSignalList"] = selected_custom_signals_list
						signal["ID"] = None
						self.signals[custom_signal_name] = signal
						self.update_treeview_selected_signals_model()

		def keyPressEvent(self, event):
			key = event.key()
			if (key == Qt.Key_Enter) or (key == Qt.Key_Return):
				self.search_text_changed()

		def search_string_in_file(self, file_name, string_to_search):
			"""Search for the given string in file and return lines containing that string,
			along with line numbers"""
			start_time = time.time()
			line_number = 0
			result_list = []

			# Open the file in read only mode
			with open(file_name, 'r') as file_obj:
				# Read all lines in the file one by one
				for line in file_obj:
					# For each line, check if line contains the string
					line_number += 1
					if self.pbutton_signal_filter_match_case.isChecked():
						if string_to_search in line:
							# If yes, then add the line number & line as a tuple in the list
							result_list.append((line))
					else:
						if string_to_search in line.lower():
							# If yes, then add the line number & line as a tuple in the list
							result_list.append((line))

			# Return list of tuples containing line numbers and lines where string is found
			end_time = time.time()
			logger.info("Searching completed in :  " + str(end_time - start_time) + " Seconds")
			return result_list

		def update_table(self, searched_items):
			self.table_widget_search.setRowCount(len(searched_items))
			self.table_widget_search.setColumnCount(2)
			self.table_widget_search_column_lables = ["Device Name", "Signal Name"]
			self.table_widget_search.setHorizontalHeaderLabels(self.table_widget_search_column_lables)
			self.row_counter = 0

			if searched_items:
				for items in searched_items:
					device = QTableWidgetItem(items.split(':\t')[0])
					device.setTextAlignment(Qt.AlignLeft)
					self.table_widget_search.setItem(self.row_counter, 0, device)
					signal = QTableWidgetItem(items.split(':\t')[1])
					signal.setTextAlignment(Qt.AlignCenter)
					self.table_widget_search.setItem(self.row_counter, 1, signal)
					self.table_widget_search.setRowHeight(self.row_counter, 25)
					self.row_counter += 1
				# Sorting signal names in ascending order
				self.table_widget_search.sortByColumn(1, Qt.AscendingOrder)
				self.table_widget_search.resizeColumnsToContents()
				self.table_widget_search.horizontalHeader().setStretchLastSection(True)
			else:
				logger.info("Signal name not available")

		# </editor-fold>

		# <editor-fold desc="Methods Selected Signals Treeview operations">

		def update_treeview_selected_signals_model(self):
				"""
				Updates model by getting device and signals from parser
				"""
				# Clear tree model
				if self.treeview_selected_signals_model.hasChildren():
						self.treeview_selected_signals_model.removeRows(0, self.treeview_selected_signals_model.rowCount())

				root_node = self.treeview_selected_signals_model.invisibleRootItem()

				for key, value in self.signals.items():
						item_alias_name = QStandardItem(value["AliasName"])
						item_alias_name.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'signal_16.png')))
						item_alias_name.setEditable(False)
						item_device_name = QStandardItem(value["DeviceName"])
						item_device_name.setEditable(False)
						item_signal_name = QStandardItem(value["SignalName"])
						item_signal_name.setEditable(False)

						item_primary_key = QStandardItem(str(key))
						item_primary_key.setEditable(False)

						root_node.appendRow(
										[item_alias_name, item_device_name, item_signal_name, item_primary_key])

				self.treeview_selected_signals.setColumnWidth(0, 100)
				self.treeview_selected_signals.setColumnWidth(1, 80)
				self.treeview_selected_signals.setColumnWidth(2, 100)
				self.treeview_selected_signals_proxy_model.sort(0)

		def selected_signal_remove(self):
				item_selection_model = self.treeview_selected_signals.selectionModel()
				if len(item_selection_model.selectedIndexes()) != 0:
						selected_row_signal_id = item_selection_model.selectedIndexes()[3]

						row_signal_id = self.treeview_selected_signals_proxy_model.mapToSource(selected_row_signal_id)

						signal_id = self.treeview_selected_signals_proxy_model.sourceModel().itemFromIndex(
										row_signal_id)

						del self.signals[signal_id.text()]
						logger.info("Successfully deleted " + signal_id.text())
						self.update_treeview_selected_signals_model()
				else:
						logger.info("please select signal first")

		def selected_signal_replace(self):
				item_selection_model = self.treeview_selected_signals.selectionModel()
				signal_id = None
				if len(item_selection_model.selectedIndexes()) != 0:
						selected_row_signal_id = item_selection_model.selectedIndexes()[3]

						row_signal_id = self.treeview_selected_signals_proxy_model.mapToSource(selected_row_signal_id)

						signal_id_object = self.treeview_selected_signals_proxy_model.sourceModel().itemFromIndex(
										row_signal_id)

						signal_id = signal_id_object.text()
				else:
						logger.info("Please select signal from selection")
						return

				if signal_id is not None:
						signal_source = self.Control.getSource(self.Channel)
						# Fetch item for the index fetched from the selection
						selected_row = self.treeview_signal_table.selectedIndexes()
						for row in selected_row:
								row = self.treeview_signal_table_proxy_model.mapToSource(row)
								signal = self.treeview_signal_table_proxy_model.sourceModel().itemFromIndex(row)

								original_signal_name = signal.text()
								signal_name = original_signal_name
								if len(original_signal_name.split('[')) == 2:
										(signal_name, index) = original_signal_name.split('[')
										signal_index = '[' + index
								else:
										signal_index = ''
								device_node = self.get_device_node(signal)
								device_name = self.long_device_names[(device_node.text(), signal_name)]

								unit = signal_source.Parser.getPhysicalUnit(device_name, signal_name)

								signal = self.signals[signal_id]
								signal["Unit"] = unit
								signal["AliasName"] = signal_name
								signal["DeviceName"] = device_name
								signal["SignalName"] = signal_name
								logger.info("Successfully replaced signal name and device name for label " + signal["Label"])
								self.update_treeview_selected_signals_model()

		def selected_signal_clear_filter(self):
				self.selected_signal_name.clear()
				self.search_selected_text_changed()
				self.treeview_selected_signals_proxy_model.sort(0)

		def search_selected_text_changed(self):
				"""
				Called automatically when the text in the search widget is modified.
				This method updates the RegExp and automatially filters the tree view
				according to the matching search.
				"""
				text = self.selected_signal_name.text()
				search_type = QtCore.QRegExp.FixedString
				match_type = QtCore.Qt.CaseInsensitive

				if self.pbutton_selected_signal_filter_regular_exp.isChecked():
						search_type = QtCore.QRegExp.RegExp

				if self.pbutton_selected_signal_filter_match_case.isChecked():
						match_type = QtCore.Qt.CaseSensitive

				self.treeview_selected_signals_proxy_model.setFilterRegExp(QtCore.QRegExp(text, match_type, search_type))
				self.treeview_selected_signals_proxy_model.setFilterKeyColumn(0)
				self.treeview_selected_signals.setColumnWidth(0, 100)
				self.treeview_selected_signals.setColumnWidth(1, 80)
				self.treeview_selected_signals.setColumnWidth(2, 100)

		def treeview_selected_signals_clicked(self):
				item_selection_model = self.treeview_selected_signals.selectionModel()
				if len(item_selection_model.selectedIndexes()) != 0:
						selected_row_signal_id = item_selection_model.selectedIndexes()[3]

						row_signal_id = self.treeview_selected_signals_proxy_model.mapToSource(selected_row_signal_id)

						signal_id = self.treeview_selected_signals_proxy_model.sourceModel().itemFromIndex(
										row_signal_id)

						signal_details = self.signals[signal_id.text()]

						if signal_details["Unit"] is not None:
								self.line_edit_unit.setText(str(signal_details["Unit"]))
						else:
								self.line_edit_unit.setText("")
						if signal_details["Label"] is not None:
								self.line_edit_label.setText(str(signal_details["Label"]))
						else:
								self.line_edit_label.setText("")
						if signal_details["Offset"] is not None:
								self.line_edit_offset.setText(str(signal_details["Offset"]))
						else:
								self.line_edit_offset.setText("")
						if signal_details["Factor"] is not None:
								self.line_edit_factor.setText(str(signal_details["Factor"]))
						else:
								self.line_edit_factor.setText("")
						# if signal_details["DisplayScaled"] is not None:
						# 		self.line_edit_display_scaled.currentText(str(signal_details["DisplayScaled"]))
						# else:
						# 		self.line_edit_display_scaled.setText("")
						self.pbutton_signal_details_save.setEnabled(False)

		def treeview_selected_signals_double_clicked(self):
				self.selected_signal_remove()

		# </editor-fold>

		# <editor-fold desc="Methods Signal Info">
		def line_edit_alias_name_onchanged(self):
				self.pbutton_signal_details_save.setEnabled(True)

		def line_edit_unit_onchanged(self):
				self.pbutton_signal_details_save.setEnabled(True)

		def line_edit_label_onchanged(self):
				self.pbutton_signal_details_save.setEnabled(True)

		def line_edit_offset_onchanged(self):
				self.pbutton_signal_details_save.setEnabled(True)

		def line_edit_factor_onchanged(self):
				self.pbutton_signal_details_save.setEnabled(True)

		def line_edit_display_scaled_onchanged(self):
				self.pbutton_signal_details_save.setEnabled(True)

		def save_signal_details(self):
				item_selection_model = self.treeview_selected_signals.selectionModel()
				if len(item_selection_model.selectedIndexes()) != 0:
						selected_row_signal_id = item_selection_model.selectedIndexes()[3]

						row_signal_id = self.treeview_selected_signals_proxy_model.mapToSource(selected_row_signal_id)

						signal_id = self.treeview_selected_signals_proxy_model.sourceModel().itemFromIndex(
										row_signal_id)

						signal_details = self.signals[signal_id.text()]
						if self.line_edit_label.text().strip() =="":
								signal_details["Label"] = signal_details["AliasName"]
						else:
								signal_details["Label"] = self.line_edit_label.text()
						if self.line_edit_offset.text().strip() == "":
								signal_details["Offset"] = None
						else:
								signal_details["Offset"] = self.line_edit_offset.text()
						if self.line_edit_factor.text().strip() == "":
								signal_details["Factor"] = None
						else:
								signal_details["Factor"] = self.line_edit_factor.text()
						signal_details["DisplayScaled"] = self.line_edit_display_scaled.currentText()
						signal_details["Unit"] = self.line_edit_unit.text()
						self.pbutton_signal_details_save.setEnabled(False)


class FrmCopyAxesDetails(QDialog):
		DatabaseManagement.db_file_path = DATABASE_PATH
		database_management = DatabaseManagement()

		def __init__(self, module_id):
				super(FrmCopyAxesDetails, self).__init__()

				self.module_id = module_id
				self.setWindowIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'add_1_24.png')))
				self.setModal(True)
				# self.setMinimumSize(350, 350)
				# self.setMaximumSize(350, 350)
				self.center()
				self.user_cancelled = False
				module_details = self.database_management.select_all_module_details_by_moduleid(self.module_id)
				if len(module_details) != 0:
						dialog_edit_module = FrmShowModuleList(module_details)
						result = dialog_edit_module.exec_()
						if result == QDialog.Accepted:
								selected_module_detail = dialog_edit_module.get_selected_module()

								self.selected_module_id = selected_module_detail[0]
								selected_module_name = selected_module_detail[1]
								axes_details = self.database_management.select_plot_details_by_module_id(self.selected_module_id)
								if len(axes_details) != 0:
										dialog_edit_axes = FrmShowAxesList(axes_details)
										result = dialog_edit_axes.exec_()
										if result == QDialog.Accepted:
												selected_axes_detail = dialog_edit_axes.get_selected_axes()
												self.plot_detail_id = selected_axes_detail[0]
												plot_detail_axes_name = selected_axes_detail[1]
												plot_detail_xlabel = selected_axes_detail[2]
												plot_detail_ylabel = selected_axes_detail[3]
												plot_detail_yticks = selected_axes_detail[4]
												plot_detail_row_number = selected_axes_detail[5]
												plot_detail_column_number = selected_axes_detail[6]

												group_box_module = QGroupBox("")
												form_layout_module = QFormLayout()

												module_info = self.database_management.select_module_by_id(self.module_id)
												form_layout_module.addRow(QLabel("Selected Module:" + module_info[1]))
												form_layout_module.addRow(
														QLabel("Coping Axes:" + plot_detail_axes_name + "  From Module:" + selected_module_name))
												group_box_module.setLayout(form_layout_module)

												self.setWindowTitle("Edit Axes Details " + module_info[1] + "-" + plot_detail_axes_name)
												group_box_plotdetails = QGroupBox("")
												form_layout_plotdetails = QFormLayout()
												self.axes_name = QLineEdit()
												self.axes_name.setText(plot_detail_axes_name)
												self.axes_name.textChanged[str].connect(self.onChanged)
												form_layout_plotdetails.addRow(QLabel("(*) Name:"), self.axes_name)
												self.axes_name_lbl = QLabel(self)
												form_layout_plotdetails.addRow(QLabel(" "), self.axes_name_lbl)

												self.xlabel = QLineEdit()
												self.xlabel.setText(plot_detail_xlabel)
												self.xlabel.setToolTip("Set X-Axis Label")
												form_layout_plotdetails.addRow(QLabel("X-Axis Label:"), self.xlabel)

												self.ylabel = QLineEdit()
												self.ylabel.setText(plot_detail_ylabel)
												self.ylabel.setToolTip("Set Y-Axis Label")
												form_layout_plotdetails.addRow(QLabel("Y-Axis Label:"), self.ylabel)

												self.yticks = QPlainTextEdit()
												self.yticks.setPlainText(plot_detail_yticks)
												self.yticks.setToolTip("Set Y-ticks Labels in dictionary format")
												form_layout_plotdetails.addRow(QLabel("Y-Ticks Labels:"), self.yticks)

												self.rownumber = QSpinBox(self)
												self.rownumber.setMinimum(0)
												self.rownumber.setMaximum(10)
												self.rownumber.setValue(plot_detail_row_number)
												self.rownumber.setAlignment(Qt.AlignRight)
												self.rownumber.setToolTip("Set Row Position")
												form_layout_plotdetails.addRow(QLabel("Row Position:"), self.rownumber)

												self.columnnumber = QSpinBox(self)
												self.columnnumber.setMinimum(0)
												self.columnnumber.setMaximum(10)
												self.columnnumber.setValue(plot_detail_column_number)
												self.columnnumber.setAlignment(Qt.AlignRight)
												self.columnnumber.setToolTip("Set Column Position")
												form_layout_plotdetails.addRow(QLabel("Column Position:"), self.columnnumber)

												group_box_plotdetails.setLayout(form_layout_plotdetails)
												button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
												button_box.accepted.connect(self.store)
												button_box.rejected.connect(self.reject)

												main_layout = QVBoxLayout()
												main_layout.addWidget(group_box_module)
												main_layout.addWidget(group_box_plotdetails)
												main_layout.addWidget(button_box)
												self.setLayout(main_layout)

												self.setTabOrder(self.axes_name, self.xlabel)
												self.setTabOrder(self.xlabel, self.ylabel)
												self.setTabOrder(self.ylabel, self.yticks)
												self.setTabOrder(self.yticks, self.rownumber)
												self.setTabOrder(self.rownumber, self.columnnumber)
										else:
												self.user_cancelled = True
								else:
										logger.warning("No axes available for copy, Please add one")
						else:
								self.user_cancelled = True
				else:
						logger.warning("No Module available for copy")

		def onChanged(self, text):
				if text == "":
						self.axes_name_lbl.setText("need user input for axes name")
						self.axes_name_lbl.setStyleSheet('color: red;')
						logger.info("Please input axes name")
						return
				self.axes_name_lbl.setText(" ")

		def center(self):
				qr = self.frameGeometry()
				cp = QDesktopWidget().availableGeometry().center()
				qr.moveCenter(cp)
				self.move(qr.topLeft())

		def store(self):
				if self.axes_name.text().strip() == "":
						self.axes_name_lbl.setText("Please provide axes name")
						self.axes_name_lbl.setStyleSheet('color: red;')
						logger.info("Please provide axes name")
						return

				axes_id = self.database_management.create_axesdetails(self.axes_name.text().strip(), self.xlabel.text(),
																															self.ylabel.text(), self.yticks.toPlainText(),
																															self.rownumber.text(), self.columnnumber.text(),
																															self.module_id)
				Signal_list = self.database_management.fetch_signallist_by_plotid(self.plot_detail_id)
				self.database_management.add_signallist_by_plotid(axes_id, Signal_list)
				logger.info("Axes details copied successfully")
				self.accept()


class FrmCopyGroupDetails(QDialog):
		DatabaseManagement.db_file_path = DATABASE_PATH
		database_management = DatabaseManagement()

		def __init__(self, module_id):
				super(FrmCopyGroupDetails, self).__init__()

				self.module_id = module_id
				self.setWindowIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'add_1_24.png')))
				self.setModal(True)
				# self.setMinimumSize(350, 350)
				# self.setMaximumSize(350, 350)
				self.center()
				self.user_cancelled = False
				module_details = self.database_management.select_all_module_details_by_moduleid(self.module_id)
				if len(module_details) != 0:
						dialog_edit_module = FrmShowModuleList(module_details)
						result = dialog_edit_module.exec_()
						if result == QDialog.Accepted:
								selected_module_detail = dialog_edit_module.get_selected_module()

								self.selected_module_id = selected_module_detail[0]
								selected_module_name = selected_module_detail[1]
								list_details = self.database_management.select_list_details_by_module_id(self.selected_module_id)
								if len(list_details) != 0:
										dialog_edit_module = FrmShowGroupList(list_details)
										result = dialog_edit_module.exec_()
										if result == QDialog.Accepted:
												selected_group_detail = dialog_edit_module.get_selected_group()
												self.list_detail_id = selected_group_detail[0]
												list_detail_group_name = selected_group_detail[1]
												list_detail_background_color = selected_group_detail[2]

												group_box_module = QGroupBox("")
												form_layout_module = QFormLayout()

												module_info = self.database_management.select_module_by_id(self.module_id)
												form_layout_module.addRow(QLabel("Selected Module: " + module_info[1]))
												form_layout_module.addRow(
														QLabel("Coping Group: " + list_detail_group_name + " From Module:" + selected_module_name))
												group_box_module.setLayout(form_layout_module)

												self.setWindowTitle("Edit Group Details " + module_info[1] + "-" + list_detail_group_name)
												group_box_listdetails = QGroupBox("")
												form_layout_listdetails = QFormLayout()
												self.group_name = QLineEdit()
												self.group_name.setText(list_detail_group_name)
												self.group_name.setToolTip(("Set Group Name"))
												self.group_name.textChanged[str].connect(self.onChanged)
												form_layout_listdetails.addRow(QLabel("(*) List Group Name:"), self.group_name)
												self.group_name_lbl = QLabel(self)
												form_layout_listdetails.addRow(QLabel(" "), self.group_name_lbl)

												self.color = QLineEdit()
												self.color.setToolTip("selected color")
												self.color.setText(list_detail_background_color)
												self.background_color = QPushButton('Open Color Dialog', self)
												self.background_color.setToolTip('Opens color dialog')
												self.background_color.move(10, 10)
												self.background_color.clicked.connect(self.open_color_dialog)
												form_layout_listdetails.addRow(QLabel("List Background Color:"), self.background_color)
												form_layout_listdetails.addRow(QLabel(""), self.color)

												group_box_listdetails.setLayout(form_layout_listdetails)
												button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
												button_box.accepted.connect(self.store)
												button_box.rejected.connect(self.reject)

												main_layout = QVBoxLayout()
												main_layout.addWidget(group_box_module)
												main_layout.addWidget(group_box_listdetails)
												main_layout.addWidget(button_box)
												self.setLayout(main_layout)

												self.setTabOrder(self.group_name, self.background_color)

										else:
												self.user_cancelled = True
								else:
										logger.warning("No group available for copy, Please add one")
						else:
								self.user_cancelled = True
				else:
						logger.warning("No module available")

		def onChanged(self, text):
				if text == "":
						self.group_name_lbl.setText("need user input for group name")
						self.group_name_lbl.setStyleSheet('color: red;')
						logger.info("Please input Group name")
						return
				self.group_name_lbl.setText(" ")

		def open_color_dialog(self):
				color = QColorDialog.getColor()

				if color.isValid():
						self.color.setText(color.name())

		def center(self):
				qr = self.frameGeometry()
				cp = QDesktopWidget().availableGeometry().center()
				qr.moveCenter(cp)
				self.move(qr.topLeft())

		def store(self):
				if self.group_name.text().strip() == "":
						self.group_name_lbl.setText("Please provide group name")
						self.group_name_lbl.setStyleSheet('color: red;')
						logger.info("Please provide group name")
						return

				group_id = self.database_management.create_listdetails(self.group_name.text().strip(), self.color.text(),
																															 self.module_id)
				Signal_list = self.database_management.fetch_signallist_by_listid(self.list_detail_id)
				self.database_management.add_signallist_by_listid(group_id, Signal_list)
				logger.info("Group details copied successfully")
				self.accept()


class FrmShowModuleList(QDialog):

		def __init__(self, axes_list):
				super(FrmShowModuleList, self).__init__()
				self.setWindowTitle("Select Module for coping axes")

				self.setWindowIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'edit_1_24.png')))
				self.setModal(True)

				self.selected_items = []
				vbox_module_selection = QVBoxLayout(self)

				self.combo_box_selected_module = QComboBox()
				for module_detail in axes_list:
						self.combo_box_selected_module.addItem(str(module_detail[1]), module_detail)
				vbox_module_selection.addWidget(self.combo_box_selected_module)

				button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
				button_box.accepted.connect(self.accept)
				button_box.rejected.connect(self.reject)

				vbox_module_selection.addWidget(button_box)

				self.setLayout(vbox_module_selection)
				# self.setMinimumSize(300, 80)
				# self.setMaximumSize(300, 80)
				self.center()

		def get_selected_module(self):
				return self.combo_box_selected_module.itemData(self.combo_box_selected_module.currentIndex())

		def center(self):
				qr = self.frameGeometry()
				cp = QDesktopWidget().availableGeometry().center()
				qr.moveCenter(cp)
				self.move(qr.topLeft())


class FrmShowCustomSignalForm(QDialog):

		def __init__(self, name, selectedSignals, selectSignalForCustomExpressionInStandardTemplate):
				super(FrmShowCustomSignalForm, self).__init__()
				self.setWindowTitle(name + " Custom expression editor")
				# self.setWindowFlags(
				# 				QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.WindowCloseButtonHint |
				# QtCore.Qt.WindowMinimizeButtonHint)
				self.setWindowIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'add_custom_signal_24.png')))
				self.setModal(False)
				self.setMaximumSize(600, 200)
				self.center()
				selectSignalForCustomExpressionInStandardTemplate.signal.connect(self.addSignalsFromSelector)

				self.selected_custom_signals_list = []

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

				pbutton_numpy_where = QPushButton("WHERE")
				pbutton_numpy_where.setToolTip('numpy.where(condition [, x, y])')
				pbutton_numpy_where.clicked.connect(self.add_numpy_where)
				hboxlayout_numpy_buttons.addWidget(pbutton_numpy_where, 1, Qt.AlignLeft)

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

				pbutton_add_to_script = QPushButton("Add signal")
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
				self.custom_expression = None

		def verify_syntax(self):
				expression = self.lineedit_custom_signal_expression.toPlainText().strip()
				if expression == "":
						logger.error("Please provide custom signal expression")
						return
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
				if expression == "":
						logger.error("Please provide custom signal expression")
						return
				unit = self.lineedit_custom_signal_unit.text()

				if self.verify_syntax() is True:
						self.refresh_signal_list()

						if len(self.selected_custom_signals_list) == 0:
								logger.error("Signals have not added in the expression")
								return
						self.custom_expression = (name, self.selected_custom_signals_list, expression, unit)
						self.close()
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
				self.lineedit_custom_signal_expression.insertPlainText(" > ")

		def action_greater(self):
				self.lineedit_custom_signal_expression.insertPlainText(" < ")

		def action_greater_equal(self):
				self.lineedit_custom_signal_expression.insertPlainText(" <= ")

		def action_less_equal(self):
				self.lineedit_custom_signal_expression.insertPlainText(" >= ")

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

		def add_numpy_where(self):
				self.lineedit_custom_signal_expression.insertPlainText(" np.where(Condition, trueValue, falseValue) ")


class FrmCopyTemplate(QDialog):
		DatabaseManagement.db_file_path = DATABASE_PATH
		database_management = DatabaseManagement()

		def __init__(self, module_id):
				super(FrmCopyTemplate, self).__init__()

				self.module_id = module_id
				self.setWindowIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'add_1_24.png')))
				self.setModal(True)
				# self.setMinimumSize(300, 350)
				# self.setMaximumSize(300, 350)
				self.center()

				template_details = self.database_management.select_module_by_id(module_id)
				geometry_row, geometry_col = eval(template_details[8])
				self.setWindowTitle("Copy Module ")

				group_box_module = QGroupBox(" ")
				form_layout_module = QFormLayout()

				self.label_type_id = QLabel()
				self.type_id = template_details[9]
				self.type_info = self.database_management.select_type_by_id(self.type_id)
				self.label_type_id.setText(self.type_info[0])
				self.label_type_id.setToolTip("Module type")

				form_layout_module.addRow(QLabel("Module Type:"), self.label_type_id)
				group_box_module.setLayout(form_layout_module)

				group_box_module_summary = QGroupBox("")
				form_layout_module_summary = QFormLayout()
				self.module_name = QLineEdit()
				self.module_name.setText(template_details[1])
				self.module_name.setToolTip("Set module name")
				self.module_name.textChanged[str].connect(self.onChanged)
				form_layout_module_summary.addRow(QLabel("(*) Name:"), self.module_name)
				self.module_name_lbl = QLabel(self)
				form_layout_module_summary.addRow(QLabel(" "), self.module_name_lbl)

				self.description = QPlainTextEdit()
				self.description.setPlainText(template_details[2])
				self.description.setToolTip("Set description of module")
				form_layout_module_summary.addRow(QLabel("Module Description:"), self.description)

				self.txt_geometry_row = QLineEdit()
				self.txt_geometry_col = QLineEdit()
				self.txt_geometry_row.setText(str(geometry_row))
				self.txt_geometry_col.setText(str(geometry_col))
				self.txt_geometry_row.setToolTip("Set Geometry Row, Only applicable for Plots")
				self.txt_geometry_col.setToolTip("Set Geometry Column, Only applicable for Plots")
				form_layout_module_summary.addRow(QLabel("Geometry (Row):"), self.txt_geometry_row)
				form_layout_module_summary.addRow(QLabel("Geometry (Column):"), self.txt_geometry_col)

				group_box_module_summary.setLayout(form_layout_module_summary)
				group_box_module_image = QGroupBox("")
				form_layout_module_image = QFormLayout()
				self.img_btn = QPushButton('Select Image')
				self.img_btn.setToolTip("select image respective of module")
				self.img_btn.clicked.connect(self.get_image_file)

				self.labelImage = QLabel()
				form_layout_module_image.addRow(self.img_btn)
				form_layout_module_image.addRow(self.labelImage)
				group_box_module_image.setLayout(form_layout_module_image)

				button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
				button_box.accepted.connect(self.store)
				button_box.rejected.connect(self.cancel)

				main_layout = QVBoxLayout()
				main_layout.setSpacing(0)
				main_layout.setContentsMargins(1, 1, 1, 1)
				main_layout.addWidget(group_box_module)
				main_layout.addWidget(group_box_module_summary)
				main_layout.addWidget(group_box_module_image)
				main_layout.addWidget(button_box)
				self.setLayout(main_layout)
				self.setTabOrder(self.module_name, self.description)
				self.setTabOrder(self.description, self.img_btn)

				self.revision = float(template_details[4])

		def onChanged(self, text):
				if text == "":
						self.module_name_lbl.setText("need user input for module name")
						self.module_name_lbl.setStyleSheet('color: red;')
						logger.info("Please input module name")

						return
				self.module_name_lbl.setText(" ")


		def center(self):
				qr = self.frameGeometry()
				cp = QDesktopWidget().availableGeometry().center()
				qr.moveCenter(cp)
				self.move(qr.topLeft())

		def get_image_file(self):
				file_name, _ = QFileDialog.getOpenFileName(self, 'Open Image File', r"<Default dir>",
																									 "Image files (*.jpg *.jpeg *.png)")
				self.labelImage.setText(file_name)

		def store(self):
				if self.module_name.text().strip() == "":
						self.module_name_lbl.setText("Please provide module name")
						self.module_name_lbl.setStyleSheet('color: red;')
						logger.info("Please provide module name")
						return
				check_if_module_with_same_name_exists = self.database_management.select_module_by_name(
								self.module_name.text().strip())
				if check_if_module_with_same_name_exists is None:
						import getpass
						author_name = getpass.getuser()
						date = datetime.datetime.now()
						import math
						fractional, whole = math.modf(self.revision)

						if fractional > 0.20:
								revision = self.revision + 1
						else:
								revision = self.revision + 0.1



						module_id=self.database_management.create_module(self.module_name.text().strip(), self.description.toPlainText(),
																									 author_name,
																									 date, self.labelImage.text(), self.type_id, revision,
																									 self.txt_geometry_row.text().strip(),
																									 self.txt_geometry_col.text().strip())
						if  self.type_info[0] =="Plot":
								axes_list = self.database_management.select_plot_details_by_module_id(self.module_id)
								for axes in axes_list :
										self.plot_detail_id = axes[0]
										axes_id = self.database_management.create_axesdetails(axes[1], axes[2],axes[3], axes[4],axes[5], axes[6],module_id)
										Signal_list = self.database_management.fetch_signallist_by_plotid(self.plot_detail_id)
										self.database_management.add_signallist_by_plotid(axes_id, Signal_list)

						if self.type_info[0] =="List":
								group_list = self.database_management.select_list_details_by_module_id(self.module_id)
								for group in group_list:
										self.group_detail_id = group[0]
										group_id = self.database_management.create_listdetails(group[1],group[2],module_id)
										Signal_list = self.database_management.fetch_signallist_by_listid(self.group_detail_id)
										self.database_management.add_signallist_by_listid(group_id, Signal_list)

						logger.info("Module Copied successfully")
						self.close()

				else:
						self.module_name_lbl.setText("Module with same name exists, Please provide different module name")
						self.module_name_lbl.setStyleSheet('color: red;')
						logger.warning("Module with same name exists, Please provide different module name")
						return

		def cancel(self):
				self.close()
# </editor-fold>

