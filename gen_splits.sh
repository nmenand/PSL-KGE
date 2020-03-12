#! /bin/bash

# $1 is the dat file. Assumed to be entire data to be split where a line is a tab separated triple
# $2 is the config file
python3 k_split.py $1 $2
