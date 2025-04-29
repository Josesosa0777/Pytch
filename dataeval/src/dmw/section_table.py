# -*- coding: utf-8 -*-

import logging
import os
import webbrowser
from urllib import pathname2url

from PySide import QtGui, QtCore
from PySide.QtGui import QIcon

from interface.modules import ModuleName
from section_models import AllModuleModel, ActiveModuleModel, AllGroupModel, \
		ActGroupModel
from section_delegates import StarDelegate, ParamDelegate, CheckBoxDelegate
from interface.module import Parameter

IMAGE_DIRECTORY = os.path.join(os.path.dirname(__file__), "images")


class SimpleSignal(QtCore.QObject):
		signal = QtCore.Signal()


class SectionFrame(QtGui.QFrame):
		VALUE = ''

		def __init__(self, config, section, sub_from_option, sub_to_option,
								 sortbys):
				QtGui.QFrame.__init__(self)
				self.config = config
				self.section = section
				self.table = QtGui.QTableView()
				self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
				self.table.setModel(self.table_model)
				self.table.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
				self.table.setEditTriggers(QtGui.QAbstractItemView.AllEditTriggers)
				self.table.doubleClicked.connect(self.set_modules)
				horizontalHeader = self.table.horizontalHeader()
				horizontalHeader.sectionClicked.connect(self._onSort)
				horizontalHeader.setResizeMode(self.table_model.columnCount() - 1,
																			 QtGui.QHeaderView.Stretch)
				self.vbox = QtGui.QVBoxLayout()
				self.vbox.setSpacing(1)
				self.vbox.setContentsMargins(1, 1, 1, 1)
				self.vbox.addWidget(self.table)
				self.init()
				self.update_config_signal = SimpleSignal()
				self.update_standard_templates = SimpleSignal()
				self.update_config_signal.signal.connect(self.config.update)
				self.setLayout(self.vbox)
				self.alignHeader2Content()
				return

		def init(self):
				return

		def _onSort(self, index):
				self.table_model._onSort(index)
				return

		def keyPressEvent(self, event):
				if event.key() == QtCore.Qt.Key_Control:
						self.table_model.control_pressed = True
				if (event.key() == QtCore.Qt.Key_Enter or \
						event.key() == QtCore.Qt.Key_Return) and \
								self.focusWidget() == self.table:
						self.set_modules(None)
				QtGui.QFrame.keyPressEvent(self, event)
				return

		def keyReleaseEvent(self, event):
				if event.key() == QtCore.Qt.Key_Control:
						self.table_model.control_pressed = False
				QtGui.QFrame.keyReleaseEvent(self, event)
				return

		def get_selected_modules(self):
				modules = []
				selection_model = self.table.selectionModel()
				selected_cells = selection_model.selectedIndexes()
				last_row = set()
				for cell in selected_cells:
						row = cell.row()
						if row in last_row:
								continue

						model = cell.model()
						module = model.get_modulename_from_table(row)
						last_row.add(row)
						modules.append(module)
				return modules

		def get_active_modules(self):
				modules = []
				model = self.table.model()
				for row in range(model.rowCount()):
						module = model.get_modulename_from_table(row)
						modules.append(module)
				return modules

		def set_modules(self, dummy):
				modules = self.get_selected_modules()
				for module in modules:
						self.config.set(self.section, module, self.VALUE)
				self.update_config_signal.signal.emit()
				self.refresh_signal.signal.emit()
				self.update_standard_templates.signal.emit()
				return

		def refresh_elemnents(self):
				self.table_model.get_elements()
				self.update_config_signal.signal.emit()
				return

		def alignHeader2Content(self):
				for i in range(len(self.table_model.HEADER)):
						self.table.resizeColumnToContents(i)
				return


###
# AllGroupFrame is intended to inherit from SectionFrame.
# It does not work for some reason, unless an intermediate GroupFrame
# class is defined and used in the inheritance chain.
# TODO: find root cause and remove GroupFrame
###
class GroupFrame(SectionFrame):
		def dummy(self):
				return


