from collections import deque

from PyQt5.QtWidgets import QDialog

from ui_control import Ui_ControlForm
import pyqtgraph as pg
import numpy as np
import pandas as pd

from ipython import ConsoleWidget


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
    def __init__(self, app):
        super(QDialog, self).__init__()
        self.serial = app.serial
        self.setupUi(self)

        self.console = ConsoleWidget(customBanner='prepare() - returns pandas\n')
        self.console.push_vars({
            'serial': self.serial,
            'prepare': lambda: pd.DataFrame(self.serial.measured)}
        )
        self.console.execute_command("import pandas as pd")
        self.console.execute_command('%matplotlib inline')
        self.jupyter_console.layout().addWidget(self.console)

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
