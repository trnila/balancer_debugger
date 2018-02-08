import serial
import time
import random
import sys

ser = serial.Serial('/dev/pts/7')

rand = len(sys.argv) != 2


def r():
    lines = list(open(sys.argv[1]))

    while True:
        for i in lines:
            yield i


iter = r()

while True:
    if rand:
        ser.write(('RX={} RY={} USX={} USY={}\n'.format(
            random.randint(0, 65000), random.randint(0, 65000),
            random.uniform(0.65, 0.85),
            random.uniform(0.65, 0.85),
        ).encode()))
    else:
        ser.write(next(iter).encode())

    time.sleep(0.02)