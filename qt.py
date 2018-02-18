import argparse

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout
from serial import Serial

from input import Input
import logging

from setup import setup_charts
from widgets import *


class App:
    def __init__(self, args):
        self.serial = Input(args.serial, args.baudrate)

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

        control = ControlWidget(self)
        control.charts.layout().addWidget(self.win)

        self.timer.start(20)
        self.w.setLayout(control.layout())
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
        p6.setXRange(-10, 0)
        p6.setYRange(*yrange)

        for i, key in enumerate(keys):
            self.charts.append(Chunked(p6, key, pen=pens[i]))


logging.getLogger().setLevel(logging.DEBUG)

parser = argparse.ArgumentParser()
parser.add_argument('--serial', default='/dev/ttyACM0')
parser.add_argument('--baudrate', default=115200)
args = parser.parse_args()


app = App(args)
app.start()
