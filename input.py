import logging
import threading
from collections import deque
from queue import Queue

from serial import Serial


def parse_line(line):
    def fix(pair):
        return pair[0], float(pair[1])

    row = dict([fix(i.split('=', 2)) for i in line.split(' ') if len(i.split('=', 2)) == 2])
    return row


class RunningAverage:
    def __init__(self, keep_last=10):
        self.last = deque()
        self.size = keep_last

    def add(self, val):
        self.last.append(val)

        if len(self.last) > self.size:
            self.last.popleft()

    def avg(self):
        return sum(self.last) / len(self.last)

    def median(self):
        items = sorted(self.last)
        return self.last[int(len(items) / 2)]


class Input:
    def __init__(self, serial):
        self.serial: Serial = serial
        self.pause = False
        self.measurements = Queue()
        self.thread = threading.Thread(target=self._do_start)
        self.thread.daemon = True

        self.measures_keys_avg = RunningAverage()

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

            row = parse_line(line)

            self.measures_keys_avg.add(len(row.keys()))
            if self.measures_keys_avg.median() != len(row.keys()):
                logging.debug("Dropped measurement", row)
                continue

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