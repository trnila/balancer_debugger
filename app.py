import gi

from widgets import Chart, Touches

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from matplotlib.backends.backend_gtk3agg import (FigureCanvasGTK3Agg as FigureCanvas)
from matplotlib.backends.backend_gtk3 import NavigationToolbar2GTK3 as NavigationToolbar
import argparse

from input import Input


class App:
    def __init__(self, window, args):
        print(args)
        self.window = window
        self.input = Input(args.serial, args.baudrate)

    def pause(self, param):
        self.input.pause = param.get_active()

    def add_chart(self, object, chart):
        canvas = FigureCanvas(chart.figure)
        canvas.set_size_request(800, 600)
        builder.get_object(object).add(NavigationToolbar(canvas, window))
        builder.get_object(object).add(canvas)

parser = argparse.ArgumentParser()
parser.add_argument('serial')
parser.add_argument('--baudrate', default=115200)

builder = Gtk.Builder()
builder.add_from_file("ui.glade")
window = builder.get_object("window")
window.connect("delete_event", Gtk.main_quit)

app = App(window, parser.parse_args())
builder.connect_signals(app)

app.add_chart("chart", Chart(app))
app.add_chart("touch", Touches(app))

window.show_all()
app.input.start_threaded()
Gtk.main()