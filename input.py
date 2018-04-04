import logging
import threading

import pandas as pd
from queue import Queue

from PyQt5.QtCore import pyqtSignal, QObject

import uart
from serial import Serial


class Input(QObject):
    pos_changed = pyqtSignal(int, int)
    pid_changed = pyqtSignal(float, float, float)

    def __init__(self, args):
        super().__init__()

        def frame_handler():
            while True:
                try:
                    cmd, data = self.client.read_next()

                    if cmd == 128:
                        self.measurements.put(data)

                        with self.lock:
                            self.measured.append(data)
                    else:
                        if cmd == 193:
                            self.pos_changed.emit(data[0], data[1])
                        elif cmd == 194:
                            self.pid_changed.emit(*data)
                except Exception as e:
                    logging.exception(e)

        self.client = uart.Client(Serial(args.serial, baudrate=args.baudrate))
        self.pause = False
        self.measurements = Queue()
        self.thread = threading.Thread(target=frame_handler)
        self.thread.daemon = True

        self.measured = []
        self.lock = threading.Lock()

    def send_cmd(self, cmd, *arguments):
        getattr(self.client, cmd)(*arguments)

    def start(self):
        self.thread.start()

    def get_available(self, max_measures=10):
        #print(self.measurements.qsize())
        measurements = []
        while not self.measurements.empty() and max_measures > 0:
            measurements.append(self.measurements.get())
            max_measures -= 1

        return measurements

    def clear_measured(self):
        self.measured = []

    def create_dataframe(self):
        with self.lock:
            return pd.DataFrame(self.measured)
