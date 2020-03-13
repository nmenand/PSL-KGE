#! /bin/bash

readonly BASE_DIR=$(realpath "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )")

# $1 is the dat file. Assumed to be entire data to be split where a line is a tab separated triple
# $2 is the config file

python3 ${BASE_DIR}/scripts/k_split.py $1 $2

