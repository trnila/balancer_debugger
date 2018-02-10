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
    def __init__(self, parent, app, data_handler, labels, ylimits, last_values=2000):
        self.last_values = last_values
        self.data = [
            collections.deque(range(0, last_values)),
            collections.deque(range(0, last_values)),
        ]
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.axes.set_ylim(*ylimits)
        self.line = [self.axes.plot(range(0, last_values), range(0, last_values), '-', label=label)[0] for label in labels]
        self.data_handler = data_handler

        canvas = FigureCanvas(self.figure)
        canvas.set_size_request(800, 600)
        parent.add(NavigationToolbar(canvas, app.window))
        parent.add(canvas)

        app.input.handlers.append(self.process)
        self.animation = FuncAnimation(self.figure, self.update)

    def process(self, row):
        a, b = self.data_handler(row)
        self.data[0].append(a)
        self.data[1].append(b)

        self.data[0].popleft()
        self.data[1].popleft()

    def update(self, *kwargs):
        for i, _ in enumerate(self.line):
            self.line[i].set_ydata(self.data[i])
        return self.line


class Touches:
    def __init__(self, parent, app, last_values=100):
        self.last_values = last_values
        self.x = []
        self.y = []
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.axes.set_ylim(0, 65535)
        self.axes.set_xlim(0, 65535)
        self.line, = self.axes.plot(self.x, self.y, '-')
        self.lock = threading.Lock()

        canvas = FigureCanvas(self.figure)
        canvas.set_size_request(800, 600)
        parent.add(NavigationToolbar(canvas, app.window))
        parent.add(canvas)

        app.input.handlers.append(self.process)
        self.animation = FuncAnimation(self.figure, self.update)

    def process(self, row):
        with self.lock:
            self.x.append(int(row['RX']))
            self.y.append(int(row['RY']))

            if len(self.y) > self.last_values:
                self.y.pop(0)
                self.x.pop(0)

    def update(self, *kwargs):
        with self.lock:
            self.line.set_xdata(self.x)
            self.line.set_ydata(self.y)
        return self.line


class Console:
    def __init__(self, target, app, max_rows=50):
        self.target = target
        self.app = app
        self.lines = []
        self.max_rows = max_rows

        app.input.handlers.append(self.fill_console)

    def fill_console(self, row):
        buffer = self.target.get_buffer()
        self.lines.append(str(row))
        if len(self.lines) > self.max_rows:
            self.lines.pop(0)


        def dothat():
            end_iter = buffer.get_end_iter()
            buffer.insert(end_iter, str(row) + "\n")
            self.target.scroll_to_mark(buffer.get_insert(), 0, False, 0, 0)

        GObject.idle_add(dothat)