import errno
import logging

import serial
import time
import random
import sys
from subprocess import Popen
import argparse

SERIAL_WRITER = '/tmp/ball_balancer.device'
SERIAL_READER = '/tmp/ball_balancer.client'
CONNECT_TRIES = 10


def from_file(file_name):
    lines = list(open(file_name))

    while True:
        for line in lines:
            def fix(v):
                return v[0], float(v[1])
            try:
                yield dict(fix(i.split('=', 2)) for i in line.strip().split(' '))
            except BaseException as e:
                logging.exception(e)


def from_rand():
    while True:
        yield {
            'RX': random.randint(0, 65000),
            'RY': random.randint(0, 65000),
            'USX': random.uniform(0.65, 0.85),
            'USY': random.uniform(0.65, 0.85)
        }


def null_processor(row):
    return row


class Fixer:
    def __init__(self):
        self.keys = ['RX', 'RY']
        self.prev = dict([(i, 0) for i in self.keys])
        self.speed = dict([(i, 0) for i in self.keys])
        self.fails = 0

    def process(self, row):
        for i in self.keys:
            v = row[i]
            if v > 60000:
                v = self.prev[i] + self.speed[i]
                self.fails += 1
                if self.fails > 20:
                    v = 65000
            else:
                self.fails = 0
            self.speed[i] = v - self.prev[i]

            row[i] = v
        return row


p = Popen([
    "socat",
    "pty,raw,echo=0,link={}".format(SERIAL_WRITER),
    "pty,raw,echo=0,link={}".format(SERIAL_READER)
])

for i in range(0, CONNECT_TRIES):
    try:
        ser = serial.Serial(SERIAL_WRITER)
        break
    except serial.SerialException as e:
        if e.errno == errno.ENOENT:
            time.sleep(0.1)

parser = argparse.ArgumentParser()
parser.add_argument('--print', '-p', help='print each line to stdout', action='store_true')
parser.add_argument('--file', '-f', help='input file with captured data')
parser.add_argument('--processor', help='path to processor script, script must contain process(row) function')

args = parser.parse_args()

iter = from_rand() if not args.file else from_file(args.file)
processor = null_processor
if args.processor:
    with open("processors/test.py") as f:
        exec(f.read())

for row in iter:
    row = processor(row)
    line = " ".join(["{}={}".format(k, row[k]) for k in row.keys()])
    if args.print:
        print(line, flush=True)
    ser.write((line + "\r\n").encode())
    ser.flushOutput()
    time.sleep(0.02)