import os
import json
import time
import re
import requests
import logging

from PySide import QtGui, QtCore
from PySide.QtCore import Qt
from PySide.QtGui import QDialog, QGroupBox, QIcon, QLabel, QListWidget, \
  QListWidgetItem, \
  QPushButton, QVBoxLayout

from interface.modules import ModuleName
IMAGE_DIRECTORY = os.path.join(os.path.dirname(__file__), "images")

class SimpleSignal(QtCore.QObject):
  signal = QtCore.Signal()

class LineEdit(QtGui.QLineEdit):
  def __init__(self, *args, **kwargs):
    QtGui.QLineEdit.__init__(self, *args, **kwargs)
    self.click_signal = SimpleSignal()
    self.clicked = self.click_signal.signal
    return

  def mousePressEvent(self, event):
    self.clicked.emit()
    QtGui.QLineEdit.mousePressEvent(self, event)
    return

class cOption(QtGui.QFrame):
  def __init__(self, root, Config, Section, Option):
    QtGui.QFrame.__init__(self)
    self.Config = Config
    self.Section = Section
    self.Option = Option
    pass

  def reset(self):
    pass

  def save(self):
    return

class cFileOption(cOption):
  def __init__(self, root, Config, Section, Option, **kwargs):
    cOption.__init__(self, root, Config, Section, Option)
    self.Label = QtGui.QLabel(Option)
    self.Value = LineEdit('')
    self.knoobleLabel = QtGui.QLabel('Knooble Result:')
    self.knoobleValue = QtGui.QComboBox()
    self.knoobleValue.currentIndexChanged.connect(self.selectionChange)
    self.knoobleValue.addItem('')
    self.Value.editingFinished.connect(self.onReturn)
    self.OpenFileBtn = QtGui.QPushButton('')
    self.knoobleQBtn = QtGui.QPushButton('')
    self.knoobleQBtn.setToolTip('Knooble search')
    self.knoobleQBtn.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'knoobleSearch.png')))
    self.knoobleQBtn.clicked.connect(self.updateKnoobleResult)
    self.OpenFileBtn.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'browse_24.png')))
    self.OpenFileBtn.setToolTip("Browse Files")
    self.OpenFileBtn.clicked.connect(self.find)

    self.is_save_last_files=False
    self.file_type=''
    self.OpenLastUsedFileBtn = QtGui.QPushButton('')
    self.OpenLastUsedFileBtn.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'history_24.png')))

    self.OpenLastUsedFileBtn.setToolTip("Select Previously Opened Files")
    self.UpdateSignal = SimpleSignal()
    self.kwargs = kwargs
    self.enable()
    self.update()
    pass

  def onReturn(self):
    Value = self.Value.text()
    self.Config.set(self.Section, self.Option, Value)
    if self.is_save_last_files is True:
      self.save_last_files(Value)
    if not os.path.exists(Value):
      self.logNotExistWarning(Value)
    return

  def logNotExistWarning(self, Value):
    self.Config.log("'%s' at '%s' does not exist (yet)" %
                    (self.Option or '', Value), Level=logging.WARNING)
    return

  def ask(self, **kwargs):
    fileName, ext = QtGui.QFileDialog.getOpenFileName(**kwargs)
    return fileName

  def find(self):
    Value = self.Config.get(self.Section, self.Option)
    Dir = os.path.dirname(Value)
    self.kwargs['dir'] = Dir
    Value = self.ask(**self.kwargs)
    if Value:
      Value = os.path.abspath(Value)
      self.Config.set(self.Section, self.Option, Value)
      if self.is_save_last_files is True:
        self.save_last_files(Value)
      self.update()
      self.reset()
      self.Config.update()
    pass

  def updateKnoobleCombo(self, file, cnt):
    self.knoobleValue.addItem(file)
    self.knoobleValue.setItemData(cnt, str(file), QtCore.Qt.ToolTipRole)
    self.Config.log("'%s'" %
                    file, Level=logging.INFO)
    cnt += 1
    return cnt

  def updateKnoobleResult(self):
    query = self.Value.text()
    self.knoobleValue.clear()
    self.Value.setText(query)

    rrec_regex_date_pattern = "\d{4}.\d{2}.\d{2}_at_\d{2}.\d{2}.\d{2}"
    h5_regex_date_pattern = "\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}"
    rrec_res = re.compile(rrec_regex_date_pattern).findall(query)

    h5_res = re.compile(h5_regex_date_pattern).findall(query)
    if query != "" and (len(rrec_res) > 0 or len(h5_res) > 0) and (
            query.endswith(".mat") or query.endswith(".h5") or query.endswith(".rrec")):
      url = 'http://bu2s0069:5023/knoobleSearch/convertedmeasurements'
      myobj = {"search": query}
      startTime = time.time()
      try:
        x = requests.post(url, json=myobj)
        output = json.loads(x.text)
      except Exception as e:
        self.Config.log(
          "Failed to establish a connection!!!\n No connection could be made because the target machine actively refused it",
          Level=logging.ERROR)
        output = {}
        return
      executionTime = (time.time() - startTime)
      self.Config.log('Total search Execution time in seconds: ' + str(executionTime), Level=logging.INFO)

      self.Config.log("Search Query: '%s'" %
                      query, Level=logging.INFO)
      result = None
      if output.has_key('convertedFiles'):
        result = output['convertedFiles']

      if result:
        startTime = time.time()
        cnt = 0
        for data in result:
          if data.has_key('filePath'):
            if str(query).endswith('.mat'):
              if str(data['filePath']).endswith('.mat'):
                cnt = self.updateKnoobleCombo(data['filePath'], cnt)
            elif str(query).endswith('.h5'):
              if str(data['filePath']).endswith('.h5'):
                cnt = self.updateKnoobleCombo(data['filePath'], cnt)
            else:
              if str(data['filePath']).endswith('.h5') or str(data['filePath']).endswith('.mat'):
                cnt = self.updateKnoobleCombo(data['filePath'], cnt)

        executionTime = (time.time() - startTime)
      else:
        self.Config.log('No convertedFiles found...', Level=logging.WARNING)
      self.Config.log('Total UI updation time in seconds: ' + str(executionTime), Level=logging.INFO)
    else:
      self.Config.log(
        "Filename does not match standard Pytch naming pattern !! format should be filename.h5/mat/rrec !!",
        Level=logging.ERROR)

  def selectionChange(self):
    selected_mesurement = self.knoobleValue.currentText()
    self.Value.setText(selected_mesurement)
    if self.knoobleValue.currentText() != u'':
      self.Config.log("" + self.knoobleValue.currentText() + " is selected..", Level=logging.INFO)
      self.Config.set(self.Section, self.Option, selected_mesurement)

  def save_last_files(self, selected_measurement):
    if self.Config.has_section("PathHistory"):
      last_opened_csv = self.Config.get("PathHistory", self.file_type)
      if last_opened_csv.strip() == '':
        last_opened_csv = []
      else:
        last_opened_csv = last_opened_csv.split(",")


      if selected_measurement not in last_opened_csv:
        if len(last_opened_csv) >= 20:
          last_opened_csv.pop(0)
        last_opened_csv.append(selected_measurement)
      last_opened_csv = ",".join(last_opened_csv)
      self.Config.set("PathHistory", self.file_type, last_opened_csv)

  def showLastOpenedFilesDialog(self):
    screen_location = self.OpenLastUsedFileBtn.mapToGlobal(QtCore.QPoint(0, 0))
    if self.Config.has_section("PathHistory"):
      last_opened_measurements_csv = self.Config.get("PathHistory", self.file_type)

      if last_opened_measurements_csv.strip() != '':
        last_opened_measurements_set = last_opened_measurements_csv.split(",")
        objShowLastOpenedFiles = FrmShowLastOpenedFiles(self.Config, last_opened_measurements_set,  screen_location)
        objShowLastOpenedFiles.show()
        if objShowLastOpenedFiles.exec_():
          selected_mesurement = objShowLastOpenedFiles.selected_measurement()
          if os.path.exists(selected_mesurement):
            selected_mesurement = os.path.abspath(selected_mesurement)
            self.Config.set(self.Section, self.Option, selected_mesurement)
            self.update()
            self.reset()
            self.Config.update()
      else:
        logging.warning("No recent files found")
    else:
      logging.warning("No Path History found")

  def update(self):
    if not self.Option:
      return
    Value = self.Config.get(self.Section, self.Option)
    self.Value.setText(Value)
    self.Value.setToolTip(Value)
    pass

  def enable(self):
    self.OpenFileBtn.setEnabled(True)
    self.Value.setEnabled(True)
    pass

  def disable(self):
    self.OpenFileBtn.setEnabled(False)
    self.Value.setEnabled(False)
    pass