class AllGroupFrame(GroupFrame):
		VALUE = 'yes'

		def __init__(self, config, section, sub_from_option = '', sub_to_option = '',
								 sortbys = [('Favs.', False), ]):
				self.table_model = AllGroupModel(config, section, sub_from_option,
																				 sub_to_option, sortbys)
				GroupFrame.__init__(self, config, section, sub_from_option, sub_to_option,
														sortbys)

				self.refresh_signal = SimpleSignal()
				grid = QtGui.QGridLayout()

				query_by = 'pos_grp_tags', 'neg_grp_tags',

				self.queries = {}
				self.match_case_btns = {}
				for i, name in enumerate(query_by):
						query = QtGui.QLineEdit()
						query.returnPressed.connect(self.filt)
						self.queries[name] = query
						grid.addWidget(query, i, 0)
						query.textChanged.connect(self.filt)

						btn = QtGui.QPushButton('aA')
						grid.addWidget(btn, i, 1)
						btn.setMaximumWidth(25)
						btn.setCheckable(True)
						btn.setToolTip('Turn matchcase on/off for filter')
						btn.clicked.connect(self.filt)
						self.match_case_btns[name] = btn

				self.vbox.addLayout(grid)
				self.insertHelp()
				return

		def init(self):
				GroupFrame.init(self)
				for i, h in enumerate(self.table_model.HEADER):
						if h == 'Favs.':
								delegate = StarDelegate()
								self.table.setItemDelegateForColumn(i, delegate)
								self.table.itemDelegateForColumn(i)
				return

		def insertHelp(self):
				self.queries['pos_grp_tags'].setPlaceholderText('Positive Group Filter')
				self.queries['pos_grp_tags'].setToolTip(
								'Filter tags can be added to reduce the number of the groups' +
								'\nThe tags have to be separated by SPACE.' +
								'\nThe entry collects the tags that GROUP names WILL contain' +
								'\nPress ENTER to run the filtering over the groups.'
				)
				self.queries['neg_grp_tags'].setPlaceholderText('Negative Group Filter')
				self.queries['neg_grp_tags'].setToolTip(
								'Filter tags can be added to reduce the number of the groups' +
								'\nThe tags have to be separated by SPACE.' +
								'\nThe entry collects the tags that PROJECT names WONT contain' +
								'\nPress ENTER to run the filtering over the groups.'
				)
				return

		def filt(self):
				QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
				pos_grp_tag = self.queries['pos_grp_tags'].text()
				pos_grp_tags = pos_grp_tag.split()
				neg_grp_tag = self.queries['neg_grp_tags'].text()
				neg_grp_tags = neg_grp_tag.split()

				pos_grp_tag_mc = self.match_case_btns['pos_grp_tags'].isChecked()
				neg_grp_tag_mc = self.match_case_btns['neg_grp_tags'].isChecked()

				self.table_model.query_elements(pos_grp_tags, neg_grp_tags,
																				pos_grp_tag_mc, neg_grp_tag_mc)

				QtGui.QApplication.restoreOverrideCursor()
				return


class ActGroupFrame(GroupFrame):
		VALUE = 'no'

		def __init__(self, config, section, sub_from_option = '', sub_to_option = '',
								 sortbys = [('Group', True), ]):
				self.table_model = ActGroupModel(config, section, sub_from_option,
																				 sub_to_option, sortbys)
				GroupFrame.__init__(self, config, section, sub_from_option, sub_to_option,
														sortbys)
				self.refresh_signal = SimpleSignal()
				return

		def set_modules(self, dummy):
				GroupFrame.set_modules(self, dummy)
				self.table_model.get_elements()
				return


class ModuleFrame(SectionFrame):
		def init(self):
				for i, h in enumerate(self.table_model.HEADER):
						if h == 'Params':
								delegate = ParamDelegate()
								self.table.setItemDelegateForColumn(i, delegate)
								self.table.itemDelegateForColumn(i)
				return


