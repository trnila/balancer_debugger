import itertools
import logging

from cobs import cobs
from serial import Serial, SerialException
import struct
import time


class Command:
    def __init__(self, num, *args):
        self.id = num
        self.args = args

    def __call__(self, **kwargs):
        args = [kwargs[i[0]] for i in self.args]
        fmt = "".join([i[1] for i in self.args])

        binary = struct.pack(("=B" + fmt), self.id, *args)
        encoded = cobs.encode(bytearray(binary))
        s.write(encoded + b"\0")
        print(len(encoded))


class MeasureEncoder:
    def __init__(self):
        self.fields = [
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

    def __call__(self, body, *args, **kwargs):
        measures = list(itertools.chain(*[[f + 'x', f + 'y'] for f in self.fields]))
        values = struct.unpack("{}f".format(len(measures)), body)
        return dict(zip(measures, values))


class Client:
    def __init__(self, serial: Serial):
        self.serial = serial
        self.serial.timeout = 0.02
        self.cmds = {
            'reset': Command(0),
            'pos': Command(1, ('x', 'I'), ('y', 'I')),
            'pid': Command(2, ('p', 'd'), ('i', 'd'), ('d', 'd'))
        }
        self.encoders = {
            128: MeasureEncoder()
        }
        self.buffer = b""

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

    def read_next(self):
        while True:
            try:
                pos = 0
                while True:
                    pos = self.buffer.find(b"\0")
                    if pos >= 0:
                        break
                    self.buffer += self.serial.read(128)

                data = cobs.decode(self.buffer[:pos])

                cmd = data[0]
                body = data[1:]

                self.buffer = self.buffer[pos+1:]
                return cmd, self.encoders[cmd](body)
            except SerialException as e:
                logging.exception(e)
                self._reopen()
            except Exception as e:
                logging.exception(e)

    def __getattr__(self, item):
        return self.cmds[item]


if __name__ == "__main__":
    s = Serial("/dev/ttyUSB0", baudrate=460800)
    c = Client(s)


    def reading():
        print("started")

        # drop garbage
        s.read_until(b"\0")

        while True:
            try:
                print(c.read_next())
            except Exception as e:
                logging.exception(e)


    import threading

    threading.Thread(target=reading).start()

    import time

    while True:
        c.pos(x=int(170 / 2), y=80)
        time.sleep(1)
        c.pos(x=int(170 / 2), y=160)
        time.sleep(1)
