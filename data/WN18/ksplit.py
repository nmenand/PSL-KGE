#!/bin/usr/env python3

import sys
import math
import random

data = []
k = int(sys.argv[2])
dataFile = sys.argv[1]

# Store data in list of triples
with open(dataFile, 'r') as fp:
    for line in fp:
        data.append(line.strip('\n').split(' '))

dataLen = len(data)
testBound = math.floor(.30 * dataLen)

# Randomize data list based on seed and create  k- train/test file pairs.
SEED = 999
for i in range(1, k+1):
    random.shuffle(data)
    trainFile = 'split' + str(i) + '_' + 'train' + '.txt'
    testFile = 'split' + str(i) + '_' + 'test' + '.txt'
    # Split data into 70% train and 30% test
    with open(trainFile, 'w+') as train, open(testFile, 'w+') as test:
        for lineNum in range(0, dataLen):
            if lineNum < testBound:
                test.write(data[lineNum][0] + '\t' + data[lineNum][1] + '\t' + data[lineNum][2] + '\n')
            else:
                train.write(data[lineNum][0] + '\t' + data[lineNum][1] + '\t' + data[lineNum][2] + '\n')
