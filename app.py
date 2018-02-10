import gi

from widgets import Chart, Touches, Console

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject
from matplotlib.backends.backend_gtk3agg import (FigureCanvasGTK3Agg as FigureCanvas)
from matplotlib.backends.backend_gtk3 import NavigationToolbar2GTK3 as NavigationToolbar
import argparse

from input import Input


class App:
    def __init__(self, window, args):
        self.window = window
        self.input = Input(args.serial, args.baudrate)

    def pause(self, param):
        self.input.pause = param.get_active()


parser = argparse.ArgumentParser()
parser.add_argument('serial')
parser.add_argument('--baudrate', default=115200)

GObject.threads_init()

builder = Gtk.Builder()
builder.add_from_file("ui.glade")
window = builder.get_object("window")
window.connect("delete_event", Gtk.main_quit)

app = App(window, parser.parse_args())
builder.connect_signals(app)

Chart(builder.get_object("chart"), app, lambda row: [row['RX'], row['RY']], ['RX', 'RY'], [0, 65535])
Chart(builder.get_object("servos"), app, lambda row: [row['USX'], row['USY']], ['USX', 'USY'], [0, 1])
Touches(builder.get_object("touch"), app)
Console(builder.get_object("console"), app)

window.show_all()
app.input.start_threaded()
Gtk.main()