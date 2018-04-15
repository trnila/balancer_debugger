import argparse
import signal
import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout
from uart import Serial

from input import Input
import logging

from setup import setup_charts
from widgets import *


class App:
    def __init__(self, args):
        self.serial = Input(args)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_charts)
        self.charts = []

        self.app = QApplication([])
        self.w = QWidget()
        self.win = pg.MultiPlotWidget()
        self.pause = False

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

        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.app.exec_()

    def update_charts(self):
        line = self.serial.get_available()
        if self.pause:
            return

        for row in line:
            for chart in self.charts:
                try:
                    chart.new_measurement(row)
                except:
                    logging.exception(sys.exc_info()[0])

    def plot(self, keys, yrange, colspan, title):
        pens = [(255, 0, 0), (0, 255, 0)]

        p6 = self.win.addPlot(colspan=colspan, title=title)
        p6.addLegend()
        p6.setXRange(-10, 0)
        p6.setYRange(*yrange)

        for i, key in enumerate(keys):
            self.charts.append(Chunked(p6, key, pen=pens[i]))


logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger('ipykernel.inprocess.ipkernel').setLevel(logging.ERROR)
logging.getLogger('traitlets').setLevel(logging.ERROR)
try:
    import colorlog

    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(levelname)s:%(name)s:%(message)s'))

    logger = colorlog.getLogger()
    logger.addHandler(handler)
except ImportError:
    # optional feature
    pass

parser = argparse.ArgumentParser()
parser.add_argument('--serial')
parser.add_argument('--baudrate', default=460800)
parser.add_argument('--csv')
args = parser.parse_args()


app = App(args)
app.start()
