'''
Created on 5 Aug 2015

@author: ext-felipes
'''
import os
from PySide import QtGui, QtCore
from NxtVideoPlayer import ObjectEmittingSignal

CONFIG_FILENAME = "ldws_overlay_config.ini"

OVR_MAX_ROTATION_DEG = 90  # degrees
LNGT_MULTIPLIER = 2  # unitless
MAX_PCNT = 100  # %
MARK_LOC = 30  # cm


class LdwOverlayConfig(object):
    """
    Storage class for the LDW overlay properties
    """

    def __init__(self, x_pos, y_pos, overlay_length, rotation,
                 zero_mark_offset, tw_mark_offset, tire_width, scale_len):
        '''
        Constructor for the LDW Overlay Configuration. Set parameters:
        -> (x,y) coordinates
        -> length in x
        -> rotation angle
        -> offset for the 0 mark, overlay x=0 as reference
        -> offset for the TW mark, overlay x=0 as reference
        -> Tire width (cms)
        '''
        self.x = x_pos
        self.y = y_pos
        self.length = overlay_length
        self.rotation = rotation
        self.zero_mark_offset = zero_mark_offset
        self.tw_mark_offset = tw_mark_offset
        self.mark_30cm_offset = 0
        self.tire_width = tire_width
        self.scale_len = scale_len

    def get_tcm_x_offset_to_right(self):
        x_to_zero = self.length * (self.zero_mark_offset / 100.0)
        x_to_tw = self.length * (self.tw_mark_offset / 100.0)
        pixel_ratio_px_cm = (x_to_zero - x_to_tw) / self.tire_width  # px / cm

        return MARK_LOC * pixel_ratio_px_cm

    def get_size_x_offset_to_right(self, size):
        x_to_zero = self.length * (self.zero_mark_offset / 100.0)
        x_to_tw = self.length * (self.tw_mark_offset / 100.0)
        pixel_ratio_px_cm = (x_to_zero - x_to_tw) / self.tire_width  # px / cm

        return size * pixel_ratio_px_cm


