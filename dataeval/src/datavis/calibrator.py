import logging
import os

from PySide import QtGui, QtCore

from dmw.base_section_model import SectionModel

from datavis.calibration_data import cCalibrationData as Calib

IMAGE_DIRECTORY = os.path.join(os.path.dirname(__file__), "images")

class CalibrationModel(SectionModel):
  HEADER = 'Date', 'Vehicle', 'Camera'
  SORT_ASC = False, True, True
  
  def __init__(self, vidcalibs):
    self.vidcalibs = vidcalibs
    sortbys = zip(self.HEADER, self.SORT_ASC)
    SectionModel.__init__(self, None, None, None, None, sortbys)
    return

  def get_elements(self):
    calibdatas = self.vidcalibs.get_all_calibdata()
    self.elements = {}
    self.visible_elements = []
    for calibdata in calibdatas:
      self.elements[calibdata.id] = {}
      element = self.elements[calibdata.id]
      element['id'] = calibdata.id
      element['Vehicle'] = self.vidcalibs.get_vehicle_name(calibdata.id)
      element['Date'] = str(self.vidcalibs.get_start(calibdata.id))
      element['Camera'] = self.vidcalibs.get_camera_name(calibdata.id)
      names = Calib.get_value_names()
      for name in names:
        value = getattr(calibdata, name)
        element[name] = value
      self.visible_elements.append(element)
    self._draw()
    return

  def data(self, index, role=QtCore.Qt.DisplayRole):
    if index.isValid():
      header_name = self.HEADER[index.column()]
      id = self.visible_elements[index.row()]['id']
      if role == QtCore.Qt.DisplayRole:
        return str(self.elements[id][header_name])
    return None

  def query_elements(self, pos_veh_tags, pos_date_tags, pos_cam_tags,
                           neg_veh_tags, neg_date_tags, neg_cam_tags,
                           pos_veh_tag_mc, pos_date_tag_mc, pos_cam_tag_mc,
                           neg_veh_tag_mc, neg_date_tag_mc, neg_cam_tag_mc):
    self.visible_elements = []
    for element in self.elements.itervalues():
      veh = element['Vehicle']
      cam = element['Camera']
      date = element['Date']
      if self.check_name(veh, pos_veh_tags, neg_veh_tags, pos_veh_tag_mc,
                         neg_veh_tag_mc) \
         and \
         self.check_name(cam, pos_cam_tags, neg_cam_tags, pos_cam_tag_mc,
                         neg_cam_tag_mc) \
         and \
         self.check_name(date, pos_date_tags, neg_date_tags, pos_date_tag_mc,
                         neg_date_tag_mc):
         if element not in self.visible_elements:
          self.visible_elements.append(element)
    self._draw()
    return

