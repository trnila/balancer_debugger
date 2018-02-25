#!/usr/bin/env python3
import logging
import sys

from input import parse_line

if len(sys.argv) <= 1:
    print("serial2csv.py serialcapture")
    exit(1)

lines = []

with open(sys.argv[1]) as f:
    for line in f:
        try:
            d = parse_line(line)
            lines.append(d)
        except Exception as e:
            logging.exception(e)

key_sizes = sorted([len(i) for i in lines])
required_size = key_sizes[int(len(key_sizes) / 2)]


correct_lines = list(filter(lambda i: len(i) == required_size, lines))
header = correct_lines[0].keys()
print(",".join(header))

for line in correct_lines:
    out = ",".join([str(line[key]) for key in correct_lines[0].keys()])
    print(out)


