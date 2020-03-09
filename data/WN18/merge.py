#!/usr/bin/env python3

import sys

data1 = data2 = data3 =  ''
with open(sys.argv[1], 'r') as fp:
    data1 = fp.read()

with open(sys.argv[2], 'r') as fp:
    data2 = fp.read()

with open(sys.argv[3], 'r') as fp:
    data3 = fp.read()

data1 += data2
data1 += data3

with open(sys.argv[4], 'w') as fp:
    fp.write(data1)

