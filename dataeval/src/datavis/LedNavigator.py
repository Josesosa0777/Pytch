from PySide import QtCore, QtGui

from Synchronizer import cNavigator

area2multiplier = {
    "top-left":         (0, 0),
    "top-center":       (1, 0),
    "top-right":        (2, 0),
    "left":             (0, 1),
    "center":           (1, 1),
    "right":            (2, 1),
    "bottom-left":      (0, 2),
    "bottom-center":    (1, 2),
    "bottom-right":     (2, 2),
}

colors = {
    "white":        QtCore.Qt.white,
    "black":        QtCore.Qt.black,
    "red":          QtCore.Qt.red,
    "darkRed":      QtCore.Qt.darkRed,
    "green":        QtCore.Qt.green,
    "darkGreen":    QtCore.Qt.darkGreen,
    "blue":         QtCore.Qt.blue,
    "darkBlue":     QtCore.Qt.darkBlue,
    "cyan":         QtCore.Qt.cyan,
    "darkCyan":     QtCore.Qt.darkCyan,
    "magenta":      QtCore.Qt.magenta,
    "darkMagenta":  QtCore.Qt.darkMagenta,
    "yellow":       QtCore.Qt.yellow,
    "darkYellow":   QtCore.Qt.darkYellow,
    "gray":         QtCore.Qt.gray,
    "darkGray":     QtCore.Qt.darkGray,
    "lightGray":    QtCore.Qt.lightGray,
}


class UpdateSignal(QtCore.QObject):
    signal = QtCore.Signal()


class LED(QtCore.QObject):
    def __init__(self, area, color, label):
        super(LED, self).__init__()

        self.x_pos = None
        self.y_pos = None

        self.color = colors[color]
        self.area = area2multiplier[area]
        self.label = label

        self.on_state = False

        self.update_signal = UpdateSignal()

        self.pen = QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.SolidLine, QtCore.Qt.FlatCap, QtCore.Qt.RoundJoin)

        self.brush = None
        self.brush_center_x = None
        self.brush_center_y = None
        return

    def setPen(self):
        self.pen.setColor(self.color if self.on_state else QtCore.Qt.black)
        return

    def setBrush(self):
        radial_gradient = QtGui.QRadialGradient(self.brush_center_x, self.brush_center_y, 50)
        radial_gradient.setColorAt(0.0, QtCore.Qt.white)
        radial_gradient.setColorAt(0.3, self.color if self.on_state else QtCore.Qt.black)
        radial_gradient.setColorAt(1.0, self.color if self.on_state else QtCore.Qt.black)
        self.brush = QtGui.QBrush(radial_gradient)
        return

    def setBrushCenter(self, cx, cy):
        self.brush_center_x = cx
        self.brush_center_y = cy
        return

    def setPosition(self, x, y):
        self.x_pos = x
        self.y_pos = y
        return

    def setState(self, state):
        self.on_state = state
        self.update()
        return

    def update(self):
        self.setPen()
        self.setBrush()
        self.update_signal.signal.emit()
        return


class RenderArea(QtGui.QWidget):
    padding_size = 4

    def __init__(self, parent=None):
        super(RenderArea, self).__init__(parent)

        self.LEDs = list()

        self.led_rect = None
        self.text_rect = None

        self.setBackgroundRole(QtGui.QPalette.Base)
        return

    def minimumSizeHint(self):
        return QtCore.QSize(300, 200)

    def addLed(self, area, color, text):
        if color not in colors.keys():
            raise KeyError
        newLED = LED(area, color, text)
        newLED.update_signal.signal.connect(self.update)
        self.LEDs.append(newLED)
        return newLED

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))

        for led in self.LEDs:
            painter.setPen(QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.SolidLine, QtCore.Qt.FlatCap, QtCore.Qt.RoundJoin))
            painter.setBrush(led.brush)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)

            painter.save()
            painter.translate(led.x_pos, led.y_pos)
            painter.drawText(self.text_rect, QtCore.Qt.AlignCenter, led.label)
            painter.setPen(led.pen)
            painter.drawEllipse(self.led_rect)

            painter.restore()

        painter.end()
        return

    def resizeEvent(self, event):
        # calculate the new size and position of the LEDs
        size = event.size()
        width, height = size.width(), size.height()
        rect_width = width / 3.0
        rect_height = height / 3.0
        rect = QtCore.QRect(0, 0, rect_width - self.padding_size, rect_height - self.padding_size)
        self.text_rect = QtCore.QRect(0, 0, rect.width(), rect.height() / 3.0)
        self.led_rect = QtCore.QRect(0, self.text_rect.height(),
                                     rect.width(), rect.height() - self.text_rect.height())
        for led in self.LEDs:
            led.setBrushCenter(self.led_rect.width() / 2.0, self.led_rect.height() / 2.0 + self.text_rect.height())
            led.setPosition((rect_width * led.area[0]) + self.padding_size / 2,
                            (rect_height * led.area[1]) + self.padding_size / 2)
            led.setBrush()
        return


class LedNavigator(cNavigator):
    def __init__(self, time):
        super(LedNavigator, self).__init__()

        self.device_time = time
        self.Led_data = []

        self.main_layout = QtGui.QVBoxLayout()

        self.renderArea = RenderArea()
        self.main_layout.addWidget(self.renderArea)

        widget = QtGui.QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)
        return

    def addLed(self, pos, color, text, status_arr):
        led = self.renderArea.addLed(pos, color, text)
        self.Led_data.append((led, status_arr))
        return

    def getIndex(self):
        return max(self.device_time.searchsorted(self.time, side='right')-1, 0)

    def seekWindow(self):
        Index = self.getIndex()
        for led, led_status in self.Led_data:
            led.setState(led_status[Index])
        return


if __name__ == '__main__':
    import sys

    app = QtGui.QApplication(sys.argv)

    Window = LedNavigator(None)
    for pos in area2multiplier.iterkeys():
        Window.addLed(pos, "red", pos, [False])
    Window.show()
    sys.exit(app.exec_())
