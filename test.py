import matplotlib.pyplot as plt 
import math
import numpy as np
import random
import sys

random.seed(1)

def gen(fn):
    x = np.arange(0.0, 10, 0.1) 
    for i in x:
        val = fn(i)

        if random.randint(0, 10) < 5:
            val = 3

        yield val


def from_input(filename):
    for line in open(filename):
        row = dict([i.split("=", 2) for i in line.strip().split(" ")])
        yield [int(i) for i in [row['RX'], row['RY']]]


class Moving:
    def __init__(self):
        self.vals = []

    def add(self, value):
        self.vals.append(value)
        if len(self.vals) > 10:
            self.vals.pop(0)

    def replace(self, value):
        self.vals = self.vals[:-1] + [value]


    def get(self):
        s = sorted(self.vals)
        return s[int(len(s) / 2)]

        remove = 3
        s = s[remove:len(s) - remove]

        if len(s) <= 0:
            return 0

        return sum(s) / len(s)




if len(sys.argv) > 1:
    inp = from_input(sys.argv[1])
else:
    inp = zip(gen(math.sin), gen(lambda x: -math.sin(x)))

y = []
prev = [0, 0]
speed = [0, 0]
moving = [Moving(), Moving()]
for read in inp:
    print(read)
    write = []
    for i, val in enumerate(read):
        if i > 0:
            continue

        moving[i].add(val)

#        if abs(val - moving[i].get()) > 1000  and 0:
 #           val = prev[i] + speed[i] 
  #      speed[i] = val - prev[i]

        v = moving[i].get()
        if v > 60000:
            v = prev[i] + speed[i]
            moving[i].replace(v)



        prev[i] = v
        write.append(val)
        write.append(v)
    y.append(write)


plt.plot(range(0, len(y)),y,'-')
plt.show()