class cLazyFileOption(cFileOption):
  def __init__(self, root, Config, Section, Option, **kwargs):
    cFileOption.__init__(self, root, Config, Section, Option, **kwargs)
    self.SelectedFile = None
    return

  def ask(self, **kwargs):
    Dialog = QtGui.QFileDialog()
    Value = self.Config.get(self.Section, self.Option)
    Dir = os.path.dirname(Value)
    Dialog.setDirectory(Dir)
    Dialog.setFileMode(QtGui.QFileDialog.AnyFile)
    Dialog.filesSelected.connect(self.selectFile)
    Dialog.exec_()
    Value = self.SelectedFile
    if Value:
      Value = os.path.abspath(Value)
      self.Config.set(self.Section, self.Option, Value)
      if self.is_save_last_files is True:
        self.save_last_files(Value)
      self.update()
      self.reset()
      self.Config.update()
    return self.SelectedFile

  def selectFile(self, File):
    self.SelectedFile, = File
    return

  def logNotExistWarning(self, Value):
    return

class cMultiFileOption(cFileOption):
  def __init__(self, Config, Section, Option, **kwargs):
    cFileOption.__init__(self, None, Config, Section, Option, **kwargs)
    self.Selector = QtGui.QPushButton()
    Menu = QtGui.QMenu()
    self.Selector.setMenu(Menu)
    self.Selector.menu()
    self.ParamGroup = QtGui.QActionGroup(Menu)
    self.ParamGroup.setExclusive(True)
    self.addItem(Option)
    self.updateItem(Option)

    if not Option:
      self.disable()
    return

  def addItem(self, itemName):
    if not itemName: return

    menu = self.Selector.menu()
    for action in menu.actions():
      if itemName == action.text():
        return

    action = QtGui.QAction(itemName, menu)
    action.triggered.connect(lambda n=itemName: self.updateItem(n))
    action.setCheckable(True)
    self.ParamGroup.addAction(action)

    menu.addAction(action)
    self.enable()
    self.updateItem(itemName)
    return

  def updateItem(self, SelectedItem):
    if not SelectedItem: return

    self.Option = SelectedItem
    self.Selector.setText(SelectedItem)
    self.update()
    action = self.findAction(SelectedItem)
    action.setChecked(True)
    return

  def rmItem(self, SelectedItem):
    if not SelectedItem:
      return

    action = self.findAction(SelectedItem)
    menu = self.Selector.menu()

    menu.removeAction(action)
    if not menu.actions():
      self.disable()
      self.Selector.setText('')
      self.Value.setText('')
    return

  def findAction(self, itemName):
    menu = self.Selector.menu()
    action = [action for action in menu.actions()
                     if itemName == action.text()]
    if len(action) != 1:
      return
    action, = action
    return action