class AllModuleFrame(ModuleFrame):
		VALUE = 'yes'

		def __init__(self, config, section, sub_from_option = '', sub_to_option = '',
								 sortbys = [('Favs.', False), ]):
				self.table_model = AllModuleModel(config, section, sub_from_option,
																					sub_to_option, sortbys)
				ModuleFrame.__init__(self, config, section, sub_from_option, sub_to_option,
														 sortbys)

				self.refresh_signal = SimpleSignal()
				grid = QtGui.QGridLayout()

				query_by = 'pos_prj_tags', 'pos_mod_tags', 'pos_param_tags', \
									 'neg_prj_tags', 'neg_mod_tags', 'neg_param_tags'

				self.queries = {}
				self.match_case_btns = {}
				for i, name in enumerate(query_by):
						row = i >= (len(query_by) / 2)
						column = 2 * i % 6
						query = QtGui.QLineEdit()
						query.returnPressed.connect(self.filt)
						query.textChanged.connect(self.filt)
						self.queries[name] = query
						grid.addWidget(query, row, column)
						btn = QtGui.QPushButton('aA')
						grid.addWidget(btn, row, column + 1)
						btn.setMaximumWidth(25)
						btn.setCheckable(True)
						btn.setToolTip('Turn matchcase on/off for filter')
						btn.clicked.connect(self.filt)
						self.match_case_btns[name] = btn

				self.vbox.addLayout(grid)
				self.insertHelp()
				return

		def init(self):
				ModuleFrame.init(self)
				for i, h in enumerate(self.table_model.HEADER):
						if h == 'Favs.':
								delegate = StarDelegate()
								self.table.setItemDelegateForColumn(i, delegate)
								self.table.itemDelegateForColumn(i)
				return

		def insertHelp(self):
				self.queries['pos_prj_tags'].setPlaceholderText(
								'Positive Subproject Filter')
				self.queries['pos_prj_tags'].setToolTip(
								'Filter tags can be added to reduce the number of the modules' +
								'\nThe tags have to be separated by SPACE.' +
								'\nThe entry collects the tags that SUBPROJECT names WILL contain' +
								'\nPress ENTER to run the filtering over the modules.'
				)
				self.queries['neg_prj_tags'].setPlaceholderText(
								'Negative Subproject Filter')
				self.queries['neg_prj_tags'].setToolTip(
								'Filter tags can be added to reduce the number of the modules' +
								'\nThe tags have to be separated by SPACE.' +
								'\nThe entry collects the tags that SUBPROJECT names WONT contain' +
								'\nPress ENTER to run the filtering over the modules.'
				)

				self.queries['pos_mod_tags'].setPlaceholderText('Positive Module Filter')
				self.queries['pos_mod_tags'].setToolTip(
								'Filter tags can be added to reduce the number of the modules' +
								'\nThe tags have to be separated by SPACE.' +
								'\nThe entry collects the tags that MODULE names WILL contain' +
								'\nPress ENTER to run the filtering over the modules.'
				)
				self.queries['neg_mod_tags'].setPlaceholderText('Negative Module Filter')
				self.queries['neg_mod_tags'].setToolTip(
								'Filter tags can be added to reduce the number of the modules' +
								'\nThe tags have to be separated by SPACE.' +
								'\nThe entry collects the tags that MODULE names WONT contain' +
								'\nPress ENTER to run the filtering over the modules.'
				)

				self.queries['pos_param_tags'].setPlaceholderText('Positive Param Filter')
				self.queries['pos_param_tags'].setToolTip(
								'Filter tags can be added to reduce the number of the modules' +
								'nThe tags have to be separated by SPACE.' +
								'\nThe entry collects the tags that PARAM names WILL contain' +
								'\nPress ENTER to run the filtering over the modules.'
				)
				self.queries['neg_param_tags'].setPlaceholderText('Negative Param Filter')
				self.queries['neg_param_tags'].setToolTip(
								'Filter tags can be added to reduce the number of the modules' +
								'\nThe tags have to be separated by SPACE.' +
								'\nThe entry collects the tags that PARAM names WONT contain' +
								'\nPress ENTER to run the filtering over the modules.'
				)
				return

		def filt(self):
				QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
				pos_prj_tag = self.queries['pos_prj_tags'].text()
				pos_prj_tags = pos_prj_tag.split()
				neg_prj_tag = self.queries['neg_prj_tags'].text()
				neg_prj_tags = neg_prj_tag.split()

				pos_mod_tag = self.queries['pos_mod_tags'].text()
				pos_mod_tags = pos_mod_tag.split()
				neg_mod_tag = self.queries['neg_mod_tags'].text()
				neg_mod_tags = neg_mod_tag.split()

				pos_param_tag = self.queries['pos_param_tags'].text()
				pos_param_tags = pos_param_tag.split()
				neg_param_tag = self.queries['neg_param_tags'].text()
				neg_param_tags = neg_param_tag.split()

				pos_prj_tag_mc = self.match_case_btns['pos_prj_tags'].isChecked()
				neg_prj_tag_mc = self.match_case_btns['neg_prj_tags'].isChecked()
				pos_mod_tag_mc = self.match_case_btns['pos_mod_tags'].isChecked()
				neg_mod_tag_mc = self.match_case_btns['neg_mod_tags'].isChecked()
				pos_param_tag_mc = self.match_case_btns['pos_param_tags'].isChecked()
				neg_param_tag_mc = self.match_case_btns['neg_param_tags'].isChecked()

				self.table_model.query_elements(pos_prj_tags, pos_mod_tags, pos_param_tags,
																				neg_prj_tags, neg_mod_tags, neg_param_tags,
																				pos_prj_tag_mc, pos_mod_tag_mc, pos_param_tag_mc,
																				neg_prj_tag_mc, neg_mod_tag_mc, neg_param_tag_mc)

				QtGui.QApplication.restoreOverrideCursor()
				return

		def show_module_info(self):
				selection_model = self.table.selectionModel()
				selected_cells = selection_model.selectedIndexes()
				last_row = set()
				for cell in selected_cells:
						row = cell.row()
						if row in last_row:
								continue

						model = cell.model()
						module = model.get_modulename_from_table(row).split('@')
						module.reverse()
						last_row.add(row)

						url = 'file:{}'.format(pathname2url(
										os.path.join(
														os.path.abspath(r'..\..\dataevalaebs\doc\build\html'),
														(module[0] + r".html")
										)))
						id = "#" + module[0] + "-" + module[1] + '-module'
						webbrowser.open(url + id)


