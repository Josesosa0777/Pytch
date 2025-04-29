import csv
import logging
import os

from PySide.QtCore import QRegExp, Qt
from PySide.QtGui import QAbstractItemView, QAction, QApplication, QDesktopWidget, \
		QDialog, \
		QDialogButtonBox, QDoubleValidator, QFileDialog, \
		QGridLayout, \
		QGroupBox, \
		QHeaderView, QIcon, QLabel, QLineEdit, \
		QMainWindow, QMenu, QMessageBox, QPushButton, QRegExpValidator, QSizePolicy, QStandardItem, QStandardItemModel, \
		QTreeView, \
		QVBoxLayout, QValidator, QWidget

IMAGE_DIRECTORY = os.path.join(os.path.dirname(__file__), "images")

logger = logging.getLogger()


class FrmAddEditEventEntry(QDialog):

		def __init__(self):
				super(FrmAddEditEventEntry, self).__init__()

				self.setModal(True)
				self.center()

				group_box_row_summary = QGroupBox(" ")
				form_gridlayout_row_summary = QGridLayout()
				form_gridlayout_row_summary.setColumnStretch(1, 4)
				form_gridlayout_row_summary.setColumnStretch(2, 4)

				self.lbl_measurement_name = QLabel("Select measurement :")
				form_gridlayout_row_summary.addWidget(self.lbl_measurement_name, 0, 0, 1, 1)
				self.txt_measurement_name = QLineEdit()
				self.txt_measurement_name.setToolTip("Set Measurement name")
				form_gridlayout_row_summary.addWidget(self.txt_measurement_name, 0, 1, 1, 1)
				self.btn_browse_measurement = QPushButton("Browse..")
				self.btn_browse_measurement.clicked.connect(self.select_measurement)
				form_gridlayout_row_summary.addWidget(self.btn_browse_measurement, 0, 2, 1, 1)

				self.lbl_start_time = QLabel("Start time[s] :")
				form_gridlayout_row_summary.addWidget(self.lbl_start_time, 1, 0, 1, 1)
				self.txt_start_time = QLineEdit()
				self.txt_start_time.setPlaceholderText("Example:1000.0")
				self.txt_start_time.setValidator(QRegExpValidator(QRegExp('^\d+.\d+$')))
				self.txt_start_time.textChanged.connect(self.on_start_time_changed)
				self.txt_start_time.setToolTip("Set start timestamp")
				form_gridlayout_row_summary.addWidget(self.txt_start_time, 1, 1, 1, 2)

				self.lbl_duration_time = QLabel("Duration[s] :")
				form_gridlayout_row_summary.addWidget(self.lbl_duration_time, 2, 0, 1, 1)
				self.txt_duration_time = QLineEdit()
				self.txt_duration_time.setText("2")
				self.txt_duration_time.setValidator(QRegExpValidator(QRegExp('^\d{2}$')))
				self.txt_duration_time.setToolTip("Set duration ")
				form_gridlayout_row_summary.addWidget(self.txt_duration_time, 2, 1, 1, 2)

				group_box_row_summary.setLayout(form_gridlayout_row_summary)

				button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
				button_box.accepted.connect(self.accept)
				button_box.rejected.connect(self.reject)

				main_layout = QVBoxLayout()
				main_layout.setSpacing(0)
				main_layout.setContentsMargins(1, 1, 1, 1)
				main_layout.addWidget(group_box_row_summary)
				main_layout.addWidget(button_box)
				self.setLayout(main_layout)
				self.setTabOrder(self.txt_measurement_name, self.txt_start_time)
				self.setTabOrder(self.txt_start_time, self.txt_duration_time)

		def on_start_time_changed(self):
				if self.txt_start_time.hasAcceptableInput():
						self.txt_start_time.setStyleSheet("color: none")
				else:
						self.txt_start_time.setStyleSheet("color: red")

		def select_measurement(self):
				path = QFileDialog.getOpenFileName(self, 'Open a file', '',
																					 'All Files (*.mat *.h5 *.mf4 *.mdf)')
				if os.path.isfile(path[0]) and os.path.exists(path[0]):
						self.txt_measurement_name.setText(str(path[0]))
				else:
						logger.error("Please select valid measurement")
				return

		def center(self):
				qr = self.frameGeometry()
				cp = QDesktopWidget().availableGeometry().center()
				qr.moveCenter(cp)
				self.move(qr.topLeft())

		def store(self):
				if (self.txt_measurement_name.text() == "" or self.txt_start_time.text() == "" or
								self.txt_duration_time.text() == ""):
						# logger.info("Please provide all fields")
						return None
				else:
						if os.path.exists(self.txt_measurement_name.text()) and os.path.isfile(self.txt_measurement_name.text()) \
										and self.txt_measurement_name.text().lower().endswith(('.h5', '.mat', '.mf4','*.mdf')):
								return [self.txt_measurement_name.text().strip(), self.txt_start_time.text().strip(),
												self.txt_duration_time.text().strip()]

		def cancel(self):
				self.close()


