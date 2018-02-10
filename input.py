from threading import Thread

import serial
import logging


class Input:
    def __init__(self, input, baudrate):
        self.serial = serial.Serial(input, baudrate=baudrate)
        self.serial.reset_input_buffer()
        self.handlers = []
        self.pause = False
        self._t = None
        self.map = {
            'RX': int,
            'RY': int,
            'USX': float,
            'USY': float
        }

    def start(self):
        while True:
            try:
                line = self.serial.readline().decode('utf-8').strip()
                print(line)
                if not self.pause:
                    data = dict([i.split('=', 2) for i in line.split(' ') if len(i.split('=', 2)) == 2])

                    if all(key in data.keys() for key in self.map.keys()):
                        for key, map in self.map.items():
                            data[key] = map(data[key])

                        for handler in self.handlers:
                            try:
                                handler(data)
                            except BaseException as e:
                                logging.exception(e)
            except Exception as e:
                logging.exception(e)

    def start_threaded(self):
        self._t = Thread(target=self.start)
        self._t.daemon = True
        self._t.start()