class ActModuleFrame(ModuleFrame):
		VALUE = 'no'

		def __init__(self, config, section, sub_from_option = '', sub_to_option = '',
								 sortbys = [('Acts.', True), ]):
				self.table_model = ActiveModuleModel(config, section, sub_from_option,
																						 sub_to_option, sortbys)
				ModuleFrame.__init__(self, config, section, sub_from_option, sub_to_option,
														 sortbys)

				self.param_layout = []
				self.refresh_signal = SimpleSignal()

				activate_btn = QtGui.QPushButton('Activate')
				self.clone_btn = QtGui.QPushButton('Clone')
				hbox = QtGui.QHBoxLayout()
				hbox.addWidget(activate_btn)
				hbox.addWidget(self.clone_btn)

				self.vbox.addLayout(hbox)

				activate_btn.clicked.connect(self.activate_param)
				self.clone_btn.clicked.connect(self.clone_param)

				selection_model = self.table.selectionModel()
				selection_model.selectionChanged.connect(self.selection_changed)
				self.temp_param_name = None
				self.selected_mod = None
				self.selected_prj = None
				return

		def clear_parameter_interface(self):
				for parameter_layout in self.param_layout:
						parameter_layout.close()
				self.param_layout = []
				self.selected_mod = None
				self.selected_prj = None
				return

		def selection_changed(self, selecteds, deselecteds):
				selecteds = self.table.selectedIndexes()

				if len(selecteds) != len(self.table_model.HEADER):
						self.clone_btn.setEnabled(False)
				else:
						self.clone_btn.setEnabled(True)
				return

		def clone_param(self):
				self.clear_parameter_interface()
				module = self.get_selected_modules()
				if not module:
						self.config.log('No module was selected!', logging.ERROR)
						return
				module, = module
				params = self.table_model.elements[module]['Params']
				if len(params) < 1:
						self.config.log('No parameter was selected!', logging.ERROR)
						return
				elif len(params) > 1:
						self.config.log('Too many parameters were selected, cloning is '
														'supported only for 1 parameter!', logging.ERROR)
						return
				param, = params
				mod, _, prj = ModuleName.split(module)
				self.temp_param_name, params = self.config.cloneModuleParam(mod, param, prj)

				if params:
						self.selected_mod = mod
						self.selected_prj = prj

				for name, value in params:
						param_label = QtGui.QLabel(name)
						param_value = QtGui.QLineEdit()
						param_value.setText(value)

						frame = QtGui.QFrame()

						param_hbox = QtGui.QHBoxLayout()
						param_hbox.addWidget(param_label)
						param_hbox.addWidget(param_value)
						frame.setLayout(param_hbox)
						frame.label = param_label
						frame.value = param_value
						self.param_layout.append(frame)

						self.vbox.addWidget(frame)
				return

		def activate_param(self):
				if not self.temp_param_name or not self.param_layout:
						return

				param_str_list = [(param_layout.label.text(), param_layout.value.text())
													for param_layout in self.param_layout]
				params = Parameter.from_str_list(param_str_list)
				param_list = params.to_str()
				self.config.param(self.selected_mod, self.temp_param_name,
													self.selected_prj, param_list)
				self.config.update()
				self.clear_parameter_interface()
				self.refresh_elemnents()
				return

		def init(self):
				ModuleFrame.init(self)
				for i, h in enumerate(self.table_model.HEADER):
						if h == 'Acts.':
								delegate = CheckBoxDelegate()
								self.table.setItemDelegateForColumn(i, delegate)
								self.table.itemDelegateForColumn(i)
				return

		def set_modules(self, dummy):
				ModuleFrame.set_modules(self, dummy)
				self.table_model.get_elements()
				return


