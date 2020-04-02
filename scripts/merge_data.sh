#! /bin/bash

readonly BASE_DIR=$(realpath "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )")

cat ${BASE_DIR}/$1/*.txt >  ${BASE_DIR}/$1/data.txt
