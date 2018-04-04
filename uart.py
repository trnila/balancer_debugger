import itertools
import logging

from cobs import cobs
from serial import Serial, SerialException
import struct


CMD_RESPONSE = 128
CMD_GETTER = 64

CMD_RESET = 0
CMD_POS = 1
CMD_PID = 2

CMD_GETPOS = CMD_GETTER | CMD_POS
CMD_GETPID = CMD_GETTER | CMD_PID
CMD_GETDIM = CMD_GETTER | (CMD_PID + 1)

CMD_MEASUREMENT = 0 | CMD_RESPONSE


def encode(cmd_id, fmt="", *args):
    binary = struct.pack("=B" + fmt, cmd_id, *args)
    return cobs.encode(bytearray(binary))


class MeasureDecoder:
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


class BinaryDecoder:
    def __init__(self, fmt):
        self.fmt = fmt

    def __call__(self, body, *args, **kwargs):
        return struct.unpack("=" + self.fmt, body)


class ClientBase:
    def __init__(self, serial: Serial):
        self.serial = serial
        self.serial.timeout = 0.02
        self.encoders = {
            CMD_MEASUREMENT | CMD_RESPONSE: MeasureDecoder(),
            CMD_GETPOS | CMD_RESPONSE: BinaryDecoder("II"),
            CMD_GETPID | CMD_RESPONSE: BinaryDecoder("ddd"),
            CMD_GETDIM | CMD_RESPONSE: BinaryDecoder("II"),
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

    def _encode(self, cmd, data):
        if cmd in self.encoders:
            return self.encoders[cmd]

        return data

    def send(self, data):
        self.serial.write(data + b"\0")


class Client(ClientBase):
    def reset(self):
        self.send(encode(CMD_RESET))

    def set_pid(self, p, i, d):
        self.send(encode(CMD_PID, "ddd", p, i, d))

    def set_pos(self, x, y):
        self.send(encode(CMD_POS, "II", x, y))

    def get_pid(self):
        self.send(encode(CMD_GETPID))

    def get_pos(self):
        self.send(encode(CMD_GETPOS))

    def get_dim(self):
        self.send(encode(CMD_GETDIM))


if __name__ == "__main__":
    s = Serial("/dev/ttyUSB0", baudrate=460800)
    c = Client(s)


    def reading():
        print("started")

        # drop garbage
        s.read_until(b"\0")

        while True:
            try:
                cmd, data = c.read_next()
                if cmd != 128:
                    print((cmd, data))
            except Exception as e:
                logging.exception(e)


    import threading

    threading.Thread(target=reading).start()

    import time

    while True:
        c.get_pos()
        time.sleep(1)

        c.get_pid()
        time.sleep(1)
