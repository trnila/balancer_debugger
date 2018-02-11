from collections import deque

from serial import Serial
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import logging
from input import Input


win = pg.GraphicsWindow()

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


win.nextRow()
p5 = win.addPlot(colspan=2, title='Resistance')
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


p3 = win.addPlot(title="Touch resistance", colspan=1)
p3.setXRange(0, 65535)
p3.setYRange(0, 65535)

charts = [
    Chunked(p5, 'RX', pen=(255, 0, 0)),
    Chunked(p5, 'RY', pen=(0, 255, 0)),

    Chunked(p6, 'USX', pen=(255, 0, 0)),
    Chunked(p6, 'USY', pen=(0, 255, 0)),

    Touch(p3)
]

serial = Serial("/dev/pts/5", 115200)

def update():
    line = serial.readline().decode().strip()
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
timer.start(50)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
