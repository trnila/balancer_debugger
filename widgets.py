from collections import deque

from PyQt5.QtWidgets import QDialog
from PyQt5 import QtCore

from uart import Client
from ui_control import Ui_ControlForm
import pyqtgraph as pg
import numpy as np
import pandas as pd
import pyqtgraph.opengl as gl

from ipython import ConsoleWidget


def normalize(v):
    l = np.linalg.norm(v)

    if l == 0:
        return v
    return v / l


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

    def new_measurement(self, row):
        now = pg.ptime.time()
        for c in self.curves:
            c.setPos(-(now - self.startTime), 0)

        i = self.i % self.chunkSize
        if i == 0:
            kwargs = {**self.kwargs}

            if self.chunk % 10 == 0:
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
    def __init__(self, plot, keys, lastPoints=50):
        self.plot = plot
        self.keys = keys
        self.lastPoints = lastPoints
        self.x = deque()
        self.y = deque()
        self.curve = self.plot.plot([], pen=(200, 200, 200), symbolBrush=(255, 0, 0), symbolPen='w')
        self.i = 0

    def new_measurement(self, row):
        self.x.append(row[self.keys[0]])
        self.y.append(row[self.keys[1]])
        self.curve.setData(self.x, self.y)
        self.i += 1

        if len(self.x) > self.lastPoints:
            self.x.popleft()
            self.y.popleft()


class ControlWidget(QDialog, Ui_ControlForm):
    def __init__(self, app):
        super(QDialog, self).__init__()
        self.client: Client = app.serial.client
        self.setupUi(self)
        self.app = app

        banner = [
            "data() - return pandas dataframe",
            "clr() - clear dataframes"
        ]

        self.console = ConsoleWidget(customBanner="\n".join(banner) + "\n")
        self.console.push_vars({
            'serial': self.client,
            'data': app.serial.create_dataframe,
            'clr': app.serial.clear_measured
        })
        self.console.execute_command("import pandas as pd")
        self.console.execute_command('%matplotlib inline')
        self.jupyter_console.layout().addWidget(self.console)

        self.const_p.valueChanged.connect(self.send_pid)
        self.const_d.valueChanged.connect(self.send_pid)
        self.const_i.valueChanged.connect(self.send_pid)
        self.pos_x.valueChanged.connect(self.send_pos)
        self.pos_y.valueChanged.connect(self.send_pos)

        self.refreshBtn.clicked.connect(self.refresh)
        self.pauseBtn.clicked.connect(self.pause)
        #self.enableServos.clicked.connect(self.send_cmd("enable_servos"))

        app.serial.pos_changed.connect(self.on_pos_changed)
        app.serial.pid_changed.connect(self.on_pid_changed)
        app.serial.dim_changed.connect(self.on_dim_changed)

        self.refresh()

    def refresh(self):
        self.client.get_pid()
        self.client.get_pos()
        self.client.get_dim()

    def on_pos_changed(self, x, y):
        self.pos_x.setValue(x)
        self.pos_y.setValue(y)

    def on_pid_changed(self, p, i, d):
        self.const_p.setValue(p)
        self.const_i.setValue(i)
        self.const_d.setValue(d)

    def on_dim_changed(self, size_x, size_y):
        self.pos_x.setMaximum(size_x)
        self.pos_y.setMaximum(size_y)

    def send_pid(self):
        self.client.set_pid(
            float(self.const_p.text()),
            float(self.const_i.text()),
            float(self.const_d.text()),
        )

    def send_pos(self):
        self.client.set_pos(
            int(self.pos_x.text()),
            int(self.pos_y.text())
        )

    def pause(self, pause):
        self.app.pause = pause