class cDirOption(cFileOption):
  def ask(self, **kwargs):
    return QtGui.QFileDialog.getExistingDirectory(**kwargs)

class cCheckFileOption(cFileOption):
  def __init__(self, root, Config, Section, Option, CheckedInit=True, TextInit=None):
    # extend functionality
    self.Check = QtGui.QCheckBox()
    self.Check.setChecked(CheckedInit)
    self.Check.stateChanged.connect(self.toggle)
    # call parent
    cFileOption.__init__(self, root, Config, Section, Option)
    # overwrite parent's behavior
    if TextInit is not None:
      self.Value.setText(TextInit)
    if CheckedInit:
      self.enable()
    else:
      self.disable()
    pass

  def toggle(self):
    if self.Check.isChecked():
      self.Config.set(self.Section, self.Option, self.Value.text())
      self.enable()
    else:
      self.Config.set(self.Section, self.Option, '')
      self.disable()
    pass

class cCheckDirOption(cCheckFileOption):
  def ask(self, **kwargs):
    return QtGui.QFileDialog.getExistingDirectory(**kwargs)

class cNameOption(cOption):
  def __init__(self, root, Config, Section, Option):
    cOption.__init__(self, root, Config, Section, Option)
    self.Var = Config.get(Section, Option)

    self.Label = QtGui.QLabel(Option, parent=root)
    self.Value = QtGui.QLineEdit()
    self.Value.editingFinished.connect(self.onReturn)
    pass

  def update(self):
    Value = self.Config.get(self.Section, self.Option)
    self.Value.setText(Value)
    pass

  def onReturn(self):
    Value = self.Value.text()
    self.Label.setFocus()
    self.Config.set(self.Section, self.Option, Value)
    pass