class LdwOverlayCalibrator(QtGui.QWidget):
    '''
    Calibrator for the LDW Overlay
    
    Spec : 
    - Open when the LDW OVRL Mode is turned on                        [x]
    - Close when the LDW OVRL Mode is turned off.                     [x]
    - Re-opened with a key if closed on Mode=on                       [x]
    - Keep the internal state                                         [x]
    - Provide the internal state to the overlay                       [X]
    - Save the state seamlessly over runs                             [x]
    - Keep the UI                                                     [x]
    - Update state AND UI when the user interacts with the sliders    [x]
    - Know some basic info about the videonav                         [x]
    - Deduce (calculate) the location of the 30cm mark                [x]
    '''

    def __init__(self, window_wdt, window_hgt):
        '''
        Constructor
        Accept the optional window width, height for default positioning.

        '''
        super(LdwOverlayCalibrator, self).__init__()

        self.window_wdt = window_wdt
        self.window_hgt = window_hgt
        self.settings = None
        self.overlay_status = None
        self.layout_size = None

        # Load the config for the overlay. this is currently independent.
        self._load_configuration()
        self.init_ui()
        self.signal_status_updated = ObjectEmittingSignal()
        return

    def init_ui(self):
        overall_layout = QtGui.QGridLayout()
        self.resize(self.layout_size)
        self.move(self.layout_pos)

        # ---------------------------------------------------------------------
        # Set control for X

        label_x = QtGui.QLabel('Overlay Position X', self)
        self.slider_x = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.slider_x.setFocusPolicy(QtCore.Qt.NoFocus)
        self.slider_x.setRange(0, self.window_wdt)
        self.slider_x.setValue(int(self.overlay_status.x))

        self.display_x = QtGui.QLabel(self)
        self.display_x.setNum(self.slider_x.value())
        self.slider_x.valueChanged.connect(self.display_x.setNum)
        self.slider_x.valueChanged.connect(self.update_overlay)

        overall_layout.addWidget(label_x, 0, 0)
        overall_layout.addWidget(self.slider_x, 0, 1)
        overall_layout.addWidget(self.display_x, 0, 2)

        # ---------------------------------------------------------------------
        # Set control for Y

        label_y = QtGui.QLabel('Overlay Position Y', self)
        self.slider_y = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.slider_y.setFocusPolicy(QtCore.Qt.NoFocus)
        self.slider_y.setRange(0, self.window_hgt)
        self.slider_y.setValue(int(self.overlay_status.y))

        self.display_y = QtGui.QLabel(self)
        self.display_y.setNum(self.slider_y.value())
        self.slider_y.valueChanged.connect(self.display_y.setNum)
        self.slider_y.valueChanged.connect(self.update_overlay)

        overall_layout.addWidget(label_y, 1, 0)
        overall_layout.addWidget(self.slider_y, 1, 1)
        overall_layout.addWidget(self.display_y, 1, 2)

        # ---------------------------------------------------------------------
        # Set control for length

        label_lngt = QtGui.QLabel('Overlay Length', self)
        self.slider_lngt = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.slider_lngt.setFocusPolicy(QtCore.Qt.NoFocus)
        self.slider_lngt.setRange(0, self.window_wdt * LNGT_MULTIPLIER)
        self.slider_lngt.setValue(int(self.overlay_status.length))

        self.display_lngt = QtGui.QLabel(self)
        self.display_lngt.setNum(self.slider_lngt.value())
        self.slider_lngt.valueChanged.connect(self.display_lngt.setNum)
        self.slider_lngt.valueChanged.connect(self.update_overlay)

        overall_layout.addWidget(label_lngt, 2, 0)
        overall_layout.addWidget(self.slider_lngt, 2, 1)
        overall_layout.addWidget(self.display_lngt, 2, 2)

        # ---------------------------------------------------------------------
        # Set control for rotation

        label_rot = QtGui.QLabel('Overlay Rotation', self)
        self.slider_rot = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.slider_rot.setFocusPolicy(QtCore.Qt.NoFocus)
        self.slider_rot.setRange(-OVR_MAX_ROTATION_DEG, OVR_MAX_ROTATION_DEG)
        self.slider_rot.setValue(int(self.overlay_status.rotation))

        self.display_rot = QtGui.QLabel(self)
        self.display_rot.setNum(self.slider_rot.value())
        self.slider_rot.valueChanged.connect(self.display_rot.setNum)
        self.slider_rot.valueChanged.connect(self.update_overlay)

        overall_layout.addWidget(label_rot, 3, 0)
        overall_layout.addWidget(self.slider_rot, 3, 1)
        overall_layout.addWidget(self.display_rot, 3, 2)

        # ---------------------------------------------------------------------
        # Set control for the zero mark

        label_zmo = QtGui.QLabel('Zero Mark : Position %', self)
        self.slider_zmo = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.slider_zmo.setFocusPolicy(QtCore.Qt.NoFocus)
        self.slider_zmo.setRange(0, MAX_PCNT)
        self.slider_zmo.setValue(int(self.overlay_status.zero_mark_offset))

        self.display_zmo = QtGui.QLabel(self)
        self.display_zmo.setNum(self.slider_zmo.value())
        self.slider_zmo.valueChanged.connect(self.display_zmo.setNum)
        self.slider_zmo.valueChanged.connect(self.update_overlay)

        overall_layout.addWidget(label_zmo, 4, 0)
        overall_layout.addWidget(self.slider_zmo, 4, 1)
        overall_layout.addWidget(self.display_zmo, 4, 2)

        # ---------------------------------------------------------------------
        # Set control for the TW mark

        label_twf = QtGui.QLabel('Tire Width : Position %', self)
        self.slider_twf = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.slider_twf.setFocusPolicy(QtCore.Qt.NoFocus)
        self.slider_twf.setRange(0, MAX_PCNT)
        self.slider_twf.setValue(int(self.overlay_status.tw_mark_offset))

        self.display_twf = QtGui.QLabel(self)
        self.display_twf.setNum(self.slider_twf.value())
        self.slider_twf.valueChanged.connect(self.display_twf.setNum)
        self.slider_twf.valueChanged.connect(self.update_overlay)

        overall_layout.addWidget(label_twf, 5, 0)
        overall_layout.addWidget(self.slider_twf, 5, 1)
        overall_layout.addWidget(self.display_twf, 5, 2)
        # ---------------------------------------------------------------------

        # Set control for the 30 cm mark

        label_tcm = QtGui.QLabel('Tire Width (cm)', self)
        self.textinput_tcm = QtGui.QLineEdit('', self)
        self.textinput_tcm.setText(str(self.overlay_status.tire_width))

        self.button_tcm = QtGui.QPushButton('Set Width', self)
        self.button_tcm.clicked.connect(self.update_overlay)

        overall_layout.addWidget(label_tcm, 8, 0)
        overall_layout.addWidget(self.textinput_tcm, 8, 1)
        overall_layout.addWidget(self.button_tcm, 8, 2)

        # ---------------------------------------------------------------------
        # Set control for the cm length
        # Set control for the User mark

        label_umf = QtGui.QLabel('User Marker (cm) ', self)
        self.slider_umf = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.slider_umf.setFocusPolicy(QtCore.Qt.NoFocus)
        self.slider_umf.setRange(0, 400)
        self.slider_umf.setValue(float(self.overlay_status.scale_len))

        self.display_umf = QtGui.QLabel(self)
        self.display_umf.setNum(self.slider_umf.value())
        self.slider_umf.valueChanged.connect(self.display_umf.setNum)
        self.slider_umf.valueChanged.connect(self.update_overlay)

        overall_layout.addWidget(label_umf, 6, 0)
        overall_layout.addWidget(self.slider_umf, 6, 1)
        overall_layout.addWidget(self.display_umf, 6, 2)
        # ---------------------------------------------------------------------

        label_len = QtGui.QLabel("User Marker (cm)", self)
        self.textinput_len = QtGui.QLineEdit('', self)
        self.textinput_len.setText(str(self.overlay_status.scale_len))
        #
        self.button_label_len = QtGui.QPushButton('Check distance', self)
        self.button_label_len.clicked.connect(self.update_overlay_text)
        #
        overall_layout.addWidget(label_len, 7, 0)
        overall_layout.addWidget(self.textinput_len, 7, 1)
        overall_layout.addWidget(self.button_label_len, 7, 2)

        # ---------------------------------------------------------------------

        self.setLayout(overall_layout)
        self.setWindowTitle('LDWS Tire Overlay Calibration')
        return

    def update_overlay(self):
        self.overlay_status.x = int(self.display_x.text())
        self.overlay_status.y = int(self.display_y.text())
        self.overlay_status.length = int(self.display_lngt.text())
        self.overlay_status.rotation = int(self.display_rot.text())
        self.overlay_status.zero_mark_offset = int(self.display_zmo.text())
        self.overlay_status.tw_mark_offset = int(self.display_twf.text())
        self.overlay_status.tire_width = float(self.textinput_tcm.text())
        self.overlay_status.scale_len = float(self.display_umf.text())
        self.textinput_len.setText(str(self.overlay_status.scale_len))
        self.signal_status_updated.signal.emit(self.overlay_status)
        return
    def update_overlay_text(self):
        self.overlay_status.x = int(self.display_x.text())
        self.overlay_status.y = int(self.display_y.text())
        self.overlay_status.length = int(self.display_lngt.text())
        self.overlay_status.rotation = int(self.display_rot.text())
        self.overlay_status.zero_mark_offset = int(self.display_zmo.text())
        self.overlay_status.tw_mark_offset = int(self.display_twf.text())
        self.overlay_status.tire_width = float(self.textinput_tcm.text())
        self.overlay_status.scale_len = float(self.textinput_len.text())
        self.slider_umf.setValue(int(self.overlay_status.scale_len))
        self.signal_status_updated.signal.emit(self.overlay_status)
        return

    def closeEvent(self, e):
        self._save_configuration()
        e.accept()
        return

    def _load_configuration(self):
        # Attempt loading from config.
        folder_path = '.' + os.getenv('DATAEVAL_NAME', 'dataeval')
        folder_path = os.path.join('~', folder_path)
        folder_path = os.path.join(os.path.expanduser(folder_path),
                                   CONFIG_FILENAME)
        self.settings = QtCore.QSettings(folder_path, QtCore.QSettings.IniFormat)
        self.settings.setFallbacksEnabled(False)  # Only file read.

        # Load the settings. A default is given if the value isn;t found.
        cnf_x = self.settings.value('X', 100)
        cnf_y = self.settings.value('Y', 100)
        cnf_len = self.settings.value('LENGTH', 400)
        cnf_rot = self.settings.value('ROTATION', 0)
        cnf_zmo = self.settings.value('ZERO_MARK_OFFSET', 95)
        cnf_twf = self.settings.value('TIRE_WIDTH_OFFSET', 15)
        cnf_tw = self.settings.value('TIRE_WIDTH', 90.0)
        scale_len = self.settings.value('SCALE_LEN', 50.0)

        self.layout_size = self.settings.value('SIZE', QtCore.QSize(370, 550))
        self.layout_pos = self.settings.value('POSITION', QtCore.QPoint(50, 50))
        self.overlay_status = LdwOverlayConfig(cnf_x, cnf_y, cnf_len, cnf_rot,
                                               cnf_zmo, cnf_twf, cnf_tw, scale_len)

        return

    def _save_configuration(self):
        self.settings.setValue('X', self.slider_x.value())
        self.settings.setValue('Y', self.slider_y.value())
        self.settings.setValue('LENGTH', self.slider_lngt.value())
        self.settings.setValue('ROTATION', self.slider_rot.value())
        self.settings.setValue('ZERO_MARK_OFFSET', self.slider_zmo.value())
        self.settings.setValue('TIRE_WIDTH_OFFSET', self.slider_twf.value())
        self.settings.setValue('TIRE_WIDTH', float(self.textinput_tcm.text()))
        self.settings.setValue('SCALE_LEN', float(self.textinput_len.text()))

        self.settings.setValue('SIZE', self.size())
        self.settings.setValue('POSITION', self.pos())
        return

    def get_overlay_state(self):
        self.update_overlay()
        return self.overlay_status
