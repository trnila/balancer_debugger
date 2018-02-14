import argparse

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout
from serial import Serial

from input import Input
import logging

from widgets import *


class App:
    def __init__(self, args):
        self.serial = Input(Serial(args.serial, args.baudrate))

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_charts)
        self.charts = []

        self.app = QApplication([])
        self.w = QWidget()
        self.win = pg.MultiPlotWidget()

    def next_row(self):
        self.win.nextRow()

    def start(self):
        self.serial.start()

        setup_charts(self)

        control = ControlWidget(self.serial)

        layout = QGridLayout()
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
