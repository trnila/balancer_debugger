import logging
import sys
import threading
import time
import itertools
import struct
import pandas as pd
from collections import deque
from queue import Queue

from serial import Serial, SerialException

def parse_line(line):
    def fix(pair):
        return pair[0], float(pair[1])

    row = dict([fix(i.split('=', 2)) for i in line.split(' ') if len(i.split('=', 2)) == 2])
    return row

class TextLineReader:
    """RX=val RY=val\n"""
    def read_next(self, io):
        line = io.readline()
        row = parse_line(line)

class BinaryReader:
    def __init__(self):
        fields = [
            'c',
            'v',
            'pos',
            'rv',
            'ra',
            'n',
            'r',
            'us',
            'raw'
        ]

        self.measures = list(itertools.chain(*[[f + 'x', f + 'y'] for f in fields]))

    def read_next(self, io):
        while True:
            x = io.read(2 + len(self.measures) * 4)
            if x[0] != 0xab or x[1] != 0xcd:
                continue

            values = struct.unpack("{}f".format(len(self.measures)), x[2:])
            return dict(zip(self.measures, values))

class RunningAverage:
    def __init__(self, keep_last=10):
        self.last = deque()
        self.size = keep_last

    def add(self, val):
        self.last.append(val)

        if len(self.last) > self.size:
            self.last.popleft()

    def median(self):
        items = sorted(self.last)
        return self.last[int(len(items) / 2)]


class SerialSource:
    def __init__(self, device, baud, reader):
        self.serial = Serial(device, baudrate=baud)
        self.measures_keys_avg = RunningAverage()
        self.reader = reader

    def handle_lines(self, announce):
        self._flush_input()
        while True:
            try:
                row = self.reader.read_next(self.serial)

                self.measures_keys_avg.add(len(row.keys()))
                if self.measures_keys_avg.median() != len(row.keys()):
                    logging.debug("Dropped measurement", row)
                    continue

                announce(row)
            except Exception as e:
                logging.exception(e)
                self._reopen()

    def write(self, text):
        self.serial.write(text.encode())

    def _reopen(self):
        self.serial.close()
        time.sleep(0.5)

        while True:
            try:
                self.serial.open()
                return
            except BaseException as e:
                logging.exception(e)

            time.sleep(0.5)

    def _readline(self):
        return self.serial.readline().decode().strip()

    def _flush_input(self):
        self.serial.timeout = 0.005
        while self.serial.readline():
            pass

        for i in range(0, 50):
            self.serial.readline()

        self.serial.timeout = None


class StreamSource:
    def __init__(self, source, reader):
        self.source = source
        self.reader = reader

    def handle_lines(self, announce):
        while True:
            try:
                announce(self.reader.read_next(self.source))
            except Exception as e:
                logging.exception(e)

    def write(self, msg):
        raise NotImplementedError()


class Input:
    def __init__(self, args):
        def new_measurement(row):
            self.measurements.put(row)

            with self.lock:
                self.measured.append(row)

        reader = BinaryReader()
        self.serial = SerialSource(args.serial, args.baudrate, reader) if args.serial else StreamSource(sys.stdin.buffer, reader)
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
        self.serial.write(text + "\n")

    def start(self):
        self.thread.start()

    def get_available(self, max_measures=10):
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

