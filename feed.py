import serial
import time
import random
import sys

ser = serial.Serial('/dev/pts/7')

rand = len(sys.argv) != 2


def from_file(file_name):
    lines = list(open(file_name))

    fixers = {
        'RX': int,
        'RY': int
    }

    while True:
        for line in lines:
            row = dict(i.split('=', 2) for i in line.strip().split(' '))

            for k, fixer in fixers.items():
                row[k] = fixer(row[k])

            yield row


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


iter = from_rand() if len(sys.argv) != 2 else from_file(sys.argv[1])
#processor = null_processor
processor = Fixer().process


for row in iter:
    row = processor(row)
    line = " ".join(["{}={}".format(k, row[k]) for k in row.keys()])
    print(line)
    ser.write((line + "\n").encode())
    time.sleep(0.02)