import threading
from queue import Queue

from serial import Serial


class Input:
    def __init__(self, serial):
        self.serial: Serial = serial
        self.pause = False
        self.measurements = Queue()
        self.thread = threading.Thread(target=self._do_start)
        self.thread.daemon = True

    def send_cmd(self, cmd, *arguments):
        def mapper(s):
            if type(s) == bool:
                s = 1 if s else 0
            elif type(s) == float:
                return format(s, '.10f')

            return str(s)

        text = " ".join([cmd] + list(map(mapper, arguments)))
        print(text)
        self.serial.write((text + "\n").encode())

    def start(self):
        self.thread.start()

    def get_available(self, max_measures=10):
        measurements = []
        while not self.measurements.empty() and max_measures > 0:
            measurements.append(self.measurements.get())
            max_measures -= 1

        return measurements

    def _do_start(self):
        self._flush_input()
        while True:
            line = self._readline()
            row = dict([i.split('=', 2) for i in line.split(' ') if len(i.split('=', 2)) == 2])

            self.measurements.put(row)

    def _readline(self):
        line = self.serial.readline().decode().strip()
        return line

    def _flush_input(self):
        self.serial.timeout = 0.005
        while self.serial.readline():
            pass

        for i in range(0, 50):
            self.serial.readline()

        self.serial.timeout = None