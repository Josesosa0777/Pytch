from PySide.QtCore import *
from PySide.QtGui import *
import sys

sensorports = {
    "FLC25_CEM_TPF": {
        "id": True,
        "valid": True,
        "time": True,
        "init": True,
        "dx": True,
        "dx_std": True,
        "dy": True,
        "dy_std": True,
        "vx_abs": True,
        "vx_abs_std": True,
        "vy_abs": True,
        "vy_abs_std": True,
        "vx": True,
        "vx_std": True,
        "vy": True,
        "vy_std": True,
        "ax": True,
        "ax_abs": True,
        "ay": True,
        "ay_abs": True,
        "dz": True,
        "dz_std": True,
        "yaw": True,
        "yaw_std": True,
        "lane": True,
        "obj_type": True,
        "video_conf": True,
        "measured_by": True,
        "tr_state": True,
        "mov_state": True,
        "range": True,
        "angle": True,
        "height": True,
        "width": True,
        "length": True,
    },
    "FLC25_EM": {
        "id": True,
        "valid": True,
        "time": True,
        "init": True,
        "dx": True,
        "dx_std": True,
        "dy": True,
        "dy_std": True,
        "vx": True,
        "vx_abs": True,
        "vx_abs_std": True,
        "vy": True,
        "vy_abs": True,
        "vy_abs_std": True,
        "ax": True,
        "ax_abs": True,
        "ay": True,
        "ay_abs": True,
        "dz": True,
        "dz_std": True,
        "yaw": True,
        "yaw_std": True,
        "lane": True,
        "obj_type": True,
        "video_conf": True,
        "height": True,
        "tr_state": True,
        "mov_state": True,
        "range": True,
        "angle": True,
        "width": True,
        "length": True,
    },
    "FLC25_CAN": {
        "id": True,
        "valid": True,
        "time": True,
        "init": True,
        "dx": True,
        "dy": True,
        "vx": True,
        "vy": True,
        "ax": True,
        "ay": True,
        "tr_state": True,
        "mov_state": True,
        "obj_type": True,
        "cut_in_cut_out": True,
        "video_conf": True,
        "measured_by": True,
        "range": True,
        "angle": True,
        "width": True,
        "can_tracking_state": True,
    },
    "FLC25_ARS_FCU": {
        "id": True,
        "valid": True,
        "time": True,
        "init": True,
        "dx": True,
        "dy": True,
        "dx_std": True,
        "dy_std": True,
        "vx": True,
        "vx_abs": True,
        "vy": True,
        "vy_abs": True,
        "ax": True,
        "ax_abs": True,
        "ay": True,
        "ay_abs": True,
        "lane": True,
        "obj_type": True,
        "tr_state": True,
        "mov_state": True,
        "video_conf": True,
        "measured_by": True,
        "acc_obj_quality": True,
        "aeb_obj_quality": True,
        "range": True,
        "angle": True,
        "width": True,
        "length": True,
    },
    "EGO_VEHICLE": {
        "vx": True,
        "ax": True,
        "yaw_rate": True,
        "time": True,
        "dir_ind": True,
        "steer_angle": True,
        "brkped_pos": True,
        "accped_pos": True,
    },
    "FLC25_CAN_LANES": {
        "C0": True,
        "C1": True,
        "C2": True,
        "C3": True,
        "Lane_View_Range": True,
        "time": True,
    },
    "FLC25_LD_LANES": {
        "C0": True,
        "C1": True,
        "C2": True,
        "C3": True,
        "Lane_View_Range": True,
        "time": True,
    },
    "FLC25_ABD_LANES": {
        "C0": True,
        "C1": True,
        "C2": True,
        "C3": True,
        "Lane_View_Range": True,
        "time": True,
    },
    "CONTI_TSR": {
        # 'sign_class'            : True,
        "traffic_sign_id": False,
        "suppl_sign_ids": False,
        "status": False,
        "uid": False,
        "uid_suppl": False,
        "valid": False,
        "time": False,
    },
    "POSTMARKER_TOOL": {
        "sign_class_id": False,
        # 'sign_class'            : True,
        "valid": False,
        "quantity": False,
        "time": False,
    },
    "TSR_DETECTION_COMPARISION": {
        "conti_detection": False,
        # 'sign_class'            : True,
        "postmarker_detection": False,
        "time": False,
    },
    "GPS": {
            "dx": False,
            "dy": False,
            "time": False,
        },
    }


class cResimExportView(QDialog):
    def __init__(self, parent=None):
        super(cResimExportView, self).__init__(parent)

        treeview_layout = QVBoxLayout()

        # <editor-fold desc="treewidget control">
        self.treeview_widget = QTreeWidget()
        self.treeview_widget.setHeaderLabels(["Select Sensor Port"])

        for sensor, signallist in sensorports.iteritems():
            parent = QTreeWidgetItem(self.treeview_widget)
            parent.setText(0, sensor)
            parent.setCheckState(0, Qt.Checked)
            parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            for signal in signallist.iteritems():
                child = QTreeWidgetItem(parent)
                child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                child.setText(0, signal[0])
                child.setCheckState(0, Qt.Checked)
        self.treeview_widget.show()
        treeview_layout.addWidget(self.treeview_widget)
        # </editor-fold>
        # <editor-fold desc="dialogbutton control">
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.button(QDialogButtonBox.Ok).setText("Export")
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        treeview_layout.addWidget(button_box)
        # </editor-fold>
        self.setLayout(treeview_layout)

    def onAccepted(self):
        iterator = QTreeWidgetItemIterator(self.treeview_widget)
        while iterator.value():
            item = iterator.value()
            for i in range(item.childCount()):
                if item.child(i).checkState(0) == Qt.Checked:
                    sensorports[str(item.text(0))][str(item.child(i).text(0))] = bool(
                        item.child(i).checkState(0)
                    )
                else:
                    sensorports[str(item.text(0))][str(item.child(i).text(0))] = bool(
                        item.child(i).checkState(1)
                    )
            iterator += 1
        # print(sensorports)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = cResimExportView()
    window.resize(1000, 500)
    window.setWindowTitle("Resimulation Export")
    window.show()
    sys.exit(app.exec_())
