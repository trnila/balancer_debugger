import argparse
import threading
from collections import deque
from queue import Queue

from serial import Serial
from ui_control import Ui_ControlForm
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtGui import QDialog
import numpy as np
import logging


class Chunked:
    def __init__(self, plot, key, **kwargs):
        self.plot = plot
        self.curves = []
        self.i = 0
        self.chunkSize = 100
        # Remove chunks after we have 10
        self.maxChunks = 10
        self.startTime = pg.ptime.time()
        self.data = np.empty((self.chunkSize + 1, 2))
        self.key = key
        self.kwargs = kwargs
        self.chunk = 0

    def update(self, row):
        now = pg.ptime.time()
        for c in self.curves:
            c.setPos(-(now - self.startTime), 0)

        i = self.i % self.chunkSize
        if i == 0:
            kwargs = {**self.kwargs}

            if self.chunk == 0:
                kwargs['name'] = self.key

            curve = self.plot.plot(**kwargs)
            self.curves.append(curve)
            last = self.data[-1]
            self.data = np.empty((self.chunkSize + 1, 2))
            self.data[0] = last
            while len(self.curves) > self.maxChunks:
                c = self.curves.pop(0)
                self.plot.removeItem(c)

            self.chunk += 1
        else:
            curve = self.curves[-1]

        self.data[i + 1, 0] = now - self.startTime
        self.data[i + 1, 1] = row[self.key]
        curve.setData(x=self.data[:i + 2, 0], y=self.data[:i + 2, 1])
        self.i += 1


class Touch:
    def __init__(self, plot, lastPoints=50):
        self.plot = plot
        self.lastPoints = lastPoints
        self.x = deque()
        self.y = deque()
        self.curve = self.plot.plot([], pen=(200, 200, 200), symbolBrush=(255, 0, 0), symbolPen='w')
        self.i = 0

    def update(self, row):
        self.x.append(row['RX'])
        self.y.append(row['RY'])
        self.curve.setData(self.x, self.y)
        self.i += 1

        if len(self.x) > self.lastPoints:
            self.x.popleft()
            self.y.popleft()


class ControlWidget(QDialog, Ui_ControlForm):
    def __init__(self, input):
        super(QDialog, self).__init__()
        self.serial = input
        self.setupUi(self)

        self.mode.currentTextChanged.connect(self.send_cmd("mode"))
        self.const_p.valueChanged.connect(self.send_cmd("set_p"))
        self.const_k.valueChanged.connect(self.send_cmd("set_k"))
        self.pauseBtn.clicked.connect(self.pause)
        self.enableServos.clicked.connect(self.send_cmd("enable_servos"))
        self.cmd.returnPressed.connect(self.prepare_cmd)

    def send_cmd(self, cmd):
        def fn(*args):
            self.serial.send_cmd(cmd, *args)
        return fn

    def prepare_cmd(self):
        args = self.cmd.text().split(' ')
        self.serial.send_cmd(*args)

    def pause(self, pause):
        self.serial.pause = pause

    def update(self, row):
        self.current.setText("[{}, {}]".format(row['RX'], row['RY']))


class Input:
    def __init__(self, serial):
        self.serial: Serial = serial
        self.pause = False
        self.measurements = Queue()
        self.thread = threading.Thread(target=self._do_start)
        self.thread.daemon = True

    def send_cmd(self, cmd, *arguments):
        def mapper(s):
            if type(s) == bool:
                s = 1 if s else 0
            elif type(s) == float:
                return format(s, '.10f')

            return str(s)

        text = " ".join([cmd] + list(map(mapper, arguments)))
        print(text)
        self.serial.write((text + "\n").encode())

    def start(self):
        self.thread.start()

    def get_available(self, max_measures=10):
        measurements = []
        while not self.measurements.empty() and max_measures > 0:
            measurements.append(self.measurements.get())
            max_measures -= 1

        return measurements

    def _do_start(self):
        self._flush_input()
        while True:
            line = self._readline()
            row = dict([i.split('=', 2) for i in line.split(' ') if len(i.split('=', 2)) == 2])

            self.measurements.put(row)

    def _readline(self):
        line = self.serial.readline().decode().strip()
        return line

    def _flush_input(self):
        self.serial.timeout = 0.005
        while self.serial.readline():
            pass

        for i in range(0, 50):
            self.serial.readline()

        self.serial.timeout = None

class App:
    def __init__(self, args):
        self.serial = Input(Serial(args.serial, args.baudrate))

        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update_charts)
        self.charts = []

        self.app = QtGui.QApplication([])
        self.w = QtGui.QWidget()
        self.win = pg.MultiPlotWidget()

    def next_row(self):
        self.win.nextRow()

    def start(self):
        self.serial.start()

        setup_charts(self)

        control = ControlWidget(self.serial)

        layout = QtGui.QGridLayout()
        self.w.setLayout(layout)
        layout.addWidget(self.win)
        layout.addWidget(control)

        self.timer.start(20)

        self.w.show()
        self.app.exec_()

    def update_charts(self):
        line = self.serial.get_available(1)
        if self.serial.pause or len(line) <= 0:
            return

        for row in line:
            for chart in self.charts:
                try:
                    chart.update(row)
                except Exception as e:
                    logging.exception(e)

    def plot(self, keys, yrange, colspan, title):
        pens = [(255, 0, 0), (0, 255, 0)]

        p6 = self.win.addPlot(colspan=colspan, title=title)
        p6.addLegend()
        p6.setLabel('bottom', 'Time', 's')
        p6.setXRange(-10, 0)
        p6.setYRange(*yrange)

        for i, key in enumerate(keys):
            self.charts.append(Chunked(p6, key, pen=pens[i]))


logging.getLogger().setLevel(logging.DEBUG)

parser = argparse.ArgumentParser()
parser.add_argument('--serial', default='/dev/ttyACM0')
parser.add_argument('--baudrate', default=115200)
args = parser.parse_args()


def setup_charts(app):
    app.next_row()
    #plot(['RX', 'RY'], [0, 65535], colspan=2)
    #plot(['USX', 'USY'], [0, 0.1], colspan=2)
    app.plot(['nx', 'ny'], [-1, 1], colspan=2, title='normal')
    app.plot(['vx', 'vy'], [-1000, 1000], colspan=2, title='speed')

    app.next_row()
    app.plot(['nsx', 'nsy'], [-1, 1], colspan=2, title='normalized speed')

    p3 = app.win.addPlot(colspan=1, title="Touch resistance")
    p3.setXRange(0, 65535)
    p3.setYRange(0, 65535)

    app.charts.append(Touch(p3))


app = App(args)
app.start()