class cListOptionFrane(QtGui.QFrame):
  def __init__(self, Config, Section):
    QtGui.QFrame.__init__(self)
    self.Config = Config
    self.Section = Section
    self.Label = QtGui.QLabel(Section)
    self.Value = QtGui.QListWidget()
    self.OpenFileBtn = QtGui.QPushButton('Configure...')
    self.update()
    return

  def update(self):
    if self.Value.count():
      self.Value.clear()
    ActiveModules = [option for option in self.Config.options(self.Section)
                            if self.Config.getboolean(self.Section, option)]
    Items = []
    for ActiveModule in ActiveModules:
      if self.Config.options(ActiveModule):
        Mod, _, Prj = ModuleName.split(ActiveModule)
        ActiveParams = [ option for option in self.Config.options(ActiveModule)
                                if self.Config.getboolean(ActiveModule, option)]
        for Param in ActiveParams:
          Name = ModuleName.create(Mod, Param, Prj)
          Items.append(Name)
      else:
        Items.append(ActiveModule)
    Items.sort()
    self.Value.addItems(Items)
    return


class FrmShowLastOpenedFiles(QDialog):
  def __init__(self, config, last_opened_measurements_set, location):
    super(FrmShowLastOpenedFiles, self).__init__()

    self.setWindowTitle("Select Previously Opened Files")
    self.setModal(True)
    self.setWindowIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'history_24.png')))
    VBoxLayoutMain = QVBoxLayout(self)
    VBoxLayoutMain.setSpacing(0)
    VBoxLayoutMain.setContentsMargins(1, 1, 1, 1)
    self.listWidgetLastOpenedFiles = QListWidget()
    self.listWidgetLastOpenedFiles.setSortingEnabled(False)
    self.listWidgetLastOpenedFiles.doubleClicked.connect(self.select_measurement)
    self.listWidgetLastOpenedFiles.setAlternatingRowColors(True)
    self.listWidgetLastOpenedFiles.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
    self.listWidgetLastOpenedFiles.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
    for index, measurement_path in enumerate(reversed(last_opened_measurements_set)):
      listWidgetItemMeasPath = QListWidgetItem()
      listWidgetItemMeasPath.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'measurement_file_24.png')))
      listWidgetItemMeasPath.setText(measurement_path)
      self.listWidgetLastOpenedFiles.addItem(listWidgetItemMeasPath)
    VBoxLayoutMain.addWidget(self.listWidgetLastOpenedFiles)
    self.listWidgetLastOpenedFiles.setMinimumWidth(self.listWidgetLastOpenedFiles.sizeHintForColumn(0))

    gbox_buttons = QGroupBox('')
    hboxlayout_buttons = QtGui.QHBoxLayout()
    hboxlayout_buttons.setSpacing(0)
    hboxlayout_buttons.setContentsMargins(1, 1, 1, 1)
    pButtonSelect = QPushButton("Select")
    pButtonSelect.setToolTip('Select File')
    pButtonSelect.clicked.connect(self.select_measurement)
    hboxlayout_buttons.addWidget(pButtonSelect, 1, Qt.AlignRight)

    pButtonClose = QPushButton("Close")
    pButtonClose.setToolTip('Close this window')
    pButtonClose.clicked.connect(self.close_clicked)
    hboxlayout_buttons.addWidget(pButtonClose, 0, Qt.AlignRight)
    gbox_buttons.setLayout(hboxlayout_buttons)

    VBoxLayoutMain.addWidget(gbox_buttons, 0, Qt.AlignBottom)

    self.setLayout(VBoxLayoutMain)
    self.move(location)

  def select_measurement(self):
    self.accept()

  def selected_measurement(self):
    item = self.listWidgetLastOpenedFiles.currentItem()
    return item.text()

  def close_clicked(self):
    self.close()