class SectionFrame(QtGui.QFrame):
		def __init__(self, config, section, sub_from_option = '', sub_to_option = ''):
				QtGui.QFrame.__init__(self)
				signal = self.all_module_frame.refresh_signal.signal
				signal.connect(self.act_module_frame.refresh_elemnents)
				signal.connect(self.all_module_frame.table_model.redraw)
				signal = self.act_module_frame.refresh_signal.signal
				signal.connect(self.all_module_frame.table_model.redraw)
				module_info_btn = QtGui.QPushButton()
				module_info_btn.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, "information_16.png")))
				module_info_btn.clicked.connect(self.modules_info)

				to_active_btn = QtGui.QPushButton('-->')
				from_active_btn = QtGui.QPushButton('<--')
				for btn in (module_info_btn,to_active_btn, from_active_btn):
						btn.setFixedSize(25, 25)
				to_active_btn.clicked.connect(self.activate_modules)
				from_active_btn.clicked.connect(self.deactivate_modules)
				vbox = QtGui.QVBoxLayout()
				vbox.addWidget(module_info_btn)
				vbox.addWidget(to_active_btn)
				vbox.addWidget(from_active_btn)
				vbox.setAlignment(QtCore.Qt.AlignVCenter)
				act_vbox = QtGui.QVBoxLayout()
				all_vbox = QtGui.QVBoxLayout()
				act_label = QtGui.QLabel('Actives')
				all_label = QtGui.QLabel('All')
				for label, layout in zip([act_label, all_label], [act_vbox, all_vbox]):
						layout.addWidget(label)
						layout.setAlignment(label, QtCore.Qt.AlignHCenter)

				act_vbox.addWidget(self.act_module_frame)
				layout = QtGui.QHBoxLayout()
				all_vbox.addWidget(self.all_module_frame)
				layout.addLayout(all_vbox)
				layout.addLayout(vbox)
				layout.addLayout(act_vbox)

				self.setLayout(layout)
				return

		def modules_info(self):
				self.all_module_frame.show_module_info()
				return

		def activate_modules(self):
				self.all_module_frame.set_modules(None)
				return

		def deactivate_modules(self):
				self.act_module_frame.set_modules(None)
				return


class ModuleTableFrame(SectionFrame):
		def __init__(self, config, section, sub_from_option = '', sub_to_option = ''):
				self.all_module_frame = AllModuleFrame(config, section,
																							 sub_from_option = sub_from_option,
																							 sub_to_option = sub_to_option)

				self.act_module_frame = ActModuleFrame(config, section,
																							 sub_from_option = sub_from_option,
																							 sub_to_option = sub_to_option)

				SectionFrame.__init__(self, config, section,
															sub_from_option = sub_from_option, sub_to_option = sub_to_option)
				return


class GroupTableFrame(SectionFrame):
		def __init__(self, config, section, sub_from_option = '', sub_to_option = ''):
				self.all_module_frame = AllGroupFrame(config, section,
																							sub_from_option = sub_from_option,
																							sub_to_option = sub_to_option)

				self.act_module_frame = ActGroupFrame(config, section,
																							sub_from_option = sub_from_option,
																							sub_to_option = sub_to_option)

				SectionFrame.__init__(self, config, section,
															sub_from_option = sub_from_option, sub_to_option = sub_to_option)
				return


if __name__ == '__main__':
		from datavis import pyglet_workaround  # necessary as early as possible (#164)

		import sys
		from argparse import ArgumentParser, RawTextHelpFormatter

		from config.Config import Config
		from config.helper import procConfigFile, getConfigPath
		from config.modules import Modules
		from dmw.sessionframes import MassFrame

		modules_name = getConfigPath('modules', '.csv')
		modules = Modules()
		modules.read(modules_name)

		sys.argv.append('--nosave')

		parser = ArgumentParser(formatter_class = RawTextHelpFormatter)
		args = Config.addArguments(parser).parse_args()
		name = procConfigFile('dataeval', args)
		config = Config(name, modules)
		config.init(args)

		app = QtGui.QApplication([])

		mod_frame = ModuleTableFrame(config, 'iView', )
		mod_frame.show()
		app_status = app.exec_()
		config.save()

		sys.exit(-1)
