import threading

from matplotlib.figure import Figure
from gi.repository import GObject


class Chart:
    def __init__(self, app, data_handler, labels, last_values=1000):
        self.last_values = last_values
        self.y = [[0, 0] for i in range(0, last_values)]
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.axes.set_ylim(0, 65535)
        self.line = [self.axes.plot(range(0, last_values), range(0, last_values), '-', label=label)[0] for label in labels]
        self.data_handler = data_handler

        GObject.timeout_add(100, self.update)
        app.input.handlers.append(self.process)

    def process(self, row):
        self.y.append(self.data_handler(row))

        if len(self.y) > self.last_values:
            self.y.pop(0)

    def update(self):
        for i, _ in enumerate(self.line):
            self.line[i].set_ydata([v[i] for v in self.y])
        self.figure.legend()
        self.figure.canvas.draw()
        return True


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