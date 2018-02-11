import argparse
from collections import deque

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
        self.const_k.valueChanged.connect(self.send_cmd("set_k"))
        self.pauseBtn.clicked.connect(self.pause)

    def send_cmd(self, cmd):
        def fn(*args):
            self.serial.send_cmd(cmd, *args)
        return fn

    def pause(self, pause):
        self.serial.pause = pause


class Input:
    def __init__(self, serial):
        self.serial: Serial = serial
        self.pause = False

    def send_cmd(self, cmd, *arguments):
        text = " ".join([cmd] + list(map(str, arguments)))
        print(text)
        self.serial.write((text + "\n").encode())

    def readline(self):
        return self.serial.readline().decode().strip()


parser = argparse.ArgumentParser()
parser.add_argument('--serial', default='/dev/ttyACM0')
parser.add_argument('--baudrate', default=115200)
args = parser.parse_args()


app = QtGui.QApplication([])
w = QtGui.QWidget()

win = pg.MultiPlotWidget()

win.nextRow()
p5 = win.addPlot(colspan=3, title='Resistance')
p5.addLegend()
p5.setLabel('bottom', 'Time', 's')
p5.setXRange(-10, 0)
p5.setYRange(0, 65535)

win.nextRow()
p6 = win.addPlot(colspan=2, title='USX/USY')
p6.addLegend()
p6.setLabel('bottom', 'Time', 's')
p6.setXRange(-10, 0)
p6.setYRange(0, 1)

p3 = win.addPlot(colspan=1, title="Touch resistance")
p3.setXRange(0, 65535)
p3.setYRange(0, 65535)

charts = [
    Chunked(p5, 'RX', pen=(255, 0, 0)),
    Chunked(p5, 'RY', pen=(0, 255, 0)),

    Chunked(p6, 'USX', pen=(255, 0, 0)),
    Chunked(p6, 'USY', pen=(0, 255, 0)),

    Touch(p3)
]

serial = Input(Serial(args.serial, args.baudrate))
control = ControlWidget(serial)

layout = QtGui.QGridLayout()
w.setLayout(layout)
layout.addWidget(win)
layout.addWidget(control)


def update():
    line = serial.readline()
    if serial.pause:
        return

    row = dict([i.split('=', 2) for i in line.split(' ') if len(i.split('=', 2)) == 2])

    mapper = {
        'USX': float,
        'USY': float,
        'RX': int,
        'RY': int
    }

    defaults = dict((key, 0) for key in mapper.keys())
    row = {**defaults, **row}

    for k, v in mapper.items():
        row[k] = v(row[k])

    for chart in charts:
        try:
            chart.update(row)
        except Exception as e:
            logging.exception(e)


timer = pg.QtCore.QTimer()
timer.timeout.connect(update)
timer.start(0)

w.show()
app.exec_()
