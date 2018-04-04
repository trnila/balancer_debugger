import logging
import threading
import pandas as pd
from queue import Queue

import uart
from serial import Serial


class SerialSource:
    def __init__(self, device, baud):
        self.source = uart.Client(Serial(device, baudrate=baud))

    def handle_lines(self, announce):
        while True:
            try:
                row = self.source.read_next()
                #announce(row[1])
            except Exception as e:
                logging.exception(e)


class Input:
    def __init__(self, args):
        def new_measurement(row):
            self.measurements.put(row)

            with self.lock:
                self.measured.append(row)

        self.serial = SerialSource(args.serial, args.baudrate)
        self.pause = False
        self.measurements = Queue()
        self.thread = threading.Thread(target=self.serial.handle_lines, args=[new_measurement])
        self.thread.daemon = True

        self.measured = []
        self.lock = threading.Lock()

    def send_cmd(self, cmd, *arguments):
        def mapper(s):
            if type(s) == bool:
                s = 1 if s else 0
            elif type(s) == float:
                return format(s, '.10f')

            return str(s)

        text = " ".join([cmd] + list(map(mapper, arguments)))
        print(text)
        #self.serial.write(text + "\n")

    def start(self):
        self.thread.start()

    def get_available(self, max_measures=10):
        print((self.measurements.qsize()))
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
