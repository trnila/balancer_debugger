import threading

import collections
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_gtk3cairo import (FigureCanvasGTK3Cairo as FigureCanvas)
from matplotlib.backends.backend_gtk3 import NavigationToolbar2GTK3 as NavigationToolbar
from gi.repository import GObject


plt.ion()

class Chart:
    def __init__(self, parent, app, data_handler, labels, last_values=1000):
        self.last_values = last_values
        self.data = [
            collections.deque(range(0, last_values)),
            collections.deque(range(0, last_values)),
        ]
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.axes.set_ylim(0, 65535)
        self.line = [self.axes.plot(range(0, last_values), range(0, last_values), '-', label=label)[0] for label in labels]
        self.data_handler = data_handler

        canvas = FigureCanvas(self.figure)
        canvas.set_size_request(800, 600)
        parent.add(NavigationToolbar(canvas, app.window))
        parent.add(canvas)

        app.input.handlers.append(self.process)
        self.animation = FuncAnimation(self.figure, self.update, interval=100)

    def process(self, row):
        a, b = self.data_handler(row)
        self.data[0].append(a)
        self.data[1].append(b)

        self.data[0].popleft()
        self.data[1].popleft()

    def update(self, *kwargs):
        for i, _ in enumerate(self.line):
            self.line[i].set_ydata(self.data[i])
        self.figure.legend()


class Touches:
    def __init__(self, app, last_values=1000):
        self.last_values = last_values
        self.x = []
        self.y = []
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.axes.set_ylim(0, 65535)
        self.axes.set_xlim(0, 65535)
        self.line, = self.axes.plot(self.x, self.y, '-')
        self.lock = threading.Lock()

        GObject.timeout_add(100, self.update)
        app.input.handlers.append(self.process)

    def process(self, row):
        with self.lock:
            self.x.append(int(row['RX']))
            self.y.append(int(row['RY']))

            if len(self.y) > self.last_values:
                self.y.pop(0)
                self.x.pop(0)

    def update(self):
        with self.lock:
            self.line.set_xdata(self.x)
            self.line.set_ydata(self.y)
        self.figure.canvas.draw()
        return True