class Calibrator(QtGui.QMainWindow):
  def __init__(self, videonavigator, vidcalibs, path):
    QtGui.QMainWindow.__init__(self)
    self.setWindowTitle("Video Calibration")
    self.videonavigator = videonavigator
    self.setWindowIcon(QtGui.QIcon(os.path.join(IMAGE_DIRECTORY, 'calibration.png')))
    self.vidcalibs = vidcalibs
    self.path = path
    self.logger = logging.getLogger()

    self.table = QtGui.QTableView()
    self.table_model = CalibrationModel(vidcalibs)
    self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
    self.table.setModel(self.table_model)

    self.table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
    horizontalHeader = self.table.horizontalHeader()
    horizontalHeader.sectionClicked.connect(self._onSort)
    self.table.setColumnWidth(0,150)
    self.table.setColumnWidth(1,250)
    selection_model = self.table.selectionModel()
    selection_model.selectionChanged.connect(self.selectionChanged)
    horizontalHeader.setResizeMode(self.table_model.columnCount() - 1,
                                   QtGui.QHeaderView.Stretch)

    selected = vidcalibs.get_calib(path)
    veh = '' if selected is None else vidcalibs.get_vehicle_name(selected.id)
    cam = '' if selected is None else vidcalibs.get_camera_name(selected.id)
    date = '' if selected is None else vidcalibs.get_start(selected.id)

    frame = QtGui.QFrame()
    vbox = QtGui.QVBoxLayout()
    vbox.addWidget(self.table)
    hbox = QtGui.QHBoxLayout()
    box = QtGui.QGroupBox('Selected Calibration')

    label = QtGui.QLabel('Date')
    self.date_edit = QtGui.QLineEdit(str(date))
    hbox.addWidget(label)
    hbox.addWidget(self.date_edit)

    label = QtGui.QLabel('Vehicle')
    hbox.addWidget(label)
    self.vehicle_edit = QtGui.QLineEdit(veh)
    hbox.addWidget(self.vehicle_edit)

    label = QtGui.QLabel('Camera')
    self.camera_edit = QtGui.QLineEdit(cam)
    hbox.addWidget(label)
    hbox.addWidget(self.camera_edit)

    grid = QtGui.QGridLayout()
    names = Calib.get_value_names()
    self.calibdata_editors = {}
    for i, name in enumerate(names):
      value = '-1000.1' if selected is None else getattr(selected, name)
      editor = QtGui.QDoubleSpinBox()
      editor.setRange(-1000.1, 1000.0)
      editor.setValue(float(value))
      editor.setSingleStep(0.001)
      editor.setDecimals(3)
      editor.setSpecialValueText("None")
      label = QtGui.QLabel(name)
      grid.addWidget(label, i / 3, 2 * (i % 3))
      grid.addWidget(editor, i / 3,  2 * (i % 3 )+ 1)
      editor.valueChanged.connect(self.load_calib_to_video_navigator)
      self.calibdata_editors[name] = editor
      
    if selected is None:
      self.read_calib_from_navigator()

    filter_box = QtGui.QGroupBox('Filters')

    query_by = 'pos_date', 'pos_veh', 'pos_cam', \
               'neg_date', 'neg_veh', 'neg_cam'

    self.queries = {}
    self.match_case_btns = {}
    filter_grid = QtGui.QGridLayout()
    for i, name in enumerate(query_by):
      row = i >= (len(query_by) / 2)
      column = 2 * i % 6
      query = QtGui.QLineEdit()
      query.textChanged.connect(self.filt)
      self.queries[name] = query
      filter_grid.addWidget(query, row, column)
      btn = QtGui.QPushButton('aA')
      filter_grid.addWidget(btn, row, column + 1)
      btn.setMaximumWidth(25)
      btn.setCheckable(True)
      btn.setToolTip('Turn matchcase on/off for filter')
      btn.clicked.connect(self.filt)
      self.match_case_btns[name] = btn

    filter_box.setLayout(filter_grid)

    vbox2 = QtGui.QVBoxLayout()
    vbox2.addLayout(hbox)
    vbox2.addLayout(grid)
    box.setLayout(vbox2)


    hbox3 = QtGui.QHBoxLayout()
    hbox3.addStretch()
    apply_btn = QtGui.QPushButton('Apply to navigator')
    export_btn = QtGui.QPushButton('Save to database')
    read_btn = QtGui.QPushButton('Read from navigator')
    hbox3.addWidget(read_btn)
    hbox3.addWidget(apply_btn)
    hbox3.addWidget(export_btn)
    export_btn.clicked.connect(self.save_calib)
    read_btn.clicked.connect(self.read_calib_from_navigator)
    apply_btn.clicked.connect(self.load_calib_to_video_navigator)
    hbox3.addStretch()

    vbox.addWidget(filter_box)
    vbox.addWidget(box)
    vbox.addLayout(hbox3)
    frame.setLayout(vbox)
    self.setCentralWidget(frame)
    self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
    self.insertHelp()
    
    # Plug signal for manual calibration update
    self.videonavigator.player.manual_calib_updated.signal.connect(self.load_values_from_navigator)
    return

  def filt(self):
    QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
    pos_veh_tag  = self.queries['pos_veh'].text()
    pos_veh_tags = pos_veh_tag.split()
    neg_veh_tag  = self.queries['neg_veh'].text()
    neg_veh_tags = neg_veh_tag.split()

    pos_date_tag  = self.queries['pos_date'].text()
    pos_date_tags = pos_date_tag.split()
    neg_date_tag  = self.queries['neg_date'].text()
    neg_date_tags = neg_date_tag.split()

    pos_cam_tag  = self.queries['pos_cam'].text()
    pos_cam_tags = pos_cam_tag.split()
    neg_cam_tag  = self.queries['neg_cam'].text()
    neg_cam_tags = neg_cam_tag.split()

    pos_veh_tag_mc = self.match_case_btns['pos_veh'].isChecked()
    neg_veh_tag_mc = self.match_case_btns['neg_veh'].isChecked()
    pos_date_tag_mc = self.match_case_btns['pos_date'].isChecked()
    neg_date_tag_mc = self.match_case_btns['neg_date'].isChecked()
    pos_cam_tag_mc = self.match_case_btns['pos_cam'].isChecked()
    neg_cam_tag_mc = self.match_case_btns['neg_cam'].isChecked()


    self.table_model.query_elements( pos_veh_tags, pos_date_tags, pos_cam_tags,
                           neg_veh_tags, neg_date_tags, neg_cam_tags,
                           pos_veh_tag_mc, pos_date_tag_mc, pos_cam_tag_mc,
                           neg_veh_tag_mc, neg_date_tag_mc, neg_cam_tag_mc)

    QtGui.QApplication.restoreOverrideCursor()
    return

  def _onSort(self, index):
    self.table_model._onSort(index)
    return

  def selectionChanged(self, selected, deselected):
    selecteds = self.table.selectedIndexes()

    if len(selecteds) < len(self.table_model.HEADER): return

    last_row = -1
    for selected in selecteds:
      current_row = selected.row()
      if last_row == current_row: continue
      id = self.table_model.visible_elements[current_row]['id']
      self.update_by_calibdata_id(id)
    return

  def update_by_calibdata_id(self, calibdata_id):
    selected = self.vidcalibs.get_calibdata_by_id(calibdata_id)
    names = Calib.get_value_names()
    for name in names:
      value = getattr(selected, name)
      self.calibdata_editors[name].setValue(value)
    veh = self.vidcalibs.get_vehicle_name(calibdata_id)
    cam = self.vidcalibs.get_camera_name(calibdata_id)
    date = self.vidcalibs.get_start(calibdata_id)

    self.vehicle_edit.setText(veh)
    self.camera_edit.setText(cam)
    self.date_edit.setText(date)
    
    self.load_calib_to_video_navigator()
    return


  def insertHelp(self):
    self.queries['pos_veh'].setPlaceholderText('Positive Vehicle Filter')
    self.queries['pos_veh'].setToolTip(
                'Filter tags can be added to reduce the number of the calibs' +
                '\nThe tags have to be separated by SPACE.' +
                '\nThe entry collects the tags that Vehicle names WILL contain'+
                '\nPress ENTER to run the filtering over the calibs.'
                                    )
    self.queries['neg_veh'].setPlaceholderText('Negative Vehicle Filter')
    self.queries['neg_veh'].setToolTip(
                'Filter tags can be added to reduce the number of the calibs' +
                '\nThe tags have to be separated by SPACE.' +
                '\nThe entry collects the tags that Vehicle names WONT contain'+
                '\nPress ENTER to run the filtering over the calibs.'
                                    )

    self.queries['pos_date'].setPlaceholderText('Positive Date Filter')
    self.queries['pos_date'].setToolTip(
                'Filter tags can be added to reduce the number of the calibs' +
                '\nThe tags have to be separated by SPACE.' +
                '\nThe entry collects the tags that Date names WILL contain' +
                '\nPress ENTER to run the filtering over the calibs.'
                                    )
    self.queries['neg_date'].setPlaceholderText('Negative Date Filter')
    self.queries['neg_date'].setToolTip(
                'Filter tags can be added to reduce the number of the calibs' +
                '\nThe tags have to be separated by SPACE.' +
                '\nThe entry collects the tags that Date names WONT contain' +
                '\nPress ENTER to run the filtering over the calibs.'
                                    )

    self.queries['pos_cam'].setPlaceholderText('Positive Camera Filter')
    self.queries['pos_cam'].setToolTip(
                'Filter tags can be added to reduce the number of the calibs' +
                '\nThe tags have to be separated by SPACE.' +
                '\nThe entry collects the tags that Camera names WILL contain' +
                '\nPress ENTER to run the filtering over the calibs.'
                                    )
    self.queries['neg_cam'].setPlaceholderText('Negative Camera Filter')
    self.queries['neg_cam'].setToolTip(
                'Filter tags can be added to reduce the number of the calibs' +
                '\nThe tags have to be separated by SPACE.' +
                '\nThe entry collects the tags that Camera names WONT contain' +
                '\nPress ENTER to run the filtering over the calibs.'
                                    )
    return

  def is_date_valid(self, date):
    datas = date.split('_')
    if len(datas) != 2: return False
    for data in datas:
      splitted_data = data.split('-')
      if len(splitted_data) != 3: return False
      for d in splitted_data:
        try:
          int(d)
        except ValueError:
          return False
    return True

  def save_calib(self):
    veh = self.vehicle_edit.text()
    if not veh:
      self.logger.error("Cannot save the calibration until a valid vehicle name "
                   "hasn't been set")
      return
    date = self.date_edit.text()
    if not date:
      self.logger.error("Cannot save the calibration until a valid date "
                        "hasn't been set")
      return
    else:
      if not self.is_date_valid(date):
        self.logger.error('Cannot recognize %s as date, please use '
                          'YYYY-MM-DD_HH-MM-SS format' %date)
        return
    cam = self.camera_edit.text()
    calibvalues = {}
    for name, editor in self.calibdata_editors.iteritems():
      value = editor.value()
      try:
        calibvalues[name] = float(value)
      except:
        self.logger.error('Cannot convert %s to float for %s' %(value, name))
        return
    calibration = Calib(**calibvalues)
    self.vidcalibs.add_calib(calibration, self.path, vehicle=veh, camera=cam,
                             date=date)
    self.table_model.get_elements()
    return

  def load_calib_to_video_navigator(self):
    calibvalues = {}
    for name, editor in self.calibdata_editors.iteritems():
      value = editor.value()
      try:
        calibvalues[name] = float(value)
      except:
        self.logger.error('Cannot convert %s to float for %s' %(value, name))
        return
    calibration = Calib(**calibvalues)
    self.videonavigator.setCalibration(calibration)
    self.videonavigator.player.on_draw()
    return

  def read_calib_from_navigator(self):
    # fill calibration parameters
    self.load_values_from_navigator()
    # Attempt to get base data
    calibdata_base = self.vidcalibs.parse_measurement(self.path)
    if calibdata_base is not None:
      vehicle, camera, date = calibdata_base
    else:
      vehicle, camera, date = "", "", ""  # None returned. Leave empty
    self.vehicle_edit.setText(vehicle)
    self.camera_edit.setText(camera)
    self.date_edit.setText(date)
    return
  
  def load_values_from_navigator(self):
    calibration = self.videonavigator.player.cali
    for name, editor in self.calibdata_editors.iteritems():
      value = getattr(calibration, name)
      editor.setValue(value)
    return

  def keyPressEvent(self, event):
    if event.key() == QtCore.Qt.Key_Control:
      self.table_model.control_pressed = True
    return QtGui.QMainWindow.keyPressEvent(self, event)

  def keyReleaseEvent(self, event):
    if event.key() == QtCore.Qt.Key_Control:
      self.table_model.control_pressed = False
    return QtGui.QMainWindow.keyReleaseEvent(self, event)


if __name__ == '__main__':
  import sys

  from measproc.vidcalibs import VidCalibs

  vidcalibs = VidCalibs('vidcalibs.db')
  calib = Calib( 0.24, 2.3,   0.0,  640, 480, 36.2,    0.249, -0.262,  0.0)
  vidcalibs.add_calib(calib, r'H566_2013-03-21_16-40-21.avi')
  calib = Calib( 1.24, 1.3,   1.0,  6410, 4810, 316.2,    1.249, -1.262,  0.1)
  #vidcalibs.add_calib(calib,
  #                r'C:\KBData\Measurements\MQBMRR_2012-07-17_14-16-00_0016.avi')
  app = QtGui.QApplication([])
  calibrator = Calibrator(None, vidcalibs,
                  r'C:\KBData\Measurements\MQBMRR_2012-07-17_14-16-00_0016.avi')
  calibrator.show()
  sys.exit(app.exec_())