class cEventEditor(QMainWindow):
		def __init__(self, parent = None):
				super(cEventEditor, self).__init__(parent)
				self.filename = None
				self.pushAddEntry = QPushButton("Add Event Entry", self)
				self.pushAddEntry.setToolTip("Add Event Entry")
				self.pushAddEntry.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'add_24.png')))
				self.pushAddEntry.clicked.connect(self.add_entry)
				self.pushAddEntry.setFixedWidth(150)
				self.pushAddEntry.setStyleSheet(stylesheet(self))

				self.pushEditEntry = QPushButton("Edit Event Entry", self)
				self.pushEditEntry.setToolTip("Edit Event Entry")
				self.pushEditEntry.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'edit_24.png')))
				self.pushEditEntry.clicked.connect(self.edit_entry)
				self.pushEditEntry.setFixedWidth(150)
				self.pushEditEntry.setStyleSheet(stylesheet(self))

				self.pushDeleteEntry = QPushButton("Delete Event Entry", self)
				self.pushDeleteEntry.setToolTip("Delete Event Entry")
				self.pushDeleteEntry.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'remove_24.png')))
				self.pushDeleteEntry.clicked.connect(self.remove_entry)
				self.pushDeleteEntry.setFixedWidth(150)
				self.pushDeleteEntry.setStyleSheet(stylesheet(self))

				self.model_view_csv_events = QStandardItemModel(self)

				self.tree_view_csv_events = QTreeView(self)
				self.tree_view_csv_events.setStyleSheet(stylesheet(self))
				self.tree_view_csv_events.setModel(self.model_view_csv_events)
				self.tree_view_csv_events.setSelectionBehavior(QAbstractItemView.SelectRows)
				self.tree_view_csv_events.setEditTriggers(QAbstractItemView.NoEditTriggers)
				self.tree_view_csv_events.setSelectionMode(QAbstractItemView.SingleSelection)
				self.tree_view_csv_events.header().setResizeMode(QHeaderView.Stretch)
				self.tree_view_csv_events.setGeometry(10, 50, 780, 645)
				self.tree_view_csv_events.setAlternatingRowColors(True)
				self.tree_view_csv_events.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

				csvmanager_widget = QWidget()
				self.setCentralWidget(csvmanager_widget)
				csvmanager_vboxlayout = QVBoxLayout()

				button_gridlayout = QGridLayout()
				button_gridlayout.setSpacing(1)
				button_gridlayout.addWidget(self.pushAddEntry, 0, 0)
				button_gridlayout.addWidget(self.pushEditEntry, 0, 1)
				button_gridlayout.addWidget(self.pushDeleteEntry, 0, 2)

				csvmanager_vboxlayout.addWidget(self.tree_view_csv_events)
				csvmanager_vboxlayout.addLayout(button_gridlayout)
				csvmanager_widget.setLayout(csvmanager_vboxlayout)
				self.create_menu()

				self.headers = ["Full Measurement Path", "Start Time [s]", "Duration [s]"]
				self.model_view_csv_events.setHorizontalHeaderLabels(self.headers)

		def create_menu(self):
				menu_bar = self.menuBar()
				self.file_menu = QMenu('&File')

				actions = []

				action_new_csv = QAction('New', self.file_menu)
				action_new_csv.setShortcut(self.tr("Ctrl+N"))
				action_new_csv.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'new_file_40.png')))
				action_new_csv.triggered.connect(self.add_csv)
				actions.append(action_new_csv)

				action_open_csv = QAction('Open ', self.file_menu)
				action_open_csv.setShortcut(self.tr("Ctrl+O"))
				action_open_csv.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'load_file_16.png')))
				action_open_csv.triggered.connect(self.on_clicked_opencsv)
				actions.append(action_open_csv)

				action_save_csv = QAction('Save', self.file_menu)
				action_save_csv.setShortcut(self.tr("Ctrl+S"))
				action_save_csv.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'save_24.png')))
				action_save_csv.triggered.connect(self.on_clicked_savecsv)
				actions.append(action_save_csv)

				action_saveas_csv = QAction('Save As..', self.file_menu)
				action_saveas_csv.setShortcut(self.tr("Ctrl+Shift+S"))
				action_saveas_csv.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'save_as_40.png')))
				action_saveas_csv.triggered.connect(self.on_clicked_saveascsv)
				actions.append(action_saveas_csv)

				action_exit = QAction('Exit', self.file_menu)
				action_exit.setShortcut(self.tr("Alt+F4"))
				action_exit.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'exit_16.png')))
				action_exit.triggered.connect(self.close)
				actions.append(action_exit)

				for action in actions:
						self.file_menu.addAction(action)

				menu_bar.addMenu(self.file_menu)

		def open_csv(self, fileName):
				self.model_view_csv_events.clear()
				self.filename = fileName
				with open(fileName, "rb") as fileInput:
						reader = csv.reader(fileInput, delimiter = '|')
						skip_first_row = next(reader)
						self.model_view_csv_events.setHorizontalHeaderLabels(self.headers)
						for row in reader:
								item_measurement_path = QStandardItem(row[0])
								item_measurement_path.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'event_entry_24.png')))
								item_measurement_path.setEditable(False)
								item_start_time = QStandardItem(row[1])
								item_start_time.setEditable(False)
								item_duration_time = QStandardItem(row[2])
								item_duration_time.setEditable(False)
								self.model_view_csv_events.appendRow([item_measurement_path, item_start_time, item_duration_time])

		def save_csv(self, fileName):
				self.filename = fileName
				with open(fileName, "wb") as fileOutput:
						writer = csv.writer(fileOutput, delimiter = '|')
						writer.writerow(['fullmeas','start [s]','duration [s]'])
						for rowNumber in range(self.model_view_csv_events.rowCount()):
								fields = [self.model_view_csv_events.data(
												self.model_view_csv_events.index(rowNumber, columnNumber),
												Qt.DisplayRole).encode("utf-8")
													for columnNumber in range(self.model_view_csv_events.columnCount())]
								writer.writerow(fields)

		def on_clicked_saveascsv(self):
				result = QFileDialog.getSaveFileName(self, "save as csv file",
																						 '/events.csv',
																						 "CSV file (*.csv)")
				if result != ('', ''):
						self.save_csv(result[0])
						logger.info("Events csv saved as : %s" % result[0])
				else:
						logger.error("Please select valid file")

		def on_clicked_savecsv(self):
				if self.filename is None:
						result = QFileDialog.getSaveFileName(self, "save as csv file",
																								 '/events.csv',
																								 "CSV file (*.csv)")
						if result != ('', ''):
								self.save_csv(result[0])
								logger.info("Events csv saved as : %s" % result[0])
				else:
						self.save_csv(self.filename)
						logger.info("Events csv saved : %s" % self.filename)

		def on_clicked_opencsv(self):
				result = QFileDialog.getOpenFileName(self, "load csv file",
																						 'C:\\',
																						 "CSV file (*.csv )")
				if result != ('', '') and os.path.exists(result[0]):
						self.open_csv(result[0])
						logger.info("Events csv loaded : %s" % result[0])

				else:
						logger.error("Please select valid file")

		def remove_entry(self):
				item_selection_row = self.tree_view_csv_events.selectionModel()
				if len(item_selection_row.selectedIndexes()) != 0:
						msgBox = QMessageBox()
						msgBox.setText("Deleting Entry")
						msgBox.setInformativeText("Do you want to delete the entry?")
						msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
						msgBox.setDefaultButton(QMessageBox.Yes)
						ret = msgBox.exec_()
						if ret == QMessageBox.Yes:
								selected_index = item_selection_row.selectedIndexes()[0]
								self.model_view_csv_events.removeRow(selected_index.row())
				else:
						logger.info("Please select the entry first")

		def edit_entry(self):
				item_selection_row = self.tree_view_csv_events.selectionModel()
				if len(item_selection_row.selectedIndexes()) != 0:
						selected_index = item_selection_row.selectedIndexes()[0]
						dialog_edit_entry = FrmAddEditEventEntry()
						dialog_edit_entry.setWindowTitle("Edit Row")
						dialog_edit_entry.setWindowIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'edit_24.png')))
						dialog_edit_entry.txt_measurement_name.setText(
								selected_index.sibling(selected_index.row(), selected_index.column()).data())
						dialog_edit_entry.txt_start_time.setText(
								selected_index.sibling(selected_index.row(), selected_index.column() + 1).data())
						dialog_edit_entry.txt_duration_time.setText(
								selected_index.sibling(selected_index.row(), selected_index.column() + 2).data())
						result = dialog_edit_entry.exec_()
						if result == QDialog.Accepted:
								rowItem = dialog_edit_entry.store()
								if rowItem is not None:
										item_measurement_path = QStandardItem(rowItem[0])
										item_measurement_path.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'event_entry_24.png')))
										item_measurement_path.setEditable(False)
										item_start_time = QStandardItem(rowItem[1])
										item_start_time.setEditable(False)
										item_duration_time = QStandardItem(rowItem[2])
										item_duration_time.setEditable(False)
										self.model_view_csv_events.setItem(selected_index.row(), 0, item_measurement_path)
										self.model_view_csv_events.setItem(selected_index.row(), 1, item_start_time)
										self.model_view_csv_events.setItem(selected_index.row(), 2, item_duration_time)
								else:
										logger.warning("Please provide correct data for the entry")
				else:
						logger.info("Please select the entry first")

		def add_entry(self):
				dialog_add_entry = FrmAddEditEventEntry()
				dialog_add_entry.setWindowTitle("Add Row")
				dialog_add_entry.setWindowIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'add_24.png')))
				result = dialog_add_entry.exec_()
				if result == QDialog.Accepted:
						rowItem = dialog_add_entry.store()
						if rowItem is not None:
								item_measurement_path = QStandardItem(rowItem[0])
								item_measurement_path.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'event_entry_24.png')))
								item_measurement_path.setEditable(False)
								item_start_time = QStandardItem(rowItem[1])
								item_start_time.setEditable(False)
								item_duration_time = QStandardItem(rowItem[2])
								item_duration_time.setEditable(False)
								self.model_view_csv_events.appendRow([item_measurement_path, item_start_time, item_duration_time])
						else:
								logger.warning("Please provide correct data for the entry")

		def add_csv(self):
				self.model_view_csv_events.clear()
				self.headers = ["Full Measurement Path", "Start Time [s]", "Duration [s]"]
				self.model_view_csv_events.setHorizontalHeaderLabels(self.headers)
				self.filename=None

def stylesheet(self):
		return """
				QTableView
				{
			border: 1px solid grey;
			border-radius: 0px;
			font-size: 12px;
		  background-color: #f8f8f8;
			selection-color: black;
			selection-background-color: lightblue;
				}

		QPushButton
		{
			font-size: 10px;
			border: 1px inset grey;
			height: 24px;
			width: 80px;
			color: black;
			background-color: #e8e8e8;
			background-position: bottom-left;
		} 
		QPushButton::hover
		{
			border: 1px inset goldenrod;
			font-weight: bold;
			color: black;
			background-color: lightblue;
		} 
	"""


if __name__ == "__main__":
		import sys

		app = QApplication(sys.argv)
		# app.setApplicationName('NewWindow')
		main = cEventEditor()
		#    main.setMaximumSize(800, 700)
		main.setMinimumSize(800, 300)
		main.setGeometry(100, 100, 800, 500)
		main.setWindowTitle("Event Editor")
		main.setWindowIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'event_editor_24.png')))
		main.show()

		sys.exit(app.exec_())
