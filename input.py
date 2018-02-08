from threading import Thread

import serial


class Input:
    def __init__(self, input, baudrate):
        self.serial = serial.Serial(input, baudrate=baudrate)
        self.handlers = []
        self.pause = False

    def start(self):
        while True:
            try:
                line = self.serial.readline().decode('utf-8').strip()
                if not self.pause:
                    data = dict(i.split('=', 2) for i in line.split(' '))

                    for handler in self.handlers:
                        handler(data)
            except Exception as e:
                print(e)

    def start_threaded(self):
        t = Thread(target=self.start)
        t.start()
