import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject
from matplotlib.backends.backend_gtk3agg import (
    FigureCanvasGTK3Agg as FigureCanvas)
from matplotlib.backends.backend_gtk3 import NavigationToolbar2GTK3 as NavigationToolbar

from matplotlib.figure import Figure
from ser import Input
import threading
import numpy as np



class Chart:
    def __init__(self, last_values=1000):
        self.last_values = last_values
        self.y = [[0, 0] for i in range(0, last_values)]
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.axes.set_ylim(0, 65535)
        self.line = self.axes.plot(range(0, len(self.y)), self.y, '-')

        GObject.timeout_add(100, self.update)

    def process(self, row):
        self.y.append([int(row['RX']), int(row['RY'])])

        if len(self.y) > self.last_values:
            self.y.pop(0)

    def update(self):
        for i, _ in enumerate(self.line):
            self.line[i].set_ydata([v[i] for v in self.y])
        self.figure.canvas.draw()
        return True

class Touches:
    def __init__(self, last_values=1000):
        self.last_values = last_values
        self.x = []
        self.y = []
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.axes.set_ylim(0, 65535)
        self.axes.set_xlim(0, 65535)
        self.lock = threading.Lock()

        GObject.timeout_add(100, self.update)

    def process(self, row):
        with self.lock:
            self.x.append(int(row['RX']))
            self.y.append(int(row['RY']))

            if len(self.y) > self.last_values:
                self.y.pop(0)
                self.x.pop(0)

    def update(self):
        self.axes.clear()
        with self.lock:
            self.axes.plot(self.x, self.y, '-')
        self.figure.canvas.draw()
        return True
d = Chart()


class Handler:
    def __init__(self, input):
        self.input = input

    def pause(self, param):
        self.input.pause = param.get_active()

i = Input()

builder = Gtk.Builder()
builder.add_from_file("ui.glade")
builder.connect_signals(Handler(i))

window = builder.get_object("window")
window.connect("delete_event", Gtk.main_quit)

canvas = FigureCanvas(d.figure)
canvas.set_size_request(800, 600)
builder.get_object("chart").add(NavigationToolbar(canvas, window))
builder.get_object("chart").add(canvas)

t = Touches()
canvas = FigureCanvas(t.figure)

canvas = FigureCanvas(t.figure)
canvas.set_size_request(800, 600)
builder.get_object("touch").add(canvas)

window.show_all()

i.handlers.append(d.process)
i.handlers.append(t.process)
i.start_threaded()

Gtk